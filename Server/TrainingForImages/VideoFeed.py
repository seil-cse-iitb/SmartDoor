import cv2
import numpy as np
SmartDoorCameraIP = "Recording/Recording_1_1.avi"

cam = cv2.VideoCapture(SmartDoorCameraIP);

while(True):
	ret, img = cam.read();
	cv2.imshow("Face", img);
	if (cv2.waitKey(1)==ord('q')):
		break
cam.release()
cv2.destroyAllWindows()
'''
        self.open = True
        self.device_index = 0
        self.fps = 6               # fps should be the minimum constant rate at which the camera can
        self.fourcc = "MJPG"       # capture images (with no decrease in speed over time; testing is required)
        self.frameSize = (640,480) # video formats and sizes also depend and vary according to the camera used
        self.video_filename = "temp_video.avi"
        self.video_cap = cv2.VideoCapture(SmartDoorCameraIP)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
        self.frame_counts = 1
        self.start_time = time.time()
'''
