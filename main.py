from telethon import TelegramClient, sync, events
import teleconfig as config

bot = TelegramClient('bot',
                     config.api_id,
                     config.api_hash).start(bot_token=config.TOKEN)


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message when the command /start is issued."""
    await event.respond('Hi!')
    raise events.StopPropagation


@bot.on(events.NewMessage)
async def echo(event):
    """Echo the user message."""
    await event.respond("Hello, world!")


def main():
    """Start the bot."""
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
