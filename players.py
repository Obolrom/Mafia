from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, nickname):
        self.nickname = nickname

    @abstractmethod
    def talk_time(self):
        pass


class Citizen(Player):
    def __init__(self, nickname):
        super(Citizen, self).__init__(nickname)

    def talk_time(self):
        pass


class Sheriff(Citizen):
    def __init__(self, nickname):
        super(Sheriff, self).__init__(nickname)

    def mafia_check(self, nickname):
        pass


class Mafia(Player):
    def __init__(self, nickname):
        super(Mafia, self).__init__(nickname)

    def talk_time(self):
        pass

    def kill_player(self, nickname):
        pass


class Godfather(Mafia):
    def __init__(self, nickname):
        super(Godfather, self).__init__(nickname)

    def sheriffs_check(self, nickname):
        pass
