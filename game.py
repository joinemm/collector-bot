# Author : Joinemm
# File   : game.py

import discord
from discord.ext import commands
import random
import database
import asyncio
from operator import itemgetter

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
        if self.current_question is not None and message.channel.id == channel.id \
                and message.content.strip().casefold() == self.current_question.get('answer').casefold():
            self.current_question = None
            response_image = database.get_random_image()
            await channel.send(f"{message.author.mention} Correct Answer! You receive "
                               f"**{response_image.split('/')[-1].partition('.')[0]}**",
                               file=discord.File(response_image))
            database.add_inventory_item(message.author, response_image)
            return

        if not self.sending and self.counter > self.threshold:
            # spawn question
            await self.spawn_question(channel)

    async def spawn_question(self, channel):
        self.sending = True
        self.current_question = random.choice(database.get_questions())
        await channel.send(self.current_question.get('question'))
        self.counter = 0
        self.threshold = random.randint(*database.get_setting("frequency", (10, 20)))
        self.sending = False

    @commands.command()
    @commands.is_owner()
    async def status(self, ctx):
        """See how close the next spawn is"""
        await ctx.send(f"Counter: **{self.counter}**\nNext spawn at: **{self.threshold}**")

    @commands.command()
    @commands.is_owner()
    async def whitelist(self, ctx, _user):
        """Whitelist someone so they can use the spawn command"""
        user = await commands.UserConverter().convert(ctx, _user)
        database.whitelist(user.id)
        await ctx.send(f"whitelisted **{user.name}**")

    @commands.command()
    @commands.is_owner()
    async def unwhitelist(self, ctx, _user):
        """Remove user from the spawn whitelist"""
        user = await commands.UserConverter().convert(ctx, _user)
        database.unwhitelist(user.id)
        await ctx.send(f"removed **{user.name}** from the whitelist")

    @commands.command()
    async def spawn(self, ctx):
        """Force question to spawn"""
        if ctx.author.id not in database.get_whitelist(ctx):
            return await ctx.send("Sorry, you are not authorized to use this command!")
        channel = ctx.guild.get_channel(database.get_setting("channel", ctx.channel.id))
        await self.spawn_question(channel)

    @commands.command()
    @commands.is_owner()
    async def distribution(self, ctx, amount=100):
        """Test the distribution of reward images"""
        results = {}
        for i in range(int(amount)):
            result = '/'.join(database.get_random_image().split('/')[:-1]) + '/...'
            if result in results:
                results[result] += 1
            else:
                results[result] = 1

        text = f"testing distribution for {amount} spawns...```"
        for x in sorted(results, key=results.get, reverse=True):
            text += f"\n{results[x]:3d} from folder : {x}"

        await ctx.send(text + "```")

    @commands.command()
    @commands.is_owner()
    async def questions(self, ctx):
        """Get a list of all questions and answers"""
        questions = database.get_questions()

        rows = []
        pages = []
        for q in questions:
            rows.append(f"{q.get('question')} : {q.get('answer')}")

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

        if len(pages) > 1:
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
    async def add(self, ctx, *, arguments):
        """Add a new question"""
        try:
            question, answer = arguments.split("|")
        except ValueError:
            await ctx.send(f"`ERROR: Invalid format` Usage: "
                           f"`{self.client.command_prefix}add <question> | <answer>`")
            return

        database.add_question(question.strip(), answer.strip())

        await ctx.send(f"Added a new question: `{question}`\n"
                       f"With correct answer: `{answer}`\n")

    @commands.command()
    @commands.is_owner()
    async def remove(self, ctx, *, question):
        result = database.remove_question(question)
        await ctx.send("Removed the question" if result else "Could not find that question")

    @commands.command()
    @commands.is_owner()
    async def setup(self, ctx, setting=None, value=None):
        """Setup bot settings"""
        if setting == 'channel':
            try:
                channel = await commands.TextChannelConverter().convert(ctx, value)
            except commands.errors.BadArgument as e:
                return await ctx.send(str(e))

            database.change_setting("channel", channel.id)
            await ctx.send(f"New questions will now only be posted to {channel.mention}")

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
    async def view(self, ctx, filename):
        for item in database.get_inventory(ctx.author):
            if '.'.join(item.split('/')[-1].split('.')[:-1]) == filename:
                return await ctx.send(file=discord.File(item))
        await ctx.send(f"No image named {filename} found in your inventory!")

    @commands.command()
    async def inventory(self, ctx):
        """see your inventory"""
        per_page = 10
        content = discord.Embed()
        content.description = ""
        rows = []
        pages = []
        total_qty = 0
        for item, qty in database.get_inventory(ctx.author).items():
            rows.append(f"{'.'.join(item.split('/')[-1].split('.')[:-1])} : **{qty}**")
            total_qty += qty

            if len(rows) == per_page:
                pages.append("\n".join(rows))
                rows = []

        content.title = f"{ctx.author.name}'s inventory - Total {total_qty} items"

        if rows:
            pages.append("\n".join(rows))

        if not pages:
            content.description = "Your inventory is empty"
        else:
            content.description = pages[0]

        if len(pages) > 1:
            content.set_footer(text=f"page 1 of {len(pages)}")

        my_msg = await ctx.send(embed=content)

        current_page = 0

        def check(_reaction, _user):
            return _reaction.message.id == my_msg.id and not _user == self.client.user

        if len(pages) > 1:
            await my_msg.add_reaction("⬅")
            await my_msg.add_reaction("➡")
        await my_msg.add_reaction("🔡")
        await my_msg.add_reaction("#⃣")

        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=3600.0, check=check)
            except asyncio.TimeoutError:
                return
            else:
                if len(pages) > 1:
                    try:
                        if reaction.emoji == "⬅":
                            if current_page > 0:
                                current_page -= 1
                                content.description = pages[current_page]
                                content.set_footer(text=f"page {current_page + 1} of {len(pages)}")

                            await my_msg.edit(embed=content)
                            await my_msg.remove_reaction("⬅", user)

                        elif reaction.emoji == "➡":
                            if current_page < len(pages) - 1:
                                current_page += 1
                                content.description = pages[current_page]
                                content.set_footer(text=f"page {current_page + 1} of {len(pages)}")

                            await my_msg.edit(embed=content)
                            await my_msg.remove_reaction("➡", user)

                    except IndexError:
                        pass
                if reaction.emoji == "🔡":
                    pages = []
                    rows = []
                    inv = database.get_inventory(ctx.author)
                    for item in sorted(inv.keys(), key=lambda x: '.'.join(x.split('/')[-1].split('.')[:-1]).lower()):
                        rows.append(f"{'.'.join(item.split('/')[-1].split('.')[:-1])} : **{inv[item]}**")

                        if len(rows) == per_page:
                            pages.append("\n".join(rows))
                            rows = []
                    if rows:
                        pages.append("\n".join(rows))

                    content.description = pages[0]
                    await my_msg.edit(embed=content)
                    await my_msg.remove_reaction("🔡", user)
                elif reaction.emoji == "#⃣":
                    pages = []
                    rows = []
                    for item, qty in sorted(database.get_inventory(ctx.author).items(),
                                            key=itemgetter(1), reverse=True):
                        rows.append(f"{'.'.join(item.split('/')[-1].split('.')[:-1])} : **{qty}**")

                        if len(rows) == per_page:
                            pages.append("\n".join(rows))
                            rows = []
                    if rows:
                        pages.append("\n".join(rows))

                    content.description = pages[0]
                    await my_msg.edit(embed=content)
                    await my_msg.remove_reaction("#⃣", user)
                else:
                    continue

    @commands.command()
    async def leaderboard(self, ctx):
        """Show the top collectors leaderboard"""
        content = discord.Embed()
        content.title = f"Top 5 collectors"
        content.description = ''

        usersdata = []
        data = database.get_users()
        for userid in data:

            user = self.client.get_user(int(userid))

            qty = 0
            for item in data[userid]:
                qty += data[userid][item]
            usersdata.append((user, qty))

        n = 0
        for user, qty in sorted(usersdata, key=itemgetter(1), reverse=True):
            if n == 5:
                break
            content.description += f"\n`{n + 1}.` **{user.name}** - **{qty}**"
            n += 1

        await ctx.send(embed=content)


def setup(client):
    client.add_cog(Game(client))
