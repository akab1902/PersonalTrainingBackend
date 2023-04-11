# PersonalTrainingBackend
Backend for Personal Training App hosts the pre-trained model and implements the preprocessing of the video received from the frontend. After a video is preprocessed, it feeds those video frames into a machine-learning algorithm to classify and identify the movements. When the movements are detected, it counts the repetitions and returns the amount back to the mobile application.

### Prerequisites: 
-	Python 3.9 or newer
-	Tensorflow 
-	Other required packages are in backend/requirements.txt. Run "pip install requirements.txt" to install them:
  numpy, matplotlib, django, django-rest-framework, ffmpeg, opencv-python 
- For dataset used in model training check out this link: https://drive.google.com/file/d/1MNGGdr1X0X4g_VdcPBk0R_pcml_95lXn/view?usp=share_link 

### Steps:
1.	Clone git repository “PersonalTrainingAppBackend”
2.	In terminal navigate to “backend” folder inside “PersonalTrainingAppBackend”
3.	Run “python manage.py runserver”
4.	Your server is running on localhost:8000
