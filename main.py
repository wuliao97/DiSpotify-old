"""Config and Funcs"""
import config as cfg

"""Libraries for Discord"""
import discord
from discord.ext import commands

"""Useing Other Libraries"""
import sys



bot = commands.Bot(
    command_prefix="s.", intents=discord.Intents.all()
)


@bot.event
async def on_command_error(inter, error):
    e = discord.Embed(title="Error", description=error, color=discord.Color.red)
    await inter.respond(embeds=[e], ephemeral=True)

"""
@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    e = discord.Embed(title="Error", description=error, color=discord.Color.red())
    await ctx.respond(embeds=[e], ephemeral=True)
"""

def main(main:bool=True):
    for i in cfg.cog_files:
        bot.load_extension(i)

    token = cfg.TOKEN if main else cfg.SUB
    bot.run(token) 


if __name__ == "__main__":
    sub = True if not "sub" in sys.argv else False
    main(sub)