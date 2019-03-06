from discord.ext import commands

TOKEN = "NTUyNzkyMTIxNjk5MjA1MTIw.D2ErjQ.jzt5tVhKr4QdbM3xcZ2uOYw63rg"
extensions = ["game"]

client = commands.Bot(command_prefix="c.")


@client.event
async def on_ready():
    print("Bot is ready")

if __name__ == "__main__":
    for extension in extensions:
        try:
            client.load_extension(extension)
            print(f"{extension} loaded successfully")
        except Exception as error:
            print(f"{extension} loading failed [{error}]")

    client.run(TOKEN)
