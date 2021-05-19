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
