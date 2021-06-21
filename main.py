# PLEASE NOTE:
# ------------
# This file contains the parts of files `automata.py` and, basically, the main
# Consider it was done in order to allow the several `async` functions (and 
# common) be realised, as they are defined at the different places, i.e.files.

# =================================== FILE 1 =================================

from __future__ import annotations

import re
import asyncio

from telethon import TelegramClient, events
from telethon.tl.custom.button import Button

from telethon.events import (
    NewMessage,
    CallbackQuery
)

import teleconfig as config
from abc import ABC, abstractmethod
from typing import List

from init import *
from players import *


class GameLoop:
    _state = None
    on_voting: List[Player] = []

    def __init__(self, player_list: List[Player], state=None):
        self._state = RolesDistribution(self)
        self.players = player_list
        self.state = state

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
        await wait(event, text=1)
        while not isinstance(self._state, GameOver):
            await self._state.handle(event)
            self.on_voting.clear()
        await self._state.handle(event)


class State(ABC):
    @property
    def context(self) -> GameLoop:
        return self._context

    @context.setter
    def context(self, context: GameLoop) -> None:
        self._context = context

    def __init__(self, game: GameLoop, event=None):
        self._context = game
        self.event = event

    @abstractmethod
    async def handle(self, event=None):
        pass


class CheckRoles(State):
    def __init__(self, state, event=None):
        super(CheckRoles, self).__init__(state, event)

    async def handle(self, event=None):
        print("Check roles")
        self.context.transition_to(PlayerSpeeches(self.context, event))


class LastSpeechAfterVoting(State):
    def __init__(self, state, event=None):
        super(LastSpeechAfterVoting, self).__init__(state, event)

    async def handle(self, event=None):
        print("LastSpeechAfterVoting")
        await event.respond("Last speech after voting")
        if self.context.is_mafia_equals_citizen_amount():
            self.context.transition_to(MafiaWin(self.context, self.event))
        elif self.context.get_mafia_amount() == 0:
            self.context.transition_to(CitizenWin(self.context, self.event))
        else:
            self.context.transition_to(Night(self.context, self.event))


class LastSpeechAfterKill(State):
    def __init__(self, state, event=None):
        super(LastSpeechAfterKill, self).__init__(state, event)

    async def handle(self, event=None):
        print("LastSpeechAfterKill")
        await event.respond("Last speech after kill")
        await wait(event, text=2)
        if self.context.is_mafia_equals_citizen_amount():
            self.context.transition_to(MafiaWin(self.context, self.event))
        elif self.context.get_mafia_amount() == 0:
            self.context.transition_to(CitizenWin(self.context, self.event))
        else:
            self.context.transition_to(PlayerSpeeches(self.context, event))


class Night(State):
    def __init__(self, state, event=None):
        super(Night, self).__init__(state, event)

    def __mafia_kill(self, num):
        player = self.context.players[num - 1]
        if player.is_alive():
            player.kill()
            self.context.transition_to(LastSpeechAfterKill(self.context, self.event))
        else:
            self.context.transition_to(PlayerSpeeches(self.context, self.event))

    async def __sheriffs_check(self, num):
        player = self.context.players[num - 1]

        if isinstance(player, Mafia):
            await self.event.respond(text := f"{player.nickname} is Mafia")
            print(f"{player.nickname} is Mafia")
        else:
            await self.event.respond(text := f"{player.nickname} is Citizen")
            print(f"{player.nickname} is Citizen")

    async def __godfather_check(self, num):
        player = self.context.players[num - 1]
        event = self.event
        if isinstance(player, Sheriff):
            print(f"{player.nickname} is Sheriff")
            await event.respond(f"{player.nickname} is Sheriff")
        else:
            print(f"{player.nickname} is not Sheriff")
            await event.respond(f"{player.nickname} is not Sheriff")

    async def handle(self, event=None):
        text = "Night"
        print(text)
        await event.respond('🌃Началась ночь')
        # num_for_kill = int(input("Введите номер для убийства: "))
        text = "Введите номер для убийства: "
        num_for_kill = await get_number(text, event)
        if self.context.is_sheriff_alive():
            text = "Введите номер для проверки шерифа: "
            num = await get_number(text, event)
            # num = int(input("Введите номер для проверки шерифа: "))
            await self.__sheriffs_check(num)
        if self.context.is_godfather_alive():
            text = "Введите номер для проверки дона: "
            num = await get_number(text, event)
            # num = int(input("Введите номер для проверки дона: "))
            await self.__godfather_check(num)
        self.__mafia_kill(num_for_kill)
        self.context.transition_to(LastSpeechAfterKill(self.context, self.event))


