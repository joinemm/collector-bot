# Author : Joinemm
# File   : main.py

from discord.ext import commands

TOKEN = "XXX"  # your token here
extensions = ["game", "errors"]

client = commands.Bot(command_prefix="q!")  # change prefix here


@client.event
async def on_ready():
    if not hasattr(client, 'appinfo'):
        client.appinfo = await client.application_info()
    print("Bot is ready")

if __name__ == "__main__":
    for extension in extensions:
        try:
            client.load_extension(extension)
            print(f"{extension} loaded successfully")
        except Exception as error:
            print(f"{extension} loading failed [{error}]")

    client.run(TOKEN)
