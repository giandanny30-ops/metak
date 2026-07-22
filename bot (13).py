"""
🌙 MRAK BOT v3.4  —  discord.py
Pokretanje: python bot.py
"""

import discord
from discord import app_commands
from discord.ext import commands
import json, os, random, asyncio, re, time, traceback, logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
from aiohttp import web

logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

# ─────────────────────────────────────────────────────────────
#  KANALI (hardkodirani ID-evi)
# ─────────────────────────────────────────────────────────────
CH_PECANJE  = 1528697228582064190   # kanal za pecanje
CH_KALADONT = 1496860023907811351   # kanal za kaladont
CH_BRAK     = 1528697409109098547   # kanal za brak/prosidbu

# ─────────────────────────────────────────────────────────────
#  STORAGE
# ─────────────────────────────────────────────────────────────
DATA_FILE = Path("data.json")

def _load():
    if not DATA_FILE.exists():
        return {}
    with open(DATA_FILE, encoding="utf-8") as f:
        try:    return json.load(f)
        except: return {}

def _save(d):
    DATA_FILE.parent.mkdir(exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)

def guild_cfg(gid):      return _load().get("guilds", {}).get(str(gid), {})
def set_cfg(gid, patch):
    d = _load()
    d.setdefault("guilds", {})[str(gid)] = {**guild_cfg(gid), **patch}
    _save(d)

def get_warns(gid, uid): return _load().get("warns", {}).get(str(gid), {}).get(str(uid), [])
def add_warn(gid, uid, entry):
    d = _load()
    d.setdefault("warns", {}).setdefault(str(gid), {}).setdefault(str(uid), []).append(entry)
    _save(d)

def get_fishing(uid):
    default = {
        "coins": 0, "total": 0, "inv": [], "last": 0,
        "xp": 0,
        "last_reka": 0, "last_jezero": 0, "last_more": 0,
        "rod": "obicni", "rod_casts": 0,
        "bait": None, "bait_count": 0,
        "aquarium": [],
        "daily_tasks": [], "daily_date": "", "daily_locs_today": [],
        "tournament_best": 0, "tournament_best_name": "",
        "daily_feed_date": "",
    }
    stored = _load().get("fishing", {}).get(str(uid), {})
    return {**default, **stored}
def save_fishing(uid, fd):
    d = _load(); d.setdefault("fishing", {})[str(uid)] = fd; _save(d)

def get_marriage(uid):  return _load().get("marriages", {}).get(str(uid))
def set_marriage(uid, v):
    d = _load(); d.setdefault("marriages", {})[str(uid)] = v; _save(d)
def del_marriage(uid):
    d = _load(); d.get("marriages", {}).pop(str(uid), None); _save(d)

def get_proposal(uid):  return _load().get("proposals", {}).get(str(uid))
def set_proposal(uid, v):
    d = _load(); d.setdefault("proposals", {})[str(uid)] = v; _save(d)
def del_proposal(uid):
    d = _load(); d.get("proposals", {}).pop(str(uid), None); _save(d)

# ── Prstenovi ───────────────────────────────────────────────
RINGS = {
    "obicni":     {"name": "Obični Prsten",     "emoji": "💍", "tier": 1, "cost": 500,     "desc": "Skroman, ali iskren."},
    "neobicni":   {"name": "Neobični Prsten",   "emoji": "💎", "tier": 2, "cost": 2_000,   "desc": "Za one koji žele malo više."},
    "rijetki":    {"name": "Rijetki Prsten",    "emoji": "🔮", "tier": 3, "cost": 10_000,  "desc": "Zasjat će u mraku noći."},
    "epski":      {"name": "Epski Prsten",      "emoji": "⚡", "tier": 4, "cost": 50_000,  "desc": "Vrijedan svake žrtve."},
    "legendarni": {"name": "Legendarni Prsten", "emoji": "🌟", "tier": 5, "cost": 250_000, "desc": "Ljubav bez granica."},
}
def get_ring(uid):
    return _load().get("fishing", {}).get(str(uid), {}).get("ring")
def set_ring(uid, ring_id):
    d = _load(); d.setdefault("fishing", {}).setdefault(str(uid), {})["ring"] = ring_id; _save(d)
def del_ring(uid):
    d = _load(); d.setdefault("fishing", {}).setdefault(str(uid), {}).pop("ring", None); _save(d)

# ── Dinamički kanali ────────────────────────────────────────
def get_ch(gid: int, feature: str) -> int:
    """Vrati ID kanala iz config-a, ili hardkodirani default."""
    defaults = {"pecanje": CH_PECANJE, "brak": CH_BRAK, "kaladont": CH_KALADONT}
    return int(guild_cfg(gid).get(f"ch_{feature}", defaults.get(feature, 0)))

# ─────────────────────────────────────────────────────────────
#  BOT SETUP
# ─────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.members         = True
intents.presences       = True
intents.guilds          = True

bot  = commands.Bot(command_prefix="!", intents=intents, help_command=None, case_insensitive=True)
tree = bot.tree

# ─────────────────────────────────────────────────────────────
#  BOJE / HELPERS
# ─────────────────────────────────────────────────────────────
C_PRI = 0xc9748a   # matte rose — jedina boja svih embera

SEP = " ゛ "   # separator za naslove

INVITE_RE = re.compile(r"discord(?:\.gg|(?:app)?\.com/invite)/[\w-]+", re.IGNORECASE)

def mask_invites(text: str) -> str:
    if not text: return text
    return INVITE_RE.sub("[invite uklonjen]", text)

def bq(text: str) -> str:
    """Formatira svaki red kao Discord blockquote (> )."""
    if not text: return text
    return "\n".join(f"> {line}" if line.strip() else "" for line in text.split("\n"))

def emb(title: str = "", desc: str = "", color: int = C_PRI, thumb: str = None) -> discord.Embed:
    e = discord.Embed(
        title=mask_invites(title) or None,
        description=bq(mask_invites(desc)) if desc else None,
        color=color
    )
    if thumb: e.set_thumbnail(url=thumb)
    e.set_footer(text="🌙 Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    return e

def err_emb(msg: str) -> discord.Embed:
    return emb(f"❌{SEP}Greška", msg)

async def update_status():
    """Postavi status bota na broj članova servera."""
    total = sum(g.member_count or 0 for g in bot.guilds)
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"{total} članova")
    )

async def require_channel(ctx, feature_or_id) -> bool:
    """Vrati True ako je komanda u pravom kanalu, inače pošalji grešku."""
    if isinstance(feature_or_id, str):
        ch_id = get_ch(ctx.guild.id, feature_or_id)
    else:
        ch_id = feature_or_id
    if ctx.channel.id != ch_id:
        msg = await ctx.send(
            embed=emb(f"❌{SEP}Pogrešan kanal", f"Ova komanda radi samo u <#{ch_id}>!")
        )
        await asyncio.sleep(6)
        try: await msg.delete()
        except: pass
        return False
    return True

# ─────────────────────────────────────────────────────────────
#  IN-MEMORY STATE
# ─────────────────────────────────────────────────────────────
raid_tracker   = {}   # guildId → {joins:[ts,...]}
kaladont_games = {}   # (guildId,channelId) → game dict

# ─────────────────────────────────────────────────────────────
#  FISHING DATA
# ─────────────────────────────────────────────────────────────
FISH = [
    # Obična
    {"name":"Šaran",            "emoji":"🐟","rarity":"Obična",    "coins":10,  "w":22},
    {"name":"Pastrmka",         "emoji":"🐠","rarity":"Obična",    "coins":15,  "w":20},
    {"name":"Karas",            "emoji":"🐟","rarity":"Obična",    "coins":8,   "w":21},
    {"name":"Bodorka",          "emoji":"🐟","rarity":"Obična",    "coins":7,   "w":19},
    {"name":"Crvenperka",       "emoji":"🐡","rarity":"Obična",    "coins":9,   "w":18},
    {"name":"Babuška",          "emoji":"🐟","rarity":"Obična",    "coins":6,   "w":17},
    {"name":"Klen",             "emoji":"🐟","rarity":"Obična",    "coins":11,  "w":18},
    {"name":"Alga",             "emoji":"🌿","rarity":"Obična",    "coins":2,   "w":20},
    {"name":"Stara Čizma",      "emoji":"👟","rarity":"Obična",    "coins":0,   "w":16},
    {"name":"Plastična Boca",   "emoji":"🍶","rarity":"Obična",    "coins":0,   "w":12},
    {"name":"Stara Kapa",       "emoji":"🧢","rarity":"Obična",    "coins":0,   "w":10},
    {"name":"Ništa",            "emoji":"🎣","rarity":"Obična",    "coins":0,   "w":18},
    {"name":"Smrdljiva Riba",   "emoji":"🐟","rarity":"Obična",    "coins":1,   "w":14},
    {"name":"Rupičasta Kanta",  "emoji":"🪣","rarity":"Obična",    "coins":0,   "w":8},
    # Neobična
    {"name":"Som",              "emoji":"🐡","rarity":"Neobična",  "coins":30,  "w":14},
    {"name":"Štuka",            "emoji":"🦈","rarity":"Neobična",  "coins":40,  "w":11},
    {"name":"Kamenica",         "emoji":"🦪","rarity":"Neobična",  "coins":25,  "w":12},
    {"name":"Škampi",           "emoji":"🍤","rarity":"Neobična",  "coins":35,  "w":10},
    {"name":"Deverika",         "emoji":"🐟","rarity":"Neobična",  "coins":28,  "w":13},
    {"name":"Mrena",            "emoji":"🐠","rarity":"Neobična",  "coins":33,  "w":11},
    {"name":"Manić",            "emoji":"🐟","rarity":"Neobična",  "coins":37,  "w":9},
    {"name":"Linjak",           "emoji":"🐡","rarity":"Neobična",  "coins":32,  "w":10},
    {"name":"Smuđ",             "emoji":"🐟","rarity":"Neobična",  "coins":45,  "w":8},
    {"name":"Bucov",            "emoji":"🐟","rarity":"Neobična",  "coins":38,  "w":9},
    {"name":"Uklija",           "emoji":"🐟","rarity":"Neobična",  "coins":26,  "w":12},
    # Rijetka
    {"name":"Losos",            "emoji":"🐟","rarity":"Rijetka",   "coins":60,  "w":6},
    {"name":"Tuna",             "emoji":"🐟","rarity":"Rijetka",   "coins":80,  "w":5},
    {"name":"Jastog",           "emoji":"🦞","rarity":"Rijetka",   "coins":90,  "w":4},
    {"name":"Pastrva",          "emoji":"🐠","rarity":"Rijetka",   "coins":70,  "w":5},
    {"name":"Sablarka",         "emoji":"🐟","rarity":"Rijetka",   "coins":75,  "w":4},
    {"name":"Grgeč",            "emoji":"🐟","rarity":"Rijetka",   "coins":72,  "w":4},
    {"name":"Krap",             "emoji":"🐟","rarity":"Rijetka",   "coins":85,  "w":3},
    {"name":"Skuša",            "emoji":"🐠","rarity":"Rijetka",   "coins":68,  "w":5},
    {"name":"Zubatac",          "emoji":"🐡","rarity":"Rijetka",   "coins":82,  "w":3},
    {"name":"Kirnja",           "emoji":"🐟","rarity":"Rijetka",   "coins":88,  "w":3},
    # Epska
    {"name":"Hobotnica",        "emoji":"🐙","rarity":"Epska",     "coins":150, "w":2},
    {"name":"Lignja",           "emoji":"🦑","rarity":"Epska",     "coins":120, "w":2.5},
    {"name":"Morska Zvijezda",  "emoji":"⭐","rarity":"Epska",     "coins":130, "w":2},
    {"name":"Murina",           "emoji":"🐍","rarity":"Epska",     "coins":160, "w":1.5},
    {"name":"Orada",            "emoji":"🐟","rarity":"Epska",     "coins":145, "w":1.7},
    {"name":"Brancin",          "emoji":"🐠","rarity":"Epska",     "coins":155, "w":1.6},
    {"name":"Morski Pes",       "emoji":"🦈","rarity":"Epska",     "coins":140, "w":1.8},
    {"name":"Jegulja",          "emoji":"🐍","rarity":"Epska",     "coins":165, "w":1.4},
    {"name":"Kornjača",         "emoji":"🐢","rarity":"Epska",     "coins":135, "w":1.9},
    # Legendarna
    {"name":"Morski Pas",       "emoji":"🦈","rarity":"Legendarna","coins":500, "w":1.0},
    {"name":"Zlatna Ribica",    "emoji":"✨","rarity":"Legendarna","coins":1000,"w":0.5},
    {"name":"Duh Vode",         "emoji":"👻","rarity":"Legendarna","coins":750, "w":0.3},
    {"name":"Morski Konj",      "emoji":"🐴","rarity":"Legendarna","coins":600, "w":0.8},
    {"name":"Kitov Repić",      "emoji":"🐋","rarity":"Legendarna","coins":800, "w":0.4},
    {"name":"Kraken",           "emoji":"🐙","rarity":"Legendarna","coins":2000,"w":0.1},
    {"name":"Sirena",           "emoji":"🧜","rarity":"Legendarna","coins":1500,"w":0.2},
    {"name":"Neptunov Trozubac","emoji":"🔱","rarity":"Legendarna","coins":3000,"w":0.05},
    {"name":"Zmaj Dubina",      "emoji":"🐉","rarity":"Legendarna","coins":2500,"w":0.08},
    {"name":"Ledeni Morž",      "emoji":"🦭","rarity":"Legendarna","coins":700, "w":0.6},
]

RARITY_STARS = {
    "Obična":    "⬜",
    "Neobična":  "🟩",
    "Rijetka":   "🟦",
    "Epska":     "🟪",
    "Legendarna":"🟨"
}

def fish_draw():
    return random.choices(FISH, weights=[f["w"] for f in FISH], k=1)[0]

# ─────────────────────────────────────────────────────────────
#  PECANJE — XP / NIVOI / OPREMA / LOKACIJE / ZADACI / TURNIR
# ─────────────────────────────────────────────────────────────

LEVEL_XP = [0, 100, 250, 450, 700, 1050, 1500, 2100, 2900, 3900,
            5200, 7000, 9500, 12500, 16500, 22000, 29000, 38000, 50000, 65000]
XP_PER_RARITY = {"Obična": 5, "Neobična": 15, "Rijetka": 35, "Epska": 75, "Legendarna": 150}

RODS = {
    "obicni":       {"name": "Obični Štap",       "emoji": "🎣", "cost": 0,    "bonus_coins": 0.00, "bonus_rare": 0.00, "max_casts": None, "desc": "Starter štap, bez bonusa"},
    "ribolovacki":  {"name": "Ribolovački Štap",  "emoji": "🪵", "cost": 200,  "bonus_coins": 0.10, "bonus_rare": 0.00, "max_casts": 40,   "desc": "+10% novčića · 40 bacanja"},
    "karbonski":    {"name": "Karbonski Štap",     "emoji": "🖤", "cost": 500,  "bonus_coins": 0.20, "bonus_rare": 0.05, "max_casts": 70,   "desc": "+20% novčića · +5% rijetke · 70 bacanja"},
    "titanijumski": {"name": "Titanijumski Štap",  "emoji": "🔩", "cost": 1200, "bonus_coins": 0.35, "bonus_rare": 0.10, "max_casts": 120,  "desc": "+35% novčića · +10% rijetke · 120 bacanja"},
    "zlatni":       {"name": "Zlatni Štap",        "emoji": "⭐", "cost": 3000, "bonus_coins": 0.50, "bonus_rare": 0.15, "max_casts": 200,  "desc": "+50% novčića · +15% rijetke · 200 bacanja"},
}

BAITS = {
    "glista":      {"name": "Glista",         "emoji": "🪱", "cost": 10,  "bonus_rarity": "Obična",   "weight_mult": 1.5, "desc": "+50% šanse za Obične"},
    "buba":        {"name": "Buba",           "emoji": "🐛", "cost": 25,  "bonus_rarity": "Neobična", "weight_mult": 1.5, "desc": "+50% šanse za Neobične"},
    "bljeskalica": {"name": "Bljeskalica",    "emoji": "🔦", "cost": 60,  "bonus_rarity": "Rijetka",  "weight_mult": 1.8, "desc": "+80% šanse za Rijetke"},
    "carobni":     {"name": "Čarobni Mamac",  "emoji": "🌟", "cost": 150, "bonus_rarity": "Epska",    "weight_mult": 2.0, "desc": "+100% šanse za Epske i Legendarne"},
}

