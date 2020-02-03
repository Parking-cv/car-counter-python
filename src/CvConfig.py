import cv2


class CvConfig:
    """
    Object containing configuration for the Detector object. This should be initialized from environment variables
    """
    def __init__(self, considerClasses, skipFrames, confidenceLevel, caffeFile, model):
        self.considerClasses = considerClasses
        self.skipFrames = skipFrames
        self.confidenceLevel = confidenceLevel
        self.trainedModel = cv2.dnn.readNetFromCaffe(caffeFile, model)
