import cv2
import numpy as np
import os
def CreateFolder(dir_name):
	if not os.path.exists(dir_name):
        	os.makedirs(dir_name)


faceDetect =cv2.CascadeClassifier('haarcascade_frontalface_default.xml');

Images_Per_Expression = 5000
LabMemberID = raw_input('Enter Lab Member ID')
ExpressionNo = int(raw_input('Enter Expression No'))
ImageIndex = int(raw_input('Enter Image No'))
CamSrc = "Recording/Recording_"+str(LabMemberID)+"_"+str(ExpressionNo)+".avi"
print(CamSrc)
cam = cv2.VideoCapture(CamSrc);

EndImageIndex = ExpressionNo * Images_Per_Expression 
DummyCounterForProperPose = 5000

DestinationFolder = "LabFacesByID/"+ LabMemberID 
CreateFolder(DestinationFolder)

while(True):
	ret, img = cam.read();
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces = faceDetect.detectMultiScale(gray,1.3,5);
	for(x,y,w,h) in faces:
		cv2.imwrite(DestinationFolder + "/User."+str(LabMemberID)+"."+str(ImageIndex)+".jpg",gray[y:y+h,x:x+w])
		cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
		cv2.waitKey(100);
		ImageIndex +=1
		#for i in range(DummyCounterForProperPose):
		#	pass
	cv2.imshow("Face", img);
	print("hello")
	if (ImageIndex>EndImageIndex):
		print("oh no")
		break
print(ImageIndex)
cam.release()
cv2.destroyAllWindows()
