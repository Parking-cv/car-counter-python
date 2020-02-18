from src.network.NetworkManager import NetworkManager
import time
from datetime import datetime
from datetime import timedelta
from skimage.metrics import structural_similarity
import os


class MotionTracker:

    def __init__(self, acceptable_difference: float, networkManager: NetworkManager, directory=None):
        self.acceptable_difference = acceptable_difference
        self.networkManager = networkManager
        if directory is None:
            self.directory = "saved_images"
        else:
            self.directory = directory

    def checkFrames(self, startFrame, endFrame):
        start = datetime.now()
        if self.check_image(startFrame, endFrame):
            globals()["motion_tracking"] = False
            time.sleep(5)
            end = datetime.now()
            self.sendStoredFiles(start, end)
            globals()["motion_tracking"] = True
        else:
            print("No motion Detected: ")

    def check_image(self, startFrame, endFrame):
        # print("Start Time: " + datetime.now().strftime("%M:%S.%f"))

        assert startFrame.shape == endFrame.shape, "Different kinds of images."
        assert startFrame.size == endFrame.size, "Different sizes."

        # For more performance get these to work
        # grayF1 = cv2.cvtColor(i1, cv2.COLOR_BAYER_BG2GRAY)
        # grayF2 = cv2.cvtColor(i2, cv2.COLOR_BAYER_BG2GRAY)

        # Currently working on about a .4 second timer, seems to be as good as I am gonna get atm
        (score, diff) = structural_similarity(startFrame, endFrame, full=True, multichannel=True)
        print("SSIM: {}".format(score))

        # print("End Time: " + datetime.now().strftime("%M:%S.%f"))
        if score < self.acceptable_difference:
            # print("something happening")
            return True
        return False

    def sendStoredFiles(self, startTime, endTime):
        sentFiles = dict()
        currentItems = os.listdir(self.directory)
        for filename in currentItems:
            timestamp = filename[filename.find("_") + 1:filename.rfind(".")]
            timeObj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            # Check 5 seconds before motion and 5 seconds after
            if (startTime - timedelta(seconds=5)) < timeObj < endTime:
                sentFiles[timestamp] = open(self.directory + "/" + filename, 'rb')
        print("Files were sent")
        self.networkManager.uploadFrames(sentFiles)
