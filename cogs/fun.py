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
import enum
import requests
import textwrap as tw

import discord_webhook as dw

from pilmoji import Pilmoji
from PIL import Image, ImageDraw, ImageFont



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
    
    wanted = discord.SlashCommandGroup(
        "wanted", "", guild_ids=[1103669665756098652]
    )

    webhook = discord.SlashCommandGroup(
        "webhook"
    )


    
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
            old_name = None
            
            if (uid:=str(inter.user.id)) in data:
                old_name = data.pop(uid)
            
            if (format_handle is False and name is not None):
                data[inter.user.id] = name            
                
                
            
            f.seek(0)
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
            f.truncate()
            
        e = discord.Embed(title="正常に登録" if format_handle is False else "正常にリセット")
        if name and format_handle is False:
            e.add_field(name="New", value=f"```{name}```")
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
        
        

    @commands.slash_command(name="heart", description="make heart with string")
    async def haert_string(self, inter:discord.Interaction, string:Option(str, "material string")):
        e = discord.Embed(description="```")
        e.description += ("\n".join(["".join([(string[(x-y)%len(string)]if((x*0.05)**2+(y*0.1)**2-1)**3-(x*0.05)**2*(y*0.1)**3<=0 else' ')for x in range(-25, 25)])for y in range(12, -12, -1)]))
        e.description += "```"
        await inter.response.send_message(embed=e)



    def make_it_a_quote_base(self, url:str, msg, mode="L"):
            icon_img = Image.open(io.BytesIO(requests.get(url).content)).convert(mode=mode)
            background_img = Image.open(f"{cfg.QUOTE}background.png")
            mask_img = Image.open(f"{cfg.QUOTE}base-gd-3.png")
            black = Image.open(f"{cfg.QUOTE}background.png")
            icon = icon_img.resize((630, 630))
            background_img.paste(icon)
            result = Image.composite(black, background_img, mask=mask_img)
            draw = ImageDraw.Draw(result)

            tsize_t = self.draw_text(result, (850, 270), msg.content, size=45, color=(255,255,255,255), split_len=14, auto_expand=True) 
            user_name:str =  f"{msg.author.display_name} ({msg.author.name})#{msg.author.discriminator}" if not msg.author.display_name==msg.author.name else f"{msg.author.name}#{msg.author.discriminator}"

            self.draw_text(result, (850, tsize_t[2] + 40), str(f"- {user_name}"), size=25, color=(255,255,255,255), split_len=25, disable_dot_wrap=True)
            
            frame = f"{cfg.QUOTE}done{os.sep}result.png"
            result.save(frame)
            
            return  frame, (result.size)
        
    def draw_text(self, im, ofs, string, font=f'{cfg.FONTS}MPLUSRounded1c-Regular.ttf', size=16, color=(0,0,0,255), split_len=None, padding=4, auto_expand=False, emojis: list = [], disable_dot_wrap=False):
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

    @commands.message_command(name="Make it a Quote(Fake)")
    async def make_it_a_quote(self, inter:discord.Interaction, message:discord.Message):
        msg = await inter.channel.fetch_message(message.id)
        url = message.author.display_avatar.url
        
        file_name, b = self.make_it_a_quote_base(url=url, msg=msg, mode="L")
        h, w = b

        e = discord.Embed(color=0x2f3136)
        e.set_image(url=f"attachment://{file_name}")
        e.set_footer(text=f"{h}x{w}, {fcs.convert_size(os.stat(file_name).st_size)}")
        file = file=discord.File(file_name)
        
        await inter.response.send_message(embed=e, file=file)



def setup(bot:discord.Bot):
    return bot.add_cog(Fun(bot))
