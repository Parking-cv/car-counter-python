from time import sleep

from src.network.NetworkManager import NetworkManager
from src.NetworkConfig import NetworkConfig


def main():
    # Test network

    config = NetworkConfig('localhost', 'c-9p)gWR', '/entry', '/exit', 3000)
    manager = NetworkManager(config)

    manager.start()

    sleep(1)

    manager.testNetwork()
    manager.testNetwork()

    sleep(1)

    manager.testNetwork()
    manager.testNetwork()

    sleep(1)

    for res in manager.getResponses():
        print(res.body)

if __name__ == "__main__":
    main()
