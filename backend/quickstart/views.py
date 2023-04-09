from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import VideoSerializer
from .models import Video

import cv2
import numpy as np
import tensorflow as tf
import ffmpeg    

# Loading the model
model = tf.keras.models.load_model("./savedModels/model.h5")

@api_view(['POST', 'GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/video/create',
            'method': 'POST',
            'body': {'name': "username", 'video': "video file"},
            'description': 'Upload video to server'
        },
        {
            'Endpoint': '/video/process',
            'method': 'POST',
            'body': {'name': "username", 'video': "video file"},
            'description': 'Process video and return count'
        },
        {
            'Endpoint': '/video/',
            'method': 'GET',
            'body': {},
            'description': 'Get videos'
        }
    ]
    return Response(routes)

@api_view(['GET'])
def getVideos(request):
    videos = Video.objects.all()
    serializer = VideoSerializer(videos, many = True)
    return Response(serializer.data)

@api_view(['POST'])
def createVideo(request):
    data = request.data
    video = Video.objects.create(
        user = data['user'],
        video = data['video']
    )
    serializer = VideoSerializer(video, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def processVideo(request):
    
    data = request.data
    
    # Create Video object
    video = Video.objects.create(
        user = data['user'],
        video = data['video']
    )

    # Start processing frames of the video 
    cap = cv2.VideoCapture(str(video.video))

    success, frame1 = cap.read()

    out = cv2.VideoWriter('result_video.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 60.0,(int(cap.get(3)),int(cap.get(4))))
    # out2 = cv2.VideoWriter('rgb_video.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 60.0,(int(cap.get(3)),int(cap.get(4))))

    prev = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame1)
    hsv[...,1] = 255

    # Variables for repetition counting
    repetitions = 0
    upward = 0
    downward = 0
    no_movement = 0
    current_move = 0
    initial = -1
    i = 0

    while (cap.isOpened()):
        i += 1
        success, frame2 = cap.read()
        if not(success): break

        # Get Optical Flow
        next = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prev,next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
        hsv[...,0] = ang*180/np.pi/2
        hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
        bgr = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)

        # Preprocess frame
        image = cv2.resize(bgr, (64, 64))
        image = image.reshape((1,) + image.shape)
        image = image/255.0

        # Classify frame
        move_type = np.argmax(model.predict(image), axis=-1)[0]
        
        if move_type == 2: # is upward
            upward += 1
            if upward == 3 and initial != -1:
                current_move = 2
            elif upward > 1:
                downward = 0 
                no_movement = 0
        elif move_type == 0: # is downward
            downward +=1 
            if downward == 3:
                if initial == -1:
                    initial = 0
                if current_move == 2:
                    repetitions+=1
                current_move = 0
            elif downward > 0:
                upward = 0
                no_movement = 0
        else: # is no_movement
            no_movement += 1
            if no_movement == 15:
                current_move = 1
            elif no_movement > 10:
                upward = 0
                downward = 0 

        # Add label to frame
        cv2.putText(frame2, "Repetitions: "+ str(repetitions), (1,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)

        out.write(frame2)
        # out2.write(bgr)

        prev = next

    # Delete processed video from DB
    Video.objects.filter(user=data['user']).delete()
    
    print("Video is processed")
    print(repetitions)

    out.release()
    # out2.release()
    cap.release()

    return Response({"repetitions": repetitions})