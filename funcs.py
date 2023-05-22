"""Config and Funcs"""
import config as cfg

import discord
from discord.ui import *
from discord.ext import commands
from discord_timestamps.formats import TimestampType

import math
import datetime



class TimeFormat:
    """Userfull Timeformat for strftime"""
    DEFAULT = "%Y/%m/%d (%a) %H:%M:%S" #2023/01/01 (Sun) 01:00:00
    ONE     = "%Y/%m/%d (%a) %H:%M"    #2023/01/01 (Sun) 01:00
    TWO     = "%Y/%m/%d %H:%M:%S"      #2023/01/01 01:00:00
    THREE   = "%Y/%m/%d %H:%M"         #2023/01/01 01:00

    FOUR    = "%m/%d (%a) %H:%M:%S"    #01/01 (Sun) 01:00:00
    FIVE    = "%m/%d (%a) %H:%M"       #01/01 (Sun) 01:00 
    SIX     = "%m/%d %H:%M:%S"         #01/01 01:00:00
    SEVEN   = "%m/%d %H:%M"            #01/01 01:00

    EIGHT   = "%H:%M:%S"               #01:00:00
    NINE    = "%H:%M"                  #01:00
    TEN     = "%M:%S"                  #00:00






class HelpView(discord.ui.View):
    def __init__(self, material, bot,  timeout=180, disable_on_timeout=False):
        super().__init__(timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.add_item(HelpSelect(material=material, bot=bot))


class HelpSelect(discord.ui.Select):
    def __init__(self, material, bot:commands.Bot):
        super().__init__(
            placeholder="Choose a category",
            options=[
                discord.SelectOption(label=name, description=cog.description) for name, cog in bot.cogs.items() if cog.__cog_commands__ and name not in ["AdminCmd"]
            ]
        )
        self.bot = bot
        
    async def callback(self, inter:discord.Interaction):
        cog = self.bot.get_cog(self.values[0])
        assert cog

        ll = {str(command) : str(command.description) for command in [i for i in cog.walk_commands()]}
        embed = discord.Embed(
            title=f"{cog.__cog_name__} Commands",
            description="\n".join(["**%s** : %s" % (key, value) for key, value in ll.items()])
        )
        await inter.response.send_message(
            embeds=[embed], ephemeral=True, 
            view=CmdSelect(placeholder="Command Cogs", command_list=ll, type=cog)
        )


class CmdSelect(discord.ui.Select):
    def __init__(self, placeholder, command_list:dict, type, disabled=False):
        super().__init__(placeholder, options=[
            discord.SelectOption(label=f"{idx} {command}", description=descroption, value=command) for idx, (command, descroption) in enumerate(command_list.items()) 
            ], disabled=disabled
        )
        self.cmd = command_list
        self.type = type

    async def callback(self, inter:discord.Interaction):
        print(self.values[0])




def is_dev():
    def checking(inter):
        return int(inter.author.id) in cfg.ADMINS
    return commands.check(checking)



def convert_size(size:int, units = "B"):
    units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")
    i = math.floor(math.log(size, 1024)) if size > 0 else 0
    size = round(size / 1024 ** i, 2)
    return f"{size} {units[i]}"




def dict_to_list(obj:dict):
    if not isinstance(obj, dict):
        raise TypeError("Only Dict")
    m = []
    for key, value in obj.items():
        m.append([key, value])
    return m



def check(view):
    return True if view == "Yes" else False



def forming_artist_2(material):
    return ", ".join(["**[%s](%s)**" % (obj["name"], obj['external_urls']['spotify']) for obj in material])



def forming_artist(artists, urls):
    if isinstance(artists, str):
        artists = artists.split(", ")
    elif isinstance(artists, list):
        pass
    
    return ", ".join(["**[%s](%s)**" % (fst, scd) for fst, scd in zip(artists, urls)])



def forming_(input_type:object, obj:list[str, str], symble:str="**") -> str:
    if  isinstance(input_type, str):
        obj = zip(obj[1].split(", "), obj[1])

    return ", ".join(["%s[%s](%s)" % (symble, fst, scd, symble) for fst, scd in obj])



def time_func(PLACE:str = "JST"):
    data = datetime.datetime.now()
    data = datetime.datetime.astimezone(datetime.timezone(datetime.timedelta(hours=+9))) if PLACE =="JST" else datetime.datetime.utcnow()
    return data.timestamp()



def format_timestamp(timestamp, time_s_type=TimestampType.SHORT_TIME) -> str:
    if isinstance(timestamp, int):
        int_timestamp = timestamp
    elif isinstance(timestamp, float):
        int_timestamp = int(timestamp)

    return f'<t:{int_timestamp}{time_s_type.value}>'



def get_time(sec) -> tuple:
    td = datetime.timedelta(seconds=sec)
    m, s = divmod(td.seconds, 60)
    h, m = divmod(m, 60)
    
    return td.days, h, m, s


