from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, nickname):
        self.nickname = nickname

    @abstractmethod
    def talk_time(self):
        pass


if __name__ == '__main__':
    player = Player()
