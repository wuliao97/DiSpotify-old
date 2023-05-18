"""Config and Funcs"""
import config as cfg
from funcs import *

import discord
from discord.ui import *

import os
import io
import random
import urllib
import textwrap, requests, datetime, dateutil

from PIL import Image, ImageDraw, ImageFont






def search_url(param):
    return "https://open.spotify.com/search/" + urllib.parse.quote(str(param))



def check_user(user:discord.Member):
    flag     = False
    material = next((activity for activity in user.activities if isinstance(activity, discord.Spotify)), None)
    message  = ""

    if user.status in ["offline", "invisible"]:
        message = "This User status is OFFLINE!"
        
    elif material is None:
        message = f"{user.mention} is not listening to Spotify!"
    
    else:
        flag = True
        
    return flag, material, message



def spotify(user:discord.Member):
    flag, material, message = check_user(user)
            
    return flag, material, message
        



def artists_cut(obj:discord.Spotify):
    return ", ".join(obj.artists) if isinstance(obj.artists, list) else obj.artist



def track_time(material:discord.Spotify):
    return dateutil.parser.parse(str(material.duration)).strftime('%M:%S')



def data_cutting(title:str, album:str) -> str:
    title = title.translate(str.maketrans({"[":"(", ")":")"}))
    title = title[:17] + "..." if len(title) > 17 else title
    album = album[:15] + "..." if len(album) > 15 else album

    return title, album




def spotify_extract(id) -> list:
    result = cfg.sp.track(id)
    material = [result['external_urls']['spotify']]
    material.append(result['album']['external_urls']['spotify'])
    material.append([artist['external_urls']['spotify'] for artist in result['artists']])

    return material


def spotify_ids_extract(id) -> list[str, list[str]]:
    song_obj = cfg.sp.track(id)
    artists  = [i["id"] for i in song_obj["artists"]]

    return [id, song_obj["album"]["id"], artists]


def id_or_url_check(id_or_url:str):
    if id_or_url.startswith(cfg.spotify_url):
        id_or_url = id_or_url.rsplit(cfg.spotify_url, "", maxsplit=3)
    return id_or_url



class SpotifyButtonS(discord.ui.View):
    def __init__(self, mode="default", url=str | list, label=None):
        super().__init__()
        if mode == "default" and isinstance(url, str):
            label = "Jump to Song" if label is None else label 
            self.add_item(Button(label=label, url=url, emoji=cfg.SP_ES["GREEN"]))
            
        elif mode == "urls" and len(url) >= 3:
            labels = ["Song", "Album", "Artist"]

            if len(url) > 3:
                for idx, _ in enumerate(url):
                    labels.append("Artist %s" % (idx + 2))

            count = 1
            for i, label in zip(url, labels):
                if count > 2 and (len(url) > 4):
                    self.add_item(Button(label=label, url=i, emoji=cfg.SP_ES["GREEN"], row=2))
                else:  
                    self.add_item(Button(label=label, url=i, emoji=cfg.SP_ES["GREEN"]))
                count += 1



