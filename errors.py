# Author : Joinemm
# File   : errors.py

from discord.ext import commands
import traceback


class Events(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        if hasattr(ctx.command, 'on_error'):
            return

        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.DisabledCommand):
            print(str(error))
            return await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            print(str(error))
            return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')

        elif isinstance(error, commands.NotOwner):
            print(str(error))

        elif isinstance(error, commands.MissingPermissions):
            print(str(error))
            perms = ', '.join([f"**{x}**" for x in error.missing_perms])
            return await ctx.send(f"`ERROR: Missing permissions` You need the {perms} permission to use this command!")

        elif isinstance(error, commands.BotMissingPermissions):
            print(str(error))
            perms = ', '.join([f"**{x}**" for x in error.missing_perms])
            return await ctx.send(f"`ERROR: Bot missing permissions` "
                                  f"I need the {perms} permission to execute this command!")

        elif isinstance(error, commands.MissingRequiredArgument):
            print(str(error))
            return await ctx.send(f"`ERROR: Missing argument` Missing required argument `{error.param}`")

        else:
            print(f"Ignoring exception in command {ctx.command}:")
            traceback.print_exception(type(error), error, error.__traceback__)
            await ctx.send(f"```\n{type(error).__name__}: {str(error)}```")


def setup(client):
    client.add_cog(Events(client))
