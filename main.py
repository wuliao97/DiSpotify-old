"""Config and Funcs"""
import config as cfg

"""Libraries for Discord"""
import discord

"""Useing Other Libraries"""
import sys



bot = discord.Bot(
    command_prefix="s.", intents=discord.Intents.all()
)


@bot.event
async def on_command_error(inter, error):
    e = discord.Embed(title="Error", description=error, color=discord.Color.red)
    await inter.respond(embeds=[e], ephemeral=True)


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
    e = discord.Embed(title="Error", description=error, color=discord.Color.red())
    await ctx.respond(embeds=[e], ephemeral=True)



def main(main:bool=True):
    for i in cfg.cog_files:
        try:
            bot.load_extension(i)
        except Exception as err:
            print(err)

    token = cfg.TOKEN if main else cfg.SUB
    bot.run(token) 


if __name__ == "__main__":
    sub = True if not "sub" in sys.argv else False
    main(sub)