class SpotifySelectUIView(discord.ui.View):
    def __init__(self, spotify_obj, limit, keyword, url, ephemeral=False, interaction=None, timeout=360, disable_on_timeout=True):
        super().__init__(timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.sobj    = spotify_obj
        self.limit   = limit
        self.keyword = keyword
        self.current = 0
        self.url     = url
        self.inter   = interaction
        self.ephemeral = ephemeral
        self.embed = discord.Embed(title="Jump to Spotify", url=self.url, color=cfg.SPFW)
        self.embed.add_field(name="",value="").add_field(name="",value="").add_field(name="",value="")


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not (flag:= False if interaction.user.id != self.inter.user.id else True):
            await interaction.response.send_message("You cannot USE THIS.", ephemeral=True)
        return flag


    @discord.ui.button(emoji="⏪", )
    async def rewind_button(self, button, inter:discord.Interaction):
        self.current = 0
        m = self.sobj["tracks"]["items"][self.current]
        self.embed.set_author(name="%s#%s is Searching" % (inter.user.display_name, inter.user.discriminator), icon_url=inter.user.display_avatar)
        self.embed.set_footer(text="Page %s/%s of Songs | Query: %s" % (self.current + 1, self.limit, self.keyword), icon_url = cfg.SP_US["GREEN"])
        self.embed.set_field_at(0, name="Title",   value="> **[%s](%s)**" % (m['name'], m['external_urls']['spotify']), inline=False)
        self.embed.set_field_at(1, name="Album",   value="> **[%s](%s)**" % (m['album']['name'], m['album']['external_urls']['spotify']))
        self.embed.set_field_at(2, name="Artists", value="> %s" % forming_artist_2(m['artists']), inline=False)
        self.embed.set_thumbnail(url=m["album"]["images"][0]["url"])

        await inter.response.edit_message(embed=self.embed)


    @discord.ui.button(emoji="◀️", )
    async def left_button(self, button, inter:discord.Interaction):
        self.current = c if (c:=self.current - 1) > 0 else self.current
        m = self.sobj["tracks"]["items"][self.current] 
        self.embed.set_author(name="%s#%s is Searching" % (inter.user.display_name, inter.user.discriminator), icon_url=inter.user.display_avatar)
        self.embed.set_footer(text="Page %s/%s of Songs | Query: %s" % (self.current + 1, self.limit, self.keyword), icon_url = cfg.SP_US["GREEN"])        
        self.embed.set_field_at(0, name="Title",   value="> **[%s](%s)**" % (m['name'], m['external_urls']['spotify']), inline=False)
        self.embed.set_field_at(1, name="Album",   value="> **[%s](%s)**" % (m['album']['name'], m['album']['external_urls']['spotify']))
        self.embed.set_field_at(2, name="Artists", value="> %s" % forming_artist_2(m['artists']), inline=False)
        self.embed.set_thumbnail(url=m["album"]["images"][0]["url"])

        await inter.response.edit_message(embed=self.embed)


    @discord.ui.button(emoji="▶️", )
    async def right_button(self, button, inter:discord.Interaction):
        self.current = c if (c:=self.current + 1) < self.limit else self.current
        m = self.sobj["tracks"]["items"][self.current]
        self.embed.set_author(name="%s#%s is Searching" % (inter.user.display_name, inter.user.discriminator), icon_url=inter.user.display_avatar)
        self.embed.set_footer(text="Page %s/%s of Songs | Query: %s" % (self.current + 1, self.limit, self.keyword), icon_url = cfg.SP_US["GREEN"])
        self.embed.set_field_at(0, name="Title",   value="> **[%s](%s)**" % (m['name'], m['external_urls']['spotify']), inline=False)
        self.embed.set_field_at(1, name="Album",   value="> **[%s](%s)**" % (m['album']['name'], m['album']['external_urls']['spotify']))
        self.embed.set_field_at(2, name="Artists", value="> %s" % forming_artist_2(m['artists']), inline=False)
        self.embed.set_thumbnail(url=m["album"]["images"][0]["url"])

        await inter.response.edit_message(embed=self.embed)


    @discord.ui.button(emoji="⏩", )
    async def fast_forward_button(self, button, inter:discord.Interaction):
        self.current = self.limit - 1
        m = self.sobj["tracks"]["items"][self.current]
        self.embed.set_author(name="%s#%s is Searching" % (inter.user.display_name, inter.user.discriminator), icon_url=inter.user.display_avatar)
        self.embed.set_footer(text="Page %s/%s of Songs | Query: %s" % (self.current + 1, self.limit, self.keyword), icon_url = cfg.SP_US["GREEN"])
        self.embed.set_field_at(0, name="Title",   value="> **[%s](%s)**" % (m['name'], m['external_urls']['spotify']), inline=False)
        self.embed.set_field_at(1, name="Album",   value="> **[%s](%s)**" % (m['album']['name'], m['album']['external_urls']['spotify']))
        self.embed.set_field_at(2, name="Artists", value="> %s" % forming_artist_2(m['artists']), inline=False)
        self.embed.set_thumbnail(url=m["album"]["images"][0]["url"])

        await inter.response.edit_message(embed=self.embed)


    @discord.ui.button(emoji="🔀")
    async def random_callback(self, button, inter:discord.Interaction):
        self.current = random.randint(0, self.limit)
        m = self.sobj["tracks"]["items"][self.current]
        self.embed.set_author(name="%s#%s is Searching" % (inter.user.display_name, inter.user.discriminator), icon_url=inter.user.display_avatar)
        self.embed.set_footer(text="Page %s/%s of Songs | Query: %s" % (self.current + 1, self.limit, self.keyword), icon_url = cfg.SP_US["GREEN"])
        self.embed.set_field_at(0, name="Title",   value="> **[%s](%s)**" % (m['name'], m['external_urls']['spotify']), inline=False)
        self.embed.set_field_at(1, name="Album",   value="> **[%s](%s)**" % (m['album']['name'], m['album']['external_urls']['spotify']))
        self.embed.set_field_at(2, name="Artists", value="> %s" % forming_artist_2(m['artists']), inline=False)
        self.embed.set_thumbnail(url=m["album"]["images"][0]["url"])

        await inter.response.edit_message(embed=self.embed)


    @discord.ui.button(emoji="☑", style=discord.ButtonStyle.primary, row=2)
    async def stop_button(self, button, inter:discord.Interaction):
        self.clear_items()
        m = self.sobj["tracks"]["items"][self.current]
        self.embed.title=None
        self.embed.set_author(name="Search Result")
        self.embed.set_field_at(0, name="Title",   value="> **[%s](%s)**" % (m['name'], m['external_urls']['spotify']), inline=False)
        self.embed.set_field_at(1, name="Album",   value="> **[%s](%s)**" % (m['album']['name'], m['album']['external_urls']['spotify']))
        self.embed.set_field_at(2, name="Artists", value="> %s" % forming_artist_2(m['artists']), inline=False)
        self.embed.set_thumbnail(url=m["album"]["images"][0]["url"])
        self.embed.set_footer(icon_url = cfg.SP_US["GREEN"], text = "Time: %s | ID: %s" % (
                datetime.datetime.fromtimestamp(m["duration_ms"] / 1000).strftime('%M:%S'), m["id"]
            )
        )
        a,b,c = spotify_ids_extract(m["id"])
        await inter.response.edit_message(embed=self.embed, view=OnlySpotifySeach(
            self.keyword, self.limit, a,b,c, self.ephemeral))


    @discord.ui.button(emoji="⚙", style=discord.ButtonStyle.green, row=2)
    async def edit_callback(self, button, inter:discord.Interaction):
        await inter.response.send_modal(
            ReSearch(
                title="Reset a Query and Limit if you need.", keyword=self.keyword, limit=self.limit, embed=self.embed, ephemeral=self.ephemeral
            )
        )
    
    """
    @discord.ui.button(emoji="🗑", style=discord.ButtonStyle.red, row=2)
    async def exit_callback(self, button, inter:discord.Interaction):
        await inter.delete_original_message()
    """



class SpotifyDetails(discord.ui.View):
    def __init__(self, song_id=None, album_id=None, artist_id=None, ephemeral=False, timeout=60, disable_on_timeout=True):
        super().__init__(timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.song_obj   = cfg.sp.track(song_id) if song_id is not None else None
        self.album_obj  = cfg.sp.album(album_id) if album_id is not None else None
        self.artist_obj = cfg.sp.artists(artist_id) if artist_id is not None else None
        self.artist_id  = artist_id
        self.ephemeral  = ephemeral

        
        if 1 <= (count:=len(self.artist_obj["artists"])) and self.artist_obj:
            for i in range(count):
                self.add_item(
                    SpotifyDetailsArtists(
                        ephemeral=ephemeral, count=i, artists_obj=self.artist_obj
                    )
                )


    @discord.ui.button(label="Album Info", style=discord.ButtonStyle.gray, emoji=cfg.SP_ES["GREEN"])
    async def album_callback(self, button:discord.Button, inter:discord.Interaction):
        if self.ephemeral is not True:
            button.disabled = True        
            await inter.response.edit_message(view=self)
    
        embed = discord.Embed(color=cfg.SPFW)
        embed.set_author(name="Album Info")
        embed.set_thumbnail(url=self.album_obj["images"][0]["url"])
        embed.add_field(
            name="Album Name",        value="> **[%s](%s)**" % (self.album_obj["name"], self.album_obj["external_urls"]["spotify"]), inline=False
        )
        embed.add_field(
            name="Artist",            value="> **[%s](%s)**" % (self.album_obj["artists"][0]["name"], self.album_obj["artists"][0]["external_urls"]["spotify"]), inline=False
        )
        embed.add_field(
            name="Total tracks",      value="> **%s**" % self.album_obj["total_tracks"]
        )
        embed.add_field(
            name="Available markets", value="> **%s**" % (len(self.album_obj["available_markets"]))
        )
        embed.add_field(
            name="Release date",      value="> **%s**" % (self.album_obj["release_date"])
        )
        
        total_time = sum([artist["duration_ms"] / 1000 for artist in self.album_obj["tracks"]["items"]])
        total_time = datetime.datetime.fromtimestamp(total_time).strftime(TimeFormat.EIGHT if total_time > 3600 else TimeFormat.TEN)
        
        embed.set_footer(
            text="%s, Label: %s" % (total_time, self.album_obj["label"]), icon_url=cfg.SP_US["GREEN"]
        )
        
        await inter.respond(embed=embed, ephemeral=self.ephemeral)



class OnlySpotifySeach(SpotifyDetails):
    def __init__(self, keyword, limit, song_id=None, album_id=None, artist_id=None, ephemeral=False, timeout=20, disable_on_timeout=True):
        super().__init__(song_id, album_id, artist_id, ephemeral, timeout, disable_on_timeout)
        self.keyword = keyword
        self.limit   = limit
    
    @discord.ui.button(label="back", row=2)
    async def back_callback(self, button, inter:discord.Interaction):
        result = cfg.sp.search(q=self.keyword, limit=self.limit)
        url    = search_url(self.keyword)
        m = result["tracks"]["items"][0]

        embed = discord.Embed(title="Jump to Spotify", url=url, color=cfg.SPFW)
        embed.set_author(name="%s#%s is Searching" % (inter.user.display_name, inter.user.discriminator), icon_url=inter.user.display_avatar)
        embed.set_footer(text="Page %s/%s of Songs | Query: %s" % (0 + 1, self.limit, self.keyword), icon_url = cfg.SP_US["GREEN"])
        embed.add_field(name="Title",   value="> **[%s](%s)**" % (m['name'], m['external_urls']['spotify']), inline=False)
        embed.add_field(name="Album",   value="> **[%s](%s)**" % (m['album']['name'], m['album']['external_urls']['spotify']), inline=False)
        embed.add_field(name="Artists", value="> %s" % (", ".join(["**[%s](%s)**" % (fst['name'], scd['external_urls']['spotify']) for fst, scd in zip(m['artists'], m['artists'])])), inline=False)
        embed.set_thumbnail(url=m["album"]["images"][0]["url"])        
        await inter.response.edit_message(
            embed = embed,
            view  = SpotifySelectUIView(
                        spotify_obj = result, 
                        limit       = self.limit, 
                        keyword     = self.keyword, 
                        url         = url,
                        interaction = inter,
                        ephemeral   = self.ephemeral)
        )



class SpotifyDetailsArtists(discord.ui.Button):
    def __init__(self, ephemeral, count, artists_obj):
        label = "Artist Info %s" % (count + 1) if count != 0 else "Artist Info "
        super().__init__(label=label, style=discord.ButtonStyle.gray, emoji=cfg.SP_ES["GREEN"])
        self.ephemeral = ephemeral
        self.count = count
        self.artists_obj = artists_obj
        

    async def callback(self, inter:discord.Interaction):
        #if self.ephemeral is not True:
        #    self.disabled = True      
        #await self.(view=self)
        
        embed = discord.Embed(color=cfg.SPFW)
        embed.set_author(name="Artist Info")
        n = self.artists_obj["artists"][self.count]["id"]
        m = cfg.sp.artist(n)
        artist_album = cfg.sp.artist_albums(self.artists_obj["artists"][self.count]['id'], limit=50)
        artist_album = [i for i in artist_album["items"] if i["artists"][0]["id"] == n]
        
        embed.set_thumbnail(url=m["images"][0]["url"])
        embed.add_field(name="Artist Name",  value="> **[%s](%s)**" % (m["name"], m["external_urls"]["spotify"]), inline=False)
        
        embed.add_field(name="Total Albums", value="> **%s**" % len(artist_album))
        embed.add_field(name="Followers",    value="> **%s**" % (m["followers"]["total"]))
        embed.add_field(name="genres",       value="> %s" % (", ".join(["**%s**" % i for i in m["genres"]])))
        
        top_tracks = cfg.sp.artist_top_tracks(n, country="JP")
        top_tracks = "\n".join(["[%s](%s)" % (i["name"], i["external_urls"]["spotify"]) for i in top_tracks["tracks"]])
        embed.add_field(name="Top Tracks", value=f">>> {top_tracks}")
        embed.set_footer(text="Artist ID: %s" % (n), icon_url=cfg.SP_US["GREEN"])
            
        await inter.response.send_message(embed=embed, ephemeral=self.ephemeral)

    
class MakeYourProfile(discord.ui.View):
    def __init__(self, embed = None, ephemeral=False, timeout=180, disable_on_timeout=False):
        super().__init__(timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.ephemeral = ephemeral
        self.embed = embed
        self.flag  = False
    
    @discord.ui.button(label="Edit", emoji="🔧", style=discord.ButtonStyle.green)
    async def edit_callback(self, button, inter:discord.Interaction):
        await inter.response.send_modal(MakeYourProfileModal(title="Type a Song and Artist! Alphabet only", embed=self.embed))


    @discord.ui.button(label="Make It!", style=discord.ButtonStyle.blurple, row=2)
    async def make_callback(self, button, inter:discord.Interaction):

        # Variables
        name = f"{inter.user.display_name}#{inter.user.discriminator}"
        if len(name) > 15:
            up, down = textwrap.wrap(name, name.find("#"))
            down = int(round(int(len(up) / 2) / 2) + 1) * " " + down
            name = up  + "\n" + down

        m = self.embed.to_dict()
        m = [i for i in m["fields"] if i["name"] != "None" and i["name"] is not None]

        TAG  = "Spotify Profile"
        TAG2 = "Generated By Dispotify (ver 1.2)"

        # Images
        image = Image.open(cfg.SP_PF + "profile.png")
        icon = Image.open(io.BytesIO(requests.get(inter.user.display_avatar.url).content)).resize((270, 270))
        icon.save(cfg.SP_PF + "icon.png")

        # Masks and Paste
        mask_L = Image.new("L", (270, 270), 0)
        draw = ImageDraw.Draw(mask_L)
        draw.ellipse((0, 0, 270, 270), fill=255)
        mask_L.save(cfg.SP_PF + "mask.png")
        image.paste(icon, (125, 153), mask=mask_L)

        # fonts
        NAME_FONT  = ImageFont.truetype(cfg.SP_FS + "Gotham-Black.otf", 45)
        TAG_FONT   = ImageFont.truetype(cfg.SP_FS + "Gotham-Black.otf", 90)
        TAG2_FONT  = ImageFont.truetype(cfg.SP_FS + "Gotham-Bold.otf", 50)
        TRACK_FONT = ImageFont.truetype(cfg.SP_FS + "Gotham-Black.otf", 55)
        #artist_font = ImageFont.truetype(cfg.SP_FS + "GothamLight.ttf")

        # positions
        Name_pos = 125, 490
        TAG_pos  = 830, 0
        TAG2_pos = 70, 823
        track_1_pos = 478, 200
        track_2_pos = 478, 350
        track_3_pos = 478, 500 
        track_4_pos = 478, 650 

        # lists
        track_poss = [
            track_1_pos,
            track_2_pos, 
            track_3_pos,
            track_4_pos
        ]
    
        # Draw
        draw_on_image = ImageDraw.Draw(image)
        draw_on_image.text(Name_pos, name, "white", font=NAME_FONT)
        draw_on_image.text(TAG_pos, TAG, "BLACK", font=TAG_FONT)
        draw_on_image.text(TAG2_pos, TAG2, "BLACK", font=TAG2_FONT)
        
        for i, position in zip(m, track_poss):
            draw_on_image.text(position, f"{i['name']}", "White", font=TRACK_FONT)
        
        # Save
        image.save(cfg.SPOTIFY_PF_DONE + "profile.png")

        file = discord.File(cfg.SPOTIFY_PF_DONE + "profile.png", filename="profile.png")
        weight, height = image.size
        image_size = convert_size(os.stat(cfg.SP_PF + 'profile.png').st_size)

        e = discord.Embed(title="Successfully Generated!", color=cfg.SPFB)
        e.set_image(url="attachment://profile.png")
        e.set_footer(text=f"{weight}x{height} {image_size}")

        await inter.response.send_message(embeds=[e], file=file, ephemeral=self.ephemeral)


    @discord.ui.button(label="Clear", style=discord.ButtonStyle.danger)
    async def clear_callback(self, button, inter:discord.Interaction):
        self.embed = discord.Embed(color=cfg.SPFW)
        for _ in range(4):
            self.embed.add_field(name="None", value="")
        self.embed.set_footer(text="Alphabet Only!")
        await inter.response.edit_message(embed=self.embed)

    

class MakeYourProfileModal(discord.ui.Modal):
    def __init__(self, embed,title: str, timeout: float = None):
        super().__init__(title=title, timeout=timeout)
        
        self.embed:discord.Embed = embed
        e = self.embed.to_dict()
        field = e["fields"]

        for i in range(4):
            self.add_item(InputText(
                style       = discord.InputTextStyle.short,
                max_length  = 50,
                label       = "Set a your favarite song `Song name / artist`",
                value       = field[i]["name"],
                placeholder = "`Music / artist`"
            )
        )
    
    async def callback(self, inter:discord.Interaction):
        for i in range(0,4):
            self.embed.set_field_at(
                index  = 0, 
                name   = self.children[i].value, 
                value  = "", 
                inline = False
            )

        await inter.response.edit_message(embed=self.embed)





class ReSearch(discord.ui.Modal):
    def __init__(self, keyword:str, limit:int, embed:discord.Embed, ephemeral:bool, title: str, timeout = None):
        super().__init__(title=title, timeout=timeout)
        self.keyword = keyword
        self.limit = limit
        self.embed = embed
        #self.ephemeral = ephemeral

        self.add_item(
                InputText(
                style      = discord.InputTextStyle.short, 
                max_length = 100, 
                label      = "set a Keyword", 
                value      = self.keyword,
            )
        )
        self.add_item(
            InputText(
                style      = discord.InputTextStyle.short, 
                max_length = 2, 
                label      = "set a Limit", 
                value      = self.limit
            )
        )
    
    async def callback(self, inter:discord.Interaction):
        keyword, limit = self.children[0].value, self.children[1].value
        limit = c if limit.isdigit and 50 >= (c:=int(limit)) else 50

        result = cfg.sp.search(q=keyword, limit=limit)
        url = search_url(keyword)

        embed = discord.Embed(title="Jump to Spotify", url=url, color=cfg.SPFW)
        embed.set_author(name="%s#%s" % (inter.user.display_name, inter.user.discriminator), icon_url=inter.user.display_avatar)
        embed.set_footer(text="Page %s/%s of Songs | Query: %s" % (0 + 1, limit, keyword), icon_url = cfg.SP_US["GREEN"])
        
        m = result["tracks"]["items"][0]
        embed.add_field(name="Title",   value="> **[%s](%s)**" % (m['name'], m['external_urls']['spotify']), inline=False)
        embed.add_field(name="Album",   value="> **[%s](%s)**" % (m['album']['name'], m['album']['external_urls']['spotify']), inline=False)
        embed.add_field(name="Artists", value="> %s" % (", ".join(["**[%s](%s)**" % (fst['name'], scd['external_urls']['spotify']) for fst, scd in zip(m['artists'], m['artists'])])), inline=False)
        embed.set_thumbnail(url=m["album"]["images"][0]["url"])
        #await inter.delete_original_response()
        await inter.respond(
            embed     = embed,
            view      = SpotifySelectUIView(
                            spotify_obj = result, 
                            limit       = limit, 
                            keyword     = keyword, 
                            url         = url,
                            interaction = inter,
                        )
        )