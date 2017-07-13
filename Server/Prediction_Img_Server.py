import socket
import MySQLdb 
import numpy as np
import pandas as pd
from sklearn.externals import joblib
import time
import datetime
import sys
from _mysql_exceptions import OperationalError
from _mysql_exceptions import IntegrityError
#import httplib2
import cv2
from FaceRecognizer import *  
import os


HOST = "10.129.23.161" 
USER = "writer" 
PSWD = "datapool" 
DB = "datapool"

def DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts ):
	if Local_Global == 1:
		(con, cursor) = ConnectDataBase()
		sql= """INSERT INTO `%s`.`SmartDoor_Diagnostics` 
			(`Failure TimeStamp`, `Failure Event`, `Failure Attempts`) 
			VALUES ('%s', '%s', '%s')"""%(DB, Failure_TimeStamp, FailureEvent, FailedAttempts )

		try:
			cursor.execute(sql)
			con.commit()
		except:
			con.rollback()
			if FailedAttempts == '': 
				FailedAttempts ='Not Applicable'
			print("Failed At Time" , Failure_TimeStamp)
			print("Failure Event", FailureEvent)
			print("FailedAttempts", FailedAttempts)
		cursor.close()
		DisconnectDataBase(con)
	else:
		if FailedAttempts == '': 
			FailedAttempts ='Not Applicable'
		print("Failed At Time" , Failure_TimeStamp)
		print("Failure Event", FailureEvent)
		print("FailedAttempts", FailedAttempts)


def ConnectDataBase():    
	CouldNotConnectToDataBase = True
	CouldNotGetCursor = True
	#connect to the database
	print ("Trying to Connect To Database")
	NotReportedDBErr = True
	NotReportedCurErr = True
	while CouldNotGetCursor:
		while CouldNotConnectToDataBase:
			try:
				con = MySQLdb.connect(HOST, USER, PSWD, DB)
				CouldNotConnectToDataBase = False
			except  OperationalError:
				CouldNotConnectToDataBase = True
				if NotReportedDBErr:		
					Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
					FailureEvent = "Failed to Connect to Database"
					Local_Global = 0 #Local is 0, Global is 1
					FailedAttempts = '' 
					DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
					NotReportedDBErr = False


		else:
			print ("Connected To Database")	
			try:
				cursor = con.cursor()
				CouldNotGetCursor = False
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				if NotReportedCurErr:		
					Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
					FailureEvent = "Failed to get the Database Cursor after Connection" + e
					Local_Global = 0 #Local is 0, Global is 1
					FailedAttempts = '' 
					DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
					NotReportedCurErr = False
	else:
		print("Cursor is Fetched") 
		return (con, cursor)

def DisconnectDataBase(con):
	try:
		con.close()
		print("Database Connection Closed")
	except:
		print("Server -- Could Not Close Database Connection")





def UpdateOn_Complete_Prediction(PredictedName, SID):
	(con, cursor) = ConnectDataBase()
	sql= """UPDATE `%s`.`SmartDoor_PeopleEntryExitDetail` 
		SET `Predicted_Name`='%s' 
		WHERE `SID`='%s'; """ %(DB, PredictedName, SID)
	try:
		cursor.execute(sql)		
		con.commit()
		print("Updated the predicted name through Complete Prediction for Session ID : ", SID)
	except:
		con.rollback()
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "SQL Error: Could not update the predicted name (Height, Weight, Image) of the Session ID : " + str(SID)
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
	cursor.close()
	DisconnectDataBase(con)

def GetNameForUserImageID(Identity, RoomNo):
	(con, cursor) = ConnectDataBase()
	result = None
	sql=  """SELECT Name
		FROM `%s`.`SmartDoor_Face_Identity` 
		WHERE Identity = '%s' 
		AND  Room_No = '%s' """  %(DB, Identity, RoomNo) 
	try:
		cursor.execute(sql)
		result = cursor.fetchone()
		print(result)
	except:
		print("SQL Error: Could not get the name for the ID given ")
		#Report Error
	cursor.close()
	DisconnectDataBase(con)
	if result is None:
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "Updation Error: There is no such Identity with that Room No!"
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
	else:
		Name = result[0]
		return Name

def StorePredictedImageResult(i,ConfidenceFactor_i, Name, SessionID):
	Rank       = (i+1)
	Identity   = ConfidenceFactor_i[0]
	Confidence = ConfidenceFactor_i[1]
	Count	   = ConfidenceFactor_i[2]
	MinFrameNo = ConfidenceFactor_i[3]
	MaxFrameNo = ConfidenceFactor_i[4]
	
	(con, cursor) = ConnectDataBase()
	sql=  """INSERT INTO `%s`.`SmartDoor_Face_PredictionRank` 
		(`SessionID`, `RankID`, `Name`, 
		`ID`, `Confidence`, `Count`, 
		`MinFrameNumber`, `MaxFrameNumber`) 
		VALUES ('%s', '%s', '%s','%s', '%s', '%s', '%s', '%s')
		""" % (DB, SessionID, Rank, Name,Identity, Confidence, Count, MinFrameNo,MaxFrameNo)
	print(sql)
	ImagePredictedResult = [Name, Rank, Confidence, Count, MinFrameNo,MaxFrameNo]
	try:
		cursor.execute(sql)		
		con.commit()
	except:
		con.rollback()
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "SQL Error: Could not insert the predicted names, confidence factors and ranks of the Session ID : " +str(SessionID)
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
	cursor.close()
	DisconnectDataBase(con)
	return ImagePredictedResult

