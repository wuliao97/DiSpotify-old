import os, json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util


"""PATHs"""
ROOT = os.path.split(os.path.abspath(__file__))[0]
RESOURCE = ROOT + os.sep + "resource" + os.sep

CONFIG = RESOURCE + "config" + os.sep
TXT   = RESOURCE + "tx"    + os.sep
IMAGE = RESOURCE + "image" + os.sep

GIF   = IMAGE + "gif"   + os.sep
PORCO = IMAGE + "porco" + os.sep
QUOTE = IMAGE + "quote" + os.sep

SPOTIFY_PROFILE = IMAGE + "spotifyprofile" + os.sep
SP_PF =  SPOTIFY_PROFILE # Alias
SPOTIFY_PF_DONE = SP_PF + "done" + os.sep


FONTS = RESOURCE + "fonts" + os.sep
HIRAGINO = FONTS + "hiragino" + os.sep
SPOTIFY_FONTS = FONTS + "Spotify-Font" + os.sep
SP_FS = SPOTIFY_FONTS # Alias

INFOR = RESOURCE + "infor" + os.sep
DATA  = INFOR + "data" + os.sep
FIVECH   = INFOR + "5ch"  + os.sep

STARRAIL = RESOURCE + "star_rail" + os.sep
SR_CH    = STARRAIL + "character.json"

#print(os.path.exists(SPOTIFY_PF_DONE))


with open(CONFIG + "config.json") as f:
    CFG = json.load(f)


"""For bot"""
TOKEN = CFG["TOKEN"]
SUB   = CFG["SUB"]


"""For Spotify"""
SP_ID    = CFG["SPOTIFY"]["CLIENT_ID"]
SP_SRC   = CFG["SPOTIFY"]["CLIENT_SECRET"]

SP_ES = CFG["SPOTIFY"]["EMOJIS"]
SP_US = CFG["SPOTIFY"]["URLS"]


"""For Verifing"""
ADMINS  = CFG["ADMINS"]
SERVERS = CFG["VERIFIED_SERVERS"]


"""Other"""
"COLOR - "
NOC  = 0x2f3136
FAV  = 0x6dc1d1
FAV2 = 191414

SPFW = 0x1DB954
SPFB = 0x191414



"""URLS"""
spotify_url = "https://open.spotify.com/"

cmdusinspti = CFG["cmd_using_mp4s"]["sp"]
cmdusingene = CFG["cmd_using_mp4s"]["general"]


sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id     = SP_ID, 
        client_secret = SP_SRC
        )
    )


"""
os.environ["SPOTIPY_CLIENT_ID"] = CFG["SPOTIFY"]["two_id]
os.environ["SPOTIPY_CLIENT_SECRET"] = CFG["SPOTIFY"]["two_sec"]
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8888"

spotify_user = CFG["SPOTIFY"]["two_name"]
scope = 'user-library-read user-read-playback-state playlist-read-private user-read-recently-played playlist-read-collaborative playlist-modify-public playlist-modify-private'

spti = spotipy.Spotify(
    auth = util.prompt_for_user_token(scope=scope)
)
"""



cog_files = [
    f"cogs.{os.path.splitext(fp)[0]}" for fp in os.listdir(ROOT + os.sep + "cogs") if fp.endswith(".py")
]
