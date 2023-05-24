"""Config and Funcs"""
from discord.emoji import Emoji
from discord.enums import ButtonStyle
from discord.interactions import Interaction
from discord.partial_emoji import PartialEmoji
from discord.ui.item import Item
import config as cfg

import discord
from discord.ui import *
from discord.ext import commands

import math



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
            embeds=[embed], ephemeral=True
        )



class UserPermissionsView(discord.ui.View):
    def __init__(self, user:discord.Member, timeout: float=180, disable_on_timeout: bool=False):
        super().__init__(timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.user = user
    

    @discord.ui.button(label="permissions", style=discord.ButtonStyle.secondary, disabled=False)
    async def callback(self, button:discord.ui.Button, inter: Interaction):
        
        button.disabled = True
        await inter.response.edit_message(view=self)
        
        perm = self.user.guild_permissions
        
        perm_vc      = ""
        perm_manage  = ""
        perm_general = ""
        
        perm_manage += f"administrator: **{perm.administrator}**\n"
        perm_general += f"add reactions: **{perm.add_reactions}**\n"
        perm_general += f"attach files: **{perm.attach_files}**\n"
        perm_manage += f"ban members: **{perm.ban_members}**\n"
        perm_general += f"change nickname: **{perm.change_nickname}**\n"
        perm_vc += f"connect: **{perm.connect}**\n"
        perm_general += f"create instant invite: **{perm.create_instant_invite}**\n"
        perm_general += f"create private threads: **{perm.create_private_threads}**\n"
        perm_general += f"create public threads: **{perm.create_public_threads}**\n"
        perm_general += f"deafen members: **{perm.deafen_members}**\n"
        perm_general += f"embed links: **{perm.embed_links}**\n"
        perm_general += f"external emojis: **{perm.external_emojis}**\n"
        perm_general += f"external stickers: **{perm.external_stickers}**\n"
        perm_manage += f"kick members: **{perm.kick_members}**\n"
        perm_manage += f"manage channels: **{perm.manage_channels}**\n"
        perm_manage += f"manage emojis: **{perm.manage_emojis}**\n"
        perm_manage += f"manage events: **{perm.manage_events}**\n"
        perm_manage += f"manage guild: **{perm.manage_guild}**\n"
        perm_manage += f"manage messages: **{perm.manage_messages}**\n"
        perm_manage += f"manage nicknames: **{perm.manage_nicknames}**\n"
        perm_manage += f"manage roles: **{perm.manage_roles}**\n"
        perm_manage += f"manage threads: **{perm.manage_threads}**\n"
        perm_manage += f"manage webhooks: **{perm.manage_webhooks}**\n"
        perm_general += f"mention everyone: **{perm.mention_everyone}**\n"
        perm_manage += f"moderate members: **{perm.moderate_members}**\n"
        perm_vc += f"move members: **{perm.move_members}**\n"
        perm_vc += f"mute members: **{perm.mute_members}**\n"
        perm_general += f"priority speaker: **{perm.priority_speaker}**\n"
        perm_general += f"read message history: **{perm.read_message_history}**\n"
        perm_vc += f"request to speak: **{perm.request_to_speak}**\n"
        perm_general += f"send messages: **{perm.send_messages}**\n"
        perm_general += f"send messages in threads: **{perm.send_messages_in_threads}**\n"
        perm_general += f"send tts messages: **{perm.send_tts_messages}**\n"
        perm_general += f"send voice messages: **{perm.send_voice_messages}**\n"
        perm_vc += f"speak: **{perm.speak}**\n"
        perm_vc += f"start embedded activities: **{perm.start_embedded_activities}**\n"
        perm_vc += f"stream: **{perm.stream}**\n"
        perm_general += f"use slash commands: **{perm.use_slash_commands}**\n"
        perm_general += f"use voice activation: **{perm.use_voice_activation}**\n"
        perm_general += f"view audit log: **{perm.view_audit_log}**\n"
        perm_general += f"view channel: **{perm.view_channel}**\n"
        perm_general += f"view guild insights: **{perm.view_guild_insights}**\n"   

        e = discord.Embed(title="User Permissions", color=cfg.SPFB)
        e.add_field(name="general", value=perm_general)
        e.add_field(name="manage", value=perm_manage)       
        e.add_field(name="VC", value=perm_vc)

        await inter.followup.send(embed=e)



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