LOC_REKA = [
    {"name": "Šaran",            "emoji": "🐟", "rarity": "Obična",    "coins": 10,  "w": 22},
    {"name": "Pastrmka",         "emoji": "🐠", "rarity": "Obična",    "coins": 15,  "w": 19},
    {"name": "Karas",            "emoji": "🐟", "rarity": "Obična",    "coins": 8,   "w": 21},
    {"name": "Bodorka",          "emoji": "🐟", "rarity": "Obična",    "coins": 7,   "w": 18},
    {"name": "Klen",             "emoji": "🐟", "rarity": "Obična",    "coins": 11,  "w": 16},
    {"name": "Alga",             "emoji": "🌿", "rarity": "Obična",    "coins": 2,   "w": 18},
    {"name": "Stara Čizma",      "emoji": "👟", "rarity": "Obična",    "coins": 0,   "w": 14},
    {"name": "Ništa",            "emoji": "🎣", "rarity": "Obična",    "coins": 0,   "w": 16},
    {"name": "Som",              "emoji": "🐡", "rarity": "Neobična",  "coins": 30,  "w": 12},
    {"name": "Štuka",            "emoji": "🦈", "rarity": "Neobična",  "coins": 40,  "w": 10},
    {"name": "Deverika",         "emoji": "🐟", "rarity": "Neobična",  "coins": 28,  "w": 11},
    {"name": "Mrena",            "emoji": "🐠", "rarity": "Neobična",  "coins": 33,  "w": 10},
    {"name": "Smuđ",             "emoji": "🐟", "rarity": "Neobična",  "coins": 45,  "w": 8},
    {"name": "Linjak",           "emoji": "🐡", "rarity": "Neobična",  "coins": 32,  "w": 9},
    {"name": "Losos",            "emoji": "🐟", "rarity": "Rijetka",   "coins": 60,  "w": 5},
    {"name": "Pastrva",          "emoji": "🐠", "rarity": "Rijetka",   "coins": 70,  "w": 4},
    {"name": "Grgeč",            "emoji": "🐟", "rarity": "Rijetka",   "coins": 72,  "w": 4},
    {"name": "Krap",             "emoji": "🐟", "rarity": "Rijetka",   "coins": 85,  "w": 3},
    {"name": "Zlatni Som",       "emoji": "🌟", "rarity": "Epska",     "coins": 160, "w": 1.5},
    {"name": "Džinovska Štuka",  "emoji": "🦈", "rarity": "Epska",     "coins": 180, "w": 1.0},
    {"name": "Riječni Div",      "emoji": "🐉", "rarity": "Legendarna","coins": 800, "w": 0.3},
]
LOC_JEZERO = [
    {"name": "Karas",            "emoji": "🐟", "rarity": "Obična",    "coins": 8,   "w": 22},
    {"name": "Šaran",            "emoji": "🐟", "rarity": "Obična",    "coins": 10,  "w": 20},
    {"name": "Bodorka",          "emoji": "🐟", "rarity": "Obična",    "coins": 7,   "w": 18},
    {"name": "Alga",             "emoji": "🌿", "rarity": "Obična",    "coins": 2,   "w": 16},
    {"name": "Ništa",            "emoji": "🎣", "rarity": "Obična",    "coins": 0,   "w": 15},
    {"name": "Stara Kapa",       "emoji": "🧢", "rarity": "Obična",    "coins": 0,   "w": 10},
    {"name": "Som",              "emoji": "🐡", "rarity": "Neobična",  "coins": 30,  "w": 14},
    {"name": "Linjak",           "emoji": "🐡", "rarity": "Neobična",  "coins": 32,  "w": 12},
    {"name": "Smuđ",             "emoji": "🐟", "rarity": "Neobična",  "coins": 45,  "w": 10},
    {"name": "Klen",             "emoji": "🐟", "rarity": "Neobična",  "coins": 33,  "w": 11},
    {"name": "Bucov",            "emoji": "🐟", "rarity": "Neobična",  "coins": 38,  "w": 9},
    {"name": "Krap",             "emoji": "🐟", "rarity": "Rijetka",   "coins": 85,  "w": 6},
    {"name": "Grgeč",            "emoji": "🐟", "rarity": "Rijetka",   "coins": 72,  "w": 5},
    {"name": "Pastrva",          "emoji": "🐠", "rarity": "Rijetka",   "coins": 70,  "w": 5},
    {"name": "Jezerska Orada",   "emoji": "🐠", "rarity": "Epska",     "coins": 145, "w": 1.8},
    {"name": "Jegulja",          "emoji": "🐍", "rarity": "Epska",     "coins": 165, "w": 1.5},
    {"name": "Kornjača",         "emoji": "🐢", "rarity": "Epska",     "coins": 135, "w": 2.0},
    {"name": "Jezerski Zmaj",    "emoji": "🐉", "rarity": "Legendarna","coins": 1200,"w": 0.25},
]
LOC_MORE = [
    {"name": "Skuša",            "emoji": "🐠", "rarity": "Obična",    "coins": 20,  "w": 22},
    {"name": "Ništa",            "emoji": "🎣", "rarity": "Obična",    "coins": 0,   "w": 14},
    {"name": "Alga",             "emoji": "🌿", "rarity": "Obična",    "coins": 2,   "w": 12},
    {"name": "Stara Mreža",      "emoji": "🪤", "rarity": "Obična",    "coins": 0,   "w": 8},
    {"name": "Kamenica",         "emoji": "🦪", "rarity": "Neobična",  "coins": 25,  "w": 14},
    {"name": "Škampi",           "emoji": "🍤", "rarity": "Neobična",  "coins": 35,  "w": 12},
    {"name": "Tuna",             "emoji": "🐟", "rarity": "Neobična",  "coins": 50,  "w": 11},
    {"name": "Zubatac",          "emoji": "🐡", "rarity": "Rijetka",   "coins": 82,  "w": 6},
    {"name": "Kirnja",           "emoji": "🐟", "rarity": "Rijetka",   "coins": 88,  "w": 5},
    {"name": "Sablarka",         "emoji": "🐟", "rarity": "Rijetka",   "coins": 75,  "w": 5},
    {"name": "Jastog",           "emoji": "🦞", "rarity": "Rijetka",   "coins": 90,  "w": 4},
    {"name": "Hobotnica",        "emoji": "🐙", "rarity": "Epska",     "coins": 150, "w": 2.0},
    {"name": "Lignja",           "emoji": "🦑", "rarity": "Epska",     "coins": 120, "w": 2.5},
    {"name": "Murina",           "emoji": "🐍", "rarity": "Epska",     "coins": 160, "w": 1.5},
    {"name": "Orada",            "emoji": "🐟", "rarity": "Epska",     "coins": 145, "w": 1.7},
    {"name": "Brancin",          "emoji": "🐠", "rarity": "Epska",     "coins": 155, "w": 1.6},
    {"name": "Morski Pes",       "emoji": "🦈", "rarity": "Epska",     "coins": 140, "w": 1.8},
    {"name": "Morski Pas",       "emoji": "🦈", "rarity": "Legendarna","coins": 500, "w": 1.0},
    {"name": "Zlatna Ribica",    "emoji": "✨", "rarity": "Legendarna","coins": 1000,"w": 0.5},
    {"name": "Neptunov Trozubac","emoji": "🔱", "rarity": "Legendarna","coins": 3000,"w": 0.05},
    {"name": "Zmaj Dubina",      "emoji": "🐉", "rarity": "Legendarna","coins": 2500,"w": 0.08},
]

LOCATIONS = {
    "reka":   {"name": "Rijeka",  "emoji": "🏞️", "fish": LOC_REKA,   "req_level": 1,  "cooldown": 300, "color": 0x5b8dd9},
    "jezero": {"name": "Jezero",  "emoji": "🏔️", "fish": LOC_JEZERO, "req_level": 5,  "cooldown": 270, "color": 0x3db8a5},
    "more":   {"name": "More",    "emoji": "🌊",  "fish": LOC_MORE,   "req_level": 10, "cooldown": 240, "color": 0x1a6b8a},
}

DAILY_TASKS_POOL = [
    {"id": "catch_saran",    "desc": "Ulovi **3 Šarana**",           "target_name": "Šaran",      "count": 3,   "reward": 80},
    {"id": "catch_som",      "desc": "Ulovi **2 Soma**",             "target_name": "Som",        "count": 2,   "reward": 100},
    {"id": "catch_rare",     "desc": "Ulovi **1 rijetku** ribu",     "target_rarity": "Rijetka",  "count": 1,   "reward": 150},
    {"id": "catch_epic",     "desc": "Ulovi **1 epsku** ribu",       "target_rarity": "Epska",    "count": 1,   "reward": 300},
    {"id": "catch_losos",    "desc": "Ulovi **1 Lososa**",           "target_name": "Losos",      "count": 1,   "reward": 120},
    {"id": "catch_5fish",    "desc": "Ulovi **5 riba** (bilo gdje)", "target_any": True,          "count": 5,   "reward": 60},
    {"id": "catch_10fish",   "desc": "Ulovi **10 riba** (bilo gdje)","target_any": True,          "count": 10,  "reward": 100},
    {"id": "catch_uncommon", "desc": "Ulovi **3 neobične** ribe",    "target_rarity": "Neobična", "count": 3,   "reward": 100},
    {"id": "earn_200",       "desc": "Zadradi **200 💰** pecanjem",  "target_coins": 200,         "count": 200, "reward": 80},
    {"id": "catch_2rare",    "desc": "Ulovi **2 rijetke** ribe",     "target_rarity": "Rijetka",  "count": 2,   "reward": 200},
]

def get_level(xp: int) -> int:
    lvl = 1
    for i, thr in enumerate(LEVEL_XP):
        if xp >= thr: lvl = i + 1
    return min(lvl, len(LEVEL_XP))

def xp_bar(xp: int, length: int = 10) -> str:
    lvl = get_level(xp)
    if lvl >= len(LEVEL_XP): return "🟪" * length + "  ✨ MAX"
    curr = LEVEL_XP[lvl - 1]; nxt = LEVEL_XP[lvl]
    filled = int(((xp - curr) / (nxt - curr)) * length)
    if lvl >= 10: clr = "🟪"
    elif lvl >= 5: clr = "🟦"
    else:          clr = "🟩"
    return clr * filled + "⬛" * (length - filled)

def xp_pct(xp: int) -> int:
    lvl = get_level(xp)
    if lvl >= len(LEVEL_XP): return 100
    curr = LEVEL_XP[lvl - 1]; nxt = LEVEL_XP[lvl]
    return int(((xp - curr) / (nxt - curr)) * 100)

def xp_to_next(xp: int) -> int:
    lvl = get_level(xp)
    if lvl >= len(LEVEL_XP): return 0
    return LEVEL_XP[lvl] - xp

def get_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def gen_daily_tasks():
    return [{"task": t, "progress": 0, "done": False} for t in random.sample(DAILY_TASKS_POOL, 3)]

def get_tournament_key() -> str:
    d = datetime.now(timezone.utc); y, w = d.isocalendar()[0], d.isocalendar()[1]
    return f"{y}_w{w}"

def get_tournament():
    key = get_tournament_key()
    return _load().get("tournament", {}).get(key, {"entries": {}}), key

def set_tournament(key, data):
    d = _load(); d.setdefault("tournament", {})[key] = data; _save(d)

def _fish_draw_loc(loc_fish: list, rod_key: str, bait_key) -> dict:
    rod = RODS.get(rod_key, RODS["obicni"])
    weights = []
    for f in loc_fish:
        w = f["w"]
        if rod["bonus_rare"] > 0 and f["rarity"] in ("Rijetka", "Epska", "Legendarna"):
            w *= (1 + rod["bonus_rare"] * 3)
        if bait_key and bait_key in BAITS:
            b = BAITS[bait_key]
            if f["rarity"] == b["bonus_rarity"]:
                w *= b["weight_mult"]
            if bait_key == "carobni" and f["rarity"] == "Legendarna":
                w *= b["weight_mult"]
        weights.append(max(w, 0.01))
    return random.choices(loc_fish, weights=weights, k=1)[0]

def _update_daily(fd: dict, fish: dict, coins_earned: int, loc_key: str) -> list:
    today = get_today()
    if fd.get("daily_date") != today:
        fd["daily_tasks"] = gen_daily_tasks()
        fd["daily_date"]  = today
        fd["daily_locs_today"] = []
    if loc_key not in fd.get("daily_locs_today", []):
        fd.setdefault("daily_locs_today", []).append(loc_key)
    completed = []
    for entry in fd.get("daily_tasks", []):
        if entry["done"]: continue
        t = entry["task"]
        if "target_name" in t and fish["name"] == t["target_name"] and fish["coins"] > 0:
            entry["progress"] += 1
        elif "target_rarity" in t and fish["rarity"] == t["target_rarity"] and fish["coins"] > 0:
            entry["progress"] += 1
        elif t.get("target_any") and fish["coins"] > 0:
            entry["progress"] += 1
        elif "target_coins" in t:
            entry["progress"] = min(entry["progress"] + coins_earned, t["count"])
        elif "target_locs" in t:
            entry["progress"] = len(fd.get("daily_locs_today", []))
        if entry["progress"] >= t["count"] and not entry["done"]:
            entry["done"] = True
            fd["coins"] = fd.get("coins", 0) + t["reward"]
            completed.append(f"✅ *{t['desc']}* → **+{t['reward']} 💰**")
    return completed

RARITY_COLORS = {
    "Obična":    0xaaaaaa,
    "Neobična":  0x2ecc71,
    "Rijetka":   0x3498db,
    "Epska":     0x9b59b6,
    "Legendarna":0xf1c40f,
}

# ─────────────────────────────────────────────────────────────
#  KALADONT WORDS
# ─────────────────────────────────────────────────────────────
KALADONT_WORDS_RAW = [
    "dan","dar","dah","dim","dom","dug","san","sat","sin","sir","sok","sol","sum","sud","suh",
    "kap","kat","kit","kob","kod","kol","kom","kon","kop","kor","kos","kot","kov",
    "lak","las","lat","lav","led","les","let","lik","lim","lin","lis","lit",
    "lom","lon","lop","los","lot","lov",
    "mir","mis","mit","mol","mor","mos","mot","mug","muk","mul",
    "nos","not","nov","pas","pat","paz","pek","per","pes","pet",
    "pol","pom","pop","por","pot","pud","puk","pun","put",
    "rak","ram","rap","rat","red","rep","rib","rim","rit","rob","rod","ros","rub","rud","rum","run",
    "sag","sak","sal","sam","san","sap","set","sij","sil","sit","siv",
    "tak","tal","tam","tan","tap","tar","tek","tel","ten","tih","tip","tis","tok","top","tor",
    "val","van","var","vas","vel","ven","ves","vez","vid","vir","vis","vit","vod","voj","vol","voz","vuk",
    "zal","zan","zar","zec","zen","zid","ziv","zlo","zob","zov","zub",
    "bac","baj","bak","bal","ban","bar","bas","bat","bez","bil","bin","bit","bol","bon","bor","bos",
    "bub","bud","bug","buk","bum","bun","bus",
    "car","cas","cep","cin","cip",
    "dag","daj","dal","dam","dan","dat","deb","del","dem","des","dig","dil","din","dip","dir","dis",
    "doc","dok","dol","don","dub","duh","dum","dur",
    "fab","fan","far","fas","faz","feb","fig","fil","fin","fir","fis","fit",
    "gab","gaj","gam","gap","gar","gas","gel","gem","gen","ger","gin","gob","god","goj","gol","gor",
    # Duže svakodnevne
    "dama","dana","dare","dato","deca","deka","dela","demo","sati","sava","sela","selo",
    "kapa","kara","kasa","kata","kava","kaza","lada","laka","lama","lana","lapa","lara","lava",
    "maca","mada","maja","maka","mala","mama","mana","mapa","mara","masa","mata",
    "nada","naga","naja","naka","nala","nama","nana","napa","nara","nasa","nata",
    "paca","pada","paja","paka","pala","pama","pana","papa","para","pasa","pata",
    "raca","rada","raja","raka","rala","rama","rana","rapa","rasa","rata","rava","raza",
    "taca","tada","taja","taka","tala","tama","tana","tapa","tara","tasa","tata",
    "vaca","vada","vaja","vaka","vala","vama","vana","vara","vasa","vata","vaza",
    "baba","baca","bada","baja","baka","bala","bama","bana","bara","basa","bata",
    "caca","cada","caja","caka","cala","cama","cana","capa","cara","casa","cata",
    # Originalne
    "abeceda","akcija","alarm","album","alatka","ananas","antena","aparat","avantura",
    "automobil","autobus","autor","baklja","balon","banana","bazen","beba","beton",
    "biber","bicikl","bijeg","biljka","bioskop","biser","bistro","blago","bomba","borba",
    "brada","brana","brat","briga","brod","brzina","bubreg","buket","bunda","bunar",
    "cesta","cigla","cipela","crkva","cvijece","daleko","datum","deblo","dijeta","disk",
    "dlan","dolina","drama","drvo","dubok","duhan","dvor","ekran","fabrika","farma",
    "flauta","fontana","fotografija","galaksija","galerija","garancija","gazda","glava",
    "glazba","gljiva","gnijezdo","golem","gora","grad","greda","grlo","grob","grudi",
    "guma","halva","harmonika","himna","hrana","hrast","igra","ikona","iluzija","imanje",
    "insekat","jagoda","jaje","jama","jasika","jato","jelen","jezero","junak","kabel",
    "kaktus","kamen","kapija","karta","kesten","kino","kiosk","kobra","kofer","komad",
    "konjak","korijen","kosa","kovac","koverta","krava","kredit","krilo","kriza","kruh",
    "kugle","kupola","kutija","labud","lampa","laptop","lava","lavina","legenda","lijek",
    "liljan","lista","livada","lobanja","lopta","lovac","lubenica","luk","luna","lupa",
    "magija","mapa","marka","maska","maslina","medved","melon","metal","minuta","misija",
    "moda","model","more","most","motor","mrak","mraz","munja","muzej","nada","naziv",
    "nebo","nered","noga","nokat","norma","novela","okean","orao","orah","orkan",
    "ostrvo","ovca","pagoda","palata","palma","pamet","parada","parfem","pauza","pero",
    "pijesak","pilot","pismo","planina","planet","platno","plod","polje","poruka","potok",
    "pravo","prizma","proba","ptica","pucanj","radar","raketa","ravan","recept","rijeka",
    "robot","rogoz","rukav","sablja","safari","salama","savana","sekunda","sestra","sidro",
    "signal","sistem","sjenka","skelet","sladoled","slavina","slon","snaga","snijeg",
    "spas","spiral","sport","staklo","stalak","standard","staza","strah","strana","stup",
    "sudbina","sultan","sumrak","suprug","talisman","tama","tamjan","tanjir","tapeta",
    "teatar","telefon","teleskop","terasa","tigar","tijesto","tinta","titula","tobogan",
    "toranj","traktor","traper","travnjak","trbuh","trofej","trokut","tuba","tunel",
    "turista","udica","ugovor","ulje","umor","ured","ustav","vakuum","vamp","vatromet",
    "vepar","veza","vihor","vijest","viking","vino","vjetar","vjera","vodopad","vojvoda",
    "volan","vrabac","vrana","vrpca","vulkan","zagrada","zakon","zalaz","zanat","zatvor",
    "zavicaj","zavist","zdela","zdravlje","zenit","zidina","zima","zlatnik","zvijer",
    "abajlija","adresa","agencija","akademija","akrobat","alergija","algoritam",
    "aligator","alkohol","alpinist","amater","ambasador","amfiteatar","apostol",
    "artiljerija","atlas","atmosfera","aurora","badava","badminton","bajka","bakar",
    "bakica","balada","balkon","banka","barut","baton","batina","baza","bazuka",
    "bedak","berba","bestija","biljar","biskvit","bitka","blok","bokal","boks","borac",
    "bumerang","burek","burma","carica","ceh","celer","centar","cimet","covjek","cvjet",
    "dabar","damask","danica","datula","debljina","dekor","delta","deviza","dijamant",
    "dinja","direktor","disciplina","dobrica","dobitak","dodir","dorucak","dragulj",
    "drum","dukat","dvoboj","dzamija","dzungla","epoha","faca","fasada","festival",
    "figura","film","finesa","fjord","flaster","flora","forma","freska","galas","garda",
    "genij","gesta","glina","globus","gnjev","grana","granit","greben","grizli","grom",
    "gusar","guska","halal","hamam","harem","harfa","harpun","hiljada","hijena",
    "hipodrom","horizont","idol","iglo","infarkt","inflacija","ironija","jabuka","jaguar",
    "jahac","javor","jelenjak","jesen","jubilar","juha","kadet","kajak","kajsija",
    "kameleon","kamion","kanal","kanap","kapela","kapetan","karanfil","karavan","kasaba",
    "kaseta","katastrofa","katedrala","kavez","kazan","kazna","kelner","kibic","kicma",
    "kisik","knjiga","kobalt","kolega","kometa","kompas","kondor","kopito","kornet",
    "kostim","kotao","kovnica","krastavac","krater","kruna","krzno","kula","kupus",
    "kurir","lakat","laser","lednik","legura","lekar","lenta","lepinja","leptir",
    "letac","limar","limun","logor","lokal","lokva","lonac","lopata","lopov","lozinka",
    "lukavac","majmun","majstor","malina","malter","mamut","manastir","manifest",
    "maraton","marmor","maslo","medusa","mejdan","merak","mineral","mir","mirovina",
    "mlinar","modem","monah","mozak","mumija","napor","napredak","naranca","narod",
    "naslov","nauka","nevjesta","neven","nitkov","nosac","novcanik","objava","oblak",
    "obrt","oglas","ogled","olovka","opasnost","operacija","opsada","orbita","organ",
    "ormar","osova","otrov","padalica","pakao","pakt","paluba","pangolin","panika",
    "panter","parabola","parking","pasteta","patron","pecivo","pejzaz","pelikan",
    "pepeo","plamenjak","plesac","ples","pogon","pogreb","pojas","polica","politika",
    "poljar","pomoc","poraz","porez","potvrda","poziv","prag","pravda","presa","prevoz",
    "prica","prijevara","printer","problem","projekt","prostirka","proza","puma","punjac",
    "radio","razlog","rebus","recnik","redak","regal","rekviem","replika","revolt","riba",
    "riznica","rob","roba","robinja","rogac","rostilj","ruda","ruglo","rutina","sabor",
    "sakatica","sakrament","salama","salata","samac","samouk","sardina","satir","savez",
    "scena","senf","sijeno","silan","silaz","sirena","skorpion","smola","snimak","soda",
    "soldat","spektar","spuzva","stadion","stampa","statua","stomak","strela","sudar",
    "suknja","sumnja","svila","tabla","tango","tarifa","tema","tenis","tesla","tikva",
    "titan","topaz","totem","trg","trijumf","tron","truba","turban","ubod","ulaz",
    "ulica","unija","uran","urna","utakmica","valuta","vampir","vatikan","vatrogasac",
    "vetar","vijak","vikend","virus","vizir","vlada","vojnik","vojska","vrba","vreme","vrh",
    "zalba","zamka","zavjesa","zemlja","zenica","zgrada","zivina","zvijezda","zvornik",
    "jahoda","jakna","jandarm","jarebica","jasmin","jastuk","javnost","jazavac",
    "jelsa","jesetra","jeza","jorgovan","karizma",
]

