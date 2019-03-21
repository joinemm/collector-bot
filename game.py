import discord
from discord.ext import commands
import random
import database

database = database.Database()


class Game(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.counter = 0
        self.threshold = random.randint(*database.get_setting("frequency", (10, 20)))
        self.current_question = None
        self.correct_answer = None
        self.sending = False

    @commands.Cog.listener()
    async def on_message(self, message):

        # correct guess
        if self.current_question is not None and message.content.lower() == self.correct_answer:
            await message.channel.send(file=discord.File(open(database.get_response(self.current_question), "rb")))
            database.add_inventory_item(message.author, self.current_question)
            self.correct_answer = None
            self.current_question = None
            return

        self.counter += 1
        if not self.sending and self.counter > self.threshold:
            # spawn image
            self.sending = True
            self.current_question = random.choices(database.get_images_list(), database.get_weights())
            await message.channel.send(file=discord.File(open(database.get_filename(self.current_question), "rb")))
            self.counter = 0
            self.threshold = random.randint(*database.get_setting("frequency", (10 - 20)))
            self.correct_answer = database.get_answer(self.current_question)
            self.sending = False

    @commands.command()
    async def status(self, ctx):
        await ctx.send(f"Counter: **{self.counter}**\nNext spawn at: **{self.threshold}**")

    @commands.command()
    @commands.is_owner()
    async def spawn(self, ctx):
        self.counter = self.threshold + 1

    @commands.command()
    async def addimage(self, ctx, *args):
        try:
            quote, answer, response, f = [x.strip() for x in " ".join(args).split("|")]
        except ValueError:
            await ctx.send(f"ERROR: Invalid format.\n"
                           f"`{self.client.command_prefix}add "
                           f"[quote.filename] | [answer] | [response.filename] | frequency`")
            return

        database.add_image(quote, answer, response, f)

        await ctx.send(f"Added a new quote image `{quote}` with frequency `{f}`", file=discord.File(open(f'img/{quote}', 'rb')))
        await ctx.send(f"with the correct answer being `{answer}`\n"
                       f"and response on success being `{response}`", file=discord.File(open(f'img/{response}', 'rb')))

    @commands.command()
    async def removeimage(self, ctx, key):
        response = database.remove_image(key)
        if response:
            await ctx.send(f"Successfully removed {key}")
        else:
            await ctx.send(f"Image {key} doesn't exist.")

    @commands.command()
    async def setup(self, ctx, setting, value):
        if setting == 'channel':
            channel = await commands.TextChannelConverter().convert(ctx, value)
            if channel is None:
                await ctx.send(f"ERROR: Invalid channel {value}")

            database.change_setting("channel", channel.id)
            await ctx.send(f"Future questions will now be sent to {channel.mention}")

        elif setting == 'frequency':
            try:
                min_value, max_value = value.split("-")

                min_value = int(min_value)
                max_value = int(max_value)
            except ValueError:
                await ctx.send("ERROR: Invalid format for frequency. `min-max`\nExample: `100-500`")
                return

            database.change_setting("frequency", (min_value, max_value))
            await ctx.send(f"New questions will now be posted every {min_value} to {max_value} messages.")

    @commands.command()
    async def inventory(self, ctx):
        content = discord.Embed(title=f"{ctx.author.name}'s inventory")
        content.description = ""
        for item, qty in database.get_inventory(ctx.author).items():
            answer = database.get_answer(item)
            content.description += f"{answer} : **{qty}**"

        if content.description == "":
            content.description = "Your inventory is empty"
        await ctx.send(embed=content)


def setup(client):
    client.add_cog(Game(client))
