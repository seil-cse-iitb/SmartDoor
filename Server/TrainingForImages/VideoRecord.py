import sys
import numpy as np
import cv2

SmartDoorCameraIP = "rtsp://10.129.23.250:554/ISAPI/streaming/channels/102?auth=YWRtaW46dGhlY2FtQHNlaWw="
CamConfig = {"Resolution": (320,240), "FrameRate(fps)": 20} #SubStream


LabMemberID = raw_input('Enter Lab Member ID')
ExpressionNo = raw_input('Enter Expression No')

Output_File = 'Recording/Recording_'+ LabMemberID+'_'+ ExpressionNo + '.avi'
Resolution = (320,240)
FrameRate_fps = 20


cap = cv2.VideoCapture(SmartDoorCameraIP)

cap.set(3,CamConfig["Resolution"][0])
cap.set(4,CamConfig["Resolution"][1])
fourcc = cv2.cv.CV_FOURCC(*'MJPG')
out = cv2.VideoWriter(Output_File, fourcc, CamConfig["FrameRate(fps)"], CamConfig["Resolution"])



while(cap.isOpened()):
    ret, frame = cap.read()

    if ret==True:
        out.write(frame)
        cv2.imshow('frame',frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    else:
        break



# Release everything if job is finished

cap.release()

out.release()

cv2.destroyAllWindows()