KALADONT_WORDS = set(w.lower() for w in KALADONT_WORDS_RAW)

def normalize_word(w: str) -> str:
    rep = {"š":"s","č":"c","ć":"c","ž":"z","đ":"d",
           "Š":"s","Č":"c","Ć":"c","Ž":"z","Đ":"d"}
    return "".join(rep.get(c, c) for c in w).lower()

# ─────────────────────────────────────────────────────────────
#  NSFW KEYWORDS
# ─────────────────────────────────────────────────────────────
NSFW_KW = re.compile(
    r"dick|cock|penis|boner|kurac|pimpek|nadrkalj|kita|karac|picka|pi[cč]ku|"
    r"pussy|vagina|nude|nudes|naked|porn|porno|xxx|nsfw|boob|tit|tits|sisa|"
    r"jebati|jebo|jeba|jeb[ai]|blowjob|handjob|cumshot|cum\b|hentai|"
    r"onlyfans|pornhub|xvideos|xhamster",
    re.IGNORECASE
)

# ─────────────────────────────────────────────────────────────
#  EVENTS
# ─────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"\n🌕 ══════════════════════════════ 🌕")
    print(f"🌸  {bot.user.name} je ONLINE!")
    print(f"👑  Tag: {bot.user}")
    print(f"🌿  Servera: {len(bot.guilds)}")
    print(f"🌕 ══════════════════════════════ 🌕\n")
    await tree.sync()
    cmds = sorted(c.name for c in bot.commands)
    print(f"✨ Sync OK | Prefix komande ({len(cmds)}): {', '.join(cmds)}")
    await update_status()


@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    cfg   = guild_cfg(guild.id)

    # Anti-Raid
    raid_cfg = cfg.get("antiraid", {})
    if raid_cfg.get("enabled"):
        gid = str(guild.id)
        now = time.time()
        t   = raid_tracker.setdefault(gid, {"joins": []})
        t["joins"] = [j for j in t["joins"] if now - j < 30]
        t["joins"].append(now)
        threshold = raid_cfg.get("threshold", 8)
        if len(t["joins"]) >= threshold:
            log_ch = cfg.get("logs_channel")
            if log_ch:
                ch = guild.get_channel(int(log_ch))
                if ch:
                    await ch.send(embed=emb(
                        f"🛡️{SEP}RAID DETEKTOVAN",
                        f"{len(t['joins'])} joinova za 30s!\n"
                        f"Threshold: `{threshold}`\n"
                        f"Preporučena akcija: `!antiraid off` + ručni pregled."
                    ))
            t["joins"] = []

    # Welcome
    wch = cfg.get("welcome_channel")
    if not wch: return
    ch = guild.get_channel(int(wch))
    if not ch: return
    e = emb(
        f"🌸{SEP}Dobrodošao/la, {member.display_name}!",
        f"Drago nam je što si tu, {member.mention}!\n"
        f"📜 Pročitaj pravila i upoznaj se sa serverom.\n"
        f"🌙 Uživaj i budi dio naše zajednice!"
    )
    e.set_thumbnail(url=member.display_avatar.url)
    e.add_field(name="👤 Član",      value=member.mention,                                 inline=True)
    e.add_field(name="🌟 Redni br.", value=f"#{guild.member_count}",                       inline=True)
    e.add_field(name="📅 Nalog",     value=f"<t:{int(member.created_at.timestamp())}:R>",  inline=True)
    btn  = discord.ui.Button(label="Poželi dobrodošlicu", emoji="🌸", style=discord.ButtonStyle.primary)
    view = discord.ui.View(); view.add_item(btn)
    await ch.send(embed=e, view=view)
    await update_status()


@bot.event
async def on_member_remove(member: discord.Member):
    cfg = guild_cfg(member.guild.id)
    gch = cfg.get("goodbye_channel")
    if not gch: return
    ch = member.guild.get_channel(int(gch))
    if not ch: return
    await ch.send(embed=emb(
        f"👋{SEP}{member.name} je napustio/la",
        f"{member.mention} više nije dio servera.\n🌙 Sretno dalje!"
    ))
    await update_status()


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild: return
    await bot.process_commands(message)

    cfg    = guild_cfg(message.guild.id)
    member = message.guild.get_member(message.author.id)
    is_admin = member and member.guild_permissions.administrator if member else False

    # Invite link auto-mod
    if not is_admin and INVITE_RE.search(message.content or ""):
        try: await message.delete()
        except: pass
        warn_e = emb(
            f"⚠️{SEP}Invite link nije dozvoljen",
            f"{message.author.mention}, slanje invite linkova nije dozvoljeno!\n"
            f"Dobivaš upozorenje i timeout od **2 minute**."
        )
        try:
            sent = await message.channel.send(embed=warn_e)
            await asyncio.sleep(8)
            await sent.delete()
        except: pass
        if member:
            try: await member.timeout(timedelta(minutes=2), reason="Auto-Mod: invite link")
            except: pass
        log_ch = cfg.get("logs_channel")
        if log_ch:
            lch = message.guild.get_channel(int(log_ch))
            if lch:
                await lch.send(embed=emb(
                    f"🔗{SEP}Invite link uhvaćen",
                    f"**Korisnik:** {message.author.mention} (`{message.author}`)\n"
                    f"**Kanal:** <#{message.channel.id}>\n"
                    f"**Akcija:** ⏱️ Timeout 2min"
                ))
        return

    # Kaladont odgovor u chatu
    key  = (str(message.guild.id), str(message.channel.id))
    game = kaladont_games.get(key)
    if game:
        content = message.content.strip().lower()
        if (content and not content.startswith("/") and not content.startswith("!")
                and " " not in content and len(content) >= 2):
            await _kaladont_handle(message, content, game)
            return

    # NSFW auto-mod
    nsfw_c = cfg.get("nsfw_filter", {})
    if not nsfw_c.get("enabled"): return
    if message.channel.id in [int(x) for x in nsfw_c.get("exempt_channels", [])]: return
    if getattr(message.channel, "nsfw", False): return
    if is_admin: return

    flagged = False; reason = ""
    if NSFW_KW.search(message.content or ""):
        flagged = True; reason = f"NSFW tekst: `{message.content[:60]}`"
    if not flagged:
        for emb_obj in message.embeds:
            text = " ".join(filter(None, [emb_obj.title, emb_obj.description, emb_obj.url or ""]))
            if NSFW_KW.search(text):
                flagged = True; reason = f"NSFW embed: `{(emb_obj.title or emb_obj.url or '')[:60]}`"; break
    if not flagged:
        for att in message.attachments:
            if NSFW_KW.search(att.filename):
                flagged = True; reason = f"NSFW fajl: `{att.filename}`"; break
    if not flagged: return

    try: await message.delete()
    except: pass

    action = nsfw_c.get("action", "timeout")
    dur    = nsfw_c.get("timeout_duration", 600)

    if action == "timeout" and member:
        try: await member.timeout(timedelta(seconds=dur), reason=f"Auto-Mod NSFW: {reason}")
        except: pass
    elif action == "ban" and member:
        try: await member.ban(reason=f"Auto-Mod NSFW: {reason}", delete_message_days=1)
        except: pass

    log_ch = nsfw_c.get("log_channel") or cfg.get("logs_channel")
    if log_ch:
        lch = message.guild.get_channel(int(log_ch))
        if lch:
            action_label = (
                f"⏱️ Timeout {dur//60}min" if action == "timeout" else
                "🔨 Ban" if action == "ban" else "🗑️ Obrisano"
            )
            await lch.send(embed=emb(
                f"🚫{SEP}NSFW uhvaćen",
                f"**Korisnik:** {message.author.mention} (`{message.author}`)\n"
                f"**Kanal:** <#{message.channel.id}>\n"
                f"**Razlog:** {reason}\n"
                f"**Akcija:** {action_label}"
            ))


# ─────────────────────────────────────────────────────────────
#  KALADONT HANDLER
# ─────────────────────────────────────────────────────────────
async def _kaladont_handle(message: discord.Message, word: str, game: dict):
    n_word  = normalize_word(word)
    n_prev  = normalize_word(game["word"])
    needed  = n_prev[-2:]

    # Isti igrač ne može dva puta zaredom
    if game.get("last_player") == message.author.id:
        await message.reply(embed=emb(
            f"⏳{SEP}Čekaj red",
            f"{message.author.mention}, ne možeš igrati dva puta zaredom!\nNeka neko drugi odigra."
        ), delete_after=5)
        return

    # Highlight zadnje 2 slova prethodne riječi
    prev_word    = game["word"]
    prev_display = (f"{prev_word[:-2]}**{prev_word[-2:]}**") if len(prev_word) > 2 else f"**{prev_word}**"
    footer_txt   = f"🔤 Runda {game['round']} • {message.author.display_name} • {len(game['used'])} riječi"

    if not n_word.startswith(needed):
        e = discord.Embed(
            title=f"❌{SEP}{word}",
            description=bq(f"Mora počinjati sa **`{needed}`**\nZadnja: {prev_display}"),
            color=C_PRI
        )
        e.set_footer(text=footer_txt)
        e.timestamp = datetime.now(timezone.utc)
        await message.reply(embed=e, delete_after=6)
        return

    if word in game["used"]:
        e = discord.Embed(
            title=f"❌{SEP}{word}",
            description=bq(f"**{word}** je već bila u igri!\nZadnja: {prev_display}"),
            color=C_PRI
        )
        e.set_footer(text=footer_txt)
        e.timestamp = datetime.now(timezone.utc)
        await message.reply(embed=e, delete_after=5)
        return

    if word not in KALADONT_WORDS:
        e = discord.Embed(
            title=f"❌{SEP}{word}",
            description=bq(f"**{word}** nije u rječniku bota.\nZadnja: {prev_display}"),
            color=C_PRI
        )
        e.set_footer(text=footer_txt)
        e.timestamp = datetime.now(timezone.utc)
        await message.reply(embed=e, delete_after=5)
        return

    game["used"].add(word)
    game["word"]        = word
    game["round"]      += 1
    game["last_player"] = message.author.id

    suf          = normalize_word(word)[-2:]
    word_display = (f"{word[:-2]}**{word[-2:]}**") if len(word) > 2 else f"**{word}**"

    e = discord.Embed(
        title=f"✅{SEP}{word}",
        description=bq(f"{word_display}\n\nSljedeća počinje sa **`{suf}`**"),
        color=C_PRI
    )
    e.set_footer(text=f"🔤 Runda {game['round']} • {message.author.display_name} • {len(game['used'])} riječi")
    e.timestamp = datetime.now(timezone.utc)
    await message.reply(embed=e)

# ─────────────────────────────────────────────────────────────
#  HELPERS — LOG
# ─────────────────────────────────────────────────────────────
async def log_action(guild, action, mod, target, reason):
    cfg    = guild_cfg(guild.id)
    log_ch = cfg.get("logs_channel")
    if not log_ch: return
    ch = guild.get_channel(int(log_ch))
    if not ch: return
    await ch.send(embed=emb(
        f"🛡️{SEP}Mod akcija — {action}",
        f"**Korisnik:** {target.mention} (`{target}`)\n"
        f"**Moderator:** {mod.mention}\n"
        f"**Razlog:** {reason}"
    ))

# ─────────────────────────────────────────────────────────────
#  SETUP COMMANDS  (/ i !)
# ─────────────────────────────────────────────────────────────
@tree.command(name="setwelcome", description="Postavi kanal za welcome poruke")
@app_commands.default_permissions(administrator=True)
async def setwelcome(i: discord.Interaction, kanal: discord.TextChannel):
    try:
        set_cfg(i.guild_id, {"welcome_channel": str(kanal.id)})
        await i.response.send_message(embed=emb(
            f"✅{SEP}Welcome kanal", f"Welcome poruke → {kanal.mention}"
        ))
    except: pass

@bot.command(name="setwelcome")
@commands.has_permissions(administrator=True)
async def p_setwelcome(ctx, kanal: discord.TextChannel):
    set_cfg(ctx.guild.id, {"welcome_channel": str(kanal.id)})
    await ctx.send(embed=emb(f"✅{SEP}Welcome kanal", f"Welcome poruke → {kanal.mention}"))


@tree.command(name="setgoodbye", description="Postavi kanal za goodbye poruke")
@app_commands.default_permissions(administrator=True)
async def setgoodbye(i: discord.Interaction, kanal: discord.TextChannel):
    try:
        set_cfg(i.guild_id, {"goodbye_channel": str(kanal.id)})
        await i.response.send_message(embed=emb(
            f"✅{SEP}Goodbye kanal", f"Goodbye poruke → {kanal.mention}"
        ))
    except: pass

@bot.command(name="setgoodbye")
@commands.has_permissions(administrator=True)
async def p_setgoodbye(ctx, kanal: discord.TextChannel):
    set_cfg(ctx.guild.id, {"goodbye_channel": str(kanal.id)})
    await ctx.send(embed=emb(f"✅{SEP}Goodbye kanal", f"Goodbye poruke → {kanal.mention}"))


@tree.command(name="setlogs", description="Postavi kanal za moderacijske logove")
@app_commands.default_permissions(administrator=True)
async def setlogs(i: discord.Interaction, kanal: discord.TextChannel):
    try:
        set_cfg(i.guild_id, {"logs_channel": str(kanal.id)})
        await i.response.send_message(embed=emb(
            f"✅{SEP}Log kanal", f"Mod logovi → {kanal.mention}"
        ))
    except: pass

@bot.command(name="setlogs")
@commands.has_permissions(administrator=True)
async def p_setlogs(ctx, kanal: discord.TextChannel):
    set_cfg(ctx.guild.id, {"logs_channel": str(kanal.id)})
    await ctx.send(embed=emb(f"✅{SEP}Log kanal", f"Mod logovi → {kanal.mention}"))

# ─────────────────────────────────────────────────────────────
#  MODERATION  (/ i !)
# ─────────────────────────────────────────────────────────────
@tree.command(name="ban", description="Banuj korisnika")
@app_commands.default_permissions(administrator=True)
async def ban(i: discord.Interaction, korisnik: discord.Member, razlog: str = "Nema razloga"):
    try:
        await korisnik.ban(reason=razlog)
        await i.response.send_message(embed=emb(
            f"🔨{SEP}Ban",
            f"{korisnik.mention} je banovan.\n**Razlog:** {razlog}"
        ))
        await log_action(i.guild, "BAN", i.user, korisnik, razlog)
    except Exception as ex:
        try: await i.response.send_message(embed=err_emb(str(ex)), ephemeral=True)
        except: pass

@bot.command(name="ban")
@commands.has_permissions(administrator=True)
async def p_ban(ctx, korisnik: discord.Member, *, razlog: str = "Nema razloga"):
    await korisnik.ban(reason=razlog)
    await ctx.send(embed=emb(f"🔨{SEP}Ban", f"{korisnik.mention} je banovan.\n**Razlog:** {razlog}"))
    await log_action(ctx.guild, "BAN", ctx.author, korisnik, razlog)


