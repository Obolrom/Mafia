from players import *
from typing import List
import random


class GameInit:
    def randomize_roles(self, players_amount):
        unrandom_setup = []
        if players_amount < 7:
            Exception("Недостаточно людей!")
        elif players_amount == 7:
            unrandom_setup = list(self.__7_players())
        elif players_amount == 8:
            unrandom_setup = list(self.__8_players())
        elif players_amount == 9:
            unrandom_setup = list(self.__9_players())
        elif players_amount == 10:
            unrandom_setup = list(self.__10_players())
        elif players_amount == 11:
            unrandom_setup = list(self.__11_players())
        elif players_amount == 12:
            unrandom_setup = list(self.__12_players())
        else:
            Exception("Слишком много людей!")
        random.shuffle(unrandom_setup)
        number = 1
        for player in unrandom_setup:
            player.number = number
            number += 1
        return unrandom_setup

    def __7_players(self) -> List[Player]:
        return [Mafia(1),
                Godfather(2),
                Sheriff(3),
                Citizen(4),
                Citizen(5),
                Citizen(6),
                Citizen(7)]

    def __8_players(self) -> List[Player]:
        setup = list(self.__7_players())
        setup.append(Citizen(8))
        return setup

    def __9_players(self) -> List[Player]:
        setup = list(self.__7_players())
        setup.append(Citizen(8))
        setup.append(Mafia(9))
        return setup

    def __10_players(self) -> List[Player]:
        setup = list(self.__7_players())
        setup.append(Citizen(8))
        setup.append(Mafia(9))
        setup.append(Citizen(10))
        return setup

    def __11_players(self) -> List[Player]:
        setup = list(self.__7_players())
        setup.append(Citizen(8))
        setup.append(Mafia(9))
        setup.append(Citizen(10))
        setup.append(Mafia(11))
        return setup

    def __12_players(self) -> List[Player]:
        setup = list(self.__7_players())
        setup.append(Citizen(8))
        setup.append(Mafia(9))
        setup.append(Citizen(10))
        setup.append(Mafia(11))
        setup.append(Citizen(12))
        return setup
