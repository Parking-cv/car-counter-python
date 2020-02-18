# Basic Usage:
# python client.py -s SERVER_IP

from imutils.video import VideoStream
from datetime import datetime
from datetime import timedelta
import argparse
import time
from skimage.metrics import structural_similarity
import asyncio
from concurrent.futures import ThreadPoolExecutor
import cv2
import os
from src.network.NetworkManager import NetworkManager
from src.client.MotionTracker import MotionTracker
from src.client.GarbageImageRemover import GarbageImageRemover

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", default='localhost',
                help="ip address of the server to which the client will connect")
ap.add_argument("-rw", "--res-width", type=int, default=272,
                help="resolution width of captured footage")
ap.add_argument("-rh", "--res-height", type=int, default=208,
                help="resolution height of captured footage")
ap.add_argument("-f", "--framerate", type=int, default=20,
                help="framerate of captured footage")
args = vars(ap.parse_args())

# Important Global but could probably be turned into a class variable
globals()["motion_tracking"] = True

time.sleep(2.0)

globals()['lastFrame'] = None

def saving_frames(frame, count):
    print("Saving something: " + str(count))
    # TimeStamp
    filename = "images/frame_" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ07:00") + ".jpg"
    cv2.imwrite(filename, frame)

async def client():
    vs = VideoStream(usePiCamera=False, resolution=(args["res_width"],
                                                    args["res_height"]), framerate=args["framerate"]).start()

    loop = asyncio.get_event_loop()
    # 2 Threads, 1 for motion tracking and 1 for saving, allocating more for tracker as it will probably be
    # happening multiple times at once
    trackerExecutor = ThreadPoolExecutor(2)
    saveExecutor = ThreadPoolExecutor(1)
    garbageCollector = ThreadPoolExecutor(1)

    lastFrame = None
    count = 0
    frameCount = 0


    manager = NetworkManager("http://localhost:3000", {"frame": "/frames"})
    manager.start()

    motionTracker = MotionTracker(.8, manager)
    # Going to go with 2 minutes at default because it seems that sending files takes a reasonable amount of time
    # Wouldn't want to remove an image that needs to be sent
    garbageRemover = GarbageImageRemover(120)
    asyncio.ensure_future(loop.run_in_executor(garbageCollector, garbageRemover.start))

    while True:
        # camera can only be read in one thread so get the frame and then send it off when needed
        frame = vs.read()
        asyncio.ensure_future(loop.run_in_executor(saveExecutor, saving_frames, frame, count))
        # Checking once every half second
        if frameCount == (args["framerate"]/2):
            if lastFrame is not None and globals()["motion_tracking"]:
                asyncio.ensure_future(loop.run_in_executor(trackerExecutor, motionTracker.checkFrames, lastFrame, frame))
            lastFrame = frame
            frameCount = 0
        count += 1
        frameCount += 1
        time.sleep(1/args["framerate"])

#Beign the client part of this
loop = asyncio.get_event_loop()
loop.run_until_complete(client())