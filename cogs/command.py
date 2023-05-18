"""Config and Funcs"""
import config as cfg
import funcs as fcs
#from main import _s_time

"""Libraries for Discord"""
import discord
from discord.ext import commands
from discord.commands import Option
from discord.ui import *

"""Useing Other Libraries"""
import os
import io
import requests
import textwrap as tw
import platform as pl
import datetime
import discord_timestamps as dts 
from PIL import Image, ImageDraw
from discord_timestamps.formats import TimestampType



class Command(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot:discord.Bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        global s_time
        s_time = datetime.datetime.now()
        
        print(datetime.datetime.now().strftime(fcs.TimeFormat.DEFAULT), self.bot.user, "on ready")
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, name="HOT DEMON B!TCHES NEAR U ! ! !",
            )
        )


    user_ = discord.SlashCommandGroup(
        "user", "various user command"
    ) 

    server_ = discord.SlashCommandGroup(
        "server", "various server command"
    )

    image = discord.SlashCommandGroup(
        name="image",
        description="For image command"
    )


    

    @commands.slash_command(name="help", description="Help about all(maybe) command!")
    async def send_help(self, inter:discord.Interaction):
        e = discord.Embed(title="Help command", color=cfg.SPFB)
        material = []
        for name, cog in self.bot.cogs.items():
            if cog.__cog_commands__ and name not in ["AdminCmd"]:
                field = [cmd for cmd in self.bot.get_cog(name).walk_commands()]
                tmp = "```" + ", ".join(map(str, field)) + "```"
                field = tw.fill(tmp, 66)

                #Cog nasme -> material.append({name:cog.description for name, cog in self.bot.cogs.items() if cog.__cog_commands__})
                material.append([field]) 
                e.add_field(name=name, value=field, inline=False)
        await inter.response.send_message(embeds = [e], view=fcs.HelpView(material, self.bot))



    @commands.user_command(name="account dates", description="Check the user Created, Joined Date")
    async def accountdetails(inter:discord.Interaction, user:discord.Member):
        e = discord.Embed(color = cfg.SPFB).set_author(icon_url = user.display_avatar, name=user)
        e.add_field(name="Created Account",   value=f"> " + dts.format_timestamp(user.created_at.timestamp(), TimestampType.RELATIVE))
        if inter.guild:
            e.add_field(
                name="Joined Server", value=f"> " + dts.format_timestamp(user.joined_at.timestamp(),  TimestampType.RELATIVE)
            )
        await inter.response.send_message(embed=e, ephemeral=True)



    @commands.slash_command(name="about-me", description="About this bot")
    async def about(self, inter:discord.Interaction):
        embed = discord.Embed(
            title="About this bot", description="For All of Spotify Lover and My friends!", color=cfg.SPFB
        )

        cogs = {name:cog for name, cog in self.bot.cogs.items() if cog.__cog_commands__ and name not in ["AdminCmd"]}
        material = list(sum(list(1 for _ in self.bot.get_cog(name).walk_commands())) for name, cog in self.bot.cogs.items() if cog.__cog_commands__ and name not in ["AdminCmd"])

        embed.add_field(
            name="Commands", value="> Cogs: **%s**\n> Total: **%s**" % (len(cogs), sum(material))
        )

        embed.add_field(name="Users", value="> Servers: **%s**\n> Members: **%s**" % (
                len(self.bot.guilds), sum([g.member_count - 1 for g in self.bot.guilds])
            )
        )
        
        u = pl.uname()
        plat =  "> OS: **%s** (*%s*)\n" % (u.system, u.release)
        plat += f"> Lang: **Python** (*{pl.python_version()}*)"

        embed.add_field(name="Platform", value=plat)
        embed.add_field(name= "Support", value= "> Deveroper: %s\n> Source: [Github.com](%s)\n> Our server: [DC Link](%s)" % (
            self.bot.get_user(1039780426564239431).mention, "https://github.com/wuliao97/Dispotify", "https://discord.gg/greta")
                        , inline=False
        )
        now = str(datetime.datetime.now() - s_time)
        embed.set_footer(text="Operaning time: %s" % (now))
        await inter.response.send_message(embeds=[embed])



    @user_.command(name="avatar", description="Get the user icon, (And Server icon If user has)")
    async def send_user_avatar(self, inter:discord.Interaction, user:discord.Member = None):
        user   = user if user else inter.user
        avatar = user.avatar.url
        e = discord.Embed(
            description = "%s's Avatar\n> **[URL](%s)**" % (user.mention, avatar),
            color       = cfg.SPFB
        )

        if (avatar == (server_avatar := user.display_avatar.url)):
            e.set_image(url=avatar)
        else:
            e.description += "\n> **[Server URL](%s)**" % server_avatar
            e.set_image(url = server_avatar)
            e.set_thumbnail(url=avatar)
        
        await inter.response.send_message(embed=e)



    @user_.command(name="banner", description="Send the User Banner If User have")
    async def send_banner_user(self, inter:discord.Interaction, user:discord.Member = None):
        user = await self.bot.fetch_user(user.id if user else inter.user.id)   
        e = discord.Embed(color = cfg.SPFB)
        if user.banner:
            e.description = f"{user.mention}'s Banner\n"
            e.description += f"> [URL]({user.banner.url})"
            e.set_image(url = user.banner.url)
            await inter.response.send_message(embed = e)
        else:
            e.description = user.name + " **haven't a Banner**. Go away."
            await inter.response.send_message(embed = e, ephemeral = True)



    @user_.command(name="information", description="Send the User Information")
    async def send_user_info(self, inter:discord.Interaction, user:discord.Member = None):
        async def extract_urls(user:discord.Member) -> list[str]:
            urls = {}
            
            try:urls["User Avatar"] = user.avatar.url
            except:pass

            if (user.avatar) != (url2:=user.display_avatar):
                urls["Server Avatr"] = url2

            if (user__ := await self.bot.fetch_user(user.id)):
                if user__.banner:
                    urls["User Banner"] = user__.banner.url

            return urls

        user = user or inter.user
        status = str(user.status)
        s_icon = "🟢" if status == "online" else "🟡" if status == "idle" else "🔴" if status == "dnd" else "⚫"
        
        embed = discord.Embed(color=cfg.SPFB)
        embed.set_thumbnail(url=user.display_avatar)
        embed.set_footer(text="Banner is User profile only!")
        embed.add_field(name="Name", value=f"> {user}")

        if (user.name != user.display_name):
            embed.add_field(name= "Nickname", value = f"> {user.display_name}")

        embed.add_field(name="Id", value=f"> {user.id}")

        if len(user.roles) >= 1:
            new_role = [r.mention for r in user.roles][1:]
            embed.add_field(
                name   = f"Roles ( {len(new_role)} )", 
                value  = f">>> {', '.join(new_role[::-1])}", 
                inline = False)

        embed.add_field(
            name  = "Created Account", 
            value = f">  {dts.format_timestamp(user.created_at.timestamp(), TimestampType.RELATIVE)}")

        embed.add_field(
            name  = "Joined Server",   
            value = f"> {dts.format_timestamp(user.joined_at.timestamp() , TimestampType.RELATIVE)}")
        

        embed.add_field(
            name  = f"Status ( {s_icon} )", 
            value = f">>> **Mobile**: `{user.mobile_status}`\n**Desktop**: `{user.desktop_status}`\n**Web status**: `{user.web_status}`",
            inline = False
        )

        urls = await extract_urls(user=user)
        embed.add_field(
            name  = "URLs",
            value = ">>> " + ", ".join([f"[{k}]({v})" for k,v in urls.items()]),
            inline = False
        )

        if (user__ := await self.bot.fetch_user(user.id)):
            if user__.banner:
                embed.set_image(url = user__.banner.url)

        await inter.response.send_message(embed=embed)




    @server_.command(name="information", description="Get information about The server")
    async def send_server_info(self, inter:discord.Interaction):
        guild                = inter.guild
        req                  = await self.bot.http.request(discord.http.Route("GET", "/guilds/" + str(guild.id)))
        tchannels, vchannels = len(guild.text_channels), len(guild.voice_channels)
        emojis   , emojis_g  = len(guild.emojis)       , sum([1 for e in guild.emojis if e.animated])
        inside  = dts.format_timestamp(guild.created_at.timestamp(), TimestampType.RELATIVE)
        outside = dts.format_timestamp(guild.created_at.timestamp(), TimestampType.SHORT_DATE)
        
        embed = discord.Embed(title=guild.name, color=cfg.SPFB)
        embed.add_field(name = "👑 Owner",    value = guild.owner.mention)
        embed.add_field(name = "🆔 ID",       value = guild.id)
        embed.add_field(name = "🗓️ Creation", value = f"{outside}({inside})")
        
        embed.add_field(name  = f"👥 Members ({guild.member_count})", value = "**%s** User | **%s** Bot\n**%s** Online(user)" % (
                            user_:=sum(1 for user in guild.members if not user.bot),
                            guild.member_count-user_,
                            sum(1 for member in guild.members if member.status != discord.Status.offline and not member.bot)))
        
        embed.add_field(
            name= f"🗨️ Channels ({tchannels + vchannels})", 
            value= "**%s** Text | **%s** Voice\n**%s** Category" % (tchannels, vchannels, len(guild.categories)))
        
        embed.add_field(
            name = f"😀 Emojis ({emojis})",
            value= "**%s** Static\n**%s** Animated\n**%s** Sticker" % (emojis-emojis_g, emojis_g, len(guild.stickers)))
        
        embed.add_field(name = "🛡️ Role", value= "**%s** Count" % (len(guild.roles)))
        
        if (guild.premium_subscription_count > 0):
            embed.add_field(name  = f"💎Boost ({guild.premium_subscription_count})", value = "**%s** Tier" % (guild.premium_tier))
        
        if (guild.icon):
            embed.set_thumbnail(url=guild.icon.url)
        
        if vanity:=req["vanity_url_code"]:
            embed.add_field(name="🔗 Vanity", value=f"`{vanity}`")
        
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        await inter.response.send_message(embed=embed)



    @server_.command(name="splash")
    async def server_splash(sedf, inter:discord.Interaction):
        e = discord.Embed(color=cfg.SPFB)
        if inter.guild.splash:
            e.title=f"{inter.guild.name}'s  Splash!"
            e.url=inter.guild.splash
            e.set_image(url=inter.guild.splash)
            flag = False
        else:
            e.title="No detected Splash."
            flag = True
        
        await inter.response.send_message(embeds=[e], ephemeral=flag)



    @image.command(name="porco", description="Generate Shit!")
    async def imageGen(
        self, 
        interaction:discord.Interaction, 
        user:discord.Member=None, 
        mode:Option(str, "画像の選択", choices=["Color", "Transparent"])="Color"
    ):
        user = user or interaction.user
        path = cfg.PORCO
        d_path  = path + "done" + os.sep

        if mode == "Color":
            base = Image.open(path + "base01.png") 
        else:
            base = Image.open(f"{path}base02.png")
        
        img = Image.open(io.BytesIO(requests.get(user.display_avatar.url).content))
        img.save(path + "material.png", format="png")

        material = Image.open(path + "material.png")
        mask_L = Image.new("L", (200, 200), 0)
        draw = ImageDraw.Draw(mask_L)
        draw.ellipse((0, 0, 200, 200), fill=255)
        mask_L.save(path + "mask_L.png")

        material = material.resize((200, 200))
        material.save(path + "material.png")
        base.paste(material, (314, 43), mask=mask_L)
        base.save(d_path + "done.png")
        
        weight, height = base.size
        e = discord.Embed(color=0x2f3136).set_image(url="attachment://porco.png")
        e.set_footer(
            text=f"{weight}x{height}, {fcs.convert_size(os.stat(f'{d_path}done.png').st_size)}")
            
        await interaction.response.send_message(
            file=discord.File(f"{d_path}done.png", filename="porco.png"), 
            embed=e
        )




"""    @commands.slash_command(name="support", description="Support command")
    async def send_support(self, inter:discord.Interaction):
        send_ch = self.bot.get_channel(1092504903907278909)
        class FeedbackModal(discord.ui.Modal):
            def __init__(self, *children: InputText, title: str, custom_id: str = None, timeout: float = None):
                super().__init__(*children, title=title, custom_id=custom_id, timeout=timeout)
                self.add_item(InputText(style=discord.InputTextStyle.short, max_length=2000, label="Must be no more than 2000 characters long"))

            async def callback(self, inter:discord.Interaction):
                e = discord.Embed(title="Sended a Feedback!", description=self.children[0].value, color=cfg.SPFB)
                e.set_footer(text=datetime.datetime.now().strftime(fcs.TimeFormat.DEFAULT))
                e.set_author(icon_url=inter.user.display_avatar.url, name=f"Requested By {inter.user}")
                await send_ch.send(embeds = [e])

        await inter.response.send_modal(FeedbackModal(title="Give "))
"""


def setup(bot:discord.Bot):
    bot.add_cog(Command(bot))