def InferThro_Img_HW_Prediction(HW_PredictionTable , ImagePredictionTable, SessionID):
	NewList = []
	if HW_PredictionTable is not None:
		for i in HW_PredictionTable:
			for j in ImagePredictionTable:
				if i[0].lower() == j[0].lower():
					Name = [ i[0].lower() ] 
					HWResult  = i[1:]
					ImgResult = j[1:]
					#Arbitrary Equation
					InferResult = [ (i[2]*100/i[1])  + (j[2] + j[3] + j[4] + j[5] ) / j[1] ]
					List = []
					List.extend(Name)
					List.extend(InferResult)
					List.extend(HWResult)
					List.extend(ImgResult)
					NewList.append(List)
		NewList.sort(key = lambda x : x[1] , reverse = True)
		if len(NewList) > 0:
			Name = NewList[0][0]
		elif len(ImagePredictionTable) >0:
			Name = ImagePredictionTable[0][0]
		elif len(HW_PredictionTable) >0:
			Name = HW_PredictionTable[0][0]
		else:
			Name = "UNKNOWN"
			Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
			FailureEvent = "Prediction Error (Height, Weight & Image Processed) for Session ID: " + str(SessionID)
			Local_Global = 1 #Local is 0, Global is 1
			FailedAttempts = '' 
			DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
		return Name
	else:
		if len(ImagePredictionTable) >0:
			Name = ImagePredictionTable[0][0]
		else:
			Name = "UNKNOWN"
			Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
			FailureEvent = "Prediction Error (Image Only Processed) for Session ID: " + str(SessionID)
			Local_Global = 1 #Local is 0, Global is 1
			FailedAttempts = '' 
			DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
		return Name

def Fetch_HWPrediction(SessionID):
	(con, cursor) = ConnectDataBase()
	sql=  """SELECT RankID, Name, Probability 
		FROM `%s`.`SmartDoor_HW_PredictionRank` 
		WHERE SessionID = '%s' """  %(DB, SessionID) 

	try:
		cursor.execute(sql)
		results = cursor.fetchall()
	except:
		print("SQL Error: Could not get the Height and Weight Prediction Results of the Session ID")
		#Report Error
	cursor.close()
	DisconnectDataBase(con)
	if results is None or len(results) < 1:
		print("Updation Error: Could not get the Height and Weight Prediction Results of the Session ID")
	else:
		HWPredictionResult = []
		for record in results:
			Name = record[1]
			Rank = int(record[0])
			Probability = float(record[2])
			HWPredictionResult.append((Name,Rank,Probability))
		return HWPredictionResult

def EstablishConnectionToRPi(PORT):
	sck = socket.socket() 
	sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#port = 12346
	sck.bind(('',PORT))
	sck.listen(5)
	RpiConn, RPIAddr = sck.accept()
	return RpiConn, RPIAddr 


if __name__ == '__main__':
	RoomID = sys.argv[1]
	PORT = sys.argv[2]
	if (RoomID,PORT) not in ( ('1','12347'), ('2','12349'))  : #SEIL - 1, ERTS - 2
		exit();
	print(60*'-')
	''' Face Detector & Recognizer'''
	print(FaceRecognizerYMLFile[int(RoomID)-1])
	if os.path.exists(FaceDetectorXMLFile):
		FaceDetector =cv2.CascadeClassifier(FaceDetectorXMLFile)
		print("Loaded Face Detector File")
	else:
		FailureEvent = "Cannot loaded Face Detector File"
		print(FailureEvent)
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
		exit();
	if os.path.exists(FaceRecognizerYMLFile[int(RoomID)-1]):
		FaceRecognizer = cv2.createLBPHFaceRecognizer()
		FaceRecognizer.load(FaceRecognizerYMLFile[int(RoomID)-1])
		print("Loaded Face Recognizer File")
	else:
		FailureEvent = "Cannot loaded Face Recognizer File"
		print(FailureEvent)
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
		exit();
	print(60*'-')
	RunScript = True
	while RunScript:
		RpiConn, RPIAddr  =  EstablishConnectionToRPi(int(PORT))
		SessionStr = RpiConn.recv(15)
		#SessionStr = '2/R'
		SessionStrS = SessionStr.split('/')
		ValidMsg = (len(SessionStrS) == 2)
		if ValidMsg:
			SessionStrS[1]= SessionStrS[1].strip('\r\n') 
			ValidMsg = (SessionStrS[1] == 'R') 
		if ValidMsg:
			SessionID = SessionStrS[0]
			print "start camera.........."
			(Enter_Time_Day, ConfidenceFactor, TotalFaceDetected, NoOfPrediction)  		= 	 						 Top3Faces(FaceDetector, FaceRecognizer, SmartDoorCameraIP[int(RoomID)-1], RoomID, SessionID)
			print("==================================")
			print(ConfidenceFactor)
			ImagePredictionTable = []
			for i in range(len(ConfidenceFactor)) :
				Name = GetNameForUserImageID(ConfidenceFactor[i][0], RoomID)
				ImagePredictedResult = StorePredictedImageResult(i,ConfidenceFactor[i], Name, SessionID)
				ImagePredictionTable.append(ImagePredictedResult)
				ImagePredictionTable.sort(key = lambda x : x[1])
			print("==================================")
			print(TotalFaceDetected)
			print("PPL are " , NoOfPrediction)
			print "Stop Camera.........." 
			#Assumption: HW values will be recorded before the camera runs
			HW_PredictionTable = Fetch_HWPrediction(SessionID)			
			PredictedName = InferThro_Img_HW_Prediction(HW_PredictionTable , ImagePredictionTable, SessionID)
			UpdateOn_Complete_Prediction(PredictedName, SessionID)
		else:
			print ("An invalid msg received from RPI ", RPIAddr)
            
