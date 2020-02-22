import os
import time
from datetime import datetime

from network.NetworkManager import NetworkManager


def main():
    manager = NetworkManager("http://192.168.1.9:4321/pi", {"frame": "/frames"})
    manager.start()

    sentFiles = dict()
    test_dir = "./assets"

    currentItems = os.listdir(test_dir)
    
    for filename in currentItems:
        time.sleep(0.01)
        sentFiles[(datetime.utcnow().isoformat('T')) + 'Z'] = open(test_dir + "/" + filename, 'rb')
     
    manager.uploadFrames(sentFiles)
    print("Files were sent")
    
    print(manager.getResponse().text)
    manager.terminate()


if __name__ == "__main__":
    close_manager()
