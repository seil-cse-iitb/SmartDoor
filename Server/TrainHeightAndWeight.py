import numpy as np
from sklearn.ensemble.forest import RandomForestClassifier
from sklearn.externals import joblib
import MySQLdb 
import sys 
import time
dataw = []
tags = []
from _mysql_exceptions import OperationalError
from _mysql_exceptions import IntegrityError

#database details
HOST = "10.129.23.161"
USER = "reader"
PSWD = "datapool"
DB = "datapool"

def ConnectDataBase():    
	CouldNotConnectToDataBase = True
	CouldNotGetCursor = True
	#connect to the database
	print ("Trying to Connect To Database")
	while CouldNotGetCursor:
		while CouldNotConnectToDataBase:
			try:
				con = MySQLdb.connect(HOST, USER, PSWD, DB)
				CouldNotConnectToDataBase = False
			except  OperationalError:
				CouldNotConnectToDataBase = True
				Time_Of_Failure =  time.strftime("%H:%M:%S")
				Day_Of_Failure =  time.strftime("%d/%m/%Y")			
				FailureEvent = "Failed to Connect to Database"
				print (Time_Of_Failure)
				print(Day_Of_Failure)
				print(FailureEvent)
		else:
			print ("Connected To Database")	
			try:
				cursor = con.cursor()
				CouldNotGetCursor = False
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				Time_Of_Failure =  time.strftime("%H:%M:%S")
				Day_Of_Failure =  time.strftime("%d/%m/%Y")			
				FailureEvent = "Failed to get the Database Cursor after Connection" + e
				print (Time_Of_Failure)
				print(Day_Of_Failure)
				print(FailureEvent)
	else:
		print("Cursor is Fetched") 
		return (con, cursor)

def DisconnectDataBase(con):
	try:
		con.close()
		print("Database Connection Closed")
	except:
		print("Could Not Close Database Connection")

def FetchFromDatabase(SessionID, RoomID):
	global dataw
	global tags
	(con, cursor) = ConnectDataBase()
	sql= """SELECT Height, Weight, Scrutinized_Name FROM `""" + DB +"""`.`SmartDoor_PeopleEntryExitDetail` 
		WHERE SID >= '%s' AND  RoomID = '%s' 
		AND  Scrutinized_Name is not null""" %(SessionID, RoomID)

	try:
		cursor.execute(sql)
		results = cursor.fetchall()
	except:
		print("Error: Could not get the information for training")
		exit();
	cursor.close()
	DisconnectDataBase(con)
	print(results)
	if results is None or len(results) <=0 :
		print("Error: Insufficient Data for Training")
		exit();
	else:
		for record in results:
			dataw.append([float(record[0]),float(record[1])])
        		tags.append(record[2].strip().lower())
			
		dataw = np.array(dataw) 
		tags = np.array(tags)


def Train_Store_RFC(RoomID):
	global dataw
	global tags
	# initializing the random forest classifier.    
	clf = RandomForestClassifier(criterion='entropy', n_estimators = 100, n_jobs = -1, max_depth = None, min_samples_split = 1)
	# train the classifier
	clf.fit(dataw,tags)
	joblib.dump(clf, 'HeightWeightModel_' + RoomID+ '/RFCforSmartDoor.pkl')
	#print clf.predict([57.48,156.68])
    
if __name__ == "__main__":
	print("Training Data ")
	if len(sys.argv) == 3:
		SessionID = str(sys.argv[1])
		RoomID = str(sys.argv[2])
		print(" From SessionID : ", SessionID)
		print(" Of Room ID : " , RoomID)
		FetchFromDatabase(SessionID, RoomID)
		Train_Store_RFC(RoomID)
		print("Training Data - Completed")
	else:
		print('''Usage :
python TrainHeightAndWeight.py <From which SessionID>  <Of Room ID :>
Parameters : 2 ''')





