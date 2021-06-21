from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, number):
        self.__nickname = "Player"
        self.number = number
        self.__alive = True

    def is_alive(self):
        return self.__alive

    def kill(self):
        self.__alive = False

    @abstractmethod
    def talk_time(self):
        pass

    @property
    def nickname(self):
        return f"{self.__nickname} {self.number}"


class Citizen(Player):
    def __init__(self, number):
        super(Citizen, self).__init__(number)

    def talk_time(self):
        pass

    def __repr__(self):
        return "Мирный житель"


class Sheriff(Citizen):
    def __init__(self,  number):
        super(Sheriff, self).__init__( number)

    def talk_time(self):
        pass

    def __repr__(self):
        return "Шериф"


class Mafia(Player):
    def __init__(self, number):
        super(Mafia, self).__init__(number)

    def talk_time(self):
        pass

    def __repr__(self):
        return "Мафия"


class Godfather(Mafia):
    def __init__(self, number):
        super(Godfather, self).__init__( number)

    def talk_time(self):
        pass

    def __repr__(self):
        return "Дон"
