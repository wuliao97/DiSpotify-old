"""Config and Funcs"""
import config as cfg
import funcs as fcs

"""Libraries for Discord"""
import discord
from discord.ext import commands
from discord.commands import Option
from discord.ui import *

"""Useing Other Libraries"""
import sys
import discord_timestamps as dts 
from discord_timestamps.formats import TimestampType


class AdminCmd(commands.Cog):
    def __init__(self, bot):
        self.bot:commands.Bot = bot


    secret = discord.SlashCommandGroup(
        name        = "secret",
        description = "ADMIN ONLY. It's Literally ",
        guild_ids   = cfg.SERVERS
    )

    s = secret.create_subgroup(
        "server", "me only"
    )
    

    @s.command(name="exit", description="only admin")
    @commands.is_owner()
    async def exit_(self, inter:discord.Interaction, optin:Option(str, choices=["exit", "kill"])):
        e = discord.Embed(title="System Exit", color=cfg.SPFB)
        await inter.response.send_message(embed=e)
        sys.exit()


    @secret.command(name="activity", desscription="Changes the activity of the bot.")
    @commands.is_owner()
    async def activity(self, interaction:discord.Interaction, activity=discord.Option(str, "activity", required=True)):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=activity))
        embed= discord.Embed(description=f"Activity has been changed to `{activity}`")
        await interaction.respond(embed=embed)

    
    @s.command(name="list", description="管理者専用", guild_ids=cfg.SERVERS)
    @commands.is_owner()
    async def inserver(self, interaction:discord.Interaction):
        e = discord.Embed(
            title       = f"Total Server {len(self.bot.guilds)}", 
            color       = cfg.SPFB,
            description = "\n".join(["||%s|| **%s**" % (s.id, s.name) for s in self.bot.guilds]))
        await interaction.response.send_message(embed = e, ephemeral=True)



    @s.command(name="xray", description="server idを入れてね!このボットが入ってるサーバーの情報を取得", guild_ids=cfg.SERVERS)
    @commands.is_owner()
    async def xserver(self, inter:discord.Interaction, id):
        guild                = self.bot.get_guild(int(id))
        req                  = await self.bot.http.request(discord.http.Route("GET", "/guilds/" + str(guild.id)))
        tchannels, vchannels = len(guild.text_channels), len(guild.voice_channels)
        emojis   , emojis_g  = len(guild.emojis)       , sum([1 for e in guild.emojis if e.animated])
            
        embed = discord.Embed(
            title = guild.name, 
            color = cfg.SPFB
        )
        embed.add_field(name = "Owner", value = guild.owner.mention)
        embed.add_field(name = "ID",    value = guild.id)
        embed.add_field(name = "Creation", value = f"{dts.format_timestamp(guild.created_at.timestamp(), TimestampType.RELATIVE)}")
        
        embed.add_field(name  = f"Members ({guild.member_count})", 
                        value = "**%s** User | **%s** Bot\n**%s** Online(user)" % (
                            user_ := sum(1 for user in guild.members if not user.bot),
                            guild.member_count - user_,
                            sum(1 for member in guild.members if member.status != discord.Status.offline and not member.bot)))

        embed.add_field(
            name  = f"Channels ({tchannels + vchannels})", 
            value ="**%s** Text | **%s** Voice\n**%s** Category" % (tchannels, vchannels, len(guild.categories)))
        
        embed.add_field(
            name  = f"Emojis ({emojis})",
            value = "**%s** Static\n**%s** Animated\n**%s** Sticker" % (emojis-emojis_g, emojis_g, len(guild.stickers)))
        
        embed.add_field(name = "Role", value= "**%s** Count" % (len(guild.roles)))
        
        if guild.premium_subscription_count > 0:
            embed.add_field(name=f"Boost ({guild.premium_subscription_count})", value="**%s** Tier" % (guild.premium_tier))
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if vanity:=req["vanity_url_code"]:
            embed.add_field(name="Vanity", value=f"`{vanity}`")

        await inter.response.send_message(embed = embed)



    @s.command(name="members", description="admin only", guild_ids=cfg.SERVERS)
    @commands.is_owner()
    async def member_list(self, inter:discord.Interaction, id=None):
        guild = self.bot.get_guild(int(id if id else inter.guild.id))
        es = [
            discord.Embed(
                title       = "TOTAL " + str(guild.member_count),
                description = "|-User (%s)\n|-Bot (%s)" % (_user := sum(1 for member in guild.members if not member.bot), guild.member_count - _user),
                color       = cfg.SPFB)
        ]
        es.append(
            discord.Embed(
            title       = "User", 
            description = "\n".join(["%s : %s" % (user.id, user) for user in guild.members if not user.bot]), 
            color       = cfg.SPFB)
        )
        es.append(
            discord.Embed(
                title       = "Bot",  
                description = "\n".join(["%s : %s" % (user.id, user) for user in guild.members if user.bot]), 
                color       = cfg.SPFB)
        )

        await inter.response.send_message(embeds=es, ephemeral=True)



    @inserver.error
    async def send_error(self, inter:discord.Interaction, error):
        e = discord.Embed(title="Error", description=error, color=discord.Color.red())
        await inter.response.send_message(embed=e, ephemeral=True)

    @xserver.error
    async def send_error(self, inter:discord.Interaction, error):
        e = discord.Embed(title="Error", description=error, color=discord.Color.red())
        await inter.response.send_message(embed=e, ephemeral=True)

    @member_list.error
    async def send_error(self, inter:discord.Interaction, error):
        e = discord.Embed(title="Error", description=error, color=discord.Color.red())
        await inter.response.send_message(embed=e, ephemeral=True)



def setup(bot:commands.Bot):
    bot.add_cog(AdminCmd(bot))