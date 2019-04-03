# Author : Joinemm
# File   : game.py

import discord
from discord.ext import commands
import random
import database
import asyncio

database = database.Database()


class Game(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.counter = 0
        self.threshold = random.randint(*database.get_setting("frequency", (10, 20)))
        self.current_question = None
        self.sending = False

    @commands.Cog.listener()
    async def on_message(self, message):
        self.counter += 1
        channel = message.guild.get_channel(database.get_setting("channel", message.channel.id))

        # correct guess
        if self.current_question is not None and message.content.lower() == self.current_question.get('answer').lower():
            response_image = database.get_random_image()
            await channel.send(file=discord.File(response_image))
            database.add_inventory_item(message.author, response_image)
            self.current_question = None
            return

        if not self.sending and self.counter > self.threshold:
            # spawn question
            self.sending = True
            quotes, weights = database.get_quotes_and_weights()
            self.current_question = random.choices(quotes, weights)[0]
            await channel.send(self.current_question.get('question'))
            self.counter = 0
            self.threshold = random.randint(*database.get_setting("frequency", (10 - 20)))
            self.sending = False

    @commands.command()
    @commands.is_owner()
    async def status(self, ctx):
        """See how close the next spawn is"""
        await ctx.send(f"Counter: **{self.counter}**\nNext spawn at: **{self.threshold}**")

    @commands.command()
    @commands.is_owner()
    async def spawn(self, ctx):
        """Set image to spawn on next message"""
        self.counter = self.threshold

    @commands.command()
    @commands.is_owner()
    async def distribution(self, ctx, amount=100):
        results = {}
        for i in range(int(amount)):
            quotes, weights = database.get_quotes_and_weights()
            result = random.choices(quotes, weights)[0].get('question')
            if result in results:
                results[result] += 1
            else:
                results[result] = 1

        text = f"testing distribution for {amount} spawns...```"
        for x in results:
            text += f"\n{results[x]:2d} : {x}"

        await ctx.send(text + "```")

    @commands.command()
    @commands.is_owner()
    async def questions(self, ctx):
        quotes, weights = database.get_quotes_and_weights()

        rows = []
        pages = []
        for q in quotes:
            rows.append(f"{q.get('frequency'):2d} : {q.get('question')}")

            if len(rows) == 20:
                pages.append("\n".join(rows))
                rows = []

        if rows:
            pages.append("\n".join(rows))

        content = discord.Embed(title="All questions and frequencies")
        if not pages:
            content.description = "No questions in database"
        else:
            content.description = pages[0]

        content.set_footer(text=f"page 1 of {len(pages)}")
        my_msg = await ctx.send(embed=content)

        if len(pages) > 1:

            current_page = 0

            def check(_reaction, _user):
                return _reaction.message.id == my_msg.id and _reaction.emoji in ["⬅", "➡"] \
                       and not _user == self.client.user

            await my_msg.add_reaction("⬅")
            await my_msg.add_reaction("➡")

            while True:
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=3600.0, check=check)
                except asyncio.TimeoutError:
                    return
                else:
                    try:
                        if reaction.emoji == "⬅" and current_page > 0:
                            content.description = pages[current_page - 1]
                            current_page -= 1
                            await my_msg.remove_reaction("⬅", user)
                        elif reaction.emoji == "➡":
                            content.description = pages[current_page + 1]
                            current_page += 1
                            await my_msg.remove_reaction("➡", user)
                        else:
                            continue
                        content.set_footer(text=f"page {current_page + 1} of {len(pages)}")
                        await my_msg.edit(embed=content)
                    except IndexError:
                        continue

    @commands.command()
    @commands.is_owner()
    async def addquestion(self, ctx, *args):
        """Add a new image"""
        try:
            variables = [x.strip() for x in " ".join(args).split("|")]
            if len(variables) == 2:
                quote, answer = variables
                f = 1
            else:
                quote, answer, f = variables
        except ValueError:
            await ctx.send(f"ERROR: Invalid format.\n"
                           f"`{self.client.command_prefix}add <question> | <answer> | <frequency>`")
            return

        database.add_quote(quote, answer, int(f))

        await ctx.send(f"Added a new question: `{quote}`\n"
                       f"Correct answer: `{answer}`\n"
                       f"Spawning frequency: `{int(f)}`")

    @commands.command()
    @commands.is_owner()
    async def setup(self, ctx, setting=None, value=None):
        """Setup bot settings"""
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
        else:
            f = database.get_setting('frequency', (10, 20))
            c = ctx.guild.get_channel(database.get_setting('channel'))
            m = f"**Current settings:**\n" \
                f"Channel = {c.mention if c is not None else 'None'}\n" \
                f"Frequency = every {f[0]} to {f[1]} messages"

            await ctx.send(m)

    @commands.command()
    async def inventory(self, ctx):
        """see your inventory"""
        content = discord.Embed(title=f"{ctx.author.name}'s inventory")
        content.description = ""
        rows = []
        pages = []
        for item, qty in database.get_inventory(ctx.author).items():
            rows.append(f"{item} : **{qty}**")

            if len(rows) == 10:
                pages.append("\n".join(rows))
                rows = []

        if rows:
            pages.append("\n".join(rows))

        if not pages:
            content.description = "Your inventory is empty"
        else:
            content.description = pages[0]

        content.set_footer(text=f"page 1 of {len(pages)}")
        my_msg = await ctx.send(embed=content)

        if len(pages) > 1:

            current_page = 0

            def check(_reaction, _user):
                return _reaction.message.id == my_msg.id and _reaction.emoji in ["⬅", "➡"] \
                       and not _user == self.client.user

            await my_msg.add_reaction("⬅")
            await my_msg.add_reaction("➡")

            while True:
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=3600.0, check=check)
                except asyncio.TimeoutError:
                    return
                else:
                    try:
                        if reaction.emoji == "⬅" and current_page > 0:
                            content.description = pages[current_page - 1]
                            current_page -= 1
                            await my_msg.remove_reaction("⬅", user)
                        elif reaction.emoji == "➡":
                            content.description = pages[current_page + 1]
                            current_page += 1
                            await my_msg.remove_reaction("➡", user)
                        else:
                            continue
                        content.set_footer(text=f"page {current_page + 1} of {len(pages)}")
                        await my_msg.edit(embed=content)
                    except IndexError:
                        continue


def setup(client):
    client.add_cog(Game(client))
