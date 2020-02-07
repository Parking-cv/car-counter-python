# Basic Usage:
# python client.py -s SERVER_IP

from imutils.video import VideoStream
import imagezmq
from PIL import Image
from datetime import datetime
import argparse
import socket
import time

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
                help="ip address of the server to which the client will connect")
ap.add_argument("-rw", "--res-width", type=int, default=272,
                help="resolution width of captured footage")
ap.add_argument("-rh", "--res-height", type=int, default=208,
                help="resolution height of captured footage")
ap.add_argument("-f", "--framerate", type=int, default=80,
                help="framerate of captured footage")
args = vars(ap.parse_args())

def check_image(frame):
    if globals()['lastFrame'] is None:
        globals()['lastFrame'] = frame
    else:
        print("Start Time: " + datetime.now().strftime("%M:%S.%f"))

        i1 = Image.open("50qualTestImage.jpg")
        i2 = Image.open("100qualTestImage.jpg")
        assert i1.mode == i2.mode, "Different kinds of images."
        assert i1.size == i2.size, "Different sizes."

        pairs = zip(i1.getdata(), i2.getdata())
        if len(i1.getbands()) == 1:
            dif = sum(abs(p1 - p2) for p1, p2 in pairs)
        else:
            dif = sum(abs(c1 - c2) for p1, p2 in pairs for c1, c2 in zip(p1, p2))

        ncomponents = i1.size[0] * i1.size[1] * 3
        print("Difference (percentage):", (dif / 255.0 * 100) / ncomponents)

        print("Start Time: " + datetime.now().strftime("%M:%S.%f"))
        globals()['lastFrame'] = frame

# initialize the ImageSender object with the socket address of the
# server
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
    args["server_ip"]))

# get the host name and initialize the video stream
rpiName = socket.gethostname()
vs = VideoStream(usePiCamera=True, resolution=(args["res_width"],
                                               args["res_height"]), framerate=args["framerate"]).start()

# camera warmup
time.sleep(2.0)

globals()['lastFrame'] = None

while True:
    # read the frame from the camera and send it to the server
    frame = vs.read()
    sender.send_image(rpiName, frame)
