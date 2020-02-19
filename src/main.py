# Basic Usage:
# python images.py -s SERVER_IP

from imutils.video import VideoStream
import argparse
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.network.NetworkManager import NetworkManager
from src.images.MotionTracker import MotionTracker
from src.images.GarbageImageRemover import GarbageImageRemover
from src.images.ImageSaver import ImageSaver

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", default='localhost',
                help="ip address of the server to which the images will connect")
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



async def main():
    vs = VideoStream(usePiCamera=False, resolution=(args["res_width"],
                                                    args["res_height"]), framerate=args["framerate"]).start()

    loop = asyncio.get_event_loop()
    # 3 Threads, 1 for motion tracking, 1 for saving, and 1 for garbage collecting, allocating more for tracker as it will probably be
    # happening multiple times at once
    trackerExecutor = ThreadPoolExecutor(2)
    saveExecutor = ThreadPoolExecutor(1)
    # May want to remove this in favor of some sort of stream buffer instead
    garbageCollector = ThreadPoolExecutor(1)

    # Used for setting frames to compare against when the motion tracking hits
    lastFrame = None
    # More for debugging than anything
    count = 0
    # This is important for controlling how often the Pi checks for motion
    frameCount = 0

    # Will need to replace this with server code soon, will be testing tomorrow
    manager = NetworkManager("http://161.6.4.165:4321", {"frame": "/frames"})
    manager.start()

    # Value between -1, 1, lower the float the less strict the image checking is to determine motion
    minimumSimilarity = .8
    motionTracker = MotionTracker(minimumSimilarity, manager)
    # Going to go with 2 minutes at default because it seems that sending files takes a reasonable amount of time
    # Wouldn't want to remove an image that needs to be sent
    garbageRemover = GarbageImageRemover(120)
    imageSaver = ImageSaver()
    asyncio.ensure_future(loop.run_in_executor(garbageCollector, garbageRemover.start))

    # Loop forever
    while True:
        # camera can only be read in one thread so get the frame and then send it off when needed
        frame = vs.read()
        asyncio.ensure_future(loop.run_in_executor(saveExecutor, imageSaver.saving_frames, frame, count))

        # Checking once every half second
        if frameCount == (args["framerate"]/2):
            if lastFrame is not None and globals()["motion_tracking"]:
                asyncio.ensure_future(loop.run_in_executor(trackerExecutor, motionTracker.checkFrames, lastFrame, frame))
            lastFrame = frame
            frameCount = 0
        count += 1
        frameCount += 1
        time.sleep(1/args["framerate"])

#Start processing images
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
