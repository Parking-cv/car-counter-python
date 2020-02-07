import cv2
import numpy as np

from time import sleep

from src.network.NetworkManager import NetworkManager
from src.NetworkConfig import NetworkConfig


def main():

    # Test network
    config = NetworkConfig('localhost', 'c-9p)gWR', {'test': '/test', 'frame': '/frame'}, 3000)
    manager = NetworkManager(config)
    image = open("../test.jpeg", 'rb')

    manager.start()

    manager.uploadFrame(image)

    # manager.testNetwork()
    # manager.testNetwork()
    # manager.testNetwork()
    # manager.testNetwork()

    sleep(1)

    for res in manager.getResponses():
        print(res['body'])

if __name__ == "__main__":
    main()
