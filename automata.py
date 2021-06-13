from __future__ import annotations

from typing import List

from players import *
from abc import ABC, abstractmethod


class GameLoop:
    _state = None
    on_voting: List[Player] = []

    def __init__(self, player_list: List[Player]):
        self._state = RolesDistribution(self)
        self.players = player_list

    def transition_to(self, state):
        self._state = state

    def get_mafia_amount(self):
        mafia_amount = 0
        for player in self.players:
            if player.is_alive() and isinstance(player, Mafia):
                mafia_amount += 1
        return mafia_amount

    def __get_citizen_amount(self):
        citizen_amount = 0
        for player in self.players:
            if player.is_alive() and isinstance(player, Citizen):
                citizen_amount += 1
        return citizen_amount

    def add_to_voting(self, player_number):
        player = self.players[player_number - 1]
        if player.is_alive():
            self.on_voting.append(player)

    def is_sheriff_alive(self) -> bool:
        for player in self.players:
            if isinstance(player, Sheriff) and player.is_alive():
                return True
        return False

    def is_godfather_alive(self) -> bool:
        for player in self.players:
            if isinstance(player, Godfather) and player.is_alive():
                return True
        return False

    def is_mafia_equals_citizen_amount(self) -> bool:
        return self.get_mafia_amount() >= self.__get_citizen_amount()

    def is_player_on_voting(self, number) -> bool:
        for player in self.on_voting:
            if player.number == number and player.is_alive():
                return True
        return False

    def start(self):
        print("the game started")
        while not isinstance(self._state, GameOver):
            self._state.handle()
            self.on_voting.clear()
        self._state.handle()


class State(ABC):
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
        print("LastSpeechAfterVoting")
        if self.context.is_mafia_equals_citizen_amount():
            self.context.transition_to(MafiaWin(self.context))
        elif self.context.get_mafia_amount() == 0:
            self.context.transition_to(CitizenWin(self.context))
        else:
            self.context.transition_to(Night(self.context))


class LastSpeechAfterKill(State):
    def __init__(self, state):
        super(LastSpeechAfterKill, self).__init__(state)

    def handle(self):
        print("LastSpeechAfterKill")
        if self.context.is_mafia_equals_citizen_amount():
            self.context.transition_to(MafiaWin(self.context))
        elif self.context.get_mafia_amount() == 0:
            self.context.transition_to(CitizenWin(self.context))
        else:
            self.context.transition_to(PlayerSpeeches(self.context))


class Night(State):
    def __init__(self, state):
        super(Night, self).__init__(state)

    def __mafia_kill(self, num):
        player = self.context.players[num - 1]
        if player.is_alive():
            player.kill()
            self.context.transition_to(LastSpeechAfterKill(self.context))
        else:
            self.context.transition_to(PlayerSpeeches(self.context))

    def __sheriffs_check(self, num):
        player = self.context.players[num - 1]
        if isinstance(player, Mafia):
            print(f"{player.nickname} is Mafia")
        else:
            print(f"{player.nickname} is Citizen")

    def __godfather_check(self, num):
        player = self.context.players[num - 1]
        if isinstance(player, Sheriff):
            print(f"{player.nickname} is Sheriff")
        else:
            print(f"{player.nickname} is not Sheriff")

    def handle(self):
        print("Night")
        num_for_kill = int(input("Введите номер для убийства: "))
        if self.context.is_sheriff_alive():
            num = int(input("Введите номер для проверки шерифа: "))
            self.__sheriffs_check(num)
        if self.context.is_godfather_alive():
            num = int(input("Введите номер для проверки дона: "))
            self.__godfather_check(num)
        self.__mafia_kill(num_for_kill)
        self.context.transition_to(LastSpeechAfterKill(self.context))


class Voting(State):
    def __init__(self, state):
        super(Voting, self).__init__(state)

    def __voting(self,num):
        player = self.context.players[num - 1]
        if self.context.is_player_on_voting(player.number):
            player.kill()
            self.context.transition_to(LastSpeechAfterVoting(self.context))
        else:
            self.context.transition_to(Night(self.context))

    def handle(self):
        print("Voting")
        num = int(input("Введите номер для голосования: "))
        self.__voting(num)
        self.context.transition_to(Night(self.context))


class GameOver(State):
    def __init__(self, state):
        super(GameOver, self).__init__(state)


class MafiaWin(GameOver):
    def __init__(self, state):
        super(MafiaWin, self).__init__(state)

    def handle(self):
        print("Mafia win!")


class CitizenWin(GameOver):
    def __init__(self, state):
        super(CitizenWin, self).__init__(state)

    def handle(self):
        print("Citizens win!")


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

        for player in self.context.players:
            if player.is_alive():
                print(f"\t{player.number} {player.nickname} speech")
                self.context.add_to_voting(int(input("Введите челика на голосование: ")))
        if len(self.context.on_voting) == 0:
            self.context.transition_to(Night(self.context))
        else:
            self.context.transition_to(Voting(self.context))


if __name__ == '__main__':
    players = [Mafia("groza_pidor", 1),
               Godfather("ebloid", 2),
               Citizen("roma_huilo", 3),
               Citizen("pidor", 4),
               Citizen("debil", 5),
               Mafia("alkash", 6),
               Sheriff("degan", 7)]

    gameLoop = GameLoop(players)
    gameLoop.start()