@tree.command(name="kick", description="Kickuj korisnika")
@app_commands.default_permissions(administrator=True)
async def kick(i: discord.Interaction, korisnik: discord.Member, razlog: str = "Nema razloga"):
    try:
        await korisnik.kick(reason=razlog)
        await i.response.send_message(embed=emb(
            f"👢{SEP}Kick",
            f"{korisnik.mention} je kickovan.\n**Razlog:** {razlog}"
        ))
        await log_action(i.guild, "KICK", i.user, korisnik, razlog)
    except Exception as ex:
        try: await i.response.send_message(embed=err_emb(str(ex)), ephemeral=True)
        except: pass

@bot.command(name="kick")
@commands.has_permissions(administrator=True)
async def p_kick(ctx, korisnik: discord.Member, *, razlog: str = "Nema razloga"):
    await korisnik.kick(reason=razlog)
    await ctx.send(embed=emb(f"👢{SEP}Kick", f"{korisnik.mention} je kickovan.\n**Razlog:** {razlog}"))
    await log_action(ctx.guild, "KICK", ctx.author, korisnik, razlog)


@tree.command(name="timeout", description="Daj timeout korisniku")
@app_commands.default_permissions(administrator=True)
async def cmd_timeout(i: discord.Interaction, korisnik: discord.Member,
                      minuta: app_commands.Range[int, 1, 10080] = 10,
                      razlog: str = "Nema razloga"):
    try:
        await korisnik.timeout(timedelta(minutes=minuta), reason=razlog)
        await i.response.send_message(embed=emb(
            f"⏱️{SEP}Timeout",
            f"{korisnik.mention} → **{minuta} min**\n**Razlog:** {razlog}"
        ))
        await log_action(i.guild, f"TIMEOUT {minuta}min", i.user, korisnik, razlog)
    except Exception as ex:
        try: await i.response.send_message(embed=err_emb(str(ex)), ephemeral=True)
        except: pass

@bot.command(name="timeout")
@commands.has_permissions(administrator=True)
async def p_timeout(ctx, korisnik: discord.Member, minuta: int = 10, *, razlog: str = "Nema razloga"):
    await korisnik.timeout(timedelta(minutes=minuta), reason=razlog)
    await ctx.send(embed=emb(f"⏱️{SEP}Timeout", f"{korisnik.mention} → **{minuta} min**\n**Razlog:** {razlog}"))
    await log_action(ctx.guild, f"TIMEOUT {minuta}min", ctx.author, korisnik, razlog)


@tree.command(name="untimeout", description="Ukloni timeout")
@app_commands.default_permissions(administrator=True)
async def untimeout(i: discord.Interaction, korisnik: discord.Member):
    try:
        await korisnik.timeout(None)
        await i.response.send_message(embed=emb(
            f"✅{SEP}Timeout uklonjen",
            f"{korisnik.mention} više nije u timeoutu."
        ))
    except Exception as ex:
        try: await i.response.send_message(embed=err_emb(str(ex)), ephemeral=True)
        except: pass

@bot.command(name="untimeout")
@commands.has_permissions(administrator=True)
async def p_untimeout(ctx, korisnik: discord.Member):
    await korisnik.timeout(None)
    await ctx.send(embed=emb(f"✅{SEP}Timeout uklonjen", f"{korisnik.mention} više nije u timeoutu."))


@tree.command(name="warn", description="Upozori korisnika")
@app_commands.default_permissions(administrator=True)
async def warn(i: discord.Interaction, korisnik: discord.Member, razlog: str = "Kršenje pravila"):
    try:
        add_warn(i.guild_id, korisnik.id, {"reason": razlog, "mod": str(i.user), "ts": int(time.time())})
        warns = get_warns(i.guild_id, korisnik.id)
        await i.response.send_message(embed=emb(
            f"⚠️{SEP}Upozorenje #{len(warns)}",
            f"{korisnik.mention}\n**Razlog:** {razlog}"
        ))
        await log_action(i.guild, f"WARN #{len(warns)}", i.user, korisnik, razlog)
    except Exception as ex:
        try: await i.response.send_message(embed=err_emb(str(ex)), ephemeral=True)
        except: pass

@bot.command(name="warn")
@commands.has_permissions(administrator=True)
async def p_warn(ctx, korisnik: discord.Member, *, razlog: str = "Kršenje pravila"):
    add_warn(ctx.guild.id, korisnik.id, {"reason": razlog, "mod": str(ctx.author), "ts": int(time.time())})
    warns = get_warns(ctx.guild.id, korisnik.id)
    await ctx.send(embed=emb(f"⚠️{SEP}Upozorenje #{len(warns)}", f"{korisnik.mention}\n**Razlog:** {razlog}"))
    await log_action(ctx.guild, f"WARN #{len(warns)}", ctx.author, korisnik, razlog)


@tree.command(name="warnings", description="Pogledaj upozorenja korisnika")
@app_commands.default_permissions(administrator=True)
async def warnings(i: discord.Interaction, korisnik: discord.Member):
    try:
        ws = get_warns(i.guild_id, korisnik.id)
        if not ws:
            await i.response.send_message(embed=emb(
                f"📋{SEP}Upozorenja", f"{korisnik.mention} nema upozorenja."
            ), ephemeral=True); return
        desc = "\n".join(
            f"**#{n+1}** {w['reason']} *(mod: {w['mod']}, <t:{w['ts']}:R>)*"
            for n, w in enumerate(ws)
        )
        await i.response.send_message(embed=emb(
            f"⚠️{SEP}Upozorenja — {korisnik.display_name}", desc
        ), ephemeral=True)
    except: pass

@bot.command(name="warnings")
@commands.has_permissions(administrator=True)
async def p_warnings(ctx, korisnik: discord.Member):
    ws = get_warns(ctx.guild.id, korisnik.id)
    if not ws:
        await ctx.send(embed=emb(f"📋{SEP}Upozorenja", f"{korisnik.mention} nema upozorenja.")); return
    desc = "\n".join(
        f"**#{n+1}** {w['reason']} *(mod: {w['mod']}, <t:{w['ts']}:R>)*"
        for n, w in enumerate(ws)
    )
    await ctx.send(embed=emb(f"⚠️{SEP}Upozorenja — {korisnik.display_name}", desc))


@tree.command(name="clear", description="Obriši poruke")
@app_commands.default_permissions(administrator=True)
async def clear(i: discord.Interaction, broj: app_commands.Range[int, 1, 100] = 10):
    try:
        await i.response.defer(ephemeral=True)
        deleted = await i.channel.purge(limit=broj)
        await i.followup.send(embed=emb(
            f"🗑️{SEP}Poruke obrisane", f"Obrisano **{len(deleted)}** poruka."
        ), ephemeral=True)
    except: pass

@bot.command(name="clear")
@commands.has_permissions(administrator=True)
async def p_clear(ctx, broj: int = 10):
    await ctx.message.delete()
    deleted = await ctx.channel.purge(limit=min(broj, 100))
    msg = await ctx.send(embed=emb(f"🗑️{SEP}Poruke obrisane", f"Obrisano **{len(deleted)}** poruka."))
    await asyncio.sleep(4)
    try: await msg.delete()
    except: pass

# ─────────────────────────────────────────────────────────────
#  ULOGE  (/ i !)
# ─────────────────────────────────────────────────────────────
def _build_uloge_embeds(guild: discord.Guild) -> list:
    """Vraća listu embedova (straničenje ako ima previše uloga)."""
    roles = [r for r in reversed(guild.roles) if r.name != "@everyone"]
    if not roles:
        return [emb(f"🎭{SEP}Uloge", "Nema uloga na ovom serveru.")]

    # Grupiraj u stranice od max 20 uloga
    pages = [roles[i:i+20] for i in range(0, len(roles), 20)]
    embeds = []
    for idx, page in enumerate(pages, 1):
        lines = "\n".join(
            f"{r.mention} — `{len(r.members)}` {'član' if len(r.members) == 1 else 'članova'}"
            for r in page
        )
        # Sigurnosni trim — Discord limit 4096 znakova za description
        if len(lines) > 3900:
            lines = lines[:3900] + "\n*...i još uloga*"
        title = f"🎭{SEP}Uloge — {guild.name}" + (f" (str. {idx}/{len(pages)})" if len(pages) > 1 else "")
        e = discord.Embed(title=title, description=lines, color=C_PRI)
        e.set_footer(text=f"📊 {len(roles)} uloga ukupno  ·  👥 {guild.member_count} članova  ·  Mrak Bot")
        e.timestamp = datetime.now(timezone.utc)
        embeds.append(e)
    return embeds

@tree.command(name="uloge", description="Prikaži sve uloge na serveru")
async def uloge(i: discord.Interaction):
    try:
        embeds = _build_uloge_embeds(i.guild)
        await i.response.send_message(embed=embeds[0])
        for e in embeds[1:]:
            await i.followup.send(embed=e)
    except Exception as ex:
        logging.error(f"[uloge slash] {ex}")
        try: await i.response.send_message("Greška pri učitavanju uloga.", ephemeral=True)
        except: pass

@bot.command(name="uloge")
async def p_uloge(ctx):
    try:
        embeds = _build_uloge_embeds(ctx.guild)
        for e in embeds:
            await ctx.send(embed=e)
    except Exception as ex:
        logging.error(f"[uloge prefix] {ex}")
        await ctx.send(embed=err_emb("Greška pri učitavanju uloga."))

# ─────────────────────────────────────────────────────────────
#  ANTI-RAID  (/ i !)
# ─────────────────────────────────────────────────────────────
raid_group = app_commands.Group(name="antiraid", description="🛡️ Anti-raid zaštita")

@raid_group.command(name="on", description="Uključi anti-raid zaštitu")
@app_commands.default_permissions(administrator=True)
async def raid_on(i: discord.Interaction, threshold: int = 8):
    try:
        cfg = guild_cfg(i.guild_id).get("antiraid", {})
        cfg.update({"enabled": True, "threshold": threshold})
        set_cfg(i.guild_id, {"antiraid": cfg})
        await i.response.send_message(embed=emb(
            f"🛡️{SEP}Anti-Raid uključen",
            f"Detektuje **{threshold}** joinova/30s."
        ))
    except: pass

@raid_group.command(name="off", description="Isključi anti-raid")
@app_commands.default_permissions(administrator=True)
async def raid_off(i: discord.Interaction):
    try:
        cfg = guild_cfg(i.guild_id).get("antiraid", {})
        cfg["enabled"] = False
        set_cfg(i.guild_id, {"antiraid": cfg})
        await i.response.send_message(embed=emb(f"🛡️{SEP}Anti-Raid isključen", ""))
    except: pass

@raid_group.command(name="threshold", description="Postavi threshold joinova/30s")
@app_commands.default_permissions(administrator=True)
async def raid_threshold(i: discord.Interaction, broj: int = 8):
    try:
        cfg = guild_cfg(i.guild_id).get("antiraid", {})
        cfg["threshold"] = broj
        set_cfg(i.guild_id, {"antiraid": cfg})
        await i.response.send_message(embed=emb(
            f"🛡️{SEP}Threshold ažuriran", f"Novi threshold: **{broj}** joinova/30s"
        ))
    except: pass

@raid_group.command(name="status", description="Status anti-raida")
@app_commands.default_permissions(administrator=True)
async def raid_status(i: discord.Interaction):
    try:
        cfg = guild_cfg(i.guild_id).get("antiraid", {})
        e = emb(f"🛡️{SEP}Anti-Raid Status", "")
        e.add_field(name="Status",    value="🟢 Aktivan" if cfg.get("enabled") else "🔴 Neaktivan", inline=True)
        e.add_field(name="Threshold", value=f"{cfg.get('threshold', 8)} joinova/30s",              inline=True)
        await i.response.send_message(embed=e, ephemeral=True)
    except: pass

tree.add_command(raid_group)

@bot.command(name="antiraid")
@commands.has_permissions(administrator=True)
async def p_antiraid(ctx, akcija: str = "status", threshold: int = 8):
    akcija = akcija.lower()
    if akcija == "on":
        cfg = guild_cfg(ctx.guild.id).get("antiraid", {})
        cfg.update({"enabled": True, "threshold": threshold})
        set_cfg(ctx.guild.id, {"antiraid": cfg})
        await ctx.send(embed=emb(f"🛡️{SEP}Anti-Raid uključen", f"Detektuje **{threshold}** joinova/30s."))
    elif akcija == "off":
        cfg = guild_cfg(ctx.guild.id).get("antiraid", {})
        cfg["enabled"] = False
        set_cfg(ctx.guild.id, {"antiraid": cfg})
        await ctx.send(embed=emb(f"🛡️{SEP}Anti-Raid isključen", ""))
    else:
        cfg = guild_cfg(ctx.guild.id).get("antiraid", {})
        e = emb(f"🛡️{SEP}Anti-Raid Status", "")
        e.add_field(name="Status",    value="🟢 Aktivan" if cfg.get("enabled") else "🔴 Neaktivan", inline=True)
        e.add_field(name="Threshold", value=f"{cfg.get('threshold', 8)} joinova/30s",              inline=True)
        await ctx.send(embed=e)

# ─────────────────────────────────────────────────────────────
#  NSFW FILTER  (/ i !)
# ─────────────────────────────────────────────────────────────
nsfw_group = app_commands.Group(name="nsfw", description="🚫 NSFW auto-mod filter")

@nsfw_group.command(name="on", description="Uključi NSFW filter")
@app_commands.default_permissions(administrator=True)
async def nsfw_on(i: discord.Interaction, akcija: str = "timeout", timeout_minuta: int = 10):
    try:
        cfg = guild_cfg(i.guild_id).get("nsfw_filter", {})
        cfg.update({"enabled": True, "action": akcija, "timeout_duration": timeout_minuta * 60,
                    "exempt_channels": cfg.get("exempt_channels", []),
                    "log_channel": cfg.get("log_channel")})
        set_cfg(i.guild_id, {"nsfw_filter": cfg})
        action_label = {"delete": "🗑️ Brisanje",
                        "timeout": f"⏱️ Timeout {timeout_minuta}min",
                        "ban": "🔨 Ban"}.get(akcija, akcija)
        await i.response.send_message(embed=emb(
            f"🚫{SEP}NSFW Filter uključen",
            f"Skenira tekst, GIF-ove i fajlove.\n**Akcija:** {action_label}"
        ))
    except: pass

@nsfw_group.command(name="off", description="Isključi NSFW filter")
@app_commands.default_permissions(administrator=True)
async def nsfw_off(i: discord.Interaction):
    try:
        cfg = guild_cfg(i.guild_id).get("nsfw_filter", {})
        cfg["enabled"] = False
        set_cfg(i.guild_id, {"nsfw_filter": cfg})
        await i.response.send_message(embed=emb(f"🚫{SEP}NSFW Filter isključen", ""))
    except: pass

@nsfw_group.command(name="status", description="Status NSFW filtera")
@app_commands.default_permissions(administrator=True)
async def nsfw_status(i: discord.Interaction):
    try:
        cfg = guild_cfg(i.guild_id).get("nsfw_filter", {})
        e = emb(f"🚫{SEP}NSFW Filter Status", "")
        e.add_field(name="Status",  value="🟢 Aktivan" if cfg.get("enabled") else "🔴 Neaktivan", inline=True)
        e.add_field(name="Akcija",  value=cfg.get("action", "timeout"),                           inline=True)
        e.add_field(name="Timeout", value=f"{cfg.get('timeout_duration', 600) // 60} min",        inline=True)
        await i.response.send_message(embed=e, ephemeral=True)
    except: pass

@nsfw_group.command(name="logkanal", description="Postavi log kanal za NSFW evente")
@app_commands.default_permissions(administrator=True)
async def nsfw_logch(i: discord.Interaction, kanal: discord.TextChannel):
    try:
        cfg = guild_cfg(i.guild_id).get("nsfw_filter", {})
        cfg["log_channel"] = str(kanal.id)
        set_cfg(i.guild_id, {"nsfw_filter": cfg})
        await i.response.send_message(embed=emb(f"📋{SEP}NSFW log kanal", f"NSFW eventi → {kanal.mention}"))
    except: pass

tree.add_command(nsfw_group)

@bot.command(name="nsfw")
@commands.has_permissions(administrator=True)
async def p_nsfw(ctx, akcija: str = "status"):
    akcija = akcija.lower()
    if akcija == "on":
        cfg = guild_cfg(ctx.guild.id).get("nsfw_filter", {})
        cfg.update({"enabled": True, "action": "timeout", "timeout_duration": 600,
                    "exempt_channels": cfg.get("exempt_channels", []), "log_channel": cfg.get("log_channel")})
        set_cfg(ctx.guild.id, {"nsfw_filter": cfg})
        await ctx.send(embed=emb(f"🚫{SEP}NSFW Filter uključen", "Akcija: ⏱️ Timeout 10min"))
    elif akcija == "off":
        cfg = guild_cfg(ctx.guild.id).get("nsfw_filter", {})
        cfg["enabled"] = False
        set_cfg(ctx.guild.id, {"nsfw_filter": cfg})
        await ctx.send(embed=emb(f"🚫{SEP}NSFW Filter isključen", ""))
    else:
        cfg = guild_cfg(ctx.guild.id).get("nsfw_filter", {})
        e = emb(f"🚫{SEP}NSFW Filter Status", "")
        e.add_field(name="Status", value="🟢 Aktivan" if cfg.get("enabled") else "🔴 Neaktivan", inline=True)
        e.add_field(name="Akcija", value=cfg.get("action", "timeout"), inline=True)
        await ctx.send(embed=e)

# ─────────────────────────────────────────────────────────────
#  PECANJE  (samo ! prefix)  — prošireni sistem v2
#  CH_PECANJE = 1528697228582064190
# ─────────────────────────────────────────────────────────────

