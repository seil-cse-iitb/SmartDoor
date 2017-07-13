SmartDoorCameraIP = [  "rtsp://10.129.23.250:554/ISAPI/streaming/channels/102?auth=YWRtaW46dGhlY2FtQHNlaWw=", 				"rtsp://10.129.26.250:1024/ISAPI/streaming/channels/102?auth=YWRtaW46dGhlY2FtQEVSVFM="]
BaseFolder = "/home/stark/SmartDoor_New/"
FaceRecognizerYMLFile = [BaseFolder + "FacialImageTraining/RecognizerFiles/TrainingData_1.yml",
BaseFolder + "FacialImageTraining/RecognizerFiles/TrainingData_2.yml"]
FaceDetectorXMLFile   = BaseFolder + "FaceDetector/haarcascade_frontalface_default.xml"
VideoRecordingFolder  = BaseFolder + "Watch/Videos/"
ImageCaptureFolder    = BaseFolder + "Watch/Images/"

CamConfig = {"Resolution": (320,240), "FrameRate(fps)": 20} #SubStream

#=================================#
Frame_Door_Start_Y	= [45,  10]	#For Camera Positioning when it is physically disturbed, 			pixel Y
Frame_Door_Top_Left 	= [80,  111]	#For Camera Positioning when it is physically disturbed, 			pixel X
Frame_Door_Top_Right 	= [280, 223]	#For Camera Positioning when it is physically disturbed, 			pixel X
Pic_Frame_Top		= [50,  20]	#Captured Picture Frame at Top Point						pixel Y
Pic_Frame_Bottom	= [240, 200]	#Captured Picture Frame at Bottom Point						pixel Y
Pic_Frame_Left		= [85,  110]	#Captured Picture Frame at Left Point						pixel X
Pic_Frame_Right		= [270, 220]	#Captured Picture Frame at Right Point						pixel X
Frame_In_Left 		= [60,  90]	#To check if a person went out of Frame towards Left, 				pixel X
Frame_In_Right 		= [300, 250]	#To check if a person went out of Frame towards Right, 				pixel X
Max_Face_Frame_Area 	= [14000,19500]	#Frame Area 	#Old Value: SEIL - 19500					pixel*pixel
Take_CamShot 		= [0.5, 1]	#Click a picture at this second							second
Time_Out 		= [1.5,2]	#After these many Seconds # Note: Video Length is different from this second	second
Time_Out_Tolerance 	= [7,5]		#Let it run for these many times after timeout seconds has reached		loop
#=================================#
