1. Change the directory to:
 cd /home/stark/SmartDoor_New

2. Run the Prediction according to Height and Weight Script as follows: Parameters: RoomID (SEIL - 1, ERTS - 2), INFOPORT (According to RPi)
python Prediction_HW_Server.py 1 12345

3. Run the Prediction according to Video Processing Script as follows: Parameters: RoomID (SEIL - 1, ERTS - 2), CAMPORT (According to RPi)
python Prediction_Img_Server.py 1 12347
