from datetime import datetime
import cv2
import os


class ImageSaver:

    def __init__(self, directory=None):
        if directory is None:
            self.directory = "saved_images"
        else:
            self.directory = directory
        self.create_directory_if_not_exist()

    def create_directory_if_not_exist(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            print("making directory")

    def saving_frames(self, frame, count):
        print("Saving something: " + str(count))
        # TimeStamp
        filename = self.directory + "/frame_" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f-06:00") + ".jpg"
        cv2.imwrite(filename, frame)
