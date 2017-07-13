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



def Get_Height_Weight(SID):
	(con, cursor) = ConnectDataBase()
	sql= """SELECT Height, Weight 
		FROM   SmartDoor_PeopleEntryExitDetail
		WHERE  SID  = '%s' """ %(SID)
	try:
		cursor.execute(sql)
		results = cursor.fetchone()
	except:
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "SQL Error: Could not get the Height and Weight of the Session ID"
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
	cursor.close()
	DisconnectDataBase(con)
	if results is None:
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "Updation Error: Could not get the Height and Weight of the Session ID"
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
	else:
		HW = [float(results[0]),float(results[1])]
		HW = np.array(HW)
		HW = HW.reshape(1,2)
		return HW


def UpdateOn_Height_Weight_Prediction(PredictedName, SID):
	(con, cursor) = ConnectDataBase()
	sql= """UPDATE `%s`.`SmartDoor_PeopleEntryExitDetail` 
		SET `Predicted_Name`='%s' 
		WHERE `SID`='%s'; """ %(DB, PredictedName, SID)
	try:
		cursor.execute(sql)		
		con.commit()
		print("Updated the predicted name through height and weight for Session ID : ", SID)
	except:
		con.rollback()
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "SQL Error: Could not update the predicted name (Height, Weight) of the Session ID : " + str(SID)
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
	cursor.close()
	DisconnectDataBase(con)

def UpdateRankOfHWPrediction(SessionID, Rank, Name, Probability):
	(con, cursor) = ConnectDataBase()
	sql=  """INSERT INTO `%s`.`SmartDoor_HW_PredictionRank` 
		(`SessionID`, `RankID`, `Name`, `Probability`) 
		VALUES ('%s', '%s', '%s', '%s')"""  %(DB, SessionID, Rank, Name, Probability ) 

	try:
		cursor.execute(sql)		
		con.commit()
		print("Inserted the predicted names with probabilities and ranks for Session ID : ", SessionID)
	except:
		con.rollback()
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "SQL Error: Could not insert the predicted names, probabilities and ranks of the Session ID : " +str(SessionID)
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
	cursor.close()
	DisconnectDataBase(con)

def EstablishConnectionToRPi(PORT):
	sck = socket.socket() 
	sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sck.bind(('',PORT))
	sck.listen(5)
	RpiConn, RPIAddr = sck.accept()
	return RpiConn, RPIAddr 

def getCalenderInfo(pred):
    scope = 'https://www.googleapis.com/auth/calendar'
    flow = flow_from_clientsecrets('client_secret.json', scope=scope)
    
    storage = Storage('credentials.dat')
    credentials = storage.get()
    
    class fakeargparse(object):  # fake argparse.Namespace
        noauth_local_webserver = True
        logging_level = "ERROR"
    flags = fakeargparse()
    
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, flags)
    
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build('calendar', 'v3', http=http)
    
    # get the next 1 hours of events
    epoch_time = time.time()
    start_time = epoch_time - 3600   #1 hour ago
    end_time = epoch_time + 3600  # 1 hours in the future
    tz_offset = - time.altzone / 3600
    if tz_offset < 0:
        tz_offset_str = "-%02d00" % abs(tz_offset)
    else:
        tz_offset_str = "+%02d00" % abs(tz_offset)
        
    start_time = datetime.datetime.fromtimestamp(start_time).strftime("%Y-%m-%dT%H:%M:%S") + tz_offset_str
    end_time = datetime.datetime.fromtimestamp(end_time).strftime("%Y-%m-%dT%H:%M:%S") + tz_offset_str
    
    print "Getting calendar events between: " + start_time + " and " + end_time
    
    inlab = []
    conf = confusionset[pred]
    for name in conf:
        url = calendar_id[name]
        events = service.events().list(calendarId=url, timeMin=start_time, timeMax=end_time, singleEvents=True).execute()
        if events['items']:
            inlab.append(name)
    
    print inlab
    print list(set(inlab) & set(conf)) #two find common elements between two lists -> reduction of confusion list

if __name__ == '__main__':
	RoomID = sys.argv[1]
	PORT = sys.argv[2]
	RunScript = False
	if (RoomID,PORT) in ( ('1','12345'), ('2','12348'))  : #SEIL - 1, ERTS - 2
		PORT = int(PORT)
		RunScript = True
	#Load The Classifier
	PKL_File = 'HeightWeightModel_'+ RoomID +'/RFCforSmartDoor.pkl'
	clf = joblib.load(PKL_File)
	while RunScript:
		RpiConn, RPIAddr  =  EstablishConnectionToRPi(PORT)
		SessionStr = RpiConn.recv(15)
		SessionStrS = SessionStr.split('/')
		ValidMsg = (len(SessionStrS) == 3)
		if ValidMsg:
			SessionStrS[2]= SessionStrS[2].strip('\r\n') 
			ValidMsg = (SessionStrS[1] == 'E') 
			Entry = (SessionStrS[2] == 'I')	
		if ValidMsg:
			SessionID = SessionStrS[0]
			HW = Get_Height_Weight(SessionID)
			PredictedNameHW = clf.predict(HW)[0]
			UpdateOn_Height_Weight_Prediction(PredictedNameHW, SessionID)
			#getCalenderInfo(PredictedNameHW) #uncomment when wish to include calender data
			if Entry :
				classes_prob_mapping = zip(clf.classes_, clf.predict_proba(HW)[0])
				classes_prob_mapping.sort(key=lambda tup: tup[1], reverse=True)
				Top_3_Predictions = classes_prob_mapping[:3]
				Rank = 0
				for a in Top_3_Predictions:
					Name = a[0]
					Probability = a[1]
					Rank +=1
					UpdateRankOfHWPrediction(SessionID, Rank, Name, Probability)
			print("Predicted Name based on Height and Weight Sensing is : " , PredictedNameHW)

		else:
			print ("An invalid msg received from RPI ", RPIAddr, SessionStrS)
        
