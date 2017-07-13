import cv2,os
import numpy as np
from PIL import Image
import pickle

recognizer = cv2.createLBPHFaceRecognizer()
FaceImgDBPath = '../FacialImageCollection/FaceDataSet'


def getImageWithID(ImgDBPath):
	imagePaths = [os.path.join(ImgDBPath,f) for f in os.listdir(ImgDBPath)]
	#print(imagePaths)
	faces =[]
	IDs =[]
	for imagePath in imagePaths:
		faceImg = Image.open(imagePath).convert('L');
		faceNp = np.array(faceImg, 'uint8')
		ID = int(os.path.split(imagePath)[-1].split('.')[1])
		print(ID)
		faces.append(faceNp)
		IDs.append(ID)
		#One Could Comment the following 2 lines for Fast Training
		cv2.imshow("training",faceNp)
		cv2.waitKey(10)
	return np.array(IDs), faces

Ids, faces  = getImageWithID(FaceImgDBPath)
recognizer.train(faces,Ids)
recognizer.save('RecognizerFiles/TrainingData.yml')
cv2.destroyAllWindows()
