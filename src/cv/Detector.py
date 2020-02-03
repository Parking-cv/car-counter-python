import imutils
import cv2
import numpy as np
import dlib

from src.cv.Camera import Camera
from src.cv.CentroidTracker import CentroidTracker
from src.network.NetworkClient import NetworkClient

# static
CONSIDER_CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                    "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                    "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                    "sofa", "train", "tvmonitor"]


class TrackableObject:
    """
    Object containing properties of a trackable object (car, etc)
    """
    def __init__(self, objectID, centroid=None):
        self.objectID = objectID
        self.centroids = [centroid]
        self.counted = False

    def appendCentroid(self, centroid):
        self.centroids.append(centroid)


class Detector:
    """
    Object containing the code for identification of an object and its movement
    """
    def __init__(self, config):
        self.centroidTracker = CentroidTracker(maxDisappeared=40, maxDistance=50)
        self.networkClient = NetworkClient()
        self.camera = Camera()
        self.numFrames = 0
        self.count = 0
        self.trackers = []
        self.trackableObjects = {}
        self.skipFrames = config.skipFrames
        self.confidenceLevel = config.confidenceLevel
        self.consider = config.considerClasses
        self.trainedModel = config.model

    # todo modularize this function
    def monitor(self):
        while True:
            frame = self.camera.getFrame()

            frame = imutils.resize(frame, width=400)
            (height, width) = frame.shape[:2]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            rects = []

            if self.numFrames % self.skipFrames == 0:
                self.trackers = []

                blob = cv2.dnn.blobFromImage(
                    cv2.resize(frame, (300, 300)),
                    0.007843,
                    (300, 300),
                    127.5
                )

                self.trainedModel.setInput(blob)
                detections = self.trainedModel.forward()

                for i in np.arange(0, detections.shape[2]):
                    confidence = detections[0, 0, i, 2]

                    if confidence > self.confidenceLevel:
                        idx = int(detections[0, 0, i, 1])

                        if CONSIDER_CLASSES[idx] in self.consider:
                            box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                            (startX, startY, endX, endY) = box.astype("int")

                            tracker = dlib.correlation_tracker()
                            rect = dlib.rectangle(startX, startY, endX, endY)
                            tracker.start_track(rgb, rect)

                            self.trackers.append(tracker)

            else:
                for tracker in self.trackers:
                    tracker.update(rgb)
                    pos = tracker.get_position()
                    rects.append(
                        (int(pos.left()),
                        int(pos.top()),
                        int(pos.right()),
                        int(pos.bottom()))
                    )

            cv2.line(frame, (width // 2, 0), (width // 2, height), (0, 0, 255), 2)

            objects = self.centroidTracker.update(rects)

            for (objectID, centroid) in objects.items():
                object = self.trackableObjects.get(objectID, None)

                if object is None:
                    object = TrackableObject(objectID)
                else:
                    direction = centroid[0] - np.mean([centroid[0] for centroid in object.centroids])
                    object.appendCentroid(centroid)

                    if not object.counted:
                        if direction < -20 and centroid[0] < width // 2:
                            self.networkClient.notifyEntry()
                            object.counted = True

                        elif direction > 20 and centroid[0] > width // 2:
                            self.networkClient.notifyExit()
                            object.counted = True

                self.trackableObjects[objectID] = object
