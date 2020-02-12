import cv2
import numpy as np
from datetime import datetime
from time import sleep

from src.network.NetworkManager import NetworkManager


def main():

    # Test network
    manager = NetworkManager("http://localhost:3000", {"frame": "/pi/frames"})
    knight = open("img/black_knight.png", "rb")

    manager.start()

    manager.uploadFrames({
		str(datetime.utcnow().isoformat('T')) + 'Z'  : knight
    })

    sleep(1)

    for res in manager.getResponses():
        print(res.text)

if __name__ == "__main__":
    main()
