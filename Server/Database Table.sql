CREATE TABLE `datapool`.`SmartDoor_PeopleEntryExitDetail` (
  `SID` INT NOT NULL,
  `TimeOfEntryExit` TIMESTAMP NOT NULL,
  `RoomID` INT NOT NULL,
  `Direction` VARCHAR(5) NOT NULL,
  `Height` DOUBLE NOT NULL,
  `Weight` DOUBLE NOT NULL,
  `Predicted_Name` VARCHAR(45)  NULL,
  `Tagged_Name` VARCHAR(45) NULL,
  `Scrutinized_Name` VARCHAR(45) NULL,
  `Image_Name` VARCHAR(45) NULL,
  `Video_Name` VARCHAR(45) NULL,
  PRIMARY KEY (`SID`));


CREATE TABLE `datapool`.`SmartDoor_PeopleCount` (
  `SID` INT NOT NULL,
  `RoomID` INT NOT NULL,
  `Count` INT NOT NULL,
  PRIMARY KEY (`SID`));

CREATE TABLE `datapool`.`SmartDoor_HW_PredictionRank` (
  `SessionID` INT NOT NULL,
  `RankID` INT NOT NULL,
  `Name` VARCHAR(45) NOT NULL,
  `Probability` DOUBLE NOT NULL,
  PRIMARY KEY (`SessionID`, `RankID`));

CREATE TABLE `datapool`.`SmartDoor_Face_Identity` (
  `Identity` INT NOT NULL,
  `Room_No` INT NOT NULL,
  `Name` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Identity`));

CREATE TABLE `datapool`.`SmartDoor_Face_PredictionRank` (
  `SessionID` INT NOT NULL,
  `RankID` INT NOT NULL,
  `Name` VARCHAR(45) NOT NULL,
  `ID` INT NOT NULL,
  `Confidence` DOUBLE NOT NULL,
  `Count` INT NOT NULL,
  `MinFrameNumber` INT NOT NULL,
  `MaxFrameNumber` INT NOT NULL,
  PRIMARY KEY (`SessionID`, `RankID`));

CREATE TABLE `datapool`.`SmartDoor_OnEnterRecordedVideo` (
	VideoID 			INT 			NOT NULL,
	TimeOfEntering			TIMESTAMP 		NOT NULL,
	VideoFileName    		CHAR(45)		NOT NULL,
	VideoTimeTaken			NUMERIC			NOT NULL,
	TotalFaceFramesInVideo		INT			NOT NULL,
	ImageFileName			CHAR(45)		NOT NULL,
	ImgPredictedID    		INT    			NOT NULL,
	ActualID 			INT,
	PRIMARY KEY (`VideoID`));

CREATE TABLE `datapool`.`SmartDoor_FaceDataSetRecentIndices`
       		(PersonID 			INT 	PRIMARY KEY     NOT NULL,
		RoomNo 				INT 			NOT NULL,
		RecentRecordedVideoNo    	INT  			NOT NULL,
       		LastExtractedImageNo    	INT  			NOT NULL);

CREATE TABLE `datapool`.`SmartDoor_FaceDataSetRecordedVideo` 
	(`RecVideoID` 	INT(11) NOT NULL AUTO_INCREMENT ,
	`PersonID` 	INT(11) NOT NULL ,
	`RoomNo` 	INT(11) NOT NULL ,
	`VideoNo`	INT(11) NOT NULL ,
	`StartImgIndex` INT(11) NOT NULL );


CREATE TABLE `datapool`.`SmartDoor_Diagnostics` (
  `FailureNo` INT NOT NULL AUTO_INCREMENT ,
  `Failure TimeStamp` VARCHAR(45) NOT NULL,
  `Failure Event` LONGTEXT NOT NULL,
  `Failure Attempts` INT(11), 
  PRIMARY KEY (`FailureNo`))


