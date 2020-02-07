import cv2
import numpy as np

from time import sleep

from src.network.NetworkManager import NetworkManager


def main():

    # Test network
    manager = NetworkManager("http://localhost:3000", {"frame": "/frames"})
    rook = open("../img/white_rook.png", 'rb')
    knight = open("../img/white_knight.png", 'rb')
    bishop = open("../img/white_bishop.png", 'rb')
    queen = open("../img/white_queen.png", 'rb')
    king = open("../img/white_king.png", 'rb')

    manager.start()

    manager.uploadFrames({
        'rook': rook,
        'knight': knight,
        'bishop': bishop,
        'queen': queen,
        'king': king
    })

    sleep(1)

    for res in manager.getResponses():
        print(res.text)

if __name__ == "__main__":
    main()
