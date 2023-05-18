"""Config and Funcs"""
import config as cfg
import funcs as fcs
import spotifyUtils as spu

"""Libraries for Discord"""
import discord
from discord.ext import commands
from discord.commands import Option
from discord.ui import *

"""Useing Other Libraries"""
import os
import time
import json
import random
import dateutil.parser



class SpotifyCmd(commands.Cog):
    def __init__(self, bot:discord.bot):
        self.bot:commands.Bot = bot

    spotify = discord.SlashCommandGroup(
        "spotify", "Various Spotify Commands!")

    spfy = spotify.create_subgroup(
        "search", "Various Spotify Search Commands!"
    )

    send_json = spotify.create_subgroup(
        "json", "Various Spotify json Commands!"
    )

    pl = spotify.create_subgroup(
        "playlist", "For Various Spotify Mylist!"
    )



    @spotify.command(name="listening")
    async def spotify_command(
        self, 
        inter:discord.Interaction, 
        user:Option(discord.Member, default=None),
        me_only :Option(str, name="me-only", description="Display to Me only?", choices=["Yes", "No"],) = "No", #default="No"),
        simple  :Option(str, name="simple", description="No buttons", choices=["Yes", "No"], default="No") = "No" 
    ):
        user:discord.Member = user or inter.user
        flag, material, message = spu.spotify(user)
        e = discord.Embed(color=cfg.SPFW)
        
        if flag:
            e.set_author(icon_url=user.display_avatar, name="%s is Listening!" % (user.display_name))
            e.set_thumbnail(url=material.album_cover_url)
            e.set_footer(
                icon_url=cfg.SP_US["GREEN"], 
                text="Time: %s | ID: %s" % (spu.track_time(material), material.track_id)
            )
            urls = spu.spotify_extract(material.track_id)
            
            e.add_field(
                name="Title", value="> **[%s](%s)**" % (material.title, urls[0])
            )
            e.add_field(
                name="Album", value="> **[%s](%s)**" % (material.album, urls[1]), inline=False
            )
            e.add_field(
                name="Artist(s)", value="> %s" % fcs.forming_artist(material.artists, urls[2]), inline=False
            )
            
            a, b, c = spu.spotify_ids_extract(material.track_id)
        
        else:
            e.description = message
            
        ephemeral = fcs.check(me_only) if flag else True
        view = discord.ui.View() if fcs.check(simple) or flag is False else spu.SpotifyDetails(a, b, c, ephemeral)
        
        await inter.response.send_message(embeds=[e], ephemeral=ephemeral, view=view)




    @spotify.command(name="track", description="Get the Spotify music URL from user activities")
    async def spotify_cmd(
        self,
        inter   :discord.Interaction, 
        user    :Option(discord.Member, default=None), 
        me_only :Option(str, "Display to just Me?", choices=["Yes", "No"], default="No")
    ):
        user = inter.user if user is None else user
        flag, material, message = spu.spotify(user)
            
        if flag:
            await inter.response.send_message(content=material.track_url, ephemeral=spu.check(me_only))
        
        else:
            await inter.response.send_message(embeds=[discord.Embed(description=message)], ephemeral=True)



    @spotify.command(name="cover", description="Get the Spotify song cover(aka Jakect) from user activities")
    async def spotify_cmd(self,
        inter   :discord.Interaction, 
        user    :discord.Member=None, 
        me_only :Option(str, name="me-only", description="Display to Me only?", choices=["Yes", "No"]) = "No"
    ):
        user:discord.Member = user or inter.user
        flag, material, message = spu.spotify(user)
        e = discord.Embed(color=cfg.SPFW)
        
        if flag:
            e = discord.Embed(title=material.title, color=cfg.SPFW).set_image(url=material.album_cover_url)
            e.set_author(icon_url=user.display_avatar.url, name=f"{user.display_name} is Listening")
            await inter.response.send_message(
                embeds    = [e],
                view      = spu.SpotifyButtonS(url=material.track_url),
                ephemeral = spu.check(me_only))

        else:
            e = discord.Embed(
                description=message, color=cfg.SPFW
            )
            
            await inter.response.send_message(embeds=[e], ephemeral=True)



    @spfy.command(name="simple", description="SpotifyAPIを用いて楽曲を検索")
    async def spotify_songs_search(self,
        inter   :discord.Interaction,
        *, keyword, 
        limit   :Option(int, "Search song Limit | Default: 5 max: 15") = 5,
        me_only :Option(str, "Display to Me only?", choices = ["Yes", "No"]) = "No"
    ):
        result = cfg.sp.search(q = keyword, limit = limit if 15 > limit else 15)
        sp_list = []
        for track in result['tracks']['items']:
            title, album = spu.data_cutting(track['name'], track['album']['name'])
            title_url  = track['external_urls']['spotify']
            artist     = track['artists'][0]['name']
            album_url  = track['album']['external_urls']['spotify']
            artist_url = track['artists'][0]['external_urls']['spotify']
            sp_list.append("**[%s](%s)** ([%s](%s)) - **[%s](%s)**" % (title, title_url, album, album_url, artist, artist_url))

        e = discord.Embed(
            description="\n\n".join(sp_list), color=cfg.SPFW
        )
        e.set_footer(text="Layout: *Title* (Album) - *Artists*")
        
        await inter.response.send_message(
            embed     = e,
            view      = spu.SpotifyButtonS(url=spu.search_url(keyword)),
            ephemeral = spu.check(me_only))



    @spfy.command(name="multi", description="Search the song with Spotify API")
    async def spotify_songs_search(self,
        inter      :discord.Interaction,
        *, keyword :str, 
        limit      :Option(
            int, "Search song Limit | Default: 20 max: 50")=20,
        me_only    :Option(
            str, name="me-only", description="Display to Me only?", choices=["Yes", "No"])="No"
    ):
        limit  = limit if 50 >= limit else 50
        result = cfg.sp.search(q=keyword, limit=limit)
        url    = spu.search_url(keyword)

        embed = discord.Embed(title="Jump to Spotify", url=url, color=cfg.SPFW)
        embed.set_author(
            name="%s#%s is Searching" % (inter.user.display_name, inter.user.discriminator), icon_url=inter.user.display_avatar
        )
        embed.set_footer(
            text="Page %s/%s of Songs | Query: %s" % (0 + 1, limit, keyword), icon_url = cfg.SP_US["GREEN"]
        )
        
        m = result["tracks"]["items"][0]
        
        embed.add_field(
            name="Title", value="> **[%s](%s)**" % (m['name'], m['external_urls']['spotify']), inline=False
        )
        embed.add_field(
            name="Album", value="> **[%s](%s)**" % (m['album']['name'], m['album']['external_urls']['spotify']), inline=False
        )
        embed.add_field(
            name="Artists", value="> %s" % (", ".join(["**[%s](%s)**" % (fst['name'], scd['external_urls']['spotify']) for fst, scd in zip(m['artists'], m['artists'])])), inline=False
        )
        
        embed.set_thumbnail(url=m["album"]["images"][0]["url"])
        await inter.response.send_message(
            embed     = embed,
            ephemeral = (me_only:=spu.check(me_only)),
            view      = spu.SpotifySelectUIView(
                            spotify_obj = result, 
                            limit       = limit, 
                            keyword     = keyword, 
                            url         = url,
                            interaction = inter,
                            ephemeral   = me_only
                        )
        )
        


    @send_json.command(name="track", description="send a json file from Track ID")
    async def send_a_json(
        self, inter:discord.Interaction, id_or_url:Option(description="Song ID or Song URL")
    ):
        id_or_url = spu.id_or_url_check(id_or_url)
        sobj = cfg.sp.track(id_or_url)
        s = time.time()
        
        with open(path:=f"{cfg.TXT}track.json", "w") as f:
            json.dump(obj=sobj, fp=f, indent=2, ensure_ascii=False)
        
        
        await inter.response.send_message(content=f"Time{round((time.time() - s), 3)} ms", file=discord.File(path))



    @send_json.command(name="album", description="send a json file from Album ID")
    async def send_a_json(
        self, inter:discord.Interaction, id_or_url:Option(description="Album ID or Album URL")
    ):
        id_or_url = spu.id_or_url_check(id_or_url)
        sobj = cfg.sp.album(id_or_url)
        s = time.time()
        
        with open(path:=f"{cfg.TXT}album.json", "w") as f:
            json.dump(obj=sobj, fp=f, indent=2, ensure_ascii=False)
        
        await inter.response.send_message(content=f"Time{round((time.time() - s), 3)} ms", file=discord.File(path))



    @send_json.command(name="artist", description="send a json file from Artist ID")
    async def send_a_json(
        self, inter:discord.Interaction, id_or_url:Option(description="Artist ID or Artist URL")
    ):
        id_or_url = spu.id_or_url_check(id_or_url)
        sobj = cfg.sp.artist(id_or_url)
        s = time.time()
        
        with open(path:=f"{cfg.TXT}artist.json", "w") as f:
            json.dump(obj=sobj, fp=f, indent=2, ensure_ascii=False)
        
        await inter.response.send_message(content=f"Time{round((time.time() - s), 3)} ms", file=discord.File(path))



    @spotify.command(name = "profile", description = "NOW CODING | Make a Spotify profile -ish")
    async def make_a_profile(
        self, 
        inter   :discord.Interaction,
        me_only :Option(str, name="me-only", description="Display Last Embed to Me only?", choices=["Yes", "No"])
    ):
        e = discord.Embed(color=cfg.SPFW)
        e.add_field(name="None", value=""
        ).add_field(name="None", value="", inline=False
        ).add_field(name="None", value=""
        ).add_field(name="None", value="", inline=False)
        e.set_footer(text="Alphabet Only!")
        
        await inter.response.send_message(
            embed=e, 
            ephemeral=True, 
            view=spu.MakeYourProfile(embed=e, ephemeral=spu.check(me_only))
        )
    