class Voting(State):
    def __init__(self, state, event=None):
        super(Voting, self).__init__(state, event)

    def __voting(self, num):
        if num == 0:
            return
        player = self.context.players[num - 1]
        if player.number == num:
            player.kill()
            self.context.transition_to(LastSpeechAfterVoting(self.context, self.event))
        else:
            self.context.transition_to(Night(self.context, self.event))

    async def handle(self, event=None):
        print("Voting")
        await event.respond("Voting")
        text = "Введите номер для голосования: "
        num_for_kill = await get_number(text, event)
        self.__voting(num_for_kill)
        self.context.transition_to(Night(self.context, self.event))


class GameOver(State):
    def __init__(self, state, event=None):
        super(GameOver, self).__init__(state, event)


class MafiaWin(GameOver):
    def __init__(self, state, event=None):
        super(MafiaWin, self).__init__(state, event)

    async def handle(self, event=None):
        await game_over("Победила мафия!")
        print("Mafia win!")


class CitizenWin(GameOver):
    def __init__(self, state, event=None):
        super(CitizenWin, self).__init__(state, event)

    async def handle(self, event=None):
        await game_over("Мирные жители выиграли!")
        print("Citizens win!")


class RolesDistribution(State):
    def __init__(self, game, event=None):
        super(RolesDistribution, self).__init__(game, event)

    async def handle(self, event=None):  # -> None:
        print("RolesDistribution")
        await event.respond("RolesDistribution")
        self.context.transition_to(MafiaAcquaintance(self.context, event))


class MafiaAcquaintance(State):
    def __init__(self, state, event=None):
        super(MafiaAcquaintance, self).__init__(state, event)

    async def handle(self, event=None):  # -> None:
        print("Hello Mafia")
        await event.respond("Приветствие мафии")
        self.context.transition_to(CheckRoles(self.context, self.event))


class PlayerSpeeches(State):
    def __init__(self, state, event=None):
        super(PlayerSpeeches, self).__init__(state, event)

    async def handle(self, event=None):
        await start_day(event)
        print("PlayerSpeeches")
        await event.respond("PlayerSpeeches")

        for player in self.context.players:
            if player.is_alive():
                nickname = player.nickname
                text = f"\t{nickname} speech"
                event = await event.respond(text)
                data = b'speach_' + bytes(nickname, encoding='utf8')
                button = Button.inline(f"🕛Начать минуту игрока {nickname}", data)
                await event.edit(
                    text=f"⏳Нажми, чтобы начать минуту игрока {nickname}",
                    buttons=button)

                print(text)

                time_elapsed = asyncio.get_event_loop().create_future()

                @bot.on(CallbackQuery(data=data))
                async def process_minute(_):
                    s = WAIT_SECONDS

                    def text_(ss):
                        return (
                            f"⏳Длится минута игрока {nickname}..."
                            f"\n\nОсталось секунд: {ss}"
                        )

                    while s:
                        s -= 1
                        await asyncio.sleep(1)
                        await event.edit(text=text_(s))

                    button = Button.inline("Время закончено", 'dummy')
                    await event.edit(text='Минута закончена', buttons=button)
                    bot.remove_event_handler(process_minute)
                    time_elapsed.set_result(True)
                    raise events.StopPropagation

                await time_elapsed

        numbers = await get_voted_people(event)
        for number in numbers:
            if number:
                # Can be done by hand?
                # self.context.add_to_voting(number)
                pass

        self.context.transition_to(Voting(self.context, event))


WAIT_SECONDS = 3  # normal: ex.: 60
MIN_PEOPLE = 7
MAX_PEOPLE = 12

players = None


def is_allowed(n):
    # print(players)
    return 0 <= n <= len(players)


bot = TelegramClient('bot',
                     config.api_id,
                     config.api_hash).start(bot_token=config.TOKEN)


async def wait(event, text):
    if text == 1:
        def text(n):
            return f"Знакомство мафии.\nОсталось: {n} сек."
    elif text == 2:
        def text(n):
            return f"Последняя речь после убийства.\nОсталось: {n} сек."
    # chat_id = event.chat.id
    # bot.send_message()
    n = WAIT_SECONDS
    message = await event.respond(text(n))
    while n:
        await asyncio.sleep(1)
        n -= 1
        await message.edit(text=text(n))
    qocontinue = Button.inline('Далее', b'confirm_continue')
    await message.edit(buttons=qocontinue)

    finished = asyncio.get_event_loop().create_future()

    @bot.on(CallbackQuery(data=b'confirm_continue'))
    async def proceed_continue(_):
        newbutton = Button.inline("✅", 'dummy')
        await message.edit(buttons=newbutton)
        bot.remove_event_handler(proceed_continue)
        finished.set_result(True)
        raise events.StopPropagation

    await finished
    # asyncio.get_event_loop().stop()  # ?


