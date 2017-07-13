import socket 
import os
import stat
#from sys import exit 
import sys
import glob 
import datetime
import time 
from time import sleep 
from serial import Serial 
import serial
import MySQLdb 
from _mysql_exceptions import OperationalError
from _mysql_exceptions import IntegrityError

#Lab Room Detail
RoomID = 1 #Subjected To Change according to Rpi

#server details
SERVER="10.129.23.161" 
 #Subjected To Change according to Rpi
#RPI : 10.129.23.214
INFOPORT = 12346
CAMPORT = 12347

'''
#RPI : 10.129.23.213
INFOPORT = 12348
CAMPORT = 12349
'''
#Calibration Details
WeightFactor = 1

#database details
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
		print("Could Not Close Database Connection")

def Get_Latest_SID():
	(con, cursor) = ConnectDataBase()
	sql= """SELECT SID 
		FROM   SmartDoor_PeopleEntryExitDetail
		ORDER BY SID DESC
		LIMIT 1"""
	try:
		cursor.execute(sql)
		results = cursor.fetchone()
	except:
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "Error: Could not get the Session ID information"
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
	cursor.close()
	DisconnectDataBase(con)
	if results is None:
		return 1
	else:
		Session_ID = int(results[0]) + 1
		print("The session ID is : " , Session_ID )
		return Session_ID 	

def Add_Entry_Exit_Details( SessionID, RoomID, Direction, Height, Weight, Name ):
	(con, cursor) = ConnectDataBase()
	Time_Of_EE =  time.strftime("%H:%M:%S")
	Day_Of_EE =  time.strftime("%Y-%m-%d")
	EE_TimeDate  = Day_Of_EE + " " + Time_Of_EE
	values = "'" + str(SessionID) + "', '" + EE_TimeDate + "', '" + str(RoomID)+ "', '" + Direction + "', '" + str(Height)+ "', '" + str(Weight)+ "', '" +  Name + "')"
	print(values)
	sql= """INSERT INTO `""" + DB +"""`.`SmartDoor_PeopleEntryExitDetail` 
		(`SID`, `TimeOfEntryExit`, `RoomID`, `Direction`, `Height`, `Weight`, `Scrutinized_Name`) 
		VALUES (""" + values
	try:
		cursor.execute(sql)
		con.commit()
		print(" A " + Direction + " Record is Saved ")
	except IntegrityError:
		con.rollback()
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "Entry/ Exit Record Not Saved - Improper Session ID"
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
	cursor.close()
	DisconnectDataBase(con)

def NoOfPeoplePresent( RoomID):
	(con, cursor) = ConnectDataBase()
	query = """	SELECT count 
			FROM SmartDoor_PeopleCount 
			WHERE RoomID = '%s'
			ORDER BY sid DESC
			LIMIT 1 """ %(RoomID)
	try:
		cursor.execute(query)
		results = cursor.fetchone()
	except:
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "Error: Could not get the number of people information"
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )

	cursor.close()
	DisconnectDataBase(con)
	if results is None:
		NoOfPeopleInRoom = 0
	else:
		NoOfPeopleInRoom = int(results[0])
	print("The Number of People in the Room previously are : ", NoOfPeopleInRoom)
	return NoOfPeopleInRoom
	

def UpdatePeoplePresent(SessionID, RoomID, Count):
	(con, cursor) = ConnectDataBase()
	sql = "INSERT INTO `" + DB + "`.`SmartDoor_PeopleCount` (`SID`, `RoomID`, `Count`) VALUES ('%s', '%s', '%s')"%(SessionID, RoomID, Count)
	try:
		cursor.execute(sql)
		con.commit()
		print(" Count Record is Saved ")
	except IntegrityError:
		con.rollback()
		Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
		FailureEvent = "Count Record Not Saved - Improper Session ID"
		Local_Global = 1 #Local is 0, Global is 1
		FailedAttempts = '' 
		DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
	cursor.close()
	DisconnectDataBase(con)



	



def ConnectArduinoSerialPort():
	print("Trying to Connect to Arduino Serial Port")
	IsNotConnected = True
	FailedAttempts = 0
	PortAvailableButUnableToConnect = False
	PortAvailableButUnableToConnectMsgGiven = False
	#Update Diagnostics Status Table that it is not Connected to Arduino
	while IsNotConnected:
		SerialPortList = glob.glob("/dev/ttyACM*")
    		if len(SerialPortList) > 0:			
			try:
				ArduinoSer = Serial(SerialPortList[0], baudrate=9600)
				IsNotConnected = False	
			except serial.serialutil.SerialException:
				try:
					os.chmod(SerialPortList[0], 777)
					ArduinoSer = Serial(SerialPortList[0], baudrate=9600)
					IsNotConnected = False	
				except :
					print("Sudden Disconnected Arduino")
					IsNotConnected = True			
			except:
				PortAvailableButUnableToConnect = True
				PortAvailableButUnableToConnectMsg = sys.exc_info()	
				Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
				FailureEvent = PortAvailableButUnableToConnectMsg
				Local_Global = 1 #Local is 0, Global is 1
				FailedAttempts = '' 
				DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
		else:
		 	print ".", 
			PortAvailableButUnableToConnect = False
			PortAvailableButUnableToConnectMsgGiven = False
			FailedAttempts +=1
		ReportOnNthFailure = 100
		if (FailedAttempts%ReportOnNthFailure) == 0 and (FailedAttempts >= ReportOnNthFailure):
			FailureEvent = "Failed to Connect to Arduino - Physical Disconnection"
			Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
			Local_Global = 1 #Local is 0, Global is 1
			DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )
		if PortAvailableButUnableToConnect and not PortAvailableButUnableToConnectMsgGiven:		
			FailureEvent = "Failed to Connect to Arduino - Port Available But Unable To Connect"
			PortAvailableButUnableToConnectMsgGiven = True
			Failure_TimeStamp =  time.strftime("%Y-%m-%d %H:%M:%S")		
			Local_Global = 1 #Local is 0, Global is 1
			DiagnosticsReportError( Failure_TimeStamp, FailureEvent, Local_Global, FailedAttempts )


	else: 
		print("Connected to Arduino Serial Port")
		sleep(5)
		return ArduinoSer


if __name__ == '__main__':
	#connect to the arduino via serial connection
	ArduinoSer = ConnectArduinoSerialPort()
	
	while True:
        #get the data serial port
		try:
			print("Beginning")
        		data = ArduinoSer.readline()
			print(data)
			datachunks = data.split('/')			
			if len(datachunks) == 3:
				SensedWeight = float(datachunks[1])
				Weight = WeightFactor * SensedWeight
				Height = float(datachunks[2])
				NoOfPeople =   NoOfPeoplePresent(RoomID)
				if datachunks[0] == 'I':
					Direction = 'Entry'
					NoOfPeople += 1
				elif datachunks[0] == 'O':
					Direction = "Exit"				
					if NoOfPeople > 0:
						NoOfPeople -= 1
				print("The Number of People in the room currently are : ", NoOfPeople)
				Session_ID =  Get_Latest_SID() 
				Name = raw_input("Name ???")
				Add_Entry_Exit_Details( Session_ID, RoomID, Direction, Height, Weight,Name )	
				UpdatePeoplePresent(Session_ID, RoomID, NoOfPeople)
				print("The End")
		except serial.serialutil.SerialException:
			ArduinoSer = ConnectArduinoSerialPort()