"""
    @pl.command(name="list")
    async def play_list(self, inter:discord.Interaction):
        current = cfg.spti.current_user_playlists()["items"]
        playlist = ["%s. **%s**" % (idx + 1, i["name"]) for idx, i in enumerate(current)]

        e = discord.Embed(title="Spotify Playlists")
        e.description = "\n".join(playlist)

        await inter.response.send_message(embeds=[e])

    @pl.command(name="create-remix")
    async def playlist_create(
        self,
        inter     :discord.Interaction,
        keyword   :str,
        playlist_name :Option(str, "name for remix"),
        limit     :Option(int, "limit for remix: default=10, max=50") = 10
    ):
        def create_play_list(list_name):
            current = cfg.spti.current_user_playlists()["items"]
            flag = all([True if list_name != i["name"] else False for i in current])

            if flag:
                cfg.spti.user_playlist_create(user=cfg.spotify_user, name=list_name)
                list_data = cfg.spti.user_playlists(user = cfg.spotify_user)
                
                for i in range(list_data['total']):
                    play_list_name = list_data['items'][i]['name']
                    if play_list_name == list_name:
                        url = list_data['items'][i]['external_urls']['spotify']

                return (url)
            
            else:
                raise NameError(f"*{list_name}* is Already Exist! Please try another name")
        
        def add_playlist(playlist_url, query="", limit=3, shuflle=True):
            result = cfg.spti.search(q=query, limit=50)

            tracks = [obj["external_urls"]["spotify"] for obj in result["tracks"]["items"]]        

            random.seed(0)
            random.shuffle(tracks)
            cfg.spti.user_playlist_add_tracks(cfg.spotify_user, playlist_url, tracks[:limit])

        try:
            url = create_play_list(playlist_name)

        except Exception as e:
            print(e)
            await inter.response.send_message(
                embeds    = [discord.Embed(title="Error", description=e)],
                ephemeral = True)

        else:
            limit = limit if 51 > limit > 0 else 50
            add_playlist(url, query=keyword, limit=limit)
            #e = discord.Embed(title=f"{playlist_name} created!", url=url)
            #e.set_footer(text="keyword: %s | Limit: %s" % (keyword, limit))
            await inter.response.send_message(content=url)
"""



def setup(bot:commands.Bot):
    bot.add_cog(SpotifyCmd(bot))