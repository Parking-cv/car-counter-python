# Basic Usage:
# python client.py -s SERVER_IP

from imutils.video import VideoStream
from datetime import datetime
import argparse
import time
from skimage.metrics import structural_similarity
import asyncio
from concurrent.futures import ThreadPoolExecutor
import cv2
import os

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

globals()["motion_tracking"] = True

def check_image(previousFrame, frame):
    # print("Start Time: " + datetime.now().strftime("%M:%S.%f"))

    i1 = previousFrame
    i2 = frame
    assert i1.shape == i2.shape, "Different kinds of images."
    assert i1.size == i2.size, "Different sizes."

    # For more performance get these to work
    # grayF1 = cv2.cvtColor(i1, cv2.COLOR_BAYER_BG2GRAY)
    # grayF2 = cv2.cvtColor(i2, cv2.COLOR_BAYER_BG2GRAY)

    # Currently working on about a .4 second timer, seems to be as good as I am gonna get atm
    (score, diff) = structural_similarity(i1, i2, full=True, multichannel=True)
    print("SSIM: {}".format(score))

    # print("End Time: " + datetime.now().strftime("%M:%S.%f"))
    if score < .9:
        # print("something happening")
        return True
    return False

# initialize the ImageSender object with the socket address of the
# server
# sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
#     args["server_ip"]))
# get the host name and initialize the video stream

# camera warmup
time.sleep(2.0)

globals()['lastFrame'] = None

def saving_frames(frame, count):
    print("Saving something: " + str(count))
    # TimeStamp
    filename = "images/frame_" + datetime.now().isoformat() + ".jpg"
    cv2.imwrite(filename, frame)

def motion_track(previousFrame, frame, count, acceptable_difference):
    # In case this frame is correct, get a correct datetime for the start time
    start = datetime.now()
    if check_image(previousFrame, frame):
        globals()["motion_tracking"] = False
        time.sleep(5)
        end = datetime.now()
        sendStoredFiles(start, end)
        globals()["motion_tracking"] = True
    else:
        print("No motion Detected: " + str(count))

def sendStoredFiles(startTime, endTime):
    sentFiles = dict()
    currentItems = os.listdir("images")
    for filename in currentItems:
        timestamp = filename[filename.find("_")+1:filename.rfind(".")]
        timeObj = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        if startTime < timeObj < endTime:
            sentFiles[timestamp] = filename
    return sentFiles


async def client():
    vs = VideoStream(usePiCamera=False, resolution=(args["res_width"],
                                                    args["res_height"]), framerate=args["framerate"]).start()

    loop = asyncio.get_event_loop()
    # 2 Threads, 1 for motion tracking and 1 for saving, allocating more for tracker as it will probably be
    # happening multiple times at once
    trackerExecutor = ThreadPoolExecutor(2)
    saveExecutor = ThreadPoolExecutor(1)

    lastFrame = None
    count = 0
    frameCount = 0
    while True:
        frame = vs.read()
        asyncio.ensure_future(loop.run_in_executor(saveExecutor, saving_frames, frame, count))
        # Checking once every half second
        if frameCount == (args["framerate"]/2):
            if lastFrame is not None and globals()["motion_tracking"]:
                asyncio.ensure_future(loop.run_in_executor(trackerExecutor, motion_track, lastFrame, frame, count, .8))
            lastFrame = frame
            frameCount = 0
        count += 1
        frameCount += 1
        time.sleep(1/args["framerate"])
#Beign the client part of this
loop = asyncio.get_event_loop()
loop.run_until_complete(client())