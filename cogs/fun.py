"""Config and Funcs"""
import config as cfg
import funcs as fcs

"""Libraries for Discord"""
import discord
from discord.ext import commands
from discord.commands import Option
from discord.ui import *

"""Useing Other Libraries"""
import os
import io
import json
import time
import requests
import textwrap as tw
import platform as pl
import datetime

import discord_timestamps as dts 
import discord_webhook as dw

from pilmoji import Pilmoji
from PIL import Image, ImageDraw, ImageFont
from discord_timestamps.formats import TimestampType




class Fun(commands.Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot
        self.count = 0
        self.webhook_url = "https://discord.com/api/webhooks/1104369374032318625/kZrkgS6CsiadKNitrmbrOiKou_4GC3DK5iJ46KwxC_4vCd1NNT460x0bFzef0g-WDEHX"
    
    
    gifcmd = discord.SlashCommandGroup(
        "gif", "various gif command"
    )
    
    fiveChCmd = discord.SlashCommandGroup(
        "5ch", "various 5ch command", guild_ids=[1103669665756098652]
    )
    
    wanted = discord.SlashCommandGroup("wanted", "")
    

    @wanted.command(name="list")
    async def wanted_list(
        self, inter:discord.Interaction, send_a_json:Option(bool, "Would you want to send a ID of File?", choices=[True, False], default=False)
    ):
        with open((c:=f".{os.sep}config{os.sep}hates.json"), encoding="utf-8") as f:
            data = json.load(f)
        e = discord.Embed(description="\n".join(map(str, data["ids"])))
        file = discord.File(c) if send_a_json else None
        
        await inter.response.send_message(embeds=[e], file=file)
    
    """
    @wanted.command(name="add")
    async def wanted_list(
        self, inter:discord.Interaction, id:str
    ):
        with open((f".{os.sep}config{os.sep}hates.json"), "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["ids"].append(id)
            
            f.seek(0)
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
            f.truncate()
            
        e = discord.Embed(title="Successfully added!")
        
        await inter.response.send_message(embeds=[e], ephemeral=True)
    """
    
    @commands.Cog.listener()
    async def on_message(self, message:discord.message.Message):
        
        if message.author.bot:
            return
        if message.channel.id != 1104245431887745095:
            return
        
        await message.delete()
        
        with open(f"{cfg.FIVECH}name.json" , encoding="utf-8") as f:
            data = json.load(f) 
    
        user_name = data[user_id] if (user_id:=str(message.author.id)) in data else "風吹けば名無し"
        self.count += 1

        name_default = "%s : %s" % (self.count, user_name)

        webhook = dw.DiscordWebhook(
            url=self.webhook_url, username=name_default, content=message.content, rate_limit_retry=True,
        )
        
        #if message.attachments != []:   
        #    webhook.add_file()
            

        if message.reference:
            reference_msg = await message.channel.fetch_message(message.reference.message_id) #メッセージIDから、元のメッセージを取得
            
            if reference_msg.embeds and reference_msg.author == self.bot.user: #返信の元のメッセージが、埋め込みメッセージかつ、このBOTが送信したメッセージのとき→グローバルチャットの他のサーバーからのメッセージと判断
                reference_message_content = reference_msg.embeds[0].description #メッセージの内容を埋め込みから取得
                reference_message_author = reference_msg.embeds[0].author.name #メッセージのユーザーを埋め込みから取得
            
            elif reference_msg.author != self.bot.user: #返信の元のメッセージが、このBOTが送信したメッセージでは無い時→同じチャンネルのメッセージと判断
                reference_message_content = reference_msg.content 
                reference_message_author = reference_msg.author.name
            
            url = message.reference.jump_url
            reference_content = "\n".join(["> " + string for string in reference_message_content.splitlines()]) 
            reference_value = "**{}**\n{}".format(reference_message_author, reference_content) 
            
            webhook.add_embed(dw.DiscordEmbed(title="Jump to URL", url=url, description=reference_value))            
            
        res = webhook.execute()

    
    
    @fiveChCmd.command(name="handle")
    async def five_ch_pin_handle(
        self, 
        inter:discord.ApplicationContext, 
        name:Option(str, "Pin Handle", max_length=20, default=None),
        format_handle:Option(bool, "ハンドルネームの削除をしますか？", choices=[False, True], default=False)
    ):
        with open(f"{cfg.FIVECH}name.json", "r+", encoding="utf-8") as f:
            data:dict= json.load(f)
            
            if (format_handle and name is None):
                data[inter.user.id] = name
            else:
                old_name = None
            
            if (uid:=str(inter.user.id)) in data:
                old_name = data.pop(uid)
            
            f.seek(0)
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
            f.truncate()
            
        e = discord.Embed(title="正常に登録").add_field(name="New", value=f"```{name}```")
        if old_name:
            e.add_field(name="Old", value=f"```{old_name}```")
            
        await inter.respond(embeds=[e], ephemeral=True)
    
    
    
    @fiveChCmd.command(name="send")
    async def five_ch_send(self, inter:discord.ApplicationContext, message:str, handle:Option(str, "", default=None)):
        with open(f"{cfg.FIVECH}name.json" , encoding="utf-8") as f:
            data = json.load(f) 

        if handle:
            user_name = handle
        else:
            user_name = data[user_id] if (user_id:=str(inter.user.id)) in data else "風吹けば名無し"
        
        self.count += 1
        name_default = "%s : %s" % (self.count, user_name)

        webhook = dw.DiscordWebhook(
            url=self.webhook_url, username=name_default, content=message, rate_limit_retry=True,
        )
        """
        if image:
            image:discord.Attachment = image
            image.save(f"{cfg.FIVECH}image.png")
            webhook.add_file(f"{cfg.FIVECH}image.png", "image.png")
        """
        res = webhook.execute()
        
        await inter.response.send_message("send!", ephemeral=True, delete_after=3)
        
    """
    @commands.command(name="test-questions")
    async def q_information_security(self, ctx):
        var = random.randint(1, 10)
        base_embed = discord.Embed(color = 0x6cd1c1)

        r_1 = "<:_1:973779279575924738>"
        r_2 = "<:_2:973779279605301248>"
        r_3 = "<:_3:973779279248785409>"
        r_4 = "<:_4:973779300258025472>"

        answer = ""
        asw = ""
        try:
            reaction, user = await self.bot.wait_for("reaction_add",timeout = 30.0,check = lambda ctx: user == ctx.author and str(reaction.emoji) in [r_1, r_2, r_3, r_4])
        except asyncio.TimeoutError:
            e = discord.Embed(title = ":timer:時間切れ！",description = "よって中断します。",color = 0xff0000)
            await ctx.send(embed=e)
        else:
            while True:
                if str(reaction.emoji) == asw:
                    e = discord.Embed(title = ":o:正解",color = 0x0000ff)
                    await ctx.send(embed= e)
                    break
                else:
                    mistake_e = discord.Embed(title = ":x:不正解",description = "None",color = 0xff0000)
    """

    @commands.slash_command(name="heart", description="make heart with string")
    async def haert_string(self, inter:discord.Interaction, string:Option(str, "material string")):
        e = discord.Embed(description="```")
        e.description += ("\n".join(["".join([(string[(x-y)%len(string)]if((x*0.05)**2+(y*0.1)**2-1)**3-(x*0.05)**2*(y*0.1)**3<=0 else' ')for x in range(-25, 25)])for y in range(12, -12, -1)]))
        e.description += "```"
        await inter.response.send_message(embed=e)



    """    @gifcmd.command(name="create")
    async def gifcmd_create(
        self, 
        inter:discord.Interaction, 
        mp4:Option(discord.Attachment, ""),
        scale:Option(int, "Image scale:  1980px > scale > 100px") = None,
        quality:Option(str, "GIF Quality", choices=["high", "low"]) = "low",
    ):
        def toGif(mp4:discord.Attachment, quality:str, scale:int):
            path = f"{cfg.GIF}"
            quality = 30 if quality == "high" else 10

            output = f"{cfg.GIF}{os.sep}done{os.sep}{mp4.filename}"
            ffmpeg = f'ffmpeg -y -i {mp4} -filter_complex "[0:v] fps={quality},scale={scale}:-1,split [a][b];[a] palettegen [p];[b][p] paletteuse=dither=none" {output}'
            
            s_time = time.time()
            systemcalling(ffmpeg)
            e_time = round((time.time() - s_time), 2)

            return output, e_time

        def systemcalling(code):
            os.system(code)

            
        file:discord.Attachment = mp4
        
        if scale is not None:
            if not 1980 > scale > 100:
                raise Exception("PLEASE THE SET IN  1980px > scale > 100px")
        else:
            scale = 680
        
        if not ".mp4" in file.filename:
            raise NameError("Please set a mp4")
        
        
        material = Image.open(io.BytesIO(mp4))
        material.save(path:=cfg.GIF + "material.mp4")
        
        fn, end_time = toGif(path, quality, scale)
        
        anon = AnonFile()
        upload = anon.upload(fn, progressbar=True)
        
        e = discord.Embed(title="Dwnload", url=upload.url.geturl(), color=cfg.SPFB)
        e.add_field(name="Time", value=f">>> {end_time}")
                
        await inter.respond("Here's your file!")
    """
    

    @commands.message_command(name="Make it a Quote(Fake)")
    async def make_it_a_quote(self, inter:discord.Interaction, message:discord.Message):
        W, H = 1200, 630
        
        def make_it_a_quote_base(url:str, msg, mode="L"):
            icon_img = Image.open(io.BytesIO(requests.get(url).content)).convert(mode=mode)
            background_img = Image.open(f"{cfg.QUOTE}background.png")
            mask_img = Image.open(f"{cfg.QUOTE}base-gd-3.png")
            black = Image.open(f"{cfg.QUOTE}background.png")
            icon = icon_img.resize((H, H))
            background_img.paste(icon)
            result = Image.composite(black, background_img, mask=mask_img)
            draw = ImageDraw.Draw(result)

            tsize_t = draw_text(result, (850, 270), msg.content, size=45, color=(255,255,255,255), split_len=14, auto_expand=True) 
            user_name:str =  f"{msg.author.display_name} ({msg.author.name})#{msg.author.discriminator}" if not msg.author.display_name==msg.author.name else f"{msg.author.name}#{msg.author.discriminator}"

            draw_text(result, (850, tsize_t[2] + 40), str(f"- {user_name}"), size=25, color=(255,255,255,255), split_len=25, disable_dot_wrap=True)
            
            frame = f"{cfg.QUOTE}done{os.sep}result.png"
            print(os.path.exists(frame))
            result.save(frame)
            
            return  frame, (result.size)
        
        def draw_text(im, ofs, string, font=f'{cfg.FONTS}MPLUSRounded1c-Regular.ttf', size=16, color=(0,0,0,255), split_len=None, padding=4, auto_expand=False, emojis: list = [], disable_dot_wrap=False):
            draw = ImageDraw.Draw(im)
            fontObj = ImageFont.truetype(font, size=size)

            pure_lines, pos, l = [], 0, ""

            if not disable_dot_wrap:
                for char in str(string):
                    if char == '\n':
                        pure_lines.append(l)
                        l = ''
                        pos += 1
                    elif char == '、' or char == ',':
                        pure_lines.append(l + ('、' if char == '、' else ','))
                        l = ''
                        pos += 1
                    elif char == '。' or char == '.':
                        pure_lines.append(l + ('。' if char == '。' else '.'))
                        l = ''
                        pos += 1
                    else:
                        l += char
                        pos += 1
                if l:
                    pure_lines.append(l)
            else:
                pure_lines = string.split('\n')

            lines = []

            for line in pure_lines:
                lines.extend(tw.wrap(line, width=split_len))
            
            dy = 0
            draw_lines = []

            for line in lines:
                tsize = fontObj.getsize(line)
                ofs_y = ofs[1] + dy
                t_height = tsize[1]

                x = int(ofs[0] - (tsize[0]/2))
                draw_lines.append((x, ofs_y, line))
                ofs_y += t_height + padding
                dy += t_height + padding
            
            adj_y = -30 * (len(draw_lines)-1)
            for dl in draw_lines:
                with Pilmoji(im) as p:
                    p.text((dl[0], (adj_y + dl[1])), dl[2], font=fontObj, fill=color, emojis=emojis, emoji_position_offset=(-4, 4))

            real_y = ofs[1] + adj_y + dy
            return (0, dy, real_y)


        msg = await inter.channel.fetch_message(message.id)
        url = message.author.display_avatar.url
        
        file_name, b = make_it_a_quote_base(url=url, msg=msg, mode="L")
        b = iter(b)

        e = discord.Embed(color=0x2f3136)
        e.set_image(url=f"attachment://{file_name}")
        e.set_footer(text=f"{next(b)}x{next(b)}, {fcs.convert_size(os.stat(file_name).st_size)}")
        file = file=discord.File(file_name)
        
        await inter.response.send_message(embed=e, file=file)


def setup(bot:discord.Bot):
    return bot.add_cog(Fun(bot))
