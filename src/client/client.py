# Basic Usage:
# python client.py -s SERVER_IP

from imutils.video import VideoStream
from datetime import datetime
import argparse
import socket
import time
from skimage.measure import compare_ssim
import asyncio
from concurrent.futures import ProcessPoolExecutor
import cv2

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

def check_image(frame):
    if globals()['lastFrame'] is None:
        globals()['lastFrame'] = frame
    else:
        # print("Start Time: " + datetime.now().strftime("%M:%S.%f"))

        i1 = globals()['lastFrame']
        i2 = frame
        assert i1.shape == i2.shape, "Different kinds of images."
        assert i1.size == i2.size, "Different sizes."

        # For more performance get these to work
        # grayF1 = cv2.cvtColor(i1, cv2.COLOR_BAYER_BG2GRAY)
        # grayF2 = cv2.cvtColor(i2, cv2.COLOR_BAYER_BG2GRAY)

        # Currently working on about a .4 second timer, seems to be as good as I am gonna get atm
        (score, diff) = compare_ssim(i1, i2, full=True, multichannel=True)
        # print("SSIM: {}".format(score))

        # print("End Time: " + datetime.now().strftime("%M:%S.%f"))
        globals()['lastFrame'] = frame
        if score < .8:
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

async def saving_frames(vs, framerate):
    while True:
        frame = vs.read()
        print("Saving something")
        await asyncio.sleep(1/framerate)

async def motion_track(vs, acceptable_difference):
    while True:
        if check_image(vs.read()):
            await sendStoredFiles()
        await asyncio.sleep(0)

async def sendStoredFiles():
    print("Sending files")

async def client():
    vs = VideoStream(usePiCamera=False, resolution=(args["res_width"],
                                                    args["res_height"]), framerate=args["framerate"]).start()

    loop = asyncio.get_event_loop()

    savingTask = loop.create_task(saving_frames(vs, args["framerate"]))
    checkingTask = loop.create_task(motion_track(vs, .8))

    await savingTask
    await checkingTask

loop = asyncio.get_event_loop()
loop.run_until_complete(client())