async def _do_pecanje(ctx, loc_key: str):
    """Zajednička logika za sve lokacije pecanja."""
    if not await require_channel(ctx, "pecanje"): return
    fd  = get_fishing(ctx.author.id)
    loc = LOCATIONS[loc_key]
    lvl = get_level(fd.get("xp", 0))

    # Provjera nivoa
    if lvl < loc["req_level"]:
        e = discord.Embed(
            title="🔒  Lokacija zaključana!",
            description=(
                f"> **{loc['emoji']} {loc['name']}** se otključava na **Nivou {loc['req_level']}**.\n"
                f"> Tvoj nivo: **{lvl}** — napreduj pecanjem na Rijeci!"
            ),
            color=0xe74c3c
        )
        e.set_footer(text="🎣 Mrak Bot")
        e.timestamp = datetime.now(timezone.utc)
        await ctx.send(embed=e); return

    # Cooldown
    last_key = f"last_{loc_key}"
    now      = int(time.time())
    rem      = loc["cooldown"] - (now - fd.get(last_key, 0))
    if rem > 0:
        m, s = divmod(rem, 60)
        e = discord.Embed(
            title=f"⏳  Udica je još u vodi!",
            description=f"> Čekaj još **{m}m {s}s** za **{loc['emoji']} {loc['name']}**.",
            color=0xe67e22
        )
        e.set_footer(text="🎣 Mrak Bot")
        e.timestamp = datetime.now(timezone.utc)
        await ctx.send(embed=e); return

    async with ctx.typing():
        await asyncio.sleep(random.uniform(1.2, 2.5))

    # Štap i mamac
    rod_key  = fd.get("rod", "obicni")
    rod      = RODS.get(rod_key, RODS["obicni"])
    bait_key = fd.get("bait") if fd.get("bait_count", 0) > 0 else None

    # Povlačenje ribe
    fish = _fish_draw_loc(loc["fish"], rod_key, bait_key)
    star = RARITY_STARS.get(fish["rarity"], "⬜")

    # Utrošak mamca
    if bait_key:
        fd["bait_count"] -= 1
        if fd["bait_count"] <= 0:
            fd["bait"] = None; fd["bait_count"] = 0

    # Utrošak štapa
    if rod.get("max_casts") is not None:
        fd["rod_casts"] = fd.get("rod_casts", 0) + 1
        if fd["rod_casts"] >= rod["max_casts"]:
            fd["rod"] = "obicni"; fd["rod_casts"] = 0
            rod_broke = True
        else:
            rod_broke = False
    else:
        rod_broke = False

    fd[last_key] = now
    fd["last"]   = now

    coins_earned = 0
    if fish["coins"] > 0:
        # Bonus od štapa
        bonus = int(fish["coins"] * rod["bonus_coins"])
        coins_earned = fish["coins"] + bonus

        inv      = fd.get("inv", [])
        existing = next((x for x in inv if x["name"] == fish["name"]), None)
        if existing: existing["count"] += 1
        else:        inv.append({**fish, "count": 1, "loc": loc_key})
        fd["inv"]   = inv
        fd["total"] = fd.get("total", 0) + 1
        fd["coins"] = fd.get("coins", 0) + coins_earned

        # XP
        xp_gain     = XP_PER_RARITY.get(fish["rarity"], 5)
        old_lvl     = get_level(fd.get("xp", 0))
        fd["xp"]    = fd.get("xp", 0) + xp_gain
        new_lvl     = get_level(fd["xp"])
        leveled_up  = new_lvl > old_lvl

        # Turnir — praćenje najboljeg ulova
        if coins_earned > fd.get("tournament_best", 0):
            fd["tournament_best"]      = coins_earned
            fd["tournament_best_name"] = fish["name"]
            t_data, t_key = get_tournament()
            t_data["entries"][str(ctx.author.id)] = {
                "name": ctx.author.display_name,
                "fish": fish["name"],
                "coins": coins_earned,
                "emoji": fish["emoji"],
            }
            set_tournament(t_key, t_data)

        # Dnevni zadaci
        completed = _update_daily(fd, fish, coins_earned, loc_key)
        save_fishing(ctx.author.id, fd)

        # ── Embed ────────────────────────────────────────────
        rarity_color = RARITY_COLORS.get(fish["rarity"], loc["color"])
        e = discord.Embed(color=rarity_color)

        # Naslov s ikonom lokacije
        e.set_author(name=f"{loc['emoji']} {loc['name']}  ·  {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        # Thumbnail — avatar igrača
        e.set_thumbnail(url=ctx.author.display_avatar.url)

        # Opis — centralni block
        rod_broke_txt = "\n⚠️ *Štap se slomio! Vraćen na Obični Štap.*" if rod_broke else ""
        bait_txt = f"  ·  {BAITS[bait_key]['emoji']} {BAITS[bait_key]['name']} (ostalo: {fd.get('bait_count',0)})" if bait_key else ""
        e.description = (
            f"## {fish['emoji']}  {fish['name']}\n"
            f"{star} **{fish['rarity']}**{rod_broke_txt}"
        )

        # Zarada + XP (inline)
        bonus_txt = f"\n*(+{bonus} bonus od štapa)*" if bonus else ""
        e.add_field(name="💰 Zarada",  value=f"**+{coins_earned} 💰**{bonus_txt}", inline=True)
        e.add_field(name="✨ XP",      value=f"**+{xp_gain} XP**",                 inline=True)
        e.add_field(name="🐟 Ukupno", value=f"**{fd['total']} riba**",              inline=True)

        # XP bar — novi vizualni stil
        bar   = xp_bar(fd["xp"])
        pct   = xp_pct(fd["xp"])
        nxt_x = xp_to_next(fd["xp"])
        lvl_txt = f"**Nivo {new_lvl}**" + (" ✨" if leveled_up else "")
        xp_line = f"{nxt_x} XP do Nivo {new_lvl+1}" if nxt_x else "**MAX NIVO!** 🏆"
        e.add_field(
            name=f"📊 {lvl_txt}  ·  {pct}%",
            value=f"{bar}\n`{xp_line}`",
            inline=False
        )

        # Level up poruka
        if leveled_up:
            unlock_msg = ""
            if new_lvl == 5:  unlock_msg = "  🏔️ **Jezero otključano!** (`!pecanjejezero`)"
            if new_lvl == 10: unlock_msg = "  🌊 **More otključano!** (`!pecanjemore`)"
            e.add_field(name=f"🎉  LEVEL UP → Nivo {new_lvl}!", value=f"Čestitamo!{unlock_msg}", inline=False)

        # Završeni zadaci
        if completed:
            e.add_field(name="🎯 Zadaci završeni!", value="\n".join(completed), inline=False)

        e.set_footer(text=f"🎣 {rod['emoji']} {rod['name']}{bait_txt}  ·  {fd['coins']} 💰 ukupno  ·  Mrak Bot")
        e.timestamp = datetime.now(timezone.utc)

    else:
        save_fishing(ctx.author.id, fd)
        e = discord.Embed(
            description=(
                f"## 😔  Ništa ovaj put...\n"
                f"> {loc['emoji']} **{loc['name']}** — riba je pobjegla!\n"
                f"> Pokušaj opet za **{loc['cooldown']//60}min**."
            ),
            color=0x4a4a5a
        )
        e.set_author(name=f"{ctx.author.display_name}  ·  {loc['name']}", icon_url=ctx.author.display_avatar.url)
        e.set_footer(text=f"🎣 {rod['emoji']} {rod['name']}  ·  Mrak Bot")
        e.timestamp = datetime.now(timezone.utc)

    await ctx.send(embed=e)


@bot.command(name="pecanje")
async def p_pecanje(ctx):
    """!pecanje — Prikaži lokacije ili pecat na rijeci"""
    if not await require_channel(ctx, "pecanje"): return
    fd  = get_fishing(ctx.author.id)
    lvl = get_level(fd.get("xp", 0))
    now = int(time.time())

    def cd_str(loc_k):
        loc = LOCATIONS[loc_k]
        rem = loc["cooldown"] - (now - fd.get(f"last_{loc_k}", 0))
        if lvl < loc["req_level"]: return f"🔒 Nivo {loc['req_level']}"
        return f"✅ Spreman!" if rem <= 0 else f"⏳ {max(rem,0)//60}m {max(rem,0)%60}s"

    xp    = fd.get("xp", 0)
    bar   = xp_bar(xp)
    pct   = xp_pct(xp)
    nxt_x = xp_to_next(xp)

    e = discord.Embed(
        description=(
            f"## 🎣  Odaberi lokaciju pecanja\n"
            f"> Svaka lokacija ima različite ribe, cooldown i ekskluzivne ulovove!"
        ),
        color=C_PRI
    )
    e.set_author(name=f"{ctx.author.display_name}  ·  Ribolovač", icon_url=ctx.author.display_avatar.url)
    e.set_thumbnail(url="https://em-content.zobj.net/source/twitter/376/fishing-pole_1f3a3.png")

    e.add_field(
        name="🏞️  Rijeka  —  `!pecanjereka`",
        value=f"Nivo **1+**  ·  ⏱️ 5 min\n{cd_str('reka')}",
        inline=True
    )
    e.add_field(
        name="🏔️  Jezero  —  `!pecanjejezero`",
        value=f"Nivo **5+**  ·  ⏱️ 4.5 min\n{cd_str('jezero')}",
        inline=True
    )
    e.add_field(
        name="🌊  More  —  `!pecanjemore`",
        value=f"Nivo **10+**  ·  ⏱️ 4 min\n{cd_str('more')}",
        inline=True
    )
    # XP bar
    xp_next_txt = f"{nxt_x} XP do Nivo {lvl+1}" if nxt_x else "MAX NIVO 🏆"
    e.add_field(
        name=f"📊  Nivo {lvl}  ·  {pct}%",
        value=f"{bar}\n`{xp_next_txt}`",
        inline=False
    )
    e.add_field(name="💰 Novčići",  value=f"**{fd.get('coins',0)}**",  inline=True)
    e.add_field(name="🐟 Ulovljeno", value=f"**{fd.get('total',0)}**", inline=True)
    rod = RODS.get(fd.get("rod","obicni"), RODS["obicni"])
    e.add_field(name="🎣 Štap",     value=f"{rod['emoji']} {rod['name']}", inline=True)
    e.set_footer(text="🎣 Mrak Bot  ·  !shop za opremu  ·  !zadaci za bonuse")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)

@bot.command(name="pecanjereka")
async def p_pecanjereka(ctx):
    """!pecanjereka — Pecaj na rijeci (Nivo 1+)"""
    await _do_pecanje(ctx, "reka")

@bot.command(name="pecanjejezero")
async def p_pecanjejezero(ctx):
    """!pecanjejezero — Pecaj na jezeru (Nivo 5+)"""
    await _do_pecanje(ctx, "jezero")

@bot.command(name="pecanjemore")
async def p_pecanjemore(ctx):
    """!pecanjemore — Pecaj na moru (Nivo 10+)"""
    await _do_pecanje(ctx, "more")


@bot.command(name="nivo", aliases=["rank", "xp"])
async def p_nivo(ctx, korisnik: discord.Member = None):
    """!nivo — Pogledaj nivo i XP"""
    if not await require_channel(ctx, "pecanje"): return
    target = korisnik or ctx.author
    fd     = get_fishing(target.id)
    xp     = fd.get("xp", 0)
    lvl    = get_level(xp)
    nxt    = xp_to_next(xp)

    bar = xp_bar(xp)
    pct = xp_pct(xp)

    # Boja se mijenja s nivoom
    if lvl >= 10:  lvl_color = 0x9b59b6   # ljubičasta — more
    elif lvl >= 5: lvl_color = 0x3498db   # plava — jezero
    else:          lvl_color = 0x2ecc71   # zelena — rijeka

    e = discord.Embed(color=lvl_color)
    e.set_author(name=f"📊  Nivo  ·  {target.display_name}", icon_url=target.display_avatar.url)
    e.set_thumbnail(url=target.display_avatar.url)

    e.add_field(name="🏅 Nivo",         value=f"**{lvl}** / {len(LEVEL_XP)}",    inline=True)
    e.add_field(name="✨ XP ukupno",     value=f"**{xp}**",                       inline=True)
    e.add_field(name="📈 Do sljedećeg", value=f"**{nxt} XP**" if nxt else "**MAX!** 🏆", inline=True)

    nxt_txt = f"do Nivo {lvl+1}" if nxt else "MAX NIVO"
    e.add_field(
        name=f"⬛ Progres  ·  {pct}%",
        value=f"{bar}\n`{nxt_txt}`",
        inline=False
    )

    unlocks = []
    if lvl < 5:  unlocks.append(f"🏔️ **Jezero** otključava se na Nivo 5 — još **{5-lvl}** nivo/a")
    if lvl < 10: unlocks.append(f"🌊 **More** otključava se na Nivo 10 — još **{10-lvl}** nivo/a")
    if unlocks:
        e.add_field(name="🔒 Sljedeća otključavanja", value="\n".join(unlocks), inline=False)

    fd2 = get_fishing(target.id)
    rod = RODS.get(fd2.get("rod","obicni"), RODS["obicni"])
    e.add_field(name="💰 Novčići",   value=f"**{fd2.get('coins',0)}**",        inline=True)
    e.add_field(name="🐟 Ulovljeno", value=f"**{fd2.get('total',0)} riba**",   inline=True)
    e.add_field(name="🎣 Štap",      value=f"{rod['emoji']} {rod['name']}",    inline=True)
    e.set_footer(text="🎣 Mrak Bot  ·  !pecanjereka za poceti")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="shop", aliases=["kupovina"])
