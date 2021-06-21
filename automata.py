# Это устаревшая версия, итоговая находится в main.py.

from __future__ import annotations
from init import *
from typing import List

from main import get_voted_people, start_day
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

    async def start(self, event):
        print("the game started")
        # await event.respond('Знакомство мафии. Выделенное время: 1 минута')
        await wait(event)
        while not isinstance(self._state, GameOver):
            await self._state.handle()
            self.on_voting.clear()
        await self._state.handle()


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

    async def handle(self):
        print("LastSpeechAfterVoting")
        await event.respond("Last speech after voting")
        if self.context.is_mafia_equals_citizen_amount():
            self.context.transition_to(MafiaWin(self.context))
        elif self.context.get_mafia_amount() == 0:
            self.context.transition_to(CitizenWin(self.context))
        else:
            self.context.transition_to(Night(self.context))


class LastSpeechAfterKill(State):
    def __init__(self, state):
        super(LastSpeechAfterKill, self).__init__(state)

    async def handle(self):
        print("LastSpeechAfterKill")
        await event.respond("Last speech after kill")
        await wait(event)
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

    async def handle(self):
        print("Night")
        # num_for_kill = int(input("Введите номер для убийства: "))
        text = "Введите номер для убийства: "
        entry = await get_number(text, event)
        if self.context.is_sheriff_alive():
            text = "Введите номер для убийства: "
            entry = await get_number(text, event)
            # num = int(input("Введите номер для проверки шерифа: "))
            self.__sheriffs_check(num)
        if self.context.is_godfather_alive():
            text = "Введите номер для убийства: "
            entry = await get_number(text, event)
            # num = int(input("Введите номер для проверки дона: "))
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

    async def handle(self):
        print("Voting")
        text = "Введите номер для голосования: "
        await get_vote_number(event, text)
        num = int(input(text))
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
        print("RolesDistribution");  # await event.
        self.context.transition_to(MafiaAcquaintance(self.context))


class MafiaAcquaintance(State):
    def __init__(self, state):
        super(MafiaAcquaintance, self).__init__(state)

    async def handle(self) -> None:
        print("Hello Mafia")
        await event.respond("Приветствие мафии")  # TODO: place the bot, actually, here
        self.context.transition_to(CheckRoles(self.context))


class PlayerSpeeches(State):
    def __init__(self, state):
        super(PlayerSpeeches, self).__init__(state)

    async def handle(self):
        await start_day(event)
        print("PlayerSpeeches")

        async for player in self.context.players:
            if player.is_alive():
                text = f"\t{player.nickname} speech"
                nickname = player.nickname
                data = b'speach_' + bytes(nickname, encoding='utf8')
                button = construct_button("Начать минуту игрока {nickname}",
                    data)
                await event.edit_message(
                    text=f"Нажми, чтобы начать минуту игрока {player.nickname}",
                    buttons=button)

                print(text)

                @bot.on(CallbackQuery(data=data))
                async def process_minute(event_):
                    s = 60
                    def text_(s):
                        return (
                            "Длится минута игрока {nickname}..."
                            f"\n\nОсталось секунд: {s}"
                            )
                    button = construct_button(text_(s), 'dummy')
                    # ^ with the dummy payload, not to propagate or trigger.
                    while s:
                        await event.edit_message(text=text_(s))
                        time.sleep(1)
                        s -= 1

                    event.edit_message(text='Минута закончена', buttons=[button])
                # event.respond(...)  # ?
                # int(input("Введите челика на голосование: "))
                number = await get_voted_people(event)
                self.context.add_to_voting(number)
        if len(self.context.on_voting) == 0:
            self.context.transition_to(Night(self.context))
        else:
            self.context.transition_to(Voting(self.context))


if __name__ == '__main__':
    game_init = GameInit()
    players = game_init.randomize_roles(8)

    gameLoop = GameLoop(players)
    gameLoop.start()