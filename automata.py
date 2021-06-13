from __future__ import annotations
from players import *
from abc import ABC, abstractmethod


class GameLoop:
    _state = None

    def __init__(self, player_list):
        self._state = RolesDistribution(self)
        self.players = player_list

    def transition_to(self, state):
        self._state = state

    def start(self):
        print("the game started")
        while not isinstance(self._state, GameOver):
            self._state.handle()


class State:
    @property
    def context(self) -> GameLoop:
        return self._context

    @context.setter
    def context(self, context: GameLoop) -> None:
        self._context = context

    def __init__(self, game: GameLoop):
        self._context = game

    @abstractmethod
    def handle(self):
        pass


class CheckRoles(State):
    def __init__(self, state):
        super(CheckRoles, self).__init__(state)

    def handle(self) -> None:
        print("Check roles")
        self.context.transition_to(PlayerSpeeches(self.context))


class LastSpeechAfterVoting(State):
    def __init__(self, state):
        super(LastSpeechAfterVoting, self).__init__(state)

    def handle(self):
        pass


class LastSpeechAfterKill(State):
    def __init__(self, state):
        super(LastSpeechAfterKill, self).__init__(state)

    def handle(self):
        pass


class MafiaShooting(State):
    def __init__(self, state):
        super(MafiaShooting, self).__init__(state)

    def handle(self):
        pass


class Voting(State):
    def __init__(self, state):
        super(Voting, self).__init__(state)

    def handle(self):
        pass


class GameOver(State):
    def __init__(self, state):
        super(GameOver, self).__init__(state)

    def handle(self):
        pass


class MafiaWin(GameOver):
    def __init__(self, state):
        super(MafiaWin, self).__init__(state)

    def handle(self):
        print("Mafia win!")


class CitizenWin(GameOver):
    def __init__(self, state):
        super(CitizenWin, self).__init__(state)

    def handle(self):
        print("Citizen win!")


class RolesDistribution(State):
    def __init__(self, game):
        super(RolesDistribution, self).__init__(game)

    def handle(self) -> None:
        print("RolesDistribution")
        self.context.transition_to(MafiaAcquaintance(self.context))


class MafiaAcquaintance(State):
    def __init__(self, state):
        super(MafiaAcquaintance, self).__init__(state)

    def handle(self) -> None:
        print("Hello Mafia")
        self.context.transition_to(CheckRoles(self.context))


class PlayerSpeeches(State):
    def __init__(self, state):
        super(PlayerSpeeches, self).__init__(state)

    def handle(self):
        print("PlayerSpeeches")
        self.context.transition_to(MafiaWin(self.context))


if __name__ == '__main__':
    players = [Mafia(""), Godfather(""), Citizen(""), Citizen(""), Citizen(""), Mafia(""), Sheriff("")]

    gameLoop = GameLoop(players)
    gameLoop.start()
