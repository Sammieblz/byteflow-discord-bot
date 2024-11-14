from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from bot_responses import get_response
from discord import File


context = {}
# STEP 0: LOAD TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# STEP 1: SETUP BOT PERMISSIONS (INTENTS)
intents: Intents = Intents.default()
intents.message_content = True # NOQA (No quality assurance: suppresses the warnings from pycharm)
client: Client = Client(intents=intents)

# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    global context
    response, file = get_response(user_message, context)

    if "What's your name?" in response:
        context['awaiting_name'] = True

    if file:  # Send file if available
        await (message.author.send(response, file=File(file)) if user_message.startswith('?') else message.channel.send(response, file=File(file)))

    else:  # Send only text response
        await (message.author.send(response) if user_message.startswith('?') else message.channel.send(response))

# STEP 3: HANDLING THE BOT STARTUP
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

# STEP 4: HANDLING INCOMING MESSAGES
@client.event
async def on_message(message: Message) -> None:
    global context

    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')

    if context.get('awaiting_name') and not user_message.startswith('?'):
        name = user_message.strip()
        context['user_name'] = name
        await send_message(message, f"Nice to meet you, {name}!")
        del context['awaiting_name']
    else:
        await send_message(message, user_message)


# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)

if __name__ == '__main__':
    main()