@bot.on(NewMessage(pattern='/start|/help'))
async def process_game(_):
    @bot.on(NewMessage(pattern='/help'))
    async def send_help_message(event):
        text = """Привет! Это — бот "Мафия". \
Начало игры: при помощи команды `/start количество_игроков`
"""
        event.respond(text)

    global players
    _event = None

    @bot.on(NewMessage(pattern='/start'))
    async def start(_event):
        """Начало игры по вводу команды /start <n>."""
        nonlocal event
        global players
        event = _event
        text = event.text
        try:
            pattern = r'/start[^\s]*\s+(\d+)'
            number = int(re.fullmatch(pattern, text).group(1))
        except (AttributeError, ValueError) as e:
            await event.respond(
                'Начало игры: ввод количества игроков'
                f' (от {MIN_PEOPLE} до {MAX_PEOPLE})\n'
                'Формат сообщения: /start число.\n'
                'Число — количество игроков'
            )
            raise events.StopPropagation
        game_init = GameInit()
        try:
            players = game_init.randomize_roles(number)
        except GameError:
            await event.respond('Слишком много/мало людей')
            raise events.StopPropagation
            return

        msg = '\n'.join(str(x + 1) + '. ' + str(y) for x, y in enumerate(players))
        await event.respond(msg)
        await confirm_start()

    event = _event
    del _event

    async def confirm_start():
        global players
        nonlocal event
        event = await event.respond('Маякни, когда ты прочитаешь, передашь и все познакомятся')
        finished = asyncio.get_event_loop().create_future()
        # builder = event.builder
        button = Button.inline('Далее', b'confirm_start')
        # buttons = builder.article(buttons=[button])

        # @bot.on(CallbackQuery(data='confirm_start'))
        await event.edit(buttons=[button])

        # test start
        '''
        @bot.on(NewMessage)
        async def test_echo(event):
            print(type(event), event)
        # test end
        '''

        @bot.on(CallbackQuery(data=b'confirm_start'))
        async def start_game(event_):
            global players
            await event.edit(text=event.text + '\n\n✅Продолжено')
            game_loop = GameLoop(players, event)
            await game_loop.start(event)
            bot.remove_event_handler(start_game)
            # await event.respond('Знакомство мафии. Выделенное время: 1 минута')

            finished.set_result(True)
            raise events.StopPropagation

        # event.respond(msg, buttons=buttons)
        await finished
        raise events.StopPropagation


async def start_day(event):
    sun = '☀️'
    # other helpful: '✅'; '⏳'; '🕛'

    text = sun + 'Начать день'
    event = await event.respond('Нажми, чтобы начать день')

    button = Button.inline(text, b'go_day')
    await event.edit(buttons=button)

    realised = asyncio.get_event_loop().create_future()

    @bot.on(CallbackQuery(data=b'go_day'))
    async def _start_day(_):
        await event.edit(text=event.text + f'\n\n{sun}Наступил день')
        bot.remove_event_handler(_start_day)
        realised.set_result(True)
        raise events.StopPropagation

    await realised


async def get_number(text, event):
    await event.respond(text)

    num = asyncio.get_event_loop().create_future()

    @bot.on(NewMessage)
    async def _get_number(event):
        try:
            # number = int(re.fullmatch(r'\d+', event.text))
            number = int(event.text)
            if is_allowed(number):
                num.set_result(number)
        except:
            None

    number = await num
    return number


numbers = None


async def get_voted_people(event):
    await event.respond(r'Идёт голосование. Выбор игрока: `/vote_for номер`. Отмена выбора: 0',
                        parse_mode='md')
    global numbers
    numbers = asyncio.get_event_loop().create_future()

    @bot.on(NewMessage(pattern='/vote_for'))
    async def vote_result(event):
        global numbers
        # pattern = r'/vote_for\s+(\d+)'  # old
        # pattern = r'/vote_for(?:\W+?(\d+?))+'  # new
        pattern = r'/vote_for(.+)'

        try:
            text = re.fullmatch(pattern, event.text).group(1).strip().split()
            nums = list(map(int, text))
            # nums = list(map(int, re.fullmatch(pattern, event.text).groups()))
            if all(map(is_allowed, nums)):
                await event.respond(f'Voted for Players {str(nums)[1:-1]}')
                numbers.set_result(nums)
        except Exception as e:
            print(e)
            await event.respond(
                'Синтаксис: /vote_for номер ... номер. '
                'Разделение номеров — пробелами')
            raise events.StopPropagation

    numbers_ = await numbers
    # 
    # return numbers_
    return []  # dummy


def main():
    """Start the bot."""
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
