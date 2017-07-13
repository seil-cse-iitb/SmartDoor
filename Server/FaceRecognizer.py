import cv2
import numpy as np
import time
import sys
sys.path.append('../')
from CamParam import *

def Top3Faces(FaceDetector, FaceRecognizer, CameraSrcIP, RoomID, SessionID):
	#EnterTime = str(time.localtime()[3]).zfill(2)+ "~" + str(time.localtime()[4]).zfill(2)+ "~" +str(time.localtime()[5]).zfill(2)
	#EnterDay = "==" + str(time.localtime()[2]).zfill(2)+ "-" +  str(time.localtime()[1]).zfill(2) + "-" + str(time.localtime()[0]) 
	#Enter_Time_Day = EnterTime + EnterDay
	Enter_Time_Day =  time.strftime("%H~%M~%S==%d-%m-%Y")
	RoomIndex = int(RoomID) - 1
	O_V_File = Enter_Time_Day + ".avi"
	Output_V_File = VideoRecordingFolder + RoomID +'/'  + O_V_File
	cam = cv2.VideoCapture(CameraSrcIP)
	cam.set(3,CamConfig["Resolution"][0])
	cam.set(4,CamConfig["Resolution"][1])
	fourcc = cv2.cv.CV_FOURCC(*'MJPG')
	out = cv2.VideoWriter(Output_V_File, fourcc, CamConfig["FrameRate(fps)"], CamConfig["Resolution"])	
	PersonID =0
	SetOfFaces =[]
	TotalFaceDetected = 0
	FrameNo = 1
	FaceConfidenceIndices = {} #ID, Tuple(Conf and No_Of_Id)
	OffFrame   	= False
	TooClose   	= False
	TimeOut    	= False
	NotClickedPic 	= True
	TimeOutTolerance = 0
	#font =cv2.cv.InitFont(cv2.cv.CV_FONT_HERSHEY_COMPLEX_SMALL,3,1,0,1)
	Click_Time 	= time.time() +	Take_CamShot[RoomIndex]
	End_Time 	= time.time() + Time_Out[RoomIndex]
	Cam_Start_Time  = time.time()
	while(True):
		ret, img = cam.read();
		if ret==True:
			gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			out.write(img)
			if (time.time() > Click_Time and NotClickedPic):
				#Out_I_File = 	str(time.localtime()[3]).zfill(2)+ "~" + str(time.localtime()[4]).zfill(2)+ "~" + 							str(time.localtime()[5]).zfill(2)+ EnterDay + ".png"
				Out_I_File = time.strftime("%H~%M~%S==%d-%m-%Y") + ".png"
				Output_I_File = ImageCaptureFolder +  RoomID +'/'  + Out_I_File
				cv2.imwrite(Output_I_File, img[Pic_Frame_Top[RoomIndex]:Pic_Frame_Bottom[RoomIndex],Pic_Frame_Left[RoomIndex]:Pic_Frame_Right[RoomIndex]])
				NotClickedPic = False
			faces = FaceDetector.detectMultiScale(gray,1.3,5);
			for(x,y,w,h) in faces:					
				PersonID,conf = FaceRecognizer.predict(gray[y:y+h,x:x+w])
				#cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
				#cv2.cv.PutText(cv2.cv.fromarray(img),str(PersonID),(x,y+h),font,(0,255,255))
				#cv2.imwrite("Sample/Frame_"+str(FrameNo)+".jpg",img)
				FaceInfo =[]
				Area =  w*h
				FaceInfo.append(Area)
				Identity = int(PersonID)
				Confidence = int(conf)
				FaceInfo.append(Identity)
				FaceInfo.append(Confidence)
				FaceInfo.append(FrameNo)	
				SetOfFaces.append(FaceInfo)
		
				if Identity not in FaceConfidenceIndices.keys():
					FaceConfidenceIndices[Identity] = (Confidence,1,FrameNo,FrameNo)
				else:
					(TempConf,Count,MinFrameNo,MaxFrameNo) = FaceConfidenceIndices[Identity]
					Confidence += TempConf
					Count +=1 
					FaceConfidenceIndices[Identity] = (Confidence,Count,MinFrameNo, FrameNo)
				FrameNo +=1 
				TotalFaceDetected +=1
			
				if( x < Frame_In_Left[RoomIndex] or x > Frame_In_Right[RoomIndex]):
					OffFrame = True
					print("offframe")
				if(Area > Max_Face_Frame_Area[RoomIndex]):
					TooClose = True
					print("TooClose")			

			#cv2.imshow("Face", img);
			if (time.time() > End_Time):
				TimeOutTolerance +=1
			if(TimeOutTolerance > Time_Out_Tolerance[RoomIndex]):
				TimeOut = True
			if (OffFrame or TooClose or TimeOut):
				break
		else:
			break
	cam.release()
	out.release()
	#cv2.destroyAllWindows()	
	Cam_End_Time  = time.time()
	Cam_Time	= Cam_End_Time - Cam_Start_Time 
	print("Camera Record Time: ",Cam_Time)
	ConfidenceFactor = []
	for x,(y,z,MinF, MaxF) in FaceConfidenceIndices.items():
		ConfidenceFactor.append([x,y/TotalFaceDetected, z,MinF, MaxF])
	ConfidenceFactor.sort(key=lambda x: x[2], reverse =True)
	TopN = len(ConfidenceFactor)
	if TopN != 0:
		ImagePredictedID = str(ConfidenceFactor[0][0])
	else:
		ImagePredictedID = "0"

	if TopN > 3:
		TopN = 3
		return(Enter_Time_Day, ConfidenceFactor[:3], TotalFaceDetected, TopN)
	else:
		return(Enter_Time_Day, ConfidenceFactor, TotalFaceDetected, TopN)




