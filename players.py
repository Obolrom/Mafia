from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, nickname, number):
        self.nickname = nickname
        self.number = number
        self.__alive = True

    def is_alive(self):
        return self.__alive

    def kill(self):
        self.__alive = False

    @abstractmethod
    def talk_time(self):
        pass


class Citizen(Player):
    def __init__(self, nickname, number):
        super(Citizen, self).__init__(nickname, number)

    def talk_time(self):
        pass



class Sheriff(Citizen):
    def __init__(self, nickname, number):
        super(Sheriff, self).__init__(nickname, number)

    def talk_time(self):
        pass


class Mafia(Player):
    def __init__(self, nickname, number):
        super(Mafia, self).__init__(nickname, number)

    def talk_time(self):
        pass


class Godfather(Mafia):
    def __init__(self, nickname, number):
        super(Godfather, self).__init__(nickname, number)

    def talk_time(self):
        pass
