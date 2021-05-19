import players
from abc import ABC, abstractmethod


class State:
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def handle(self):
        pass

    @abstractmethod
    def set_state(self, state):
        pass


class CheckRoles(State):
    def __init__(self, state):
        super(CheckRoles, self).__init__(state)

    def handle(self):
        pass

    def set_state(self, state):
        pass


class LastSpeech(State):
    def __init__(self, state):
        super(LastSpeech, self).__init__(state)

    def handle(self):
        pass

    def set_state(self, state):
        pass


class MafiaShooting(State):
    def __init__(self, state):
        super(MafiaShooting, self).__init__(state)

    def handle(self):
        pass

    def set_state(self, state):
        pass


class Voting(State):
    def __init__(self, state):
        super(Voting, self).__init__(state)

    def handle(self):
        pass

    def set_state(self, state):
        pass


class MafiaWin(State):
    def __init__(self, state):
        super(MafiaWin, self).__init__(state)

    def handle(self):
        pass

    def set_state(self, state):
        pass


class CitizenWin(State):
    def __init__(self, state):
        super(CitizenWin, self).__init__(state)

    def handle(self):
        pass

    def set_state(self, state):
        pass


class RolesDistribution(State):
    def __init__(self, state):
        super(RolesDistribution, self).__init__(state)

    def handle(self):
        pass

    def set_state(self, state):
        pass


class MafiaAcquaintance(State):
    def __init__(self, state):
        super(MafiaAcquaintance, self).__init__(state)

    def handle(self):
        pass

    def set_state(self, state):
        pass


class PlayerSpeeches(State):
    def __init__(self, state):
        super(PlayerSpeeches, self).__init__(state)

    def handle(self):
        pass

    def set_state(self, state):
        pass
