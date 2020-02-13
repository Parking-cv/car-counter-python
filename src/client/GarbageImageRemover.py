from datetime import datetime
from datetime import timedelta
import os
import time

class GarbageImageRemover():

    def __init__(self, secondsToWait):
        self.secondsToWait = secondsToWait

    def start(self):
        while True:
            print("Attempting to remove images")
            now = datetime.now()
            currentItems = os.listdir("images")
            for filename in currentItems:
                timestamp = filename[filename.find("_") + 1:filename.rfind(".")]
                timeObj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
                if timeObj < (now - timedelta(seconds=self.secondsToWait)):
                    print("Removing Files: " + filename)
                    os.remove("images/" + filename)
            time.sleep(self.secondsToWait)