async def p_shop(ctx):
    """!shop — Prodavnica opreme"""
    if not await require_channel(ctx, "pecanje"): return
    fd = get_fishing(ctx.author.id)
    e = discord.Embed(
        title="🛒  Prodavnica opreme",
        description="> Kupi štap: `!kupistap <id>`\n> Kupi mamac: `!kupimamac <id> [količina]`",
        color=0x2ecc71
    )
    rod_lines = []
    for rid, r in RODS.items():
        owned = "✅ *imaš*" if fd.get("rod") == rid else f"`{r['cost']} 💰`"
        rod_lines.append(f"{r['emoji']} **{r['name']}** · `{rid}`\n  {r['desc']} · {owned}")
    e.add_field(name="🎣 Štapovi", value="\n".join(rod_lines), inline=False)

    bait_lines = []
    for bid, b in BAITS.items():
        bait_lines.append(f"{b['emoji']} **{b['name']}** · `{bid}` · `{b['cost']} 💰/kom`\n  {b['desc']}")
    e.add_field(name="🪱 Mamci", value="\n".join(bait_lines), inline=False)
    e.add_field(name="💰 Tvoji novčići", value=f"**{fd.get('coins', 0)} 💰**", inline=False)
    e.set_footer(text="🎣 Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="kupistap")
async def p_kupistap(ctx, rod_id: str = ""):
    """!kupistap <id> — Kupi štap"""
    if not await require_channel(ctx, "pecanje"): return
    rod_id = rod_id.lower()
    if rod_id not in RODS or rod_id == "obicni":
        valid = ", ".join(k for k in RODS if k != "obicni")
        await ctx.send(embed=err_emb(f"Nepoznat štap! Validan ID: `{valid}`")); return
    rod = RODS[rod_id]
    fd  = get_fishing(ctx.author.id)
    if fd.get("rod") == rod_id:
        await ctx.send(embed=err_emb(f"Već imaš **{rod['name']}**!")); return
    if fd.get("coins", 0) < rod["cost"]:
        await ctx.send(embed=err_emb(
            f"Nemaš dovoljno! Treba **{rod['cost']} 💰**, imaš **{fd['coins']} 💰**."
        )); return
    fd["coins"] -= rod["cost"]; fd["rod"] = rod_id; fd["rod_casts"] = 0
    save_fishing(ctx.author.id, fd)
    e = discord.Embed(
        title=f"{rod['emoji']}  Kupljeno: {rod['name']}",
        description=f"> {rod['desc']}\n> Ostalo: **{fd['coins']} 💰**",
        color=0x2ecc71
    )
    e.set_footer(text="🎣 Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="kupimamac")
async def p_kupimamac(ctx, bait_id: str = "", kolicina: int = 1):
    """!kupimamac <id> [količina] — Kupi mamac"""
    if not await require_channel(ctx, "pecanje"): return
    bait_id = bait_id.lower()
    if bait_id not in BAITS:
        valid = ", ".join(BAITS.keys())
        await ctx.send(embed=err_emb(f"Nepoznat mamac! Valid: `{valid}`")); return
    kolicina = max(1, min(kolicina, 50))
    bait     = BAITS[bait_id]
    ukupno   = bait["cost"] * kolicina
    fd       = get_fishing(ctx.author.id)
    if fd.get("coins", 0) < ukupno:
        await ctx.send(embed=err_emb(
            f"Nemaš dovoljno! Treba **{ukupno} 💰**, imaš **{fd['coins']} 💰**."
        )); return
    fd["coins"] -= ukupno
    if fd.get("bait") == bait_id:
        fd["bait_count"] = fd.get("bait_count", 0) + kolicina
    else:
        fd["bait"] = bait_id; fd["bait_count"] = kolicina
    save_fishing(ctx.author.id, fd)
    e = discord.Embed(
        title=f"{bait['emoji']}  Kupljeno: {bait['name']} ×{kolicina}",
        description=f"> {bait['desc']}\n> Plaćeno: **{ukupno} 💰** · Ostalo: **{fd['coins']} 💰**",
        color=0x2ecc71
    )
    e.set_footer(text="🎣 Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="ulov")
async def p_ulov(ctx):
    """!ulov — Pogledaj uhvaćene ribe (inventar)"""
    if not await require_channel(ctx, "pecanje"): return
    fd  = get_fishing(ctx.author.id)
    inv = fd.get("inv", [])
    if not inv:
        e = discord.Embed(
            title="🎒  Inventar je prazan",
            description="> Idi pecati! `!pecanje`",
            color=0x7f8c8d
        )
        e.set_footer(text="🎣 Mrak Bot"); await ctx.send(embed=e); return

    order      = {"Obična": 0, "Neobična": 1, "Rijetka": 2, "Epska": 3, "Legendarna": 4}
    sorted_inv = sorted(inv, key=lambda x: order.get(x.get("rarity", "Obična"), 0), reverse=True)
    lines = [
        f"{RARITY_STARS.get(f.get('rarity'), '⬜')} {f['emoji']} **{f['name']}** ×{f['count']}"
        for f in sorted_inv
    ]
    # Split into pages of 15
    chunk = "\n".join(lines[:20])
    e = discord.Embed(title=f"🎒  Ulov — {ctx.author.display_name}", description=f"> {chunk.replace(chr(10), chr(10)+'> ')}", color=C_PRI)
    e.add_field(name="💰 Novčići",  value=f"**{fd.get('coins', 0)}**",  inline=True)
    e.add_field(name="🐟 Ukupno",   value=f"**{fd.get('total', 0)}**",  inline=True)
    e.add_field(name="🗂️ Vrsta",    value=f"**{len(inv)}**",            inline=True)
    rod = RODS.get(fd.get("rod","obicni"), RODS["obicni"])
    e.add_field(name="🎣 Štap",     value=f"{rod['emoji']} {rod['name']}", inline=True)
    if fd.get("bait") and fd.get("bait_count",0) > 0:
        b = BAITS.get(fd["bait"], {})
        e.add_field(name="🪱 Mamac", value=f"{b.get('emoji','')} {b.get('name','')} ×{fd['bait_count']}", inline=True)
    e.set_footer(text="🎣 Mrak Bot  ·  !prodaj da prodaš sve")
    e.set_thumbnail(url=ctx.author.display_avatar.url)
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="profil")
async def p_profil(ctx, korisnik: discord.Member = None):
    """!profil — Ribolovački profil"""
    if not await require_channel(ctx, "pecanje"): return
    target = korisnik or ctx.author
    fd     = get_fishing(target.id)
    inv    = fd.get("inv", [])
    xp     = fd.get("xp", 0)
    lvl    = get_level(xp)
    top    = sorted(inv, key=lambda x: x.get("coins", 0), reverse=True)[:3]

    e = discord.Embed(
        title=f"🎣  Profil — {target.display_name}",
        color=C_PRI
    )
    e.set_thumbnail(url=target.display_avatar.url)
    e.add_field(name="🏅 Nivo",      value=f"**{lvl}**",                      inline=True)
    e.add_field(name="✨ XP",         value=f"**{xp}**",                       inline=True)
    e.add_field(name="💰 Novčići",   value=f"**{fd.get('coins', 0)}**",        inline=True)
    e.add_field(name="🐟 Ulovljeno", value=f"**{fd.get('total', 0)} riba**",   inline=True)
    e.add_field(name="🗂️ Vrsta",     value=f"**{len(inv)} vrsta**",            inline=True)
    e.add_field(name="🐠 Akvarijum", value=f"**{len(fd.get('aquarium',[]))} / 10**", inline=True)
    e.add_field(name="📊 XP Bar",    value=f"`{xp_bar(xp)}`  *do sljedećeg: {xp_to_next(xp)} XP*", inline=False)
    rod = RODS.get(fd.get("rod","obicni"), RODS["obicni"])
    e.add_field(name="🎣 Štap",      value=f"{rod['emoji']} {rod['name']}", inline=True)
    if fd.get("bait") and fd.get("bait_count",0) > 0:
        b = BAITS.get(fd["bait"], {})
        e.add_field(name="🪱 Mamac", value=f"{b.get('emoji','')} {b.get('name','')} ×{fd['bait_count']}", inline=True)
    if top:
        e.add_field(
            name="🏆 Top 3 ulova",
            value="\n".join(f"{f['emoji']} **{f['name']}** — {f['coins']} 💰" for f in top),
            inline=False
        )
    e.set_footer(text="🎣 Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="prodaj")
async def p_prodaj(ctx):
    """!prodaj — Prodaj sve ribe za novčiće"""
    if not await require_channel(ctx, "pecanje"): return
    fd  = get_fishing(ctx.author.id)
    inv = fd.get("inv", [])
    if not inv:
        e = discord.Embed(title="🐟  Nema ribe za prodaju", description="> Inventar je prazan! Idi pecati.", color=0x7f8c8d)
        e.set_footer(text="🎣 Mrak Bot"); await ctx.send(embed=e); return
    zarada = sum(f.get("coins", 0) * f.get("count", 1) for f in inv)
    fd["coins"] = fd.get("coins", 0) + zarada
    fd["inv"]   = []
    save_fishing(ctx.author.id, fd)
    e = discord.Embed(
        title="💰  Ribe prodane!",
        description=(
            f"> Prodao/la si **{sum(f.get('count',1) for f in inv)} riba**\n"
            f"> Zarada: **+{zarada} 💰**\n"
            f"> Ukupno: **{fd['coins']} 💰**"
        ),
        color=0xf1c40f
    )
    e.set_footer(text="🎣 Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="zadaci", aliases=["daily"])
async def p_zadaci(ctx):
    """!zadaci — Dnevni zadaci pecanja"""
    if not await require_channel(ctx, "pecanje"): return
    fd    = get_fishing(ctx.author.id)
    today = get_today()
    if fd.get("daily_date") != today:
        fd["daily_tasks"]     = gen_daily_tasks()
        fd["daily_date"]      = today
        fd["daily_locs_today"] = []
        save_fishing(ctx.author.id, fd)

    e = discord.Embed(
        title="🎯  Dnevni zadaci",
        description="> Završi zadatke za bonuse! Resetuju se svaki dan u ponoć (UTC).",
        color=0xe74c3c
    )
    for i, entry in enumerate(fd.get("daily_tasks", []), 1):
        t    = entry["task"]
        prog = entry["progress"]
        total = t["count"]
        done  = entry["done"]
        bar   = "█" * int((min(prog, total) / total) * 8) + "░" * (8 - int((min(prog, total) / total) * 8))
        status = "✅ Završeno!" if done else f"`{bar}` {min(prog,total)}/{total}"
        e.add_field(
            name=f"{'✅' if done else '🎯'} Zadatak {i}",
            value=f"{t['desc']}\nNagrada: **{t['reward']} 💰** · {status}",
            inline=False
        )
    e.set_footer(text="🎣 Mrak Bot  ·  Nagrade se isplaćuju automatski")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="akvarijum")
async def p_akvarijum(ctx, korisnik: discord.Member = None):
    """!akvarijum [@korisnik] — Pogledaj akvarijum"""
    if not await require_channel(ctx, "pecanje"): return
    target = korisnik or ctx.author
    fd     = get_fishing(target.id)
    aq     = fd.get("aquarium", [])

    e = discord.Embed(
        title=f"🐠  Akvarijum — {target.display_name}",
        color=0x1a6b8a
    )
    e.set_thumbnail(url=target.display_avatar.url)
    if not aq:
        e.description = (
            "> Akvarijum je prazan!\n"
            + ("> Dodaj ribu sa `!dodajuakvarijum <naziv>`" if target.id == ctx.author.id else "")
        )
    else:
        lines = [f"{RARITY_STARS.get(f.get('rarity','Obična'),'⬜')} {f['emoji']} **{f['name']}** — {f['coins']} 💰" for f in aq]
        e.description = "\n".join(f"> {l}" for l in lines)
        e.add_field(name="🐟 Riba u akvarijumu", value=f"**{len(aq)} / 10**", inline=True)
        best = max(aq, key=lambda x: x.get("coins", 0))
        e.add_field(name="🏆 Najvrijednija", value=f"{best['emoji']} **{best['name']}** ({best['coins']} 💰)", inline=True)
    e.set_footer(text="🎣 Mrak Bot  ·  !nahrani za dnevni bonus")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="dodajuakvarijum", aliases=["daj"])
async def p_dodajuakvarijum(ctx, *, naziv: str = ""):
    """!dodajuakvarijum <naziv ribe> — Premjesti ribu u akvarijum"""
    if not await require_channel(ctx, "pecanje"): return
    if not naziv:
        await ctx.send(embed=err_emb("Upotreba: `!dodajuakvarijum <naziv ribe>`")); return
    fd = get_fishing(ctx.author.id)
    inv = fd.get("inv", [])
    aq  = fd.get("aquarium", [])
    if len(aq) >= 10:
        await ctx.send(embed=err_emb("Akvarijum je pun! Maksimum je **10 riba**.")); return
    naziv_l = naziv.lower()
    match   = next((f for f in inv if f["name"].lower() == naziv_l), None)
    if not match:
        await ctx.send(embed=err_emb(f"Nemaš ribu **{naziv}** u inventaru!")); return
    if match["count"] > 1: match["count"] -= 1
    else:                   inv.remove(match)
    aq.append({**match, "count": 1})
    fd["inv"] = inv; fd["aquarium"] = aq
    save_fishing(ctx.author.id, fd)
    e = discord.Embed(
        title=f"{match['emoji']}  Dodano u akvarijum!",
        description=f"> **{match['name']}** je sada u tvom akvarijumu.\n> `!akvarijum` za pregled",
        color=0x1a6b8a
    )
    e.set_footer(text="🎣 Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="nahrani")
async def p_nahrani(ctx):
    """!nahrani — Nahrani akvarijum za dnevni bonus"""
    if not await require_channel(ctx, "pecanje"): return
    fd    = get_fishing(ctx.author.id)
    today = get_today()
    if fd.get("daily_feed_date") == today:
        await ctx.send(embed=err_emb("Već si nahranio/la ribe danas! Vrati se sutra. 🐠")); return
    aq = fd.get("aquarium", [])
    if not aq:
        await ctx.send(embed=err_emb("Akvarijum je prazan! Dodaj ribe sa `!dodajuakvarijum`.")); return
    bonus = sum(max(1, f.get("coins", 0) // 20) for f in aq)
    fd["coins"] = fd.get("coins", 0) + bonus
    fd["daily_feed_date"] = today
    save_fishing(ctx.author.id, fd)
    e = discord.Embed(
        title="🐠  Ribe nahranjena!",
        description=(
            f"> Nahranio/la si **{len(aq)} riba** u akvarijumu.\n"
            f"> Dnevni bonus: **+{bonus} 💰**\n"
            f"> Ukupno: **{fd['coins']} 💰**"
        ),
        color=0x3db8a5
    )
    e.set_footer(text="🎣 Mrak Bot  ·  Vrati se sutra!")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="takmicenje", aliases=["turnir"])
async def p_takmicenje(ctx):
    """!takmicenje — Trenutni turnir u pecanju"""
    if not await require_channel(ctx, "pecanje"): return
    t_data, t_key = get_tournament()
    entries = sorted(t_data.get("entries", {}).values(), key=lambda x: x["coins"], reverse=True)
    d = datetime.now(timezone.utc)
    week = d.isocalendar()[1]

    e = discord.Embed(
        title=f"🏆  Tjedni turnir — Sedmica {week}",
        description=(
            "> Svaki tjedan se bira **najboljи ulov** (po vrijednosti).\n"
            "> Automatski se upisujete pri ulovu!\n"
        ),
        color=0xf39c12
    )
    if not entries:
        e.add_field(name="📋 Rang lista", value="> Još nema učesnika! Idi pecati.", inline=False)
    else:
        medals = ["🥇", "🥈", "🥉"]
        lines  = []
        for i, entry in enumerate(entries[:10]):
            m = medals[i] if i < 3 else f"**#{i+1}**"
            lines.append(f"{m} {entry['emoji']} **{entry['fish']}** — {entry['coins']} 💰 (*{entry['name']}*)")
        e.add_field(name="📋 Rang lista", value="\n".join(f"> {l}" for l in lines), inline=False)

    fd = get_fishing(ctx.author.id)
    if fd.get("tournament_best", 0) > 0:
        e.add_field(
            name="👤 Tvoj best",
            value=f"{fd['tournament_best_name']} — **{fd['tournament_best']} 💰**",
            inline=False
        )
    e.set_footer(text="🎣 Mrak Bot  ·  Nova sedmica, novi turnir!")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)

# ─────────────────────────────────────────────────────────────
#  BRAK / PROSIDBA / RASKID  (samo ! prefix)
#  CH_BRAK = 1528697409109098547
# ─────────────────────────────────────────────────────────────
class ProposalView(discord.ui.View):
    def __init__(self, from_user: discord.User, to_user: discord.User, ring: dict = None):
        super().__init__(timeout=60)
        self.from_user = from_user
        self.to_user   = to_user
        self.ring      = ring or RINGS["obicni"]

    @discord.ui.button(label="Prihvati 💍", style=discord.ButtonStyle.success)
    async def accept(self, i: discord.Interaction, btn: discord.ui.Button):
        if i.user.id != self.to_user.id:
            await i.response.send_message("Samo ta osoba može prihvatiti!", ephemeral=True); return
        if not get_proposal(self.to_user.id):
            await i.response.send_message("Prijedlog je istekao!", ephemeral=True); return
        del_proposal(self.to_user.id)
        # Potroši prsten
        del_ring(self.from_user.id)
        now = int(time.time())
        set_marriage(self.from_user.id, {"partner_id": self.to_user.id,   "partner_tag": str(self.to_user),   "at": now, "ring": self.ring["name"]})
        set_marriage(self.to_user.id,   {"partner_id": self.from_user.id, "partner_tag": str(self.from_user), "at": now, "ring": self.ring["name"]})
        e = discord.Embed(
            description=(
                f"## {self.ring['emoji']}  Vjenčanje!\n"
                f"> 💜 {self.from_user.mention} i {self.to_user.mention} su se vjenčali!\n"
                f"> Prsten: **{self.ring['name']}**\n"
                f"> 🌸 Čestitamo mladencima!\n"
                f"> 📅 Datum: <t:{now}:D>"
            ),
            color=0xe91e63
        )
        e.set_thumbnail(url="https://em-content.zobj.net/source/twitter/376/ring_1f48d.png")
        e.set_footer(text="💍 Mrak Bot")
        e.timestamp = datetime.now(timezone.utc)
        self.stop()
        for child in self.children: child.disabled = True
        await i.response.edit_message(embed=e, view=self)

    @discord.ui.button(label="Odbij ❌", style=discord.ButtonStyle.danger)
    async def reject(self, i: discord.Interaction, btn: discord.ui.Button):
        if i.user.id != self.to_user.id:
            await i.response.send_message("Samo ta osoba može odbiti!", ephemeral=True); return
        del_proposal(self.to_user.id)
        e = discord.Embed(
            description=(
                f"## 💔  Prijedlog odbijen\n"
                f"> {self.to_user.mention} je odbio/la prijedlog od {self.from_user.mention}.\n"
                f"> Prsten ostaje kod {self.from_user.mention}."
            ),
            color=0xe74c3c
        )
        e.set_footer(text="💍 Mrak Bot")
        e.timestamp = datetime.now(timezone.utc)
        self.stop()
        for child in self.children: child.disabled = True
        await i.response.edit_message(embed=e, view=self)

    async def on_timeout(self):
        del_proposal(self.to_user.id)


class DivorceView(discord.ui.View):
    def __init__(self, user_id: int, partner_id: int):
        super().__init__(timeout=30)
        self.user_id    = user_id
        self.partner_id = partner_id

    @discord.ui.button(label="Potvrdi razvod 💔", style=discord.ButtonStyle.danger)
    async def confirm(self, i: discord.Interaction, btn: discord.ui.Button):
        if i.user.id != self.user_id:
            await i.response.send_message("Nije tvoj razvod!", ephemeral=True); return
        del_marriage(self.user_id); del_marriage(self.partner_id)
        e = emb(f"💔{SEP}Brak raskinut", f"<@{self.user_id}> i <@{self.partner_id}> su se razveli.\n🌙 Sve ima kraj...")
        self.stop()
        for child in self.children: child.disabled = True
        await i.response.edit_message(embed=e, view=self)

    @discord.ui.button(label="Odustani 💜", style=discord.ButtonStyle.success)
    async def cancel(self, i: discord.Interaction, btn: discord.ui.Button):
        if i.user.id != self.user_id:
            await i.response.send_message("Nije tvoj razvod!", ephemeral=True); return
        e = emb(f"💜{SEP}Razvod otkazan", "Ostajete zajedno! Ljubav pobjeđuje! 🌸")
        self.stop()
        for child in self.children: child.disabled = True
        await i.response.edit_message(embed=e, view=self)


@bot.command(name="prosidba")
async def p_prosidba(ctx, korisnik: discord.Member = None):
    """!prosidba @korisnik — Zaprosi nekoga za brak 💍"""
    if not await require_channel(ctx, "brak"): return
    if not korisnik:
        await ctx.send(embed=err_emb("Upotreba: `!prosidba @korisnik`\n💍 Kupi prsten prvo: `!prstenishop`")); return
    if korisnik.id == ctx.author.id:
        await ctx.send(embed=err_emb("Ne možeš prositi sam/a sebe!")); return
    if korisnik.bot:
        await ctx.send(embed=err_emb("Botovi ne mogu biti u braku! 🤖")); return
    if get_marriage(ctx.author.id):
        await ctx.send(embed=err_emb("Već si u braku! Prvo se razvedi.")); return
    if get_marriage(korisnik.id):
        await ctx.send(embed=err_emb(f"{korisnik.mention} je već u braku!")); return
    if get_proposal(korisnik.id):
        await ctx.send(embed=err_emb("Ta osoba već ima aktivan prijedlog!")); return

    # Prsten — potreban za prosidbu
    ring_id = get_ring(ctx.author.id)
    if not ring_id:
        e = discord.Embed(
            description=(
                "## 💍  Trebaš prsten!\n"
                "> Kupi prsten u `!prstenishop` pa zaprosi.\n"
                "> Skupljaj novčiće pecanjem i izaberi nivo prstena!\n\n"
                "> 💍 `!kupuprsten obicni` — 500 💰\n"
                "> 💎 `!kupuprsten neobicni` — 2,000 💰\n"
                "> 🔮 `!kupuprsten rijetki` — 10,000 💰\n"
                "> ⚡ `!kupuprsten epski` — 50,000 💰\n"
                "> 🌟 `!kupuprsten legendarni` — 250,000 💰"
            ),
            color=0xe74c3c
        )
        e.set_footer(text="💍 Mrak Bot  ·  !prstenishop za više info")
        e.timestamp = datetime.now(timezone.utc)
        await ctx.send(embed=e); return

    ring = RINGS[ring_id]
    set_proposal(korisnik.id, {"from_id": ctx.author.id, "from_tag": str(ctx.author)})

    e = discord.Embed(
        description=(
            f"## {ring['emoji']}  Prijedlog braka!\n"
            f"> {ctx.author.mention} je zaprosio/la {korisnik.mention}\n"
            f"> sa **{ring['name']}** !\n\n"
            f"> 🌸 {korisnik.mention}, prihvataš li prijedlog?\n"
            f"> ⏰ Imaš **60 sekundi**."
        ),
        color=0xe91e63
    )
    e.set_thumbnail(url="https://em-content.zobj.net/source/twitter/376/ring_1f48d.png")
    e.set_footer(text=f"💍 {ring['name']}  ·  Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e, view=ProposalView(ctx.author, korisnik, ring))


@bot.command(name="brak")
async def p_brak(ctx, korisnik: discord.Member = None):
    """!brak [@korisnik] — Pogledaj bračni status"""
    if not await require_channel(ctx, "brak"): return
    target = korisnik or ctx.author
    m = get_marriage(target.id)
    if not m:
        e = discord.Embed(
            description=f"## 💔  Nije u braku\n> {target.mention} trenutno nije u braku.\n> Pronađi nekoga i zaprosi! `!prosidba @korisnik`",
            color=0x888888
        )
        e.set_footer(text="💍 Mrak Bot")
        e.timestamp = datetime.now(timezone.utc)
        await ctx.send(embed=e); return
    ring_name = m.get("ring", "Obični Prsten")
    e = discord.Embed(
        description=(
            f"## 💍  Bračni status\n"
            f"> 💜 {target.mention} je u braku sa <@{m['partner_id']}>!\n"
            f"> 💍 Prsten: **{ring_name}**\n"
            f"> 📅 Vjenčali se: <t:{m['at']}:D>\n"
            f"> ⏰ Zajedno: <t:{m['at']}:R>"
        ),
        color=0xe91e63
    )
    e.set_thumbnail(url=target.display_avatar.url)
    e.set_footer(text="💍 Mrak Bot  ·  !raskid za razvod")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="raskid")
async def p_raskid(ctx):
    """!raskid — Razvedi se 💔"""
    if not await require_channel(ctx, "brak"): return
    m = get_marriage(ctx.author.id)
    if not m:
        await ctx.send(embed=err_emb("Nisi u braku!")); return
    e = emb(
        f"💔{SEP}Potvrdi razvod",
        f"Zaista hoćeš razvod od <@{m['partner_id']}>?\n⚠️ Ova akcija je nepovratna!"
    )
    await ctx.send(embed=e, view=DivorceView(ctx.author.id, int(m["partner_id"])))

# ─────────────────────────────────────────────────────────────
#  PRSTENI  (samo ! prefix)  — CH_BRAK
# ─────────────────────────────────────────────────────────────

@bot.command(name="prstenishop", aliases=["prsten", "ringshop"])
async def p_prstenishop(ctx):
    """!prstenishop — Pogledaj prstene za kupovinu"""
    if not await require_channel(ctx, "brak"): return
    fd = get_fishing(ctx.author.id)
    my_ring = get_ring(ctx.author.id)

    e = discord.Embed(
        description=(
            "## 💍  Prodavnica prstena\n"
            "> Kupi prsten pecanjem novčića, pa zaprosi nekoga!\n"
            "> Koristi: **`!kupuprsten <id>`**\n"
            "> Zaprosi: **`!prosidba @korisnik`**"
        ),
        color=0xe91e63
    )
    e.set_thumbnail(url="https://em-content.zobj.net/source/twitter/376/ring_1f48d.png")

    lines = []
    for rid, r in RINGS.items():
        owned = "  ✅ **imaš!**" if my_ring == rid else f"  `{r['cost']:,} 💰`"
        lines.append(f"{r['emoji']} **{r['name']}** · `{rid}`{owned}\n  ↳ *{r['desc']}*")
    e.add_field(name="💍 Dostupni prsteni", value="\n".join(lines), inline=False)

    if my_ring:
        r = RINGS[my_ring]
        e.add_field(name="👤 Tvoj prsten", value=f"{r['emoji']} **{r['name']}**  ·  Spreman za prosidbu!", inline=False)
    else:
        e.add_field(name="👤 Tvoj prsten", value="Nemaš prsten — kupi jedan i zaprosi! 💔", inline=False)

    e.add_field(name="💰 Tvoji novčići", value=f"**{fd.get('coins', 0):,} 💰**", inline=False)
    e.set_footer(text="💍 Mrak Bot  ·  Skupljaj novčiće pecanjem!")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


@bot.command(name="kupuprsten", aliases=["kupiprsten"])
async def p_kupuprsten(ctx, ring_id: str = ""):
    """!kupuprsten <id> — Kupi prsten"""
    if not await require_channel(ctx, "brak"): return
    ring_id = ring_id.lower()
    if ring_id not in RINGS:
        valid = ", ".join(f"`{k}`" for k in RINGS)
        await ctx.send(embed=err_emb(f"Nepoznat prsten! Dostupno: {valid}\n\nVidi `!prstenishop`")); return
    fd   = get_fishing(ctx.author.id)
    ring = RINGS[ring_id]
    if fd.get("coins", 0) < ring["cost"]:
        await ctx.send(embed=err_emb(
            f"Nemaš dovoljno novčića!\n"
            f"Treba: **{ring['cost']:,} 💰**\n"
            f"Imaš: **{fd.get('coins',0):,} 💰**\n\n"
            f"Idi pecati i skupi dovoljno! 🎣"
        )); return
    old_ring = get_ring(ctx.author.id)
    if old_ring:
        old = RINGS[old_ring]
        # Refund 50% starog prstena
        refund = old["cost"] // 2
        fd["coins"] = fd.get("coins", 0) + refund
        save_fishing(ctx.author.id, fd)
        refund_txt = f"\n> 🔄 Stari prsten refundiran za **{refund:,} 💰**"
    else:
        refund_txt = ""
    fd["coins"] = fd.get("coins", 0) - ring["cost"]
    save_fishing(ctx.author.id, fd)
    set_ring(ctx.author.id, ring_id)
    e = discord.Embed(
        description=(
            f"## {ring['emoji']}  Prsten kupljen!\n"
            f"> Kupio/la si **{ring['name']}**!\n"
            f"> *{ring['desc']}*{refund_txt}\n"
            f"> Ostalo: **{fd['coins']:,} 💰**\n\n"
            f"> Zaprosi nekoga sa `!prosidba @korisnik`! 💍"
        ),
        color=0xe91e63
    )
    e.set_thumbnail(url="https://em-content.zobj.net/source/twitter/376/ring_1f48d.png")
    e.set_footer(text="💍 Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)


# ─────────────────────────────────────────────────────────────
#  SOCIJALNE KOMANDE  (samo ! prefix)  — CH_BRAK
# ─────────────────────────────────────────────────────────────

SOCIAL_GIFS = {
    "klupa": [
        "https://media.tenor.com/images/5a9efad30a0d3b77b23c2e25b42bd4c5/tenor.gif",
        "https://media.tenor.com/images/a0cf16c28a2e72c91451fff3af93b3b5/tenor.gif",
        "https://media.tenor.com/images/bc92a7c73756cc8ef5e9c98aff76b59e/tenor.gif",
    ],
    "spavanje": [
        "https://media.tenor.com/images/b8b1a4adaef0c3e26d36382e8a5c0aa2/tenor.gif",
        "https://media.tenor.com/images/0f9b78c18e052c60d0e58a073d23dd6a/tenor.gif",
        "https://media.tenor.com/images/e5f66c21b61de4fac23c95b69f4dc8c0/tenor.gif",
    ],
    "grljenje": [
        "https://media.tenor.com/images/4f3e99d22fa6d3ef00fb4e2e1a8d19f5/tenor.gif",
        "https://media.tenor.com/images/24da2bd9da067c8bb4e73e6cda780a60/tenor.gif",
        "https://media.tenor.com/images/b84c50c66dab4df5a8d96b8a6b9f8ee2/tenor.gif",
    ],
    "udarac": [
        "https://media.tenor.com/images/b498e3c0ce80a4a64741b1c4f4e20c87/tenor.gif",
        "https://media.tenor.com/images/9dc618bed8c2d617c63aed56e51d6e2a/tenor.gif",
        "https://media.tenor.com/images/2fce77e02cfb67e6a20d6b3c012e27c5/tenor.gif",
    ],
    "pljesak": [
        "https://media.tenor.com/images/eee0e3a7c2c2e7a9e87e7c30c91dba46/tenor.gif",
        "https://media.tenor.com/images/1f55d33c0e93a27bfa19fc6f4ed8f2b6/tenor.gif",
        "https://media.tenor.com/images/5cd03b55a9b4c38b9b0bbaf65f9e7b6c/tenor.gif",
    ],
    "hrana": [
        "https://media.tenor.com/images/dd42b4d9d6b7a0a0e0a43b3e08f7b44e/tenor.gif",
        "https://media.tenor.com/images/a28b8bb5e95b5a6e2a7e5d3c01e1fac4/tenor.gif",
        "https://media.tenor.com/images/7c0c5eb2b3c3d7fb89a3bfb1c1d4e5f6/tenor.gif",
    ],
    "kafa": [
        "https://media.tenor.com/images/3fc18a63a8b9d7e4e3f0c2b1a5d6e7f8/tenor.gif",
        "https://media.tenor.com/images/8b7a6c5d4e3f2a1b0c9d8e7f6a5b4c3/tenor.gif",
        "https://media.tenor.com/images/1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6/tenor.gif",
    ],
    "pogled": [
        "https://media.tenor.com/images/7f6e5d4c3b2a1f0e9d8c7b6a5f4e3d2/tenor.gif",
        "https://media.tenor.com/images/2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7/tenor.gif",
        "https://media.tenor.com/images/9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4/tenor.gif",
    ],
}

def social_emb(title: str, desc: str, gif_key: str, color: int = C_PRI) -> discord.Embed:
    e = discord.Embed(title=title, description=desc, color=color)
    e.set_image(url=random.choice(SOCIAL_GIFS[gif_key]))
    e.set_footer(text="🌙 Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    return e


@bot.command(name="klupa")
async def p_klupa(ctx, korisnik: discord.Member = None):
    """!klupa @korisnik — Pošalji nekoga na klupu"""
    if not await require_channel(ctx, "brak"): return
    if not korisnik:
        await ctx.send(embed=err_emb("Upotreba: `!klupa @korisnik`")); return
    if korisnik.id == ctx.author.id:
        await ctx.send(embed=err_emb("Ne možeš sebe poslati na klupu! 😄")); return
    await ctx.send(embed=social_emb(
        f"🪑{SEP}Klupa!",
        f"> {ctx.author.mention} je poslao/la {korisnik.mention} na klupu!\n"
        f"> Sjedni i razmisli o svojim postupcima. 😤",
        "klupa", 0xe67e22
    ))


@bot.command(name="spavanje")
async def p_spavanje(ctx, korisnik: discord.Member = None):
    """!spavanje [@korisnik] — Idi spavati ili uspavaj nekoga"""
    if not await require_channel(ctx, "brak"): return
    if korisnik:
        if korisnik.id == ctx.author.id:
            await ctx.send(embed=social_emb(
                f"😴{SEP}Laku noć!",
                f"> {ctx.author.mention} ide spavati. Laku noć svima! 🌙",
                "spavanje", 0x9b59b6
            ))
        else:
            await ctx.send(embed=social_emb(
                f"😴{SEP}Uspavan/a!",
                f"> {ctx.author.mention} je uspavao/la {korisnik.mention}! 💤\n"
                f"> Laku noć, {korisnik.mention}~ 🌙",
                "spavanje", 0x9b59b6
            ))
    else:
        await ctx.send(embed=social_emb(
            f"😴{SEP}Laku noć!",
            f"> {ctx.author.mention} ide spavati. Laku noć svima! 🌙",
            "spavanje", 0x9b59b6
        ))


@bot.command(name="grli")
async def p_grli(ctx, korisnik: discord.Member = None):
    """!grli @korisnik — Zagrli nekoga"""
    if not await require_channel(ctx, "brak"): return
    if not korisnik:
        await ctx.send(embed=err_emb("Upotreba: `!grli @korisnik`")); return
    if korisnik.id == ctx.author.id:
        await ctx.send(embed=err_emb("Ne možeš grliti sam/a sebe! 🤗")); return
    await ctx.send(embed=social_emb(
        f"🤗{SEP}Zagrljaj!",
        f"> {ctx.author.mention} grli {korisnik.mention}! 💜\n"
        f"> Osjećaš li ljubav? 🌸",
        "grljenje", 0xe91e63
    ))


@bot.command(name="udarac")
async def p_udarac(ctx, korisnik: discord.Member = None):
    """!udarac @korisnik — Udari nekoga"""
    if not await require_channel(ctx, "brak"): return
    if not korisnik:
        await ctx.send(embed=err_emb("Upotreba: `!udarac @korisnik`")); return
    if korisnik.id == ctx.author.id:
        await ctx.send(embed=err_emb("Ne možeš udariti sam/a sebe! 😅")); return
    poruke = [
        f"> {ctx.author.mention} je šamarao/la {korisnik.mention}! 👋",
        f"> {ctx.author.mention} je lupio/la {korisnik.mention}! 💥",
        f"> {ctx.author.mention} je udario/la {korisnik.mention} kao grom! ⚡",
    ]
    await ctx.send(embed=social_emb(
        f"👊{SEP}Udarac!",
        random.choice(poruke),
        "udarac", 0xe74c3c
    ))


@bot.command(name="pljesak")
async def p_pljesak(ctx, korisnik: discord.Member = None):
    """!pljesak @korisnik — Aplaudiraj nekome"""
    if not await require_channel(ctx, "brak"): return
    if not korisnik:
        await ctx.send(embed=err_emb("Upotreba: `!pljesak @korisnik`")); return
    await ctx.send(embed=social_emb(
        f"👏{SEP}Aplauz!",
        f"> {ctx.author.mention} plješće {korisnik.mention}! 👏\n"
        f"> Bravo, {korisnik.mention}! 🌟",
        "pljesak", 0xf1c40f
    ))


@bot.command(name="hrani")
async def p_hrani(ctx, korisnik: discord.Member = None):
    """!hrani @korisnik — Ponudi hranu nekome"""
    if not await require_channel(ctx, "brak"): return
    if not korisnik:
        await ctx.send(embed=err_emb("Upotreba: `!hrani @korisnik`")); return
    if korisnik.id == ctx.author.id:
        await ctx.send(embed=err_emb("Hraniti ćeš se sam/a? 😄")); return
    hrana = random.choice(["🍕 picu", "🎂 tortu", "🍫 čokoladu", "🍜 tjesteninu", "🍩 krofnu", "🥐 kroasan"])
    await ctx.send(embed=social_emb(
        f"🍽️{SEP}Hrana!",
        f"> {ctx.author.mention} nudi {korisnik.mention} {hrana}!\n"
        f"> Prijatno, {korisnik.mention}! 😋",
        "hrana", 0x2ecc71
    ))


@bot.command(name="kafa")
async def p_kafa(ctx, korisnik: discord.Member = None):
    """!kafa [@korisnik] — Pij kafu ili ponudi nekome"""
    if not await require_channel(ctx, "brak"): return
    if korisnik and korisnik.id != ctx.author.id:
        await ctx.send(embed=social_emb(
            f"☕{SEP}Kafa!",
            f"> {ctx.author.mention} nudi {korisnik.mention} šolju kafe! ☕\n"
            f"> Uživaj, {korisnik.mention}! 🌙",
            "kafa", 0x795548
        ))
    else:
        await ctx.send(embed=social_emb(
            f"☕{SEP}Kafa!",
            f"> {ctx.author.mention} pije kafu. ☕\n"
            f"> Uživaj u tišini i mirisu kafe! 🌙",
            "kafa", 0x795548
        ))


@bot.command(name="pogled")
async def p_pogled(ctx, korisnik: discord.Member = None):
    """!pogled @korisnik — Gledaj nekoga sumnjičavo"""
    if not await require_channel(ctx, "brak"): return
    if not korisnik:
        await ctx.send(embed=err_emb("Upotreba: `!pogled @korisnik`")); return
    if korisnik.id == ctx.author.id:
        await ctx.send(embed=err_emb("Gledaš se u ogledalo? 🪞")); return
    poruke = [
        f"> {ctx.author.mention} te gleda veoma sumnjičavo, {korisnik.mention}... 👀",
        f"> {ctx.author.mention} baca ljutit pogled prema {korisnik.mention}. 😤",
        f"> {ctx.author.mention} ne skida oči sa {korisnik.mention}... 🤨",
    ]
    await ctx.send(embed=social_emb(
        f"👀{SEP}Pogled!",
        random.choice(poruke),
        "pogled", 0x607d8b
    ))


# ─────────────────────────────────────────────────────────────
#  KALADONT  (samo ! prefix)
#  CH_KALADONT = 1496860023907811351
# ─────────────────────────────────────────────────────────────
@bot.command(name="kaladont")
async def p_kaladont(ctx, akcija: str = "start"):
    """!kaladont [start|stop|status|pravila]"""
    if not await require_channel(ctx, "kaladont"): return
    akcija = akcija.lower()
    key    = (str(ctx.guild.id), str(ctx.channel.id))

    if akcija == "start":
        if key in kaladont_games:
            await ctx.send(embed=err_emb("Igra je već aktivna! Koristi `!kaladont stop` da završiš.")); return
        start_word = random.choice(list(KALADONT_WORDS))
        kaladont_games[key] = {"word": start_word, "used": {start_word}, "round": 1, "last_player": None}
        suf = normalize_word(start_word)[-2:]
        word_display = (f"{start_word[:-2]}**{start_word[-2:]}**") if len(start_word) > 2 else f"**{start_word}**"
        e = discord.Embed(
            title=f"🔤{SEP}Kaladont — Start!",
            description=bq(
                f"Startna riječ: {word_display}\n\n"
                f"Sljedeća mora počinjati sa: **`{suf}`**\n\n"
                f"💬 Piši direktno u chat!\n"
                f"📌 Svaki igrač igra jednom, zatim čeka.\n"
                f"🛑 `!kaladont stop` za kraj igre."
            ),
            color=C_PRI
        )
        e.set_footer(text=f"🔤 Mrak Bot • {len(KALADONT_WORDS):,} riječi u rječniku")
        e.timestamp = datetime.now(timezone.utc)
        await ctx.send(embed=e)

    elif akcija == "stop":
        if key not in kaladont_games:
            await ctx.send(embed=err_emb("Nema aktivne igre.")); return
        game = kaladont_games.pop(key)
        await ctx.send(embed=emb(
            f"🔤{SEP}Kaladont završen",
            f"**Rundi odigrano:** {game['round']}\n**Različitih riječi:** {len(game['used'])}"
        ))

    elif akcija == "status":
        game = kaladont_games.get(key)
        if not game:
            await ctx.send(embed=err_emb("Nema aktivne igre.")); return
        suf = normalize_word(game["word"])[-2:]
        word_display = (f"{game['word'][:-2]}**{game['word'][-2:]}**") if len(game["word"]) > 2 else f"**{game['word']}**"
        e = emb(
            f"🔤{SEP}Kaladont Status",
            f"Zadnja riječ: {word_display}\nSljedeća počinje sa: **`{suf}`**"
        )
        e.add_field(name="🔢 Runda",       value=str(game["round"]),     inline=True)
        e.add_field(name="📖 Iskorišćeno", value=str(len(game["used"])), inline=True)
        await ctx.send(embed=e)

    else:  # pravila
        e = emb(
            f"📖{SEP}Pravila Kaladonta",
            "**Kaladont** je igra lančanja riječi:\n\n"
            "1️⃣ Bot daje startnu riječ\n"
            "2️⃣ Naredna mora počinjati zadnja **2 slova** prethodne\n"
            "3️⃣ Ista riječ ne smije se ponoviti\n"
            "4️⃣ Isti igrač ne može igrati dva puta zaredom\n"
            "5️⃣ Piši direktno u chat (ne komandom!)\n\n"
            "**Primjer:**\n"
            "`radar` → `ra**dar**` → `ar` → `arkan` → `an` → `ananas`"
        )
        e.add_field(name="📚 Rječnik", value=f"{len(KALADONT_WORDS):,} bosanskih/srpskih riječi", inline=False)
        await ctx.send(embed=e)

# ─────────────────────────────────────────────────────────────
#  FUN COMMANDS  (/ i !)
# ─────────────────────────────────────────────────────────────
EIGHT_BALL = [
    "Da, sigurno!", "Naravno!", "Možeš računati na to!", "Bez ikakve sumnje!",
    "Izgleda da je da.", "Vjerovatno da.", "Moguće je.", "Ne sada, ali uskoro.",
    "Teško.", "Sumnjičav/a sam.", "Vjerovatno ne.", "Nikako.", "Definitivno NE.",
    "Moje viđenje kaže ne.", "Izgledi nisu dobri.", "Pitaj ponovo.", "Još nije jasno.",
]

@tree.command(name="8ball", description="Postavi pitanje čarobnoj kugli 🎱")
async def eightball(i: discord.Interaction, pitanje: str):
    try:
        await i.response.send_message(embed=emb(
            f"🎱{SEP}Čarobna Kugla",
            f"❓ **{pitanje}**\n\n🔮 {random.choice(EIGHT_BALL)}"
        ))
    except: pass

@bot.command(name="8ball")
async def p_eightball(ctx, *, pitanje: str):
    await ctx.send(embed=emb(
        f"🎱{SEP}Čarobna Kugla",
        f"❓ **{pitanje}**\n\n🔮 {random.choice(EIGHT_BALL)}"
    ))


@tree.command(name="coinflip", description="Baci novčić 🪙")
async def coinflip(i: discord.Interaction):
    try:
        result = random.choice(["Glava", "Pismo"])
        await i.response.send_message(embed=emb(
            f"🪙{SEP}{'Glava! 👑' if result == 'Glava' else 'Pismo! 📜'}",
            f"Bačen novčić je pao na: **{result}**"
        ))
    except: pass

@bot.command(name="coinflip")
async def p_coinflip(ctx):
    result = random.choice(["Glava", "Pismo"])
    await ctx.send(embed=emb(
        f"🪙{SEP}{'Glava! 👑' if result == 'Glava' else 'Pismo! 📜'}",
        f"Bačen novčić je pao na: **{result}**"
    ))


@tree.command(name="poll", description="Kreiraj glasanje 📊")
async def poll(i: discord.Interaction, pitanje: str,
               opcija_a: str = "Da", opcija_b: str = "Ne",
               opcija_c: str = None, opcija_d: str = None):
    try:
        opcije = [o for o in [opcija_a, opcija_b, opcija_c, opcija_d] if o]
        emojis = ["🇦", "🇧", "🇨", "🇩"]
        desc   = "\n".join(f"{emojis[n]} **{o}**" for n, o in enumerate(opcije))
        e = emb(f"📊{SEP}{pitanje}", desc)
        e.set_footer(text="🌙 Mrak Bot • Glasaj reakcijama!")
        await i.response.send_message(embed=e)
        msg = await i.original_response()
        for n in range(len(opcije)): await msg.add_reaction(emojis[n])
    except: pass

@bot.command(name="poll")
async def p_poll(ctx, pitanje: str, opcija_a: str = "Da", opcija_b: str = "Ne"):
    emojis = ["🇦", "🇧"]
    desc   = f"🇦 **{opcija_a}**\n🇧 **{opcija_b}**"
    e = emb(f"📊{SEP}{pitanje}", desc)
    e.set_footer(text="🌙 Mrak Bot • Glasaj reakcijama!")
    msg = await ctx.send(embed=e)
    for em in emojis: await msg.add_reaction(em)

# ─────────────────────────────────────────────────────────────
#  INFO COMMANDS  (/ i !)
# ─────────────────────────────────────────────────────────────
@tree.command(name="userinfo", description="Informacije o korisniku")
async def userinfo(i: discord.Interaction, korisnik: discord.Member = None):
    try:
        m     = korisnik or i.user
        roles = [r.mention for r in m.roles if r.name != "@everyone"]
        e     = emb(f"👤{SEP}{m.display_name}", "")
        e.set_thumbnail(url=m.display_avatar.url)
        e.add_field(name="🏷️ Tag",          value=m.mention,                                        inline=True)
        e.add_field(name="🔢 ID",            value=str(m.id),                                        inline=True)
        e.add_field(name="🤖 Bot",           value="Da" if m.bot else "Ne",                          inline=True)
        e.add_field(name="📅 Nalog kreiran", value=f"<t:{int(m.created_at.timestamp())}:D>",         inline=True)
        e.add_field(name="📥 Pridružio/la",  value=f"<t:{int(m.joined_at.timestamp())}:D>",          inline=True)
        e.add_field(name="🎭 Uloge",         value=" ".join(roles) if roles else "*nema*",            inline=False)
        await i.response.send_message(embed=e)
    except: pass

@bot.command(name="userinfo")
async def p_userinfo(ctx, korisnik: discord.Member = None):
    m     = korisnik or ctx.author
    roles = [r.mention for r in m.roles if r.name != "@everyone"]
    e     = emb(f"👤{SEP}{m.display_name}", "")
    e.set_thumbnail(url=m.display_avatar.url)
    e.add_field(name="🏷️ Tag",          value=m.mention,                                    inline=True)
    e.add_field(name="🔢 ID",            value=str(m.id),                                    inline=True)
    e.add_field(name="📅 Nalog kreiran", value=f"<t:{int(m.created_at.timestamp())}:D>",     inline=True)
    e.add_field(name="📥 Pridružio/la",  value=f"<t:{int(m.joined_at.timestamp())}:D>",      inline=True)
    e.add_field(name="🎭 Uloge",         value=" ".join(roles) if roles else "*nema*",        inline=False)
    await ctx.send(embed=e)


@tree.command(name="serverinfo", description="Informacije o serveru")
async def serverinfo(i: discord.Interaction):
    try:
        g = i.guild
        e = emb(f"🌙{SEP}{g.name}", "")
        if g.icon: e.set_thumbnail(url=g.icon.url)
        e.add_field(name="👑 Vlasnik", value=g.owner.mention if g.owner else "*?*",          inline=True)
        e.add_field(name="👥 Članova", value=str(g.member_count),                             inline=True)
        e.add_field(name="📢 Kanala",  value=str(len(g.channels)),                            inline=True)
        e.add_field(name="🎭 Uloga",   value=str(len(g.roles)),                               inline=True)
        e.add_field(name="😄 Emojija", value=str(len(g.emojis)),                              inline=True)
        e.add_field(name="📅 Kreiran", value=f"<t:{int(g.created_at.timestamp())}:D>",        inline=True)
        await i.response.send_message(embed=e)
    except: pass

@bot.command(name="serverinfo")
async def p_serverinfo(ctx):
    g = ctx.guild
    e = emb(f"🌙{SEP}{g.name}", "")
    if g.icon: e.set_thumbnail(url=g.icon.url)
    e.add_field(name="👑 Vlasnik", value=g.owner.mention if g.owner else "*?*", inline=True)
    e.add_field(name="👥 Članova", value=str(g.member_count),                   inline=True)
    e.add_field(name="📢 Kanala",  value=str(len(g.channels)),                  inline=True)
    e.add_field(name="🎭 Uloga",   value=str(len(g.roles)),                     inline=True)
    e.add_field(name="😄 Emojija", value=str(len(g.emojis)),                    inline=True)
    e.add_field(name="📅 Kreiran", value=f"<t:{int(g.created_at.timestamp())}:D>", inline=True)
    await ctx.send(embed=e)


@tree.command(name="avatar", description="Pogledaj avatar korisnika")
async def avatar(i: discord.Interaction, korisnik: discord.Member = None):
    try:
        m = korisnik or i.user
        e = discord.Embed(title=f"🖼️{SEP}Avatar — {m.mention}", color=C_PRI)
        e.set_image(url=m.display_avatar.url)
        e.set_footer(text="🌙 Mrak Bot")
        e.timestamp = datetime.now(timezone.utc)
        await i.response.send_message(embed=e)
    except: pass

@bot.command(name="avatar")
async def p_avatar(ctx, korisnik: discord.Member = None):
    m = korisnik or ctx.author
    e = discord.Embed(title=f"🖼️{SEP}Avatar — {m.mention}", color=C_PRI)
    e.set_image(url=m.display_avatar.url)
    e.set_footer(text="🌙 Mrak Bot")
    e.timestamp = datetime.now(timezone.utc)
    await ctx.send(embed=e)

# ─────────────────────────────────────────────────────────────
#  HELP  (/ i !)
# ─────────────────────────────────────────────────────────────
@tree.command(name="help", description="Lista svih komandi")
async def help_cmd(i: discord.Interaction):
    try:
        e = emb(f"📖{SEP}Mrak Bot v3.3 — Pomoć", "")
        e.add_field(
            name="🛡️ Moderacija  (! i /)",
            value=(
                "`!ban @korisnik [razlog]` — Banuj\n"
                "`!kick @korisnik [razlog]` — Kickuj\n"
                "`!timeout @korisnik [min] [razlog]` — Timeout\n"
                "`!untimeout @korisnik` — Ukloni timeout\n"
                "`!warn @korisnik [razlog]` — Upozorenje\n"
                "`!warnings @korisnik` — Pregled upozorenja\n"
                "`!clear [broj]` — Briši poruke"
            ),
            inline=False
        )
        e.add_field(
            name="⚙️ Setup  (! i /)",
            value=(
                "`!setwelcome #kanal` — Welcome kanal\n"
                "`!setgoodbye #kanal` — Goodbye kanal\n"
                "`!setlogs #kanal` — Mod log kanal\n"
                "`!antiraid on/off/status [threshold]` — Anti-raid\n"
                "`!nsfw on/off/status` — NSFW filter"
            ),
            inline=False
        )
        e.add_field(
            name=f"🎣 Pecanje  (samo !)  → <#{CH_PECANJE}>",
            value=(
                "`!pecanje` — Pregled lokacija\n"
                "`!pecanjereka` · `!pecanjejezero` · `!pecanjemore` — Pecaj\n"
                "`!nivo [@korisnik]` — XP i nivo\n"
                "`!shop` — Prodavnica (štapovi i mamci)\n"
                "`!kupistap <id>` · `!kupimamac <id> [kom]` — Kupi opremu\n"
                "`!ulov` · `!profil` · `!prodaj` — Inventar i prodaja\n"
                "`!akvarijum [@k]` · `!dodajuakvarijum <riba>` · `!nahrani` — Akvarijum\n"
                "`!zadaci` — Dnevni zadaci  ·  `!takmicenje` — Tjedni turnir"
            ),
            inline=False
        )
        e.add_field(
            name=f"💍 Brak & Socijalno  (samo !)  → <#{CH_BRAK}>",
            value=(
                "`!prosidba @korisnik` — Zaprosi nekoga\n"
                "`!brak [@korisnik]` — Pogledaj bračni status\n"
                "`!raskid` — Razvedi se\n"
                "`!klupa @k` · `!grli @k` · `!udarac @k` · `!pljesak @k`\n"
                "`!hrani @k` · `!kafa [@k]` · `!pogled @k` · `!spavanje [@k]`"
            ),
            inline=False
        )
        e.add_field(
            name=f"🔤 Kaladont  (samo !)  → <#{CH_KALADONT}>",
            value=(
                "`!kaladont` — Pokreni igru (= start)\n"
                "`!kaladont stop` — Zaustavi igru\n"
                "`!kaladont status` — Pogledaj status\n"
                "`!kaladont pravila` — Pravila igre\n"
                "💬 Tokom igre piši direktno u chat!"
            ),
            inline=False
        )
        e.add_field(
            name="🎮 Fun  (! i /)",
            value=(
                "`!8ball [pitanje]` — Čarobna kugla\n"
                "`!coinflip` — Baci novčić\n"
                "`!poll \"pitanje\" [a] [b]` — Glasanje"
            ),
            inline=False
        )
        e.add_field(
            name="ℹ️ Info  (! i /)",
            value=(
                "`!userinfo [@korisnik]` — Info o korisniku\n"
                "`!serverinfo` — Info o serveru\n"
                "`!avatar [@korisnik]` — Avatar\n"
                "`!uloge` — Lista svih uloga"
            ),
            inline=False
        )
        await i.response.send_message(embed=e, ephemeral=True)
    except: pass

@bot.command(name="help")
async def p_help(ctx):
    e = emb(f"📖{SEP}Mrak Bot v3.3 — Pomoć", "")
    e.add_field(
        name="🛡️ Moderacija",
        value="`!ban` `!kick` `!timeout` `!untimeout` `!warn` `!warnings` `!clear`",
        inline=False
    )
    e.add_field(
        name="⚙️ Setup",
        value="`!setwelcome` `!setgoodbye` `!setlogs` `!antiraid` `!nsfw`",
        inline=False
    )
    e.add_field(
        name=f"🎣 Pecanje → <#{CH_PECANJE}>",
        value=(
            "`!pecanje` `!pecanjereka` `!pecanjejezero` `!pecanjemore`\n"
            "`!nivo` `!shop` `!kupistap` `!kupimamac`\n"
            "`!ulov` `!profil` `!prodaj` `!zadaci`\n"
            "`!akvarijum` `!dodajuakvarijum` `!nahrani` `!takmicenje`"
        ),
        inline=False
    )
    e.add_field(
        name=f"💍 Brak & Socijalno → <#{CH_BRAK}>",
        value=(
            "`!prosidba @k` `!brak` `!raskid`\n"
            "`!klupa` `!grli` `!udarac` `!pljesak`\n"
            "`!hrani` `!kafa` `!pogled` `!spavanje`"
        ),
        inline=False
    )
    e.add_field(
        name=f"🔤 Kaladont → <#{CH_KALADONT}>",
        value="`!kaladont` `!kaladont stop` `!kaladont status` `!kaladont pravila`",
        inline=False
    )
    e.add_field(
        name="🎮 Fun",
        value="`!8ball` `!coinflip` `!poll`",
        inline=False
    )
    e.add_field(
        name="ℹ️ Info",
        value="`!userinfo` `!serverinfo` `!avatar` `!uloge`",
        inline=False
    )
    await ctx.send(embed=e)

# ─────────────────────────────────────────────────────────────
#  ERROR HANDLERS
# ─────────────────────────────────────────────────────────────
@bot.listen("on_command_error")
async def on_command_error(ctx, error):
    # Unwrap invoke errors
    if isinstance(error, commands.CommandInvokeError):
        error = error.original

    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        try: await ctx.send(embed=err_emb("Nemaš dovoljno permisija za ovu komandu!"))
        except: pass
    elif isinstance(error, commands.MemberNotFound):
        try: await ctx.send(embed=err_emb("Korisnik nije pronađen!"))
        except: pass
    elif isinstance(error, commands.BadArgument):
        try: await ctx.send(embed=err_emb("Pogrešan argument! Provjeri komandu."))
        except: pass
    elif isinstance(error, commands.MissingRequiredArgument):
        try: await ctx.send(embed=err_emb(f"Nedostaje argument: `{error.param.name}`"))
        except: pass
    elif isinstance(error, discord.errors.Forbidden):
        try: await ctx.send(embed=err_emb("Bot nema permisiju za ovu akciju!"))
        except: pass
    elif isinstance(error, discord.errors.NotFound):
        pass  # Poruka/kanal obrisan — ignoriši
    else:
        # Loguj neočekivane greške ali NE gasi bota
        logging.error(f"[on_command_error] {ctx.command}: {error}\n{traceback.format_exc()}")

@bot.event
async def on_error(event, *args, **kwargs):
    """Globalni handler — sprječava crash bota."""
    logging.error(f"[on_error] event={event}\n{traceback.format_exc()}")

# ─────────────────────────────────────────────────────────────
#  KEEP-ALIVE  (sprječava Replit hibernaciju)
# ─────────────────────────────────────────────────────────────
async def _keepalive():
    """Minimalni HTTP server — Replit ga pinguje i ne gasi repl."""
    async def handle(request):
        return web.Response(text="🌙 MRAK BOT je online!", content_type="text/plain")

    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Probaj portove redom dok ne nađe slobodan
    for port in [5000, 5050, 5100, 5200, 5300]:
        try:
            site = web.TCPSite(runner, "0.0.0.0", port)
            await site.start()
            logging.info(f"[keep-alive] HTTP server pokrenut na portu {port}")
            return
        except OSError:
            continue
    logging.warning("[keep-alive] Nije moguće pokrenuti HTTP server — svi portovi zauzeti.")

# ─────────────────────────────────────────────────────────────
#  START
# ─────────────────────────────────────────────────────────────
if not TOKEN:
    print("❌ GREŠKA: DISCORD_BOT_TOKEN nije postavljen!")
    exit(1)

async def main():
    async with bot:
        await _keepalive()
        await bot.start(TOKEN, reconnect=True)

asyncio.run(main())
