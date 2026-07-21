import discord, random, asyncio, json, os, time, aiohttp, re
from itertools import combinations as _pk_comb
from collections import defaultdict, deque, Counter
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timezone, timedelta
import sys as _sys

# ═══ SQUAD Bot v3.0 — Custom Discord Emojis ════════════════════════════════════
E_GAME    = "<:icon_game:1519358323667767346>"
E_MUSIC   = "<:icon_music:1519358320337752125>"
E_COINS   = "<:icon_coins:1519358244827697424>"
E_TROPHY  = "<:icon_trophy:1519358248942047342>"
E_SHIELD  = "<:icon_shield:1519358252234707115>"
E_CHECK   = "<:icon_check:1519358376268533810>"
E_CROSS   = "<:icon_cross:1519358379917836508>"
E_WARN    = "<:icon_warning:1519358274284032030>"
E_STAR    = "<:e_star2:1519363084253266031>"
E_FIRE    = "<:icon_fire:1519358312188088466>"
E_LEVEL   = "<:icon_level:1519358485647720510>"
E_LOCK    = "<:icon_lock:1519358358010724352>"
E_CROWN   = "<:e_crown2:1519363047163166922>"
E_HEART   = "<:icon_heart:1519358309008674848>"
E_SWORD   = "<:icon_sword:1519358255925825667>"
E_DICE    = "<:icon_dice:1519358259171950724>"
E_BOLT    = "<:icon_lightning:1519358316327997612>"
E_BANK    = "<:icon_bank:1519358302285332540>"
E_GIFT    = "<:icon_gift:1519358266738737274>"
E_HUNT    = "<:icon_hunt:1519358331192344687>"
E_FISH    = "<:icon_fish:1519358327140651029>"
E_QUIZ    = "<:icon_quiz:1519358335068147836>"
E_GEO     = "<:icon_geo:1519358339748855808>"
E_HELP    = "<:icon_help:1519358364889383084>"
E_TIME    = "<:icon_time:1519358368773308457>"
E_PARTY   = "<:e_party:1519363028334674070>"
E_SKULL   = "<:e_skull:1519362992502997125>"
E_DEVIL   = "<:e_devil:1519362989470253187>"
BOT_PREFIX = "-"
# ═════════════════════════════════════════════════════════════════════════════

try: _sys.stdout.reconfigure(line_buffering=True)
except Exception: pass

# ═══════════════════════════════════════════
#           KONFIGURACIJA
# ═══════════════════════════════════════════
BOT_NAME = "SQUAD"
VERSION  = "v3.0"
TOKEN    = os.environ.get("DISCORD_TOKEN")
APP_ID   = 1451057022245146745  # Discord developer portal app ID

# ═══════════════════════════════════════════
#    <:e_lock3:1519362717394403432> LICENCA — Jedini originalni bot
# ═══════════════════════════════════════════
# Bot radi SAMO ako je član zvaničnog GIAN servera (GIAN).
# Ako je neko klonirao kod i pokrenuo svoju kopiju — bot napušta sve servere
# i gasi se automatski.
OFFICIAL_INVITE   = "gian"               # GIAN
OFFICIAL_GUILD_ID = 1494043955980140754  # ID zvaničnog GIAN servera

_LP = 0xB39DDB  # Svetlo ljubičasta — jedina boja svih embeda (nikad se ne mijenja)

COLORS = {
    "default": _LP, "success": _LP, "error":   _LP,
    "warning": _LP, "info":    _LP, "gold":    _LP,
    "balkan":  _LP, "purple":  _LP, "fun":     _LP,
    "dark":    _LP, "teal":    _LP, "love":    _LP,
    "pink":    _LP, "aqua":    _LP,
    # Igre — ista boja
    "mafia":   _LP,
    "amogus":  _LP,
    "slots":   _LP,
}

# ── Custom animirani emoji (već postoje na serveru) — za ljepši izgled igara ──
E_FIRE1 = "<:icon_fire:1519358312188088466>"
E_FIRE2 = "<:e_fire2:1519362671491678280>"
E_FIRE3 = "<:icon_fire:1519358312188088466>"
E_FIRE4 = "<:e_fire2:1519362671491678280>"
E_GAME  = "<:icon_game:1519358323667767346>"
E_MUSIC = "<:icon_music:1519358320337752125>"

# Akcentne boje po igri — sve svetlo ljubičasta (nikad se ne mijenja)
GAME_COLORS = {
    "kaladont": _LP,
    "wordle":   _LP,
    "kviz":     _LP,
    "geo":      _LP,
}
# ═══════════════════════════════════════════
#    PANEL API — Live embed integracija
# ═══════════════════════════════════════════
PANEL_API_URL = os.environ.get("PANEL_API_URL", "https://giann.uk")

async def get_panel_embed(name: str) -> dict | None:
    """Fetch embed data from GIAN panel API (fallback to hardcoded on error)."""
    try:
        async with aiohttp.ClientSession() as _s:
            async with _s.get(f"{PANEL_API_URL}/api/embeds/{name}",
                              timeout=aiohttp.ClientTimeout(total=3)) as _r:
                if _r.status == 200:
                    return await _r.json()
    except Exception as _pe:
        print(f"[panel-embed] Cannot fetch '{name}': {_pe}")
    return None

# ── Panel protection config (anti-raid + anti-nsfw settings) ─────────────────
_prot_cfg: dict = {}

# ── Games config (panel → bot) ───────────────────────────
_games_cfg: dict = {}

async def get_panel_games() -> dict:
    """Fetch games/economy settings from panel API. Falls back to defaults on error."""
    global _games_cfg
    try:
        async with aiohttp.ClientSession() as _s:
            async with _s.get(f"{PANEL_API_URL}/api/games",
                              timeout=aiohttp.ClientTimeout(total=3)) as _r:
                if _r.status == 200:
                    _games_cfg = await _r.json()
                    print(f"[panel-games] Config refreshed OK")
    except Exception as _ge:
        print(f"[panel-games] Fetch error (using last/defaults): {_ge}")
    return _games_cfg

def _g_eco(cmd: str) -> dict:
    """Vrati economy config za datu komandu."""
    defaults = {
        "posao": {"enabled": True, "cooldown_min": 30,  "reward_min": 150, "reward_max": 600},
        "daily": {"enabled": True, "cooldown_hours": 24, "reward_min": 300, "reward_max": 800},
        "kradi": {"enabled": True, "cooldown_hours": 2,  "success_rate": 38, "steal_min": 50, "steal_max": 300},
    }
    eco = _games_cfg.get("economy", {})
    return {**defaults.get(cmd, {}), **eco.get(cmd, {})}

def _g_gamble(cmd: str) -> dict:
    """Vrati gambling config za datu komandu."""
    defaults = {
        "slots":     {"enabled": True, "cooldown_sec": 15, "max_bet": 1_000_000_000},
        "blackjack": {"enabled": True, "cooldown_sec": 30},
        "poker":     {"enabled": True, "min_bet": 50,  "max_bet": 50_000},
        "kviz":      {"enabled": True, "min_bet": 10},
        "geografija":{"enabled": True, "min_bet": 10},
        "kpm":       {"enabled": True},
        "vjasala":   {"enabled": True},
        "kaladont":  {"enabled": True, "reward": 1500},
        "wordle":    {"enabled": True, "reward": 1200},
        "toplo_hladno":{"enabled": True},
        "amogus":    {"enabled": True},
    }
    gam = _games_cfg.get("gambling", {})
    return {**defaults.get(cmd, {}), **gam.get(cmd, {})}

def _g_social() -> bool:
    return _games_cfg.get("social", {}).get("enabled", True)

def _g_hunt() -> dict:
    defaults = {"enabled": True, "cooldown_sec": 7}
    return {**defaults, **_games_cfg.get("animals", {}).get("hunt", {})}

async def _games_refresh_loop():
    """Osvježava games config svakih 5 minuta."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(300)
        await get_panel_games()

# ── Protection config (panel → bot) ──────────────────────
async def get_panel_protection() -> dict:
    """Fetch protection settings from panel API. Falls back to defaults on error."""
    global _prot_cfg
    try:
        async with aiohttp.ClientSession() as _s:
            async with _s.get(f"{PANEL_API_URL}/api/protection",
                              timeout=aiohttp.ClientTimeout(total=3)) as _r:
                if _r.status == 200:
                    _prot_cfg = await _r.json()
                    print(f"[panel-protection] Config refreshed — antiRaid={_prot_cfg.get('antiRaid',{}).get('enabled')}, antiNsfw={_prot_cfg.get('antiNsfw',{}).get('enabled')}")
    except Exception as _pe:
        print(f"[panel-protection] Fetch error (using last/defaults): {_pe}")
    return _prot_cfg

def _prot_raid() -> dict:
    ar = _prot_cfg.get("antiRaid", {})
    return {
        "enabled":      ar.get("enabled", True),
        "window":       ar.get("windowSeconds", 30),
        "limit":        ar.get("joinLimit", 5),
        "age_days":     ar.get("suspiciousAgeDays", 7),
        "lockdown_min": ar.get("lockdownMinutes", 5),
        "action":       ar.get("action", "kick"),
    }

def _prot_nsfw() -> dict:
    an = _prot_cfg.get("antiNsfw", {})
    return {
        "enabled":       an.get("enabled", True),
        "strikes":       an.get("strikesBeforeTimeout", 3),
        "timeout_min":   an.get("timeoutMinutes", 60),
        "extra_sites":   [s.lower() for s in an.get("extraBlockedSites", [])],
        "extra_keywords": [k.lower() for k in an.get("extraBlockedKeywords", [])],
    }

async def _protection_refresh_loop():
    """Osvježava protection config svakih 5 minuta."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        await get_panel_protection()
        await asyncio.sleep(300)

def _ev(text: str, member, count: int) -> str:
    """Replace panel template variables in embed text."""
    if not text: return text
    return (text
        .replace("{user}", member.mention)
        .replace("{memberCount}", str(count))
        .replace("{user.name}", member.display_name)
        .replace("{server}", member.guild.name if member.guild else "")
    )



JOBS = [
    "Radio si kao konobar <:e_coffee:1519362856884371526>", "Čuvao si baku <:e_grandma:1519362798189150370>", "Prodavao ćevape <:e_wrap:1519363373748195502>",
    "Vozio si taksi <:e_taxi:1519363380513603615>", "Radio si na građevini <:e_construct:1519363385328799826>️", "Popravljao auta <:e_wrench:1519362745772802078>",
    "Čuvao parking <:e_car:1519362749598269510>", "Nosio poštu <:e_mail:1519362754732097546>", "Prodavao lubenicu <:e_wrap:1519363373748195502>",
    "Brao paprike u polju <:e_flask:1519363469013422181>️", "Radio u pekari <:e_bread:1519363376969420930>", "Čuvao ovce <:e_sheep:1519363388789227611>",
    "Prodavao karte na stanici <:e_bus:1519363391939018857>", "Radio kao zaštitar <:e_muscle:1519362764244652122>", "Prao automobile <:e_shower:1519363395239804998>",
]

EIGHTBALL_REPLIES = [
    "<:e_green:1519362769047126028> Definitivno da!", "<:e_green:1519362769047126028> Sve znakovi govore — DA.",
    "<:e_green:1519362769047126028> Bez ikakve sumnje, majstore!", "<:e_green:1519362769047126028> Računaj na to, brate.",
    "<:e_green:1519362769047126028> Pitaj ponovo malo kasnije.", "<:e_green:1519362769047126028> Nisam baš siguran, brate.",
    "<:e_green:1519362769047126028> Teško reći u ovom trenutku.", "<:e_green:1519362769047126028> Magla mi zaklanja odgovor.",
    "<:e_red:1519362782192210041> Ne računaj na to.", "<:e_red:1519362782192210041> Odgovor je jasno — NE.",
    "<:e_red:1519362782192210041> Izgledi su jako loši.", "<:e_red:1519362782192210041> Zaboravi na to, majstore.",
]

# ═══════════════════════════════════════════
#    MEMOVI (veliki bazen sa rotacijom)
# ═══════════════════════════════════════════
MEMES = [
    "Kad kažeš 'samo još 5 minuta' a prođe 3 sata. <:e_sleep:1519362785291669644><:e_phone:1519362788462559323>",
    "Baka: 'Jesi li jeo?' Ti: 'Jesam.' Baka: 'A jesi li gladan?' <:e_plate:1519362791591378975>️<:e_grandma:1519362798189150370>",
    "Kad upališ klimu na 16°C a napolju je 40°C. <:e_snow:1519362801703977110>️<:e_fire2:1519362671491678280>",
    "Turbofolk u 3 ujutru, sutra na posao u 7. <:e_music2:1519362679310127114><:e_dizzy:1519362812554510509>",
    "Kad kažeš 'idemo na kafu' a završiš na roštilju do zore. <:e_plate:1519362791591378975><:e_coffee:1519362856884371526>",
    "Svaki Balkanac ima ujaka koji sve zna popraviti. <:e_wrench:1519362745772802078><:e_sparkles:1519363032185176198>",
    "'Sačekaj 5 minuta' — Balkan vreme: 45 minuta minimum. <:e_time2:1519362726952964227><:e_pray:1519363406078021863>",
    "Kad pitaš baku za recept: 'Malo ovog, malo onog, dok ne bude dobro.' <:e_measure:1519363626006351975><:e_grandma:1519362798189150370>",
    "Kad kaže 'idem odmah' a gleda TV već sat vremena. <:e_tv:1519362825670230097><:e_couch:1519362828484477012>️",
    "Ništa me ne boli više nego kad mi telefon padne na lice u krevetu. <:e_phone:1519362788462559323><:e_dizzy:1519362812554510509>",
    "Balkan dijetа: ne jedeš između obroka. Obroci su svaki sat. <:e_fork:1519362833668772000><:e_time2:1519362726952964227>️",
    "Komšija u 11 noću: buši zidove. Normalnost. <:e_hammer:1519362836671762494><:e_house:1519362841369378961>",
    "Kad mama kaže 'pričekaj dok dođemo kući' — Bog te čuvaj. <:e_dizzy:1519362812554510509><:e_house:1519362841369378961>",
    "'Idemo samo na malo' — 6 sati kasnije. <:e_sparkles:1519363032185176198><:e_time2:1519362726952964227>",
    "Kad vidiš stranca u selu svi izlaze da gledaju. <:e_eyes:1519362845970530577><:e_house:1519362841369378961>",
    "Balkan autopilot: čim sjedneš — telefon u ruci. <:e_phone:1519362788462559323><:e_brain:1519362849548406975>",
    "Svaka baka misli da je njeno dijete premršavo. Vaga se ne slaže. <:e_scales:1519362852853649439>️<:e_grandma:1519362798189150370>",
    "Na Balkanu se ne kaže 'hvala' u kafani. Prstom se kuca po stolu. <:e_user:1519363093736718518><:e_coffee:1519362856884371526>",
    "Kad kažeš da si sit a vidiš čevape. <:e_wrap:1519363373748195502><:e_muscle:1519362764244652122>",
    "Balkanska logika: ne možeš biti bolestan ljeti, samo zimi. <:e_sun:1519362860218843399>️<:e_snow:1519362801703977110>",
    "Baka čuva svaku vrećicu od kupovine već 30 godina. <:e_cart:1519362665347153930>️<:e_recycle:1519362875129335849>️",
    "Kad ti kaže 'nisam ljuta' — bježi. <:e_dizzy:1519362812554510509><:e_wind:1519362878300229883>",
    "Balkanska dijalektika: svaka rasprava završi pričom o ratu. <:e_sword2:1519362631146930317>️<:e_speaker:1519363314524881048>️",
    "Pranje auta = kiša za 2 sata garantovana. <:e_car:1519362749598269510><:e_rain:1519362881756336168>️",
    "Kada slušaš muziku na slušalicama a mama govori s tobom. <:e_headphones:1519363484377284770><:e_muscle:1519362764244652122>",
    "Spavanje na plaži sa šeširom na licu. Balkanski ljetni odmor. <:e_palm:1519363442597695600>️<:e_sun:1519362860218843399>",
    "Na Balkanu svadbena muzika mora biti glasnija od aviona. <:e_rocket2:1519363332266524813>️<:e_music2:1519362679310127114>",
    "'Ajde brzo' — 20 minuta čekanja. <:e_run:1519362884868636883><:e_time2:1519362726952964227>",
    "Kad dobiješ viber poruku od mame u 2 noću: 'Jesi li stigao?' <:e_phone:1519362788462559323><:e_dizzy:1519362812554510509>",
    "Piknik bez kajmaka — nije piknik. <:e_plate:1519362791591378975><:e_herb:1519363706243387573>",
    "Svaki kvar na autu Balkanac može dijagnosticirati zvukom. <:e_car:1519362749598269510><:e_ear:1519362891210424473>",
    "Kad ti komšija javi vijest koja nije tvoja stvar. <:e_clipboard:1519363052871614627><:e_eye:1519362936777478326>",
    "Ljeto = hvatanje klime ispod jorgana. <:e_bed:1519363663654293665>️<:e_snow:1519362801703977110>️",
    "Balkan parking: dvije linije? Staju četiri auta. <:e_car:1519362749598269510><:e_sparkles:1519363032185176198>",
    "Fritula je rješenje za sve životne probleme. <:e_plate:1519362791591378975><:e_heart2:1519362668644012133>",
    "Kad dođe familija iznenada a kuća nije čista. <:e_skull:1519362992502997125><:e_broom:1519362900681298000>",
    "Svako putovanje počinje sa 'imaš li pare za autoput?'. <:e_taxi:1519363380513603615>️<:e_coins3:1519362621206298666>",
    "Baka na kafi: zna sve o svima u gradu. <:e_grandma:1519362798189150370><:e_coffee:1519362856884371526><:e_clipboard:1519363052871614627>",
    "Balkanska statistika: 9 od 10 problema se rješava uz kafu. <:e_coffee:1519362856884371526><:e_chart:1519362656568475880>",
    "'Otišao sam samo po hleb' — vratio se sa pola marketa. <:e_cart:1519362665347153930><:e_dizzy:1519362812554510509>",
    "Kad igraš fudbal na ulici i lopta ode kod ljutog komšije. <:e_soccer:1519363521140359410><:e_dizzy:1519362812554510509>",
    "Svaki razgovor na Balkanu počne sa: 'Brate, slušaj ovo...' <:e_speaker:1519363314524881048>️<:e_ear:1519362891210424473>",
    "Dnevna soba samo za goste. Gosti nikad ne dolaze. <:e_couch:1519362828484477012>️<:e_lock3:1519362717394403432>",
    "Šalter na pošti: radi jedan, čekaju trideset. <:e_internet:1519363106395000994><:e_user:1519363093736718518>",
    "Kad se probudi baka u 5 ujutru i odmah počne pjevati. <:e_sunrise:1519362915801501767><:e_music2:1519362679310127114><:e_grandma:1519362798189150370>",
    "Balkanski sat: 'Dođi u 7' znači dođi u 8:30. <:e_time2:1519362726952964227><:e_sparkles:1519363032185176198>",
    "Svaka kuća ima baku koja čuva bombone od 1998. <:e_sparkles:1519363032185176198><:e_grandma:1519362798189150370>",
    "Na Balkanu, ako ne jedeš treću porciju, nisi počašćen. <:e_plate:1519362791591378975>️<:e_dizzy:1519362812554510509>",
    "Kad završiš posao i nema struje za punjač. <:e_battery:1519363589897588868><:e_dizzy:1519362812554510509>",
    "Balkanac na moru: čeka red u restoranu, naruči duplo, pojede četvoro. <:e_fork:1519362833668772000><:e_dolphin:1519363432615510078>",
    "Usred filma: 'Koliko još traje?' — Baš na napetom dijelu. <:e_camera:1519363493701091348><:e_muscle:1519362764244652122>",
    "Kad kaže 'jesi li gladan?' a hrana je već na stolu. <:e_plate:1519362791591378975><:e_run:1519362884868636883>",
    "Svaka balkanska mama je doktor, kuhar i psiholog u jednom. <:e_woman:1519362926622806046>‍<:e_doctor:1519363600047673415>️<:e_woman:1519362926622806046>‍<:e_plate:1519362791591378975><:e_brain:1519362849548406975>",
    "Kad ideš kod zubara a zub prestane boljeti čim sjedneš u čekaonicu. <:e_doctor:1519363600047673415><:e_muscle:1519362764244652122>",
    "Balkan net: radi samo kad ne trebaš. <:e_signal:1519362931689525422><:e_refresh:1519362959187509461>",
    "Djeca na Balkanu idu van da se igraju — mama zna sve što su radila. <:e_run:1519362884868636883><:e_eye:1519362936777478326>️",
    "Kad vidiš kišu a majka te pita jesi li ponio kapu. <:e_rain:1519362881756336168>️<:e_sun:1519362860218843399>",
    "Jedina stvar brža od vijesti na Balkanu — trač. <:e_ear:1519362891210424473><:e_bolt:1519362674717102160>",
    "Svaki rodjak želi znati kada se ženiš. Svake godine. <:e_ring:1519362941617438750><:e_cry:1519362944717160530>",
    "Na ljetovanju: sunce, more i debata gdje ćemo ručati 2 sata. <:e_sun:1519362860218843399><:e_plate:1519362791591378975>️",
    "Balkanac u inostranstvu: pronađe Balkanca u roku 10 minuta. <:e_globe2:1519362694887637004><:e_shake:1519362947766554737>",
    "Kad čistiš sobu a mama kaže 'baciš li to, ubijam te'. <:e_trash:1519362951247691898>️<:e_dizzy:1519362812554510509>",
    "Fijaker sa konjima sporiji od balkanskog interneta. <:e_taxi:1519363380513603615><:e_signal:1519362931689525422>",
    "Svaka baka krije novac u džepu kecelje. <:e_moneywing:1519362955437805771><:e_grandma:1519362798189150370>",
    "Domaći sok od šljive — lijek za sve. <:e_plate:1519362791591378975><:e_pill:1519363593366147255>",
    "Balkan dijalog: 'Jesi jeo?' 'Jesam.' 'Jedi još.' <:e_plate:1519362791591378975>️<:e_refresh:1519362959187509461>",
    "Kad nema struje — svi izađu napolje i postanu filozofi. <:e_idea:1519363006599794799>️<:e_brain:1519362849548406975>",
    "Majka ne razumije 'meni ništa ne treba za rodjendan'. <:e_gift:1519362618341462067><:e_woman:1519362926622806046>‍<:e_boy:1519362962530373742>",
    "Na Balkanu kafu piješ u svakoj kući čak i ako si 'samo svrnuo'. <:e_coffee:1519362856884371526><:e_house:1519362841369378961>",
    "Djeca na Balkanu nemaju 'slobodnog vremena' — ima posla uvijek. <:e_broom:1519362900681298000><:e_time2:1519362726952964227>",
    "Balkan parking 2: dvostruki parking je tradicija, ne greška. <:e_car:1519362749598269510><:e_car:1519362749598269510>",
    "Svako selo ima svog vračara i svi tvrde da ne vjeruju. <:e_crystal:1519362965558657146><:e_crystal:1519362965558657146>",
    "Kad mama pita 'gdje si bio?' a ti bio u WC-u. <:e_shower:1519363395239804998><:e_muscle:1519362764244652122>",
    "Balkan zimovanje: pečenje kestena i debata o politici. <:e_herb:1519363706243387573><:icon_stats:1519358289173807246>️",
    "Sendvič koji je spakovao ko znaš uvijek je bolji. <:e_wrap:1519363373748195502><:e_heart2:1519362668644012133>️",
    "Svaki kafić ima isti TV kanal i uvijek su vijesti. <:e_tv:1519362825670230097><:e_coffee:1519362856884371526>",
    "Balkanski wifi lozinka: nešto poput 'qwerty1234'. <:e_signal:1519362931689525422><:e_sparkles:1519363032185176198>",
    "Kad igraš tablić i gledaš protivnikove karte u odrazu prozora. <:e_cards2:1519362702835712010><:e_eye:1519362936777478326>️",
    "Balkan letovanje: čekaš godinu dana, provedeš 7 dana, žališ se pola godine. <:e_dolphin:1519363432615510078><:e_muscle:1519362764244652122>",
    "Svaka balkanska mama reciklira plastične flaše u vazi. <:e_flower:1519362984818901173><:e_recycle:1519362875129335849>️",
    "Kad rjeknete 'ajde' a niko se ne miče. <:e_run:1519362884868636883><:e_castle:1519363568645177457>",
    "Balkan shopping: ideš po jedno, vratiš se sa svime osim tog jednog. <:e_cart:1519362665347153930>️<:e_dizzy:1519362812554510509>",
]

MEME_STATE: dict = {}  # guild_id -> shuffled list of remaining indices

def get_next_meme(guild_id: int) -> str:
    key = str(guild_id)
    if key not in MEME_STATE or not MEME_STATE[key]:
        idxs = list(range(len(MEMES)))
        random.shuffle(idxs)
        MEME_STATE[key] = idxs
    return MEMES[MEME_STATE[key].pop()]

# ═══════════════════════════════════════════
#    VJEŠALA — rječnik
# ═══════════════════════════════════════════
VJASALA_RJECNIK = [
    "RAKIJA","CEVAPI","BALKON","KAFANA","MARKET","TRAKTOR","KOMSIJA","BONTON",
    "FUDBAL","PAPRIKA","BUREK","KAJMAK","SARMA","KIFLA","PEKARA","BAKLAVA",
    "KOMPJUTER","INTERNET","MOBITEL","PUNJAC","SLUSALICE","TASTATURA","MIŠKA",
    "PLANINA","JEZERO","RIJEKA","SUMSKA","LIVADA","VRELO","KLISURA","BRDOVIT",
    "LIJENOST","MUDROST","HRABROST","ZIVAHNA","BRZINA","TOPLINA","VESELJE",
    "BAKA","DJED","STRIC","UJNA","BRAT","SESTRA","MAJKA","OTAC","DIJETE",
    "KREVET","STOLICA","ORMAR","ZAVJESA","TEPIH","OGLEDALO","PROZOR","VRATA",
    "KOKOSOVO","JAGODA","MALINA","BOROVNICA","SMOKVA","SLJIVA","TRESNJA",
    "AUTOMOBIL","MOTOCIKL","BICIKL","AVION","BROD","VAGON","TRAMVAJ","METRO",
    "GITARA","VIOLINA","BUBNJEVI","FLAUTA","KLAVIR","HARMONIKA","SAKSOFON",
    "POLICAJAC","VATROGASAC","LJEKAR","UCITELJ","NOVINAR","ARHITEKT","INZENJER",
    "SUNCOKREO","RUZA","LAVANDA","KAKTUS","TULIPAN","JORGOVANA","MASLACAK",
    "OBLAK","MUNJA","GROM","SNIJEG","ROSA","MAGLA","VJETAR","OLUJA","DUGA",
    "LEPTIR","PCELICA","BUBAMARA","VJEVERICA","JELEN","LISICA","MEDVJED","VUK",
    "TORTA","KOLAC","KROFNA","PALACINKA","WAFFLE","BROWNIE","TIRAMISU","MACARON",
    "KUHINJA","KUPATILO","HODNIK","PODRUM","TAVAN","GARAZ","BALKON","TERASA",
    "SLOBODA","JEDNAKOST","LJUBAV","NADA","VJERA","SREĆA","ISTINA","PRAVDA",
    "GIMNASTIKA","PLIVANJE","ATLETIKA","KOSARKA","ODBOJKA","TENIS","SAHI","BOKS",
    "JANUAR","FEBRUAR","OKTOBAR","NOVEMBAR","DECEMBAR","SUBOTA","NEDJELJA",
    "DUGACAK","KRATAK","VISOK","NIZAK","DEBEO","MRSAV","BRZO","POLAKO","GLASNO",
]

VJASALA_FAZE = [
    "```\n  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========```",
    "```\n  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n=========```",
]

# ═══════════════════════════════════════════
#    KALADONT — RJEČNIK VALIDNIH RIJEČI (BHS)
#    Velika baza: imenice, glagoli, pridjevi, pojmovi.
#    Sve riječi u UPPERCASE bez dijakritika dvojnih (Š→S, Č→C, Ž→Z, Đ→DJ, Ć→C)
#    NORMALIZACIJA: korisničku riječ prebacujemo u UPPERCASE i mapiramo dijakritike.
# ═══════════════════════════════════════════
def _kaladont_normalize(w: str) -> str:
    """Normalizuj riječ: uppercase + skidanje dijakritika (Š→S, Č→C, Ž→Z, Đ→DJ, Ć→C)."""
    w = (w or "").upper().strip()
    repl = {"Š":"S","Č":"C","Ž":"Z","Đ":"DJ","Ć":"C","Ä":"A","Ö":"O","Ü":"U","Ñ":"N"}
    out = []
    for ch in w:
        out.append(repl.get(ch, ch))
    return "".join(out)

KALADONT_DICT = set([
    # === Hrana, piće, kuhinja ===
    "RAKIJA","CEVAPI","BUREK","KAJMAK","SARMA","KIFLA","PEKARA","BAKLAVA","PALACINKA",
    "TORTA","KOLAC","KROFNA","SLADOLED","KESTEN","ORAH","BADEM","LJESNJAK","KIKIRIKI",
    "JAGODA","MALINA","BOROVNICA","SMOKVA","SLJIVA","TRESNJA","JABUKA","KRUSKA","BANANA",
    "LIMUN","NARANCA","GROZDJE","LUBENICA","DINJA","BRESKVA","KAJSIJA","ANANAS","KIVI",
    "KRASTAVAC","PARADAJZ","KROMPIR","LUK","BIJELILUK","PAPRIKA","TIKVA","SPINAT","SALATA",
    "KARFIOL","BROKULA","KUPUS","REPA","ROTKVA","KELERABA","CESNJAK","GRAH","MAHUNE",
    "PASULJ","RIZA","TJESTENINA","HLEB","KRUH","LEPINJA","SOMUN","POGACA","PROJA",
    "KUKURUZ","PSENICA","JECAM","ZOB","RAZ","BRASNO","SECER","SOL","BIBER","VANILA",
    "CIMET","KAFA","CAJ","MLIJEKO","JOGURT","SIR","MASLAC","JAJE","MEDU","MED",
    "VINO","PIVO","SOK","VODA","LIMUNADA","KAKAO","COKOLADA","BOMBONA","DZEM","MARMELADA",
    "KOBASICA","SUNKA","SLANINA","BIFTEK","ROSTILJ","RIBA","TUNJEVINA","SARDINE","SKAMPI",
    "JUHA","COPRA","SUPA","CORBA","GULAS","PILAV","RIZOTO","LAZANJE","PIZZA","PASTA",
    # === Životinje ===
    "MACKA","PAS","KONJ","KRAVA","OVCA","KOZA","SVINJA","KOKOSKA","PETAO","PILE",
    "PATKA","GUSKA","CURKA","PURAN","ZEC","KUNIC","STAKOR","MIS","HRCAK","JEZ",
    "VJEVERICA","JELEN","SRNA","LISICA","VUK","MEDVJED","RIS","DABAR","JAZAVAC","TVOR",
    "LASICA","KUNA","NERC","TIGAR","LAV","LEOPARD","GEPARD","PANTER","PUMA","JAGUAR",
    "SLON","NOSOROG","NILSKI","ZIRAFA","ZEBRA","KAMILA","LAMA","ALPAKA","BIVOL","BIK",
    "MAJMUN","GORILA","SIMPANZA","ORANGUTAN","KENGUR","KOALA","PANDA","DELFIN","KIT",
    "MORSKIPAS","LOSOS","PASTRMKA","KARP","SARAN","SOM","STUKA","HARINGA","BAKALAR",
    "ORAO","SOKO","JASTREB","SOVA","GAVRAN","VRANA","SVRAKA","GOLUB","VRABAC","LASTAVICA",
    "PJEVAC","KOLIBRI","PINGVIN","NOJ","FLAMINGO","KOKOS","PAUN","TUKAN","PAPIGA",
    "ZMIJA","GUSTER","KORNJACA","KROKODIL","ALIGATOR","ZABA","PUNOGLAVAC","SALAMANDER",
    "PCELA","OSA","STRSLJEN","MRAV","BUBA","BUBAMARA","LEPTIR","MOLJAC","MUHA","KOMARAC",
    "PAUK","SKORPION","RAK","ROKER","OKTOPOD","LIGNJA","MEDUZA","KORAL","SKOLJKA","PUZ",
    # === Priroda ===
    "PLANINA","JEZERO","RIJEKA","POTOK","IZVOR","VRELO","KLISURA","KANJON","DOLINA",
    "POLJE","LIVADA","SUMA","SUMICA","GAJ","PARK","BAZEN","MORE","OCEAN","VAL",
    "PIJESAK","SLJUNAK","KAMEN","STIJENA","BRDO","HUM","POLUOTOK","OTOK","ATOL","UVALA",
    "OBALA","PLAZA","LAGUNA","MOCVARA","PUSTINJA","TUNDRA","GLECER","VULKAN","GEJZIR",
    "CVIJET","RUZA","TULIPAN","LJILJAN","KARANFIL","BOZUR","JORGOVAN","LAVANDA","KAKTUS",
    "MASLACAK","NEVEN","SUNCOKRET","PERUNIKA","VISIBABA","KAMILICA","METVICA","MAJCINA",
    "STABLO","DRVO","HRAST","BUKVA","JAVOR","BREZA","TOPOLA","JELA","BOR","SMRECA",
    "MASLINA","LIPA","KESTEN","BAGREM","PALMA","BAMBUS","PAPRAT","MAHOVINA","TRAVA",
    "SUNCE","MJESEC","ZVIJEZDA","PLANETA","KOMETA","METEOR","NEBO","OBLAK","KISA",
    "SNIJEG","LED","MAGLA","ROSA","INJE","MUNJA","GROM","OLUJA","DUGA","VJETAR",
    "PROLJECE","LJETO","JESEN","ZIMA","JUTRO","PODNE","VECE","NOC","PONOC","ZORA",
    # === Tijelo, ljudi ===
    "GLAVA","KOSA","CELO","OKO","NOS","USTA","JEZIK","ZUB","USNA","UHO",
    "VRAT","RAME","RUKA","SAKA","PRST","NOKAT","LAKAT","LEDJA","GRUDI","TRBUH",
    "NOGA","BUTINA","KOLJENO","STOPALO","PETA","KUK","KICMA","REBRO","SRCE","PLUCA",
    "ZELUDAC","JETRA","BUBREG","CRIJEVO","MOZAK","KOST","KOZA","KRV","ZIVAC","MISIC",
    "BAKA","DJED","STRIC","UJAK","TETKA","UJNA","BRAT","SESTRA","MAJKA","OTAC",
    "DIJETE","SIN","KCERKA","ROD","FAMILIJA","KOMSIJA","PRIJATELJ","DRUGAR","KOLEGA",
    "DJEVOJKA","MOMAK","ZENA","COVJEK","STARAC","BABA","BEBA","KLINAC","DJEVOJCICA","DJECAK",
    # === Profesije ===
    "POLICAJAC","VATROGASAC","LJEKAR","DOKTOR","UCITELJ","PROFESOR","NOVINAR","ARHITEKT",
    "INZENJER","PROGRAMER","PISAC","PJESNIK","SLIKAR","KIPAR","MUZICAR","GLUMAC","REZISER",
    "PJEVAC","PLESAC","FOTOGRAF","KUVAR","KONOBAR","PEKAR","MESAR","KROJAC","FRIZER",
    "ZUBAR","VETERINAR","FARMER","RIBAR","LOVAC","MORNAR","PILOT","VOZAC","SOFER","STUDENT",
    "GLUMICA","SUDIJA","ADVOKAT","TUZILAC","NOTAR","BANKAR","TRGOVAC","PRODAVAC","KASIRKA",
    # === Kuća, predmeti ===
    "KUHINJA","KUPATILO","HODNIK","PODRUM","TAVAN","GARAZA","BALKON","TERASA","DVORISTE",
    "VRATA","PROZOR","KROV","ZID","POD","STROP","STEPENICE","LIFT","HODNJAK","SOBA",
    "KREVET","STOLICA","STOL","ORMAR","KOMODA","FOTELJA","KAUC","ZAVJESA","TEPIH","SAG",
    "OGLEDALO","SLIKA","UKRAS","VAZA","SVIJECA","LAMPA","LUSTER","SAT","BUDILNIK","KALENDAR",
    "PEC","STEDNJAK","RERNA","FRIZIDER","ZAMRZIVAC","PERILICA","SUSILICA","TOSTER","BLENDER",
    "TANJUR","SOLJA","CASA","BOCA","TAVA","LONAC","NOZ","VILJUSKA","KASIKA","ZLICA",
    "TORBA","RANAC","KOFER","NOVCANIK","NAOCALE","KISOBRAN","KAPA","SAL","RUKAVICE","CARAPE",
    "MAJICA","KOSULJA","SAKO","JAKNA","KAPUT","HLACE","TRENERKA","SUKNJA","HALJINA","CIPELE",
    "PATIKE","CIZME","SANDALE","PAPUCE","KORZET","KAIS","KRAVATA","PIDZAMA","KUPACI","BIKINI",
    # === Tehnika ===
    "KOMPJUTER","RACUNAR","LAPTOP","TABLET","MOBITEL","TELEFON","INTERNET","WIFI","KABL","MODEM",
    "PUNJAC","BATERIJA","SLUSALICE","TASTATURA","MIS","KAMERA","FOTOAPARAT","TELEVIZOR","RADIO",
    "ZVUCNIK","MIKROFON","KONZOLA","DZOJSTIK","DRON","ROBOT","SERVER","DISPLEJ","EKRAN","MONITOR",
    # === Vozila ===
    "AUTOMOBIL","AUTO","KAMION","MOTOCIKL","BICIKL","ROMOBIL","SKUTER","TRAKTOR","BAGER","KOMBI",
    "AUTOBUS","TRAMVAJ","TROLEJBUS","METRO","VOZ","VLAK","BRZIVOZ","BROD","JAHTA","JEDRILICA",
    "CAMAC","KAJAK","KANU","SPLAV","PODMORNICA","AVION","HELIKOPTER","RAKETA","BALON","ZEPELIN",
    # === Geografija ===
    "DRZAVA","REPUBLIKA","GRAD","SELO","NASELJE","ULICA","TRG","PARK","MOST","TUNEL",
    "AUTOPUT","CESTA","PUT","STAZA","ZELJEZNICA","ASTANA","BEOGRAD","SARAJEVO","ZAGREB",
    "MOSTAR","SPLIT","RIJEKA","ZADAR","DUBROVNIK","PULA","NIS","SUBOTICA","TIRANA","SKOPLJE",
    "BANJALUKA","TUZLA","ZENICA","BIHAC","TREBINJE","JAJCE","BUGOJNO","TRAVNIK","KISELJAK","BREZA",
    "FRANCUSKA","NJEMACKA","ITALIJA","SPANIJA","ENGLESKA","RUSIJA","KINA","JAPAN","INDIJA","BRAZIL",
    "AMERIKA","MEKSIKO","KANADA","TURSKA","GRCKA","BUGARSKA","RUMUNIJA","MADJARSKA","POLJSKA","CESKA",
    "EUROPA","AZIJA","AFRIKA","AUSTRALIJA","ANTARKTIK","BALKAN","SREDOZEMLJE","JADRAN","DANUBIJ",
    # === Sport ===
    "FUDBAL","NOGOMET","KOSARKA","ODBOJKA","RUKOMET","TENIS","STOLNI","BOKS","KARATE","DZUDO",
    "HOKEJ","RAGBI","BEJZBOL","KRIKET","PLIVANJE","RONJENJE","JEDRENJE","VESLANJE","SKIJANJE",
    "SNOWBOARD","KLIZANJE","BICIKLIZAM","GIMNASTIKA","ATLETIKA","TRCANJE","SAH","DAMA","BILIJAR",
    "PIKADO","KUGLANJE","GOLF","JAHANJE","STRIJELJASTVO","PIANISTIKA","JOGGING","FITNESS",
    # === Muzika, umjetnost ===
    "GITARA","VIOLINA","BUBNJEVI","FLAUTA","KLAVIR","HARMONIKA","SAKSOFON","TRUBA","SAZ",
    "TAMBURA","MANDOLINA","UKULELE","KSILOFON","ORGULJE","SINTISAJZER","KLARINET","OBOJA",
    "FAGOT","CELO","KONTRABAS","HARFA","NOTA","PJESMA","STIH","AKORD","RIFF","RITAM","MELODIJA",
    "ROCK","POP","JAZZ","BLUES","FOLK","TURBOFOLK","NARODNJACI","RAP","HIPHOP","REGGAE","TECHNO",
    "OPERA","BALET","KAZALISTE","POZORISTE","KONCERT","FESTIVAL","SCENA","BINA","MIKROFON",
    # === Apstraktno, osjećanja ===
    "SLOBODA","JEDNAKOST","LJUBAV","NADA","VJERA","SRECA","TUGA","RADOST","STRAH","BIJES",
    "LJUTNJA","MIR","RAT","BORBA","POBJEDA","PORAZ","PRIJATELJSTVO","NEPRIJATELJ","ISTINA",
    "LAZ","PRAVDA","NEPRAVDA","HRABROST","KUKAVICA","MUDROST","GLUPOST","ZNANJE","UMIJECE",
    "TALENT","DAR","SUDBINA","SREĆA","PROBLEM","RJESENJE","ODGOVOR","PITANJE","IDEJA","PLAN",
    "SAN","SNOVI","MASTA","REALNOST","ZIVOT","SMRT","RODJENJE","PROSLOST","BUDUCNOST","SADASNJOST",
    # === Vrijeme ===
    "JANUAR","FEBRUAR","MART","APRIL","MAJ","JUNI","JULI","AVGUST","SEPTEMBAR","OKTOBAR",
    "NOVEMBAR","DECEMBAR","PONEDJELJAK","UTORAK","SRIJEDA","CETVRTAK","PETAK","SUBOTA","NEDJELJA",
    "DAN","SEDMICA","MJESEC","GODINA","DECENIJA","STOLJECE","MILENIJ","SAT","MINUTA","SEKUNDA",
    # === Boje ===
    "CRVENA","ZUTA","ZELENA","PLAVA","BIJELA","CRNA","SIVA","ROZE","NARANCASTA","LJUBICASTA",
    "BRAON","BORDO","BEZ","ZLATNA","SREBRNA","TIRKIZNA","TURKIZ","KAKI","INDIGO","KORALNA",
    # === Pridjevi (osnovni oblik) ===
    "DUGACAK","KRATAK","VISOK","NIZAK","DEBEO","MRSAV","BRZ","SPOR","JAK","SLAB",
    "TVRD","MEK","TOPAO","HLADAN","VRUC","LEDEN","SVIJETAO","TAMAN","PUN","PRAZAN",
    "STAR","MLAD","NOV","TEZAK","LAGAN","SKUP","JEFTIN","DOBAR","LOS","LIJEP",
    "RUZAN","PAMETAN","GLUP","HRABAR","STRASLJIV","BOGAT","SIROMAH","SRECAN","TUZAN","UMORAN",
    "BIJESAN","SMIJEAN","OZBILJAN","TIH","GLASAN","MIRAN","DIVLJI","PITOM","OPASAN","SIGURAN",
    # === Glagoli (infinitiv, kratki oblici) ===
    "RADITI","UCITI","CITATI","PISATI","CRTATI","SLIKATI","KUVATI","PECI","PRZITI","KUHATI",
    "JESTI","PITI","SPATI","BUDITI","TRCATI","HODATI","SETATI","PLIVATI","RONITI","LETJETI",
    "VOZITI","JAHATI","TRAZITI","GUBITI","NACI","DOBITI","DATI","UZETI","KUPITI","PRODATI",
    "PLATITI","ZARADITI","RACUNATI","BROJATI","MJERITI","VAGATI","PUSITI","GLEDATI","SLUSATI",
    "GOVORITI","SAPUTATI","VIKATI","PJEVATI","PLESATI","SVIRATI","POMOCI","VOLJETI","MRZJETI",
    "SMIJATI","PLAKATI","SPAVATI","SANJATI","RAZMISLJATI","OBJASNJAVATI","RAZUMJETI","ZNATI","UMJETI",
    # === Razni pojmovi ===
    "KARTA","NOVAC","BANKA","KASA","KREDIT","ZAJAM","KAMATA","POREZ","RACUN","FAKTURA",
    "UGOVOR","DOKUMENT","PEČAT","POTPIS","PISMO","KOVERTA","PAKET","POSILJKA","POSTA","KURIR",
    "SKOLA","FAKULTET","UCIONICA","TABLA","KREDA","SVESKA","KNJIGA","UDZBENIK","RJECNIK","ATLAS",
    "ZADATAK","TEST","ISPIT","DIPLOMA","OCJENA","ODGOJ","PRAVILO","ZAKON","KAZNA","NAGRADA",
    "BOLNICA","KLINIKA","AMBULANTA","HITNA","APOTEKA","LIJEK","TABLETA","INJEKCIJA","ZAVOJ","VAKCINA",
    "TRZNICA","PIJACA","DUCAN","PRODAVNICA","MARKET","CENTAR","TRZNI","BUTIK","KIOSK","BAZAR",
    "POZORNICA","SALA","KINO","BIOSKOP","MUZEJ","GALERIJA","BIBLIOTEKA","ARHIV","KATEDRALA","CRKVA",
    "DZAMIJA","SINAGOGA","HRAM","SAMOSTAN","MANASTIR","ZVONIK","MUNARA","OLTAR","IKONA","KRST",
    "GRAD","TVRDJAVA","KULA","DVORAC","PALACA","VILA","KOLIBA","CATRJA","STAN","KUCA",
    "FARMA","RANC","MLINI","STAJA","STAJSKA","KOKOSARNIK","KOSNICA","VOCNJAK","VINOGRAD","BASTA",
    # === Tehnologija, online ===
    "EMAIL","FORUM","BLOG","STRANICA","SAJT","LINK","KLIK","DOWNLOAD","UPLOAD","FAJL",
    "FOLDER","DATOTEKA","BACKUP","SOFTVER","PROGRAM","APLIKACIJA","KORISNIK","LOZINKA","PROFIL",
    "NALOG","RACUN","KOMENTAR","LAJK","DISLAJK","SHARE","POST","STORY","REELS","TIKTOK",
    # === Igre, zabava ===
    "IGRA","IGRACKA","LUTKA","KOCKA","PUZZLE","KARTA","TABLA","FIGURA","TOPIC","KONJ",
    "LOVAC","KRALJ","KRALJICA","PJEŠAK","TURNIR","LIGA","KUP","FINALE","POBJEDNIK","GUBITNIK",
    # === Specifične BHS riječi ===
    "MERAK","BERICET","INSAN","SEVDAH","SEVDALINKA","CARSIJA","BAHAR","BAHCIVAN","TESPIH","HAMAM",
    "KALDRMA","SOKAK","AVLIJA","CARDAK","CESMA","BUNAR","SOFRA","DZEZVA","FILDZAN","RAHAT",
    "BAKLAVA","TUFAHIJA","HURMASICE","REVANIJA","HALVA","SUDZUK","PASTRMA","CICVARA","UJSCAK",
    # === Nastavak — više riječi za bolju igrivost ===
    "ANANAS","ABDIJA","AUTOR","ATOM","ANTENA","ASPIRIN","ANGINA","ARMIJA","ARMATURA","AKCIJA",
    "ATLAS","ATOMSKI","ADRESA","AGENT","AHOJ","AKADEMIJA","AKORD","AKVARIJ","ALARM","ALGEBRA",
    "ALEJA","AMETIST","ANALIZA","ANGEO","ANJON","ANSAMBL","APARAT","APETIT","ARENA","ARHIV",
    "ATOMSKI","AUDIO","AURA","AVET","AVION","AVIS","AZBUKA","AZUR","ASOVAN","ATEIST",
    "BABILON","BACVA","BADANJ","BADEM","BAJONET","BAKAR","BALADA","BALAST","BALKON","BALOTA",
    "BAMBUS","BANANE","BARABA","BARAKA","BARJAK","BAROKNI","BARUT","BASIST","BATALJON","BATERIJA",
    "BELI","BENZIN","BICIKL","BIDE","BIFTEK","BIGAMIJA","BIKINI","BILBORD","BIMBAS","BIRO",
    "BISER","BISTRO","BITKA","BJEKSTVO","BLAGAJNA","BLAGOSLOV","BLATO","BLISTAV","BLITVA","BOLEST",
    "BOSANAC","BOTANIKA","BOTOX","BRADAVICA","BRAJIN","BRANIK","BRAVAR","BREZA","BRITVA","BROD",
    "BUBANJ","BUDISTA","BUDZET","BUKVAR","BUMERANG","BUSEN","BUVA",
    "CASTITI","CEDAR","CEDULJA","CENTAR","CESTAR","CIGLA","CILJ","CIMET","CINIK","CISTA",
    "CITRUS","COLA","CRTA","CRTEZ","CUNJ","CUPAVAC","CARLI","COKLA","CUREVI","CIRIL",
    "CADA","CALMA","CARAPA","CARDA","CESALJ","CIGRA","CILIM","CINEMA","CIPELE","CIVIJA",
    "DAJ","DALEKO","DARDA","DARILO","DASKA","DAVID","DEBELA","DEFTER","DELFIN","DESET",
    "DIJAGONALA","DIPLOMA","DIVAN","DIVAS","DIVOT","DJEVOJKA","DOBOS","DODIR","DOJAVA","DOLAR",
    "DOMAR","DOMETI","DRAMA","DRENA","DRSKO","DRVO","DUGA","DUKAT","DUVAR","DZIN",
    "EBOLA","EDEN","EGIPAT","EHO","EKIPA","EKLER","EKRAN","ELASTIK","ELEMENT","EMAJL",
    "EPIZODA","ERA","ESEJ","ESKIM","ETAPA","ETIKETA","EVROPA",
    "FAJL","FAKIR","FALANGA","FARMA","FAUNA","FAZA","FAZON","FELERAN","FESTIVAL","FIGURA",
    "FIJASKO","FILDZAN","FILM","FILTER","FINALE","FIRMA","FISKAL","FLOKA","FLOTA","FOAJE",
    "FOKA","FOND","FORUM","FREJM","FUGA",
    "GALEB","GALIJA","GAMA","GARDA","GARNIR","GASTRO","GAZAP","GAZDA","GENIJ","GIBAK",
    "GIROS","GLAS","GLAVA","GLINA","GLODAR","GLUMAC","GMAZ","GOLOB","GORAN","GORJE",
    "GRABLJE","GRAD","GRAH","GRANA","GREDA","GROB","GROZD","GRUDI","GUSTERA","GUMA",
    "HALDA","HALJINA","HARFA","HARING","HEROJ","HIDRA","HIDROAVION","HILJADA","HIPNOZA","HISTORIJA",
    "HLAD","HOBI","HODAC","HORIZONT","HORMON","HRAM","HRAST","HRPA","HUMOR","HVALA",
    "IGLA","IGRA","ILUZIJA","IMITATOR","INGOT","INJE","INKA","INSEKT","INTERVJU","ISKRA",
    "ISTOK","IZLAZ","IZMET","IZVAN","IZVOR",
    "JAGNJE","JAJE","JANJE","JARAC","JARAK","JARGON","JASIKA","JAVNOST","JEDAN","JEDINKA",
    "JELEN","JEZIK","JOGA","JOGURT","JORGAN","JUG","JUHA","JUNAK","JURNJAVA",
    "KABAO","KADET","KAFANA","KAJAK","KAKAO","KALAJ","KALDRMA","KALORIJA","KAMEN","KAMPER",
    "KAPETAN","KARMIN","KARNEVAL","KARTA","KASA","KASETA","KASKO","KESTEN","KEVA","KIFLA",
    "KILIM","KINEZ","KIPAR","KIRO","KISELO","KIT","KLATNO","KLAVIR","KLIN","KLISURA",
    "KLOPKA","KLUB","KNEZ","KNJIGA","KOBASICA","KOFER","KOKA","KOKOS","KOLAC","KOLIBA",
    "KOMAR","KOMODA","KONJUSAR","KONOP","KORAK","KORAL","KORICE","KORPA","KOSA","KOSNICA",
    "KOST","KOSTIM","KOSULJA","KOTAR","KRAJ","KRALJ","KRASTAVAC","KRATER","KRESIVO","KRIZA",
    "KROV","KRPA","KRUH","KRUNA","KRZNO","KUFER","KUGLA","KUMA","KUPA","KUPATILO",
    "LAJAVAC","LAKAT","LAMPA","LANAC","LATICA","LAVOR","LEDENJAK","LEGENDA","LEPTIR","LIBELA",
    "LIDER","LIFER","LIK","LILJAN","LIMUN","LIPA","LISICA","LJEKARNA","LJEPILO","LJESA",
    "LJESNJAK","LJULJASKA","LOGOR","LOKVA","LONAC","LOPATA","LOPOV","LOZA","LUBENICA","LUDARA",
    "LULA","LUNA","LUPA","LUSTER",
    "MACETA","MAFIN","MAGIJA","MAGLA","MAJKA","MAKARONI","MALINA","MAMA","MAMUT","MARAMA",
    "MARATON","MARGARIN","MARKA","MARMELADA","MARTINI","MASAZA","MASKA","MASLINA","MATERIJA","MEDIJ",
    "MEDONOSA","MEDUZA","MELEM","MEN","MERAK","METAR","METLA","MIRIS","MISLI","MITRALJEZ",
    "MJERA","MOC","MODA","MOJA","MOLBA","MORE","MOST","MOTAR","MOTIV","MOZAIK",
    "MUFLON","MUKA","MUMIJA","MUNJA","MUTA","MUZEJ",
    "NABOJ","NACRT","NAFTA","NAJLON","NAKIT","NAOCALE","NAPAD","NAPOJ","NAPOR","NARAVAN",
    "NAREDBA","NAROD","NASLJEDNIK","NAUKA","NEBO","NEDA","NEMIR","NERAST","NESTASIK","NEUTRON",
    "NEVRIJEME","NIDAS","NIKAD","NIMFA","NIVO","NOC","NOGA","NOTA","NOVAC","NOVCANIK",
    "OAZA","OBALA","OBARAC","OBLAK","OBLIK","OBROK","OBRT","OCJENA","ODGOJ","ODOBOR",
    "ODORA","OGANJ","OGRADA","OKO","OKLOP","OLIMP","OLOVKA","OPATICA","OPTIKA","ORAH",
    "ORAO","ORBIT","ORDEN","ORGAN","ORLOVI","ORMAN","OROMIR","OSAM","OSIGURAC","OSJET",
    "OSMIJEH","OTAC","OTOK","OZIBAC",
    "PAJAC","PAKET","PALAC","PALACA","PALACINKA","PALETA","PAMUK","PAPIR","PAPUC","PARTIJA",
    "PASKVIL","PASOS","PASTA","PASTIR","PAUK","PAUZA","PCELA","PECINA","PEHAR","PERIVOJ",
    "PERLA","PERSPEKTIVA","PESMA","PIANIST","PICA","PIDZAMA","PIJUK","PILA","PILOT","PIPA",
    "PISMO","PJEGA","PLAFON","PLAKAT","PLAN","PLATA","PLATFORMA","PLAVUSA","PLEMSTVO","PLIN",
    "PLOCA","PODNOZJE","POEZIJA","POJAS","POKER","POLE","POLITIKA","POLJANA","POMOC","PONOC",
    "POROD","POSAO","POSLOVI","POSTUDA","POVRCE","POZIV","PRASAK","PRAVDA","PREDAK","PREDSJEDNIK",
    "PREGRADA","PREPAD","PREPRJEK","PRES","PRIBOR","PRIVOZNIK","PROGRAM","PROLOM","PROSAC","PRSTEN",
    "PSALAM","PUDING","PUNJAC",
    "RACA","RACUN","RADIJA","RAJ","RAKIJA","RAKOVI","RAMA","RANAC","RAT","RATAR",
    "RAVAN","RAZBORIT","RAZUM","REKA","REPLIKA","REZIJA","RIBA","RIJEC","RIKVERC","RIMA",
    "RISTO","RIZA","ROBA","ROBOT","RODA","RODBINA","RODOSLOV","ROK","ROMOR","ROVAS",
    "RUPA","RUTINA","RUZA",
    "SABOR","SAJAM","SAKO","SALATA","SALON","SAMAC","SAMUR","SAN","SANJAR","SANJKE",
    "SAPUN","SARAJ","SARGO","SARMA","SAT","SAVA","SAVJET","SAVRSEN","SCENA","SCIT",
    "SECER","SEDLO","SELO","SEMAFOR","SEPTUNA","SESTRA","SEVDAH","SEZONA","SIDRO","SIJALICA",
    "SIJEDA","SIKIRA","SILAZAK","SIMFONIJA","SIMPATIJA","SINOC","SIROMAH","SIROVI","SISTEM","SITAN",
    "SITNICA","SJAJ","SJEME","SJENA","SKALA","SKICA","SKLAP","SKOLA","SKULPTURA","SLATKO",
    "SLIKAR","SLOBODA","SLON","SLUSALICE","SMOKVA","SNAJPER","SOFER","SOK","SOL","SOLI",
    "SOMUN","SOSO","SPARTA","SPEKTAR","SPLAV","SPOMENIK","SPORT","SPREJ","SREDISTE","STADION",
    "STAJA","STAKA","STALAK","STAN","STAPSKI","STARAC","STARINA","STAZA","STEPENICE","STIH",
    "STOKA","STOL","STOLAR","STRAH","STRELA","STRIJELA","STROJ","STUDENT","SUDIJA","SUMA",
    "SUNCE","SVIJET","SVJETLO",
    "TABLA","TANJUR","TARAKAN","TARABA","TASNA","TAVA","TEKO","TELEFON","TELEVIZOR","TEMA",
    "TENISER","TEORIJA","TEPIH","TEREN","TERMIT","TIGAR","TIKVA","TINEJDZER","TIPKA","TIRKIZ",
    "TKANINA","TLOCRT","TOCAK","TOPLOMJER","TOPOR","TORBA","TORTA","TORZO","TRAGAC","TRAKA",
    "TRAKTOR","TRAVA","TREN","TRENER","TRG","TRGOVAC","TRIBUNA","TRKA","TROFEJ","TRUBA",
    "TRUP","TUFNA","TUGA","TULIPAN","TUNA","TURPIJA",
    "UDOVAC","UJAK","UJEDINJENA","UKRAS","ULICA","ULOVAR","UMOR","UMOR","UPALA","URAGAN",
    "URAR","UROK","USPJEH","USPON","USTAJANJE","UTOR","UZBUNA",
    "VAGA","VAGON","VAKCINA","VALOVI","VANJA","VARNICA","VARTILO","VATRA","VEKER","VENTIL",
    "VESELJE","VIDIK","VIGOR","VIJORI","VIKTORIJA","VILA","VILJUSKA","VINO","VIORI","VITAMIN",
    "VITEZ","VITRINA","VJEDRO","VJENCANJE","VJESTAK","VJEVERICA","VLAK","VOCNJAK","VODA","VOJNIK",
    "VOLAN","VRABAC","VRH","VRHUNAC","VRT","VUCJAK","VULKAN",
    "ZADATAK","ZADNJAK","ZAGRLJAJ","ZAJC","ZAKLON","ZAKON","ZAMOR","ZANIMANJE","ZAOBILAZAK","ZAPIS",
    "ZAPLET","ZARADA","ZASEDA","ZASIK","ZASLON","ZAVISA","ZAVOJ","ZBIRKA","ZDRAVO","ZEC",
    "ZELENI","ZEMLJA","ZGRADA","ZID","ZIMA","ZIVOT","ZLATO","ZMAJ","ZMIJA","ZNAK",
    "ZOLJA","ZORA","ZRAK","ZRNO","ZUB","ZVUK",
    # === Dodatne kratke 3-4 slovne riječi ===
    "BOG","DOM","DAR","SAN","JAJ","RAJ","ČAJ","ROJ","BOJ","BOJA","BOL","BOLI","BOR","BUS",
    "CAR","CIK","DAH","DAB","DAR","DJED","FEN","GAS","GRB","GRM","HOR","HUM","IGO","ILI",
    "JAJE","JAK","JAR","KAD","KAJ","KAP","KIT","KOM","KOS","KOZA","LAV","LEK","LET","LED",
    "LIK","LIM","LIN","LOM","LOV","LUK","MAH","MAK","MAJ","MIR","MOR","MOST","NEK","NIT",
    "NOC","NOJ","NOS","ORO","OBL","OKO","OPA","OSA","PAS","PAR","PAT","PIR","POD","POJ",
    "POP","POT","PUH","PUT","RAD","RAJ","RAP","RAT","RED","REP","REZ","RIM","ROD","ROK",
    "ROM","ROZ","RUB","RUC","SAJ","SAN","SAP","SAT","SLON","SOK","SON","SOR","STO","SUD",
    "SUH","SUR","SVE","TAJ","TAN","TAS","TIH","TIK","TIM","TIP","TON","TUR","UAL","UKA",
    "ULJ","UMI","UVA","VAL","VAR","VAS","VEC","VEK","VID","VIK","VIR","VOD","VOL","VOZ",
    "VRH","VUK","ZID","ZIK","ZIM","ZNA","ZOR","ZUB","ZUM","ZID","ZIV",
    # === Hemija, nauka, medicina ===
    "ACETON","ACETILEN","ACETILSALICILIK","ACID","AGAR","AGENIJUM","ALKOHOL","ALUMINIUM","AMONIJAK",
    "ANALOG","ANALIZA","ANATOMIJA","ANTIBIOTIK","ANTIDOT","ANTIGEN","ANTISEPTIK","APSORPCIJA",
    "ATOM","ATOMSKA","BAKTERIJA","BAZA","BENZEN","BIOHEMIJA","BIOKEMIJA","BIOLOGIJA","BIOMASA",
    "BIOPSIN","BIOTIT","BIZMUT","BOKSIT","BORAKS","BROM","BRZINA","CEZIJ","CITOLOGIA",
    "DEJSTVO","DIODA","DIOXID","DIPLOID","DISANJE","DIOKSID","ELEMENT","EMULZIJA","ENCIM",
    "ENERGIJA","ENZIM","ERITROCIT","ERLEN","ETANOL","ETER","EVOLUCIJA","FIZIKA","FLUOR",
    "FOSFAT","FOSFOR","FOTOSINTEZA","FRAKCIJA","GENETIKA","GLUKOZA","HELIJ","HEMIJA","HLORID",
    "HLORIN","HORMON","IMUNITET","INZULIN","ION","IZOMER","JELEN","JODIN","KALIJUM","KALCIJ",
    "KALCIJUM","KARBON","KATALIZATOR","KEMIJA","KISIK","KLADOGRAM","KLOR","KLOROFIL",
    "KOBALT","KOJI","KOMPAS","KOSTUR","KRISTAL","KVARCIT","LABORATORIJ","LASERSKI","LEGURA",
    "LEUKOCIT","LEUKOZA","MAGNEZIJ","MAGNEZIJUM","MAGNEZIT","MANGAN","MASA","MEHANIZAM",
    "MIKROB","MIKROSKOP","MINERAL","MOLEKUL","NEON","NEUTRON","NITRAT","NITROGEN","NUKLEOTID",
    "OKSIDAT","OKSIGEN","OPTICKA","OPTIKA","ORBITA","ORGANIZAM","OSMOZA","OKSIGEN","PARAZIT",
    "PERIODA","PROTON","PROTOPLAZMA","REAKCIJA","REAGENS","RECEPTOR","RESPIRACIJA","RIBA",
    "RIBOZOM","SELEN","SILICIJ","SIMULATOR","SINAPTICKI","SINTEZA","SINTEROVANJE","SPEKTAR",
    "SPIRALA","SREBRO","STIMULANS","STRUKTURA","SUPSTANCA","URAN","VAKUUM","VALENCA","VIRUS",
    "VITAMIN","VODIK","VOLUMEN","ZAGRIJAVANJE","ZRAK","ZRENJE",
    # === Više svakodnevnih BHS riječi ===
    "ACENA","ACIN","ADET","ADRESA","AGENCIJA","AGRESIJA","AHILEJ","AJET","AKCIJA","AKLAM",
    "AKCENT","AKORD","AKTIV","AKVARIJUM","ALARM","ALATKA","ALEJA","AMALGAM","AMBIS","AMORTIZER",
    "ANANAS","ANES","ANKETA","ANSAMBL","ANTENA","APARAT","APRIL","APSOLVENT","APTEKA","ARBA",
    "ARDOV","ARENA","ARHITEKT","ASFALT","ASISTENT","ASOCIJACIJA","ASPIK","ASTROLABIJ","ATAR",
    "ATLETIKA","ATMOSFERA","AVAN","AVION","AZIL","AZUR","BAGER","BAGREM","BAJKA","BAJPAS",
    "BAJRAK","BAKRAC","BALON","BANEM","BAOBAB","BARIJERA","BARKA","BARUT","BASAMAK","BASNA",
    "BASTON","BATINA","BETON","BLJESAK","BONUS","BRAVURA","BRDO","BREZAN","BRIGADA","BRONZA",
    "BRUCA","BRZINA","BUBREG","BUJRUM","BUNAR","BUREGDZIJA","CARICA","CEKINJ","CENTURIJA",
    "CETINA","CIMBALO","CIVIL","COFAK","CRTALICA","CUBURA","CUPRIJADA","CVIJET","DACIJA",
    "DAKLE","DALIJA","DANIJEL","DARMAR","DASKALOS","DAVITELJ","DEBAKL","DECIBEL","DEFICIJT",
    "DEFORA","DEIKSA","DEJANSKI","DELIJA","DENAR","DEPONIJA","DESIL","DIDAK","DIJALOG",
    "DINAMIT","DIRIGENT","DISKRETNO","DIZEN","DOKAZ","DOMACINSTVO","DOMAKIN","DOMET","DORUCAK",
    "DOZIVOTNI","DRANGULIJA","DRSKA","DUMAC","DUNAVAC","DUVAN","DUZNOST","DZEPNI","DZIN",
    "EFEKAT","EGOIZAM","EKONOMIJA","EKRAN","EKSPLOZIJA","EKSPRES","EKSTAZO","ELEKTRARNA",
    "ELEKTRON","EMISIJA","EMOTIVNI","EPRUVET","ERUPTIVNI","ESTETIKA","ETIKETA","EVOLUCIJA",
    "FABRIKA","FAKTURA","FASADA","FAVORIT","FAZANIN","FERMENT","FESTIVAL","FIGURA","FINANCIJE",
    "FITNES","FLAGEL","FOLIRANT","FOTOGRAF","FRATAR","FRONTA","FURUNA","GASOVOD","GAZIJA",
    "GEOGRAF","GLAGOL","GLASAN","GLISTA","GMIZAVAC","GOBLEN","GOSPODA","GOSTIONICA","GOVEDO",
    "GRADITEL","GRAMOFON","GREBEN","GRICKALICA","GRIJANJE","GRMLJAVINA","GROBLJE","GRUPACIJA",
    "GUBITAK","GUMA","GUSAR","GUTLJAJ","HAMAM","HAOS","HAUBICA","HEROIN","HIDROELEKTRANA",
    "HILJADU","HISTORIJA","HOROR","HVATAC","ILUZIJA","ISFORSIRANI","ISKUSNI","ISPIT","ISTINA",
    "ISTRAGA","ISUSOVAC","JECMENI","JEGULJA","JELKA","JERSEJ","JEZGRA","JORGOVAN","JUBILARNI",
    "JUBILEJ","JUMBO","JURNJAVA","JUTARNJI","KADIFA","KAFTAN","KALEM","KALEIDOSKOP","KAMEN",
    "KANALIZACIJA","KAPACITET","KAPLAR","KARDINAL","KARTICA","KASAPIN","KASARNA","KATALOG",
    "KATANA","KAVGADZI","KAZNITI","KECELJ","KERBER","KESTEN","KEZMA","KIBLIC","KILOGRAM",
    "KISELINA","KLINICKI","KLUPKO","KNJIZEVNOST","KOBASICARA","KOLOBARA","KOMANDIR","KOMPJUTOR",
    "KOMPROMIS","KONKURS","KONJIC","KOPISTAN","KORIDOR","KORISNIK","KOSTUR","KOTLINA","KOVNICA",
    "KUVARICA","KUVAR","KUVARSAND","KVADRAT","LAKONSKI","LANDAR","LASTAVICA","LAVIRINT",
    "LEKSIKON","LETOPIS","LICITACIJA","LIJEVAK","LIKOVNI","LJEKARNA","LOJALNOST","LOMACA",
    "LOPUSTA","LOPTANJE","LUBENICA","LUGARNICA","LUNAPARK","LURISTAN","MAGNETNA","MAJONEZA",
    "MANJI","MARLJIV","MATURANT","MAZGA","MEDICINAR","MENTOR","METALURGI","METAR","METODIKA",
    "MINA","MISTIKA","MITING","MITRALJEZ","MODULATOR","MONARHIJA","MONTAZA","MORAVAC","MOSTOVI",
    "MOTIVACIJA","MRAK","NAGLAS","NAKLADA","NAMESTNIK","NASLAGA","NASLOV","NASTUP","NATJECANJE",
    "NAUKA","NAVIGATOR","NEBODER","NESRETAN","NEVJERNIK","NOMAD","NORMA","NOSAC","NOSNICA",
    "OBAVEZA","OBRAZOVANJE","ODISEJA","ODRED","ODMAH","ODPAD","ODSJAJ","OGLEDALO","OGRANAK",
    "OKLOPNJACA","OLIMPIJADA","OMILJEN","OPASNOST","OPREMA","OPTUZNICA","ORGANIZATOR","ORIJENT",
    "ORKESTRA","OSVAJAC","OTPRILIKE","OTPUSTIT","OVLASTITI","OZDRAVLJENJE","PADOBRAN","PAKET",
    "PAMETNICA","PANDUR","PANTALONE","PARCELA","PARKING","PASIJANS","PASTIRSKA","PATROLA",
    "PENZIJA","PERIVOJ","PERON","PIRANIJA","PISAC","PISMENOST","PLANINAR","PLATINA","PLEDOVI",
    "POBJEDA","POBUNA","PODUZECE","POGLAVLJE","POHRANA","POKLON","POLICA","POLITICAR","PORTRET",
    "PORUKA","POVJERA","PRAVNIK","PRISTUP","PRIVILEGIJ","PROCESIJA","PROGRAMER","PROMET",
    "PRIJEVOD","PROSTORIJA","PROTONIK","PUCISTA","RASADNIK","RASKOLNIK","RASPAD","RASPORED",
    "RATNIK","RAZBOJNIK","RAZMJENA","REDAR","REFORMA","REGISTAR","REPORTAZA","RESTORANT",
    "REVOLUCIJA","RIBOLOV","RITUAL","ROBOTIKA","ROKADA","ROTACIJA","RUBRIKA","RUDNIK","RUGALICA",
    "SABORNIK","SADRZAJ","SAOBRACAJ","SAVJESTAN","SELIDBA","SEMINAR","SENSOR","SERIJA","SISTEM",
    "SITNO","SJEDNICA","SKIJALISTE","SKLADISTE","SKUPSTINA","SLAVLJE","SLUZBA","SLOBODNOST",
    "SMJERNICA","SOCIOLOG","SOMOT","SPASAVANJE","SPAVAC","SRETAN","STAMPA","STATISTIKA",
    "STATUTARNA","STEVAN","STRUCNJAK","STUDIJA","SURADNIK","SUVENIRI","TABELA","TAKMICENJE",
    "TALOG","TALMUD","TAMBURICA","TAMNICA","TARAFIKA","TARCIN","TARTUF","TVORNICA","UGLJENDIOKSID",
    "ULAGANJE","ULOMAK","ULJARA","UMJESTO","UNIKAT","UPRAVLJAC","UPRAVLJANJE","USTAV","UZGOJ",
    "UZORNOST","VAGON","VATROMET","VATROGASAC","VELEPRODAJA","VELIK","VERESIJA","VESELJE",
    "VETERINAR","VIJECENICA","VIKEND","VILAJET","VJESNIK","VJESTACKI","VLASNIK","VOCNJAK",
    "VOJARNA","VOJNIK","VOJVODA","VOLONTER","VRTLAR","VULKANSKA","YADRAN","ZADRUGA","ZAHTJEV",
    "ZAJEDNICA","ZAKLADA","ZALAGAONICA","ZALBA","ZAMETAK","ZAPOVIJEDNI","ZARADJIVATI","ZARUCNIK",
    "ZASTAVA","ZASTITNIK","ZDRAVLJE","ZELJEZNICKA","ZEMLJA","ZGODA","ZIDAR","ZIVOTINJA","ZLINAC",
    # === Magicna rijec ===
    "KALADONT",
])

# ── KALADONT — laka pravila: BLOKIRAMO SAMO IMENA i nemoguće završetke ──
# Korisnik je tražio: NEMA strogog rječnika.
#   • blokiraj imena (lista najčešćih balkanskih imena)
#   • blokiraj završetke koji nemaju nastavak (KT, QU, MK, NJ, GH, ZH, MJ, NJ, BJ)
#   • SVE OSTALO PROLAZI (nema više "nije u rječniku" greške)
KALADONT_NAMES = set([
    # muška
    "MARKO","IVAN","STEFAN","NIKOLA","PETAR","LUKA","FILIP","DUSAN","MIHAJLO","MILOS",
    "ALEKSA","LAZAR","DJORDJE","BORIS","DAVID","DANIEL","NEMANJA","UROS","STRAHINJA",
    "VUK","RADOMIR","BRANIMIR","MILAN","BOJAN","ZORAN","DRAGAN","GORAN","SLAVKO",
    "MILOVAN","RANKO","ZELJKO","MLADEN","NENAD","SASA","PREDRAG","DRAGOMIR","NEBOJSA",
    "EMIR","HARIS","FARUK","ADNAN","KENAN","TARIK","AMAR","DENIS","ARMIN","HAMZA",
    "MUHAMED","MUHAMMAD","ALMIR","ELVIS","EDIN","ENES","SEMIR","SENAD","DAMIR","NEDIM",
    "SAMIR","MIRZA","MIRSAD","FUAD","DZENAN","HARUN","BAKIR","SULEJMAN","IBRAHIM",
    "AMER","JASMIN","SEAD","KEMAL","DARKO","DALIBOR","DRAZEN","NIKOLINA","TIN","IVO",
    "IGOR","TOMA","MATE","MATEJ","MATEO","ANTE","JOSIP","ANDRIJA","HRVOJE","MISLAV",
    "DOMAGOJ","ZVONIMIR","BORNA","LOVRO","KRESIMIR","SINISA","RAJKO",
    # ženska
    "ANA","MARIJA","JELENA","MILICA","TIJANA","TAMARA","SANJA","JOVANA","KATARINA",
    "ANDJELA","ANDREJA","ANDREA","SARA","NADJA","SELMA","HANA","MELISA","AMINA",
    "LEJLA","EMINA","ALMA","MEDINA","ELMA","LAMIJA","DZENANA","MERIMA","IVANA",
    "MARIJANA","BILJANA","SNEZANA","DANIJELA","DRAGANA","GORDANA","SLOBODANKA",
    "DJURDJA","DJURDJICA","SLAVICA","MILENA","NEVENA","DUNJA","TEODORA","ELENA",
    "VESNA","JASMINA","JADRANKA","BOSILJKA","MARTA","NIKA","LANA","MIA","NORA",
    "EMA","DORA","PETRA","IVA","MAJA","LUCIJA","KARMELA","KLARA","MATEJA","ROZA",
    "TINA","ANJA","KIKO","DANNY","ALEKSA","YUGO","GIAN",
])

KALADONT_BAD_END = ("KT","QU","MK","NJ","GH","ZH","MJ","BJ","CJ","FJ","HJ","KJ","LJ","NJ","PJ","SJ","TJ","VJ","ZJ")

# ── 50/50 sistem — poruke kada sudbina odbije valjanu riječ ──────────────
KALADONT_50_FAIL = [
    "<:e_devil:1519362989470253187> Sudbina je rekla **NE**! Pokušaj ponovo.",
    "<:e_skull:1519362992502997125> Sreća te napustila ovaj put! Pokušaj drugu.",
    "<:e_dice2:1519362633763913931> Kocka nije bila na tvojoj strani! (50% šansa te ubila)",
    "<:e_wind:1519362878300229883>️ Vjetar sudbine te odnio! Probaj opet.",
    "<:e_bolt:1519362674717102160> Grom te udario! Tvoja riječ propala zbog nesreće.",
    "<:e_cards2:1519362702835712010> Džoker je rekao NE! Sudbina odlučuje ovdje.",
    "<:e_moon:1519363445466595522> Crna mačka prešla put! Probaj drugu riječ.",
    "<:e_skull2:1519362997443629186>️ Loša energija! Tvoja riječ bila je ispravna, ali sreća te izdala.",
    "<:e_masks:1519363003424706671> Drama sudbine — ispravna riječ, ali nemaš sreće danas!",
    "<:e_crystal:1519362965558657146> Kristalna kugla je rekla NE! (50/50 sistem udario)",
]

def kaladont_word_valid(word: str):
    """Vraća (ok, razlog). NE provjeravamo rječnik — samo imena i nemoguće završetke."""
    nw = _kaladont_normalize(word)
    if nw == "KALADONT":
        return True, ""
    if nw in KALADONT_NAMES:
        return False, "ime"
    # provjera završetka — uzima zadnja 2 slova
    if len(nw) >= 2 and nw[-2:] in KALADONT_BAD_END:
        return False, "kraj"
    return True, ""

def get_kaladont_hint(req: str, used: set) -> list:
    """Vrati do 4 primjera riječi iz baze koje počinju sa req i nisu još korištene."""
    req_up = req.upper()
    candidates = [w for w in KALADONT_DICT if w.startswith(req_up) and w not in used and w != "KALADONT"]
    random.shuffle(candidates)
    return candidates[:4]


# ═══════════════════════════════════════════
#    UNICODE EMOJI FALLBACK — prefix bridge
#    channel.send() ne renderuje app emojije
#    → zamjenjujemo ih Unicode ekvivalentima
# ═══════════════════════════════════════════
_EMOJI_UNICODE: dict[str, str] = {
    "1519358244827697424": "🪙",
    "1519358248942047342": "🏆",
    "1519358252234707115": "🛡️",
    "1519358255925825667": "⚔️",
    "1519358259171950724": "🎲",
    "1519358266738737274": "🎁",
    "1519358274284032030": "⚠️",
    "1519358278356959284": "🚫",
    "1519358285902254242": "⚙️",
    "1519358289173807246": "📈",
    "1519358302285332540": "🏦",
    "1519358309008674848": "❤️",
    "1519358312188088466": "🔥",
    "1519358316327997612": "⚡",
    "1519358320337752125": "🎵",
    "1519358323667767346": "🎮",
    "1519358327140651029": "🎣",
    "1519358331192344687": "🏹",
    "1519358335068147836": "🧠",
    "1519358339748855808": "🌍",
    "1519358353208508566": "📋",
    "1519358358010724352": "🔒",
    "1519358364889383084": "❓",
    "1519358368773308457": "⏰",
    "1519358376268533810": "✅",
    "1519358379917836508": "❌",
    "1519358485647720510": "📊",
    "1519358512336212091": "🥈",
    "1519358517633355919": "🥉",
    "1519362615069904977": "💼",
    "1519362618341462067": "🎁",
    "1519362621206298666": "🪙",
    "1519362624742232146": "🏆",
    "1519362627795554374": "🛡️",
    "1519362631146930317": "⚔️",
    "1519362633763913931": "🎲",
    "1519362637534597221": "🎟️",
    "1519362640961474601": "💎",
    "1519362648972595289": "🔇",
    "1519362652516782194": "⚙️",
    "1519362656568475880": "📊",
    "1519362659676455046": "📅",
    "1519362662515871744": "🏦",
    "1519362665347153930": "🛒",
    "1519362668644012133": "💗",
    "1519362671491678280": "🔥",
    "1519362674717102160": "⚡",
    "1519362679310127114": "🎵",
    "1519362682296209498": "⌨️",
    "1519362685957963940": "🐟",
    "1519362689212874883": "🦌",
    "1519362691813085386": "❓",
    "1519362694887637004": "🌍",
    "1519362699014967297": "🎰",
    "1519362702835712010": "🃏",
    "1519362710469476405": "📨",
    "1519362714198347886": "📋",
    "1519362717394403432": "🔒",
    "1519362720506449960": "🔓",
    "1519362723148726534": "❓",
    "1519362726952964227": "⏰",
    "1519362730057007268": "✅",
    "1519362733613776967": "❌",
    "1519362736566304818": "📣",
    "1519362739749785610": "📊",
    "1519362745772802078": "🔧",
    "1519362749598269510": "🚗",
    "1519362754732097546": "📧",
    "1519362764244652122": "💪",
    "1519362769047126028": "🟢",
    "1519362782192210041": "🔴",
    "1519362785291669644": "😴",
    "1519362788462559323": "📱",
    "1519362791591378975": "🍽️",
    "1519362798189150370": "👵",
    "1519362801703977110": "❄️",
    "1519362812554510509": "💫",
    "1519362825670230097": "📺",
    "1519362828484477012": "🛋️",
    "1519362833668772000": "🍴",
    "1519362836671762494": "🔨",
    "1519362841369378961": "🏠",
    "1519362845970530577": "👀",
    "1519362849548406975": "🧠",
    "1519362852853649439": "⚖️",
    "1519362856884371526": "☕",
    "1519362860218843399": "☀️",
    "1519362875129335849": "♻️",
    "1519362878300229883": "🌬️",
    "1519362881756336168": "🌧️",
    "1519362884868636883": "🏃",
    "1519362891210424473": "👂",
    "1519362900681298000": "🧹",
    "1519362915801501767": "🌅",
    "1519362926622806046": "👩",
    "1519362931689525422": "📶",
    "1519362936777478326": "👁️",
    "1519362941617438750": "💍",
    "1519362944717160530": "😢",
    "1519362947766554737": "🤝",
    "1519362951247691898": "🗑️",
    "1519362955437805771": "💸",
    "1519362959187509461": "🔄",
    "1519362962530373742": "👦",
    "1519362965558657146": "🔮",
    "1519362984818901173": "🌸",
    "1519362989470253187": "😈",
    "1519362992502997125": "💀",
    "1519362997443629186": "☠️",
    "1519363003424706671": "🎭",
    "1519363006599794799": "💡",
    "1519363009883934740": "🔁",
    "1519363015147913396": "💾",
    "1519363018725658675": "🚫",
    "1519363022399995914": "🛑",
    "1519363028334674070": "🎉",
    "1519363032185176198": "✨",
    "1519363038107406447": "⏸️",
    "1519363047163166922": "👑",
    "1519363052871614627": "📋",
    "1519363057199878144": "📝",
    "1519363059909398610": "✏️",
    "1519363063738925187": "🔔",
    "1519363066545045756": "🔑",
    "1519363069925654609": "🎯",
    "1519363074824343592": "💚",
    "1519363084253266031": "⭐",
    "1519363093736718518": "👤",
    "1519363096601301120": "👥",
    "1519363099478458498": "📦",
    "1519363103064723547": "🔍",
    "1519363106395000994": "🌐",
    "1519363307998417148": "💬",
    "1519363311207186482": "📡",
    "1519363314524881048": "🔊",
    "1519363318391771326": "🖼️",
    "1519363321458065408": "🔗",
    "1519363326109417613": "🏷️",
    "1519363329259208836": "📌",
    "1519363332266524813": "🚀",
    "1519363345252090081": "⬇️",
    "1519363348288901221": "🎊",
    "1519363351354937497": "📥",
    "1519363357436543099": "📍",
    "1519363362322907218": "🪶",
    "1519363367712591922": "▶️",
    "1519363370694738072": "💎",
    "1519363373748195502": "🌯",
    "1519363376969420930": "🍞",
    "1519363380513603615": "🚕",
    "1519363385328799826": "🏗️",
    "1519363388789227611": "🐑",
    "1519363391939018857": "🚌",
    "1519363395239804998": "🚿",
    "1519363399845154958": "➡️",
    "1519363402890346658": "🦁",
    "1519363406078021863": "🙏",
    "1519363409421008987": "🐉",
    "1519363412625326161": "🐺",
    "1519363415871590420": "🦊",
    "1519363418790822029": "🐻",
    "1519363422716825600": "🐯",
    "1519363429394153633": "🦅",
    "1519363432615510078": "🐬",
    "1519363439385116812": "🍒",
    "1519363442597695600": "🌴",
    "1519363445466595522": "🌙",
    "1519363450084786376": "☁️",
    "1519363453347696821": "🌈",
    "1519363456334168255": "💣",
    "1519363469013422181": "🧪",
    "1519363484377284770": "🎧",
    "1519363490228343067": "🎨",
    "1519363493701091348": "📷",
    "1519363499875242104": "⌨️",
    "1519363516002467871": "💻",
    "1519363521140359410": "⚽",
    "1519363547514015764": "🏅",
    "1519363558809272371": "🎪",
    "1519363568645177457": "🏰",
    "1519363571815809179": "🗺️",
    "1519363589897588868": "🔋",
    "1519363593366147255": "💊",
    "1519363600047673415": "🩺",
    "1519363612978839642": "📚",
    "1519363621912576191": "📏",
    "1519363626006351975": "📏",
    "1519363642808729690": "📁",
    "1519363657404776661": "🚪",
    "1519363663654293665": "🛏️",
    "1519363694549667881": "🍀",
    "1519363697728815175": "🌹",
    "1519363706243387573": "🌿",
}

def _emoji_safe(text: str) -> str:
    """Zamijeni <:name:id> i <a:name:id> sa Unicode ekvivalentom."""
    if not text or "<:" not in text and "<a:" not in text:
        return text
    def _repl(m):
        eid = m.group(2)
        return _EMOJI_UNICODE.get(eid, "")  # prazan string ako nema mape
    return re.sub(r"<a?:[\w]+:(\d+)>", lambda m: _EMOJI_UNICODE.get(m.group(1), ""), text)

def _embed_safe(embed) -> "discord.Embed":
    """Vrati kopiju embeda sa zamijenjenim emoji stringovima (za prefix bridge)."""
    import copy
    e = copy.copy(embed)
    d = e.to_dict()
    def _walk(obj):
        if isinstance(obj, str): return _emoji_safe(obj)
        if isinstance(obj, dict): return {k: _walk(v) for k, v in obj.items()}
        if isinstance(obj, list): return [_walk(i) for i in obj]
        return obj
    d = _walk(d)
    return discord.Embed.from_dict(d)

class _SafeMessage:
    """Wrapper oko discord.Message — primjenjuje emoji safe na edit() pozivima."""
    __slots__ = ("_msg",)
    def __init__(self, msg): self._msg = msg
    async def edit(self, **kwargs):
        if "embed"   in kwargs: kwargs["embed"]   = _embed_safe(kwargs["embed"])
        if "embeds"  in kwargs: kwargs["embeds"]  = [_embed_safe(e) for e in kwargs["embeds"]]
        if "content" in kwargs and kwargs["content"]: kwargs["content"] = _emoji_safe(kwargs["content"])
        return await self._msg.edit(**kwargs)
    async def delete(self, **kwargs): return await self._msg.delete(**kwargs)
    def __getattr__(self, name): return getattr(self._msg, name)

# ═══════════════════════════════════════════
#    INTENTS & BOT
# ═══════════════════════════════════════════
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True  # potrebno za /vanity (čitanje custom statusa)
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

# ═══════════════════════════════════════════
#    PREFIX BRIDGE — .kpm radi kao /kpm
# ═══════════════════════════════════════════
class _FakeResponse:
    def __init__(self, fake): self.fake = fake; self._sent = False
    async def send_message(self, content=None, *, embed=None, embeds=None, view=None, ephemeral=False, **kw):
        # Zamijeni custom emojije sa Unicode (ne renderuju u channel.send)
        if content is not None: content = _emoji_safe(content)
        if embed   is not None: embed   = _embed_safe(embed)
        if embeds  is not None: embeds  = [_embed_safe(e) for e in embeds]
        kwargs = {}
        if content is not None: kwargs["content"] = content
        if embed   is not None: kwargs["embed"]   = embed
        if embeds  is not None: kwargs["embeds"]  = embeds
        if view    is not None: kwargs["view"]    = view
        cmd_name = (self.fake.message.content[1:].split(maxsplit=1)[0].lower() if self.fake.message.content.startswith(".") else "")
        if ephemeral and cmd_name == "help":
            try:
                msg = await self.fake.user.send(**kwargs)
                try: await self.fake.message.add_reaction("📧")
                except: pass
                self.fake._original = msg; self._sent = True
                return msg
            except: pass
        if ephemeral:
            kwargs["delete_after"] = 10
        _raw = await self.fake.channel.send(**kwargs)
        msg = _SafeMessage(_raw)
        self.fake._original = _raw; self._sent = True
        return msg
    async def defer(self, ephemeral=False, thinking=False): self._sent = True
    async def edit_message(self, **kw):
        try: await self.fake._original.edit(**{k:v for k,v in kw.items() if v is not None})
        except: pass
    def is_done(self): return self._sent

class _FakeFollowup:
    def __init__(self, fake): self.fake = fake
    async def send(self, content=None, *, embed=None, embeds=None, view=None, ephemeral=False, **kw):
        # Zamijeni custom emojije sa Unicode (ne renderuju u channel.send)
        if content is not None: content = _emoji_safe(content)
        if embed   is not None: embed   = _embed_safe(embed)
        if embeds  is not None: embeds  = [_embed_safe(e) for e in embeds]
        kwargs = {}
        if content is not None: kwargs["content"] = content
        if embed   is not None: kwargs["embed"]   = embed
        if embeds  is not None: kwargs["embeds"]  = embeds
        if view    is not None: kwargs["view"]    = view
        cmd_name = (self.fake.message.content[1:].split(maxsplit=1)[0].lower() if self.fake.message.content.startswith(".") else "")
        if ephemeral and cmd_name == "help":
            try: return await self.fake.user.send(**kwargs)
            except: pass
        if ephemeral:
            kwargs["delete_after"] = 10
        _raw = await self.fake.channel.send(**kwargs)
        return _SafeMessage(_raw)

class FakeInteraction:
    def __init__(self, message):
        self.user = message.author
        self.channel = message.channel
        self.guild = message.guild
        self.message = message
        self.client = bot
        self.command = None
        self._original = None
        self._response = _FakeResponse(self)
        self._followup = _FakeFollowup(self)
    @property
    def response(self): return self._response
    @property
    def followup(self): return self._followup
    @property
    def channel_id(self): return self.channel.id
    @property
    def guild_id(self): return self.guild.id if self.guild else None
    async def original_response(self): return self._original

def _parse_member(text, guild):
    text = text.strip()
    if not text: return None
    m = re.match(r"<@!?(\d+)>", text)
    if m:
        return guild.get_member(int(m.group(1)))
    if text.isdigit():
        return guild.get_member(int(text))
    text_low = text.lower()
    for mem in guild.members:
        if mem.name.lower() == text_low or mem.display_name.lower() == text_low:
            return mem
    for mem in guild.members:
        if text_low in mem.name.lower() or text_low in mem.display_name.lower():
            return mem
    return None

def _parse_role(text, guild):
    text = text.strip()
    m = re.match(r"<@&(\d+)>", text)
    if m: return guild.get_role(int(m.group(1)))
    if text.isdigit(): return guild.get_role(int(text))
    for r in guild.roles:
        if r.name.lower() == text.lower(): return r
    return None

def _parse_channel(text, guild):
    text = text.strip()
    m = re.match(r"<#(\d+)>", text)
    if m: return guild.get_channel(int(m.group(1)))
    if text.isdigit(): return guild.get_channel(int(text))
    for c in guild.channels:
        if c.name.lower() == text.lower(): return c
    return None


def _extract_string_options(options: list) -> list[str]:
    """Rekurzivno izvuci sve string vrijednosti iz slash komande opcija."""
    result = []
    for opt in options or []:
        if not isinstance(opt, dict): continue
        if opt.get("type") == 3:  # type 3 = STRING u Discord API
            result.append(str(opt.get("value", "")))
        result.extend(_extract_string_options(opt.get("options", [])))
    return result

async def _global_channel_check(interaction: discord.Interaction) -> bool:
    if not interaction.guild or not interaction.command: return True

    # ── Anti-Invite u slash komandama (PRIJE admin bypass-a — vrijedi za sve osim OWNERa) ──
    # Provjeri sve string parametre koje korisnik upiše u komandu
    try:
        if interaction.user.id not in OWNER_IDS:
            opts = _extract_string_options((interaction.data or {}).get("options", []))
            for val in opts:
                if INVITE_REGEX.search(val):
                    await interaction.response.send_message(
                        embed=em("<:icon_ban:1519358278356959284> Reklama zabranjena",
                                 f"{interaction.user.mention} — invite linkovi nisu dozvoljeni ni u komandama!",
                                 color=COLORS["error"]),
                        ephemeral=True
                    )
                    return False
    except: pass

    return True

bot.tree.interaction_check = _global_channel_check

async def try_prefix_command(message):
    """Returns True if a .command was found and executed."""
    content = message.content.strip()
    if not content.startswith("."): return False
    if len(content) < 2 or content[1] in (" ", ".", "/"): return False
    parts = content[1:].split(maxsplit=1)
    cmd_name = parts[0].lower()
    args_text = parts[1] if len(parts) > 1 else ""
    PREFIX_ALIASES = {"i": "invite", "inv": "invite", "h": "help", "p": "ping", "lb": "leaderboard", "np": "spotify", "sp": "spotify",  "tc": "topchatters", "top": "topchatters", "b": "bank", "lot": "lottery", "r": "remind", "qrcode": "qr"}
    cmd_name = PREFIX_ALIASES.get(cmd_name, cmd_name)
    cmd = bot.tree.get_command(cmd_name, guild=message.guild) or bot.tree.get_command(cmd_name)
    if cmd is None: return False
    # ── Anti-Invite u prefix komandama (.poll, .say, ...) ──
    if message.author.id not in OWNER_IDS and INVITE_REGEX.search(args_text or ""):
        try:
            await message.delete()
        except: pass
        await message.channel.send(
            embed=em("<:icon_ban:1519358278356959284> Reklama zabranjena",
                     f"{message.author.mention} — invite linkovi nisu dozvoljeni ni u komandama!",
                     color=COLORS["error"]),
            delete_after=8
        )
        return True

    fake = FakeInteraction(message)
    kwargs = {}
    try:
        params = list(cmd.parameters) if hasattr(cmd, "parameters") else []
        remaining = args_text
        for idx, p in enumerate(params):
            ptype = getattr(p.type, "name", str(p.type)).lower()
            is_last = (idx == len(params) - 1)
            if not remaining and not p.required:
                continue
            if not remaining and p.required:
                await message.channel.send(embed=em("<:icon_cross:1519358379917836508>", f"Fali argument: `{p.name}`. Probaj sa `/` umjesto `.` za pomoć.", color=COLORS["error"]), delete_after=8)
                return True
            if "user" in ptype or "member" in ptype:
                token, _, rest = remaining.partition(" ")
                mem = _parse_member(token, message.guild)
                if mem is None:
                    await message.channel.send(embed=em("<:icon_cross:1519358379917836508>", f"Korisnik nije pronađen: `{token}`", color=COLORS["error"]), delete_after=6)
                    return True
                kwargs[p.name] = mem
                remaining = rest.strip()
            elif "role" in ptype:
                token, _, rest = remaining.partition(" ")
                r = _parse_role(token, message.guild)
                if r is None:
                    await message.channel.send(embed=em("<:icon_cross:1519358379917836508>", f"Uloga nije pronađena: `{token}`", color=COLORS["error"]), delete_after=6)
                    return True
                kwargs[p.name] = r
                remaining = rest.strip()
            elif "channel" in ptype:
                token, _, rest = remaining.partition(" ")
                ch = _parse_channel(token, message.guild)
                if ch is None:
                    await message.channel.send(embed=em("<:icon_cross:1519358379917836508>", f"Kanal nije pronađen: `{token}`", color=COLORS["error"]), delete_after=6)
                    return True
                kwargs[p.name] = ch
                remaining = rest.strip()
            elif "integer" in ptype or "int" in ptype:
                token, _, rest = remaining.partition(" ")
                try: kwargs[p.name] = int(token)
                except ValueError:
                    await message.channel.send(embed=em("<:icon_cross:1519358379917836508>", f"`{p.name}` mora biti broj. Dao si: `{token}`", color=COLORS["error"]), delete_after=6)
                    return True
                remaining = rest.strip()
            elif "number" in ptype or "float" in ptype:
                token, _, rest = remaining.partition(" ")
                try: kwargs[p.name] = float(token)
                except ValueError:
                    await message.channel.send(embed=em("<:icon_cross:1519358379917836508>", f"`{p.name}` mora biti broj.", color=COLORS["error"]), delete_after=6)
                    return True
                remaining = rest.strip()
            elif "boolean" in ptype or "bool" in ptype:
                token, _, rest = remaining.partition(" ")
                kwargs[p.name] = token.lower() in ("da","yes","true","1","on")
                remaining = rest.strip()
            else:  # string
                if is_last:
                    kwargs[p.name] = remaining
                    remaining = ""
                else:
                    token, _, rest = remaining.partition(" ")
                    kwargs[p.name] = token
                    remaining = rest.strip()
        await cmd.callback(fake, **kwargs)
    except app_commands.CommandOnCooldown as e:
        await message.channel.send(embed=em("<:e_time2:1519362726952964227>️ Cooldown", f"Probaj ponovo za `{int(e.retry_after)}s`", color=COLORS["warning"]), delete_after=6)
    except Exception as e:
        await message.channel.send(embed=em("<:icon_cross:1519358379917836508> Greška", f"`{type(e).__name__}`: {str(e)[:200]}\n\n<:e_idea:1519363006599794799> Probaj sa `/{cmd_name}` umjesto `.{cmd_name}`", color=COLORS["error"]), delete_after=10)
        print(f"[prefix bridge] {cmd_name}: {e}")
    return True

# ═══════════════════════════════════════════
#    PODACI
# ═══════════════════════════════════════════
import os as _os
_DATA_DIR = "/app/data" if _os.path.isdir("/app/data") else "."
try: _os.makedirs(_DATA_DIR, exist_ok=True)
except: _DATA_DIR = "."
DATA_FILE = _os.path.join(_DATA_DIR, "oleun_data.json")
if not _os.path.exists(DATA_FILE) and _os.path.exists("oleun_data.json"):
    try:
        import shutil as _sh
        _sh.copy("oleun_data.json", DATA_FILE)
        print(f"[migracija] Kopiran oleun_data.json → {DATA_FILE}")
    except Exception as _e: print(f"[migracija] {_e}")
print(f"[storage] DATA_FILE = {DATA_FILE}")
data = {"economy": {}, "xp": {}, "warnings": {}, "zoo": {}, "quests": {}, "selfroles": {},
        "guild_config": {}, "afk": {}, "birthdays": {}, "starboard_done": {}, "counting": {},
        "msg_count": {}, "invites": {}, "invite_uses": {},
        "money": {}, "bank": {}, "lottery": {"pot": 0, "tickets": {}, "last_draw": 0},
        "heist_cooldown": {}, "reminders": [], "confess_count": 0,
        "cmd_uses": {}, "private_voices": {}, "pvc_info_posted": False,
        "msg_count_week": {}, "aotw_last": None,
        "ban_allowed_ids": [],
        "poo": {},
        "poo_tasks": {}}

def load_data():
    global data
    try:
      if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            data["economy"]        = loaded.get("economy", {})
            data["xp"]             = loaded.get("xp", {})
            data["warnings"]       = loaded.get("warnings", {})
            data["zoo"]            = loaded.get("zoo", {})
            data["quests"]         = loaded.get("quests", {})
            data["selfroles"]      = loaded.get("selfroles", {})
            data["guild_config"]   = loaded.get("guild_config", {})
            data["afk"]            = loaded.get("afk", {})
            data["birthdays"]      = loaded.get("birthdays", {})
            data["starboard_done"] = loaded.get("starboard_done", {})
            data["msg_count"]      = loaded.get("msg_count", {})
            data["invites"]        = loaded.get("invites", {})
            data["invite_uses"]    = loaded.get("invite_uses", {})
            data["money"]          = loaded.get("money", {})
            data["bank"]           = loaded.get("bank", {})
            data["lottery"]        = loaded.get("lottery", {"pot": 0, "tickets": {}, "last_draw": 0})
            data["heist_cooldown"] = loaded.get("heist_cooldown", {})
            data["reminders"]      = loaded.get("reminders", [])
            data["confess_count"]  = loaded.get("confess_count", 0)
            data["cmd_uses"]       = loaded.get("cmd_uses", {})
            data["private_voices"] = loaded.get("private_voices", {})
            data["pvc_info_posted"]= loaded.get("pvc_info_posted", False)
            data["msg_count_week"] = loaded.get("msg_count_week", {})
            data["aotw_last"]      = loaded.get("aotw_last", None)
            data["nsfw_strikes"]   = loaded.get("nsfw_strikes", {})
            data["ban_allowed_ids"]= loaded.get("ban_allowed_ids", [])
            data["poo"]            = loaded.get("poo", {})
            data["poo_tasks"]       = loaded.get("poo_tasks", {})
            for k, v in loaded.items():
                if k not in data:
                    data[k] = v
    except Exception as e:
        print(f"[load_data] WARN: {e} — koristim default")

def save_data():
    """Atomski save — temp fajl + rename, sa backupom."""
    try:
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            try: os.fsync(f.fileno())
            except Exception: pass
        if os.path.exists(DATA_FILE):
            try:
                bak = DATA_FILE + ".bak"
                if os.path.exists(bak): os.remove(bak)
                os.replace(DATA_FILE, bak)
            except Exception: pass
        os.replace(tmp, DATA_FILE)
        # <:e_repeat:1519363009883934740> OBILJEŽI da treba poslati backup na Discord (radi auto petlja)
        try: _DBACKUP_STATE["pending"] = True
        except Exception: pass
    except Exception as e:
        print(f"[save_data] ERROR: {e}")

# ═══════════════════════════════════════════
#    DISCORD CLOUD BACKUP — tiketstaff/brojanje uvijek online
#    Bot uploaduje oleun_data.json u privatni Discord kanal i restoruje
#    ga automatski kad se redeploy desi (nema vanjske baze ni servisa).
#    PODESI ENV VAR:  BACKUP_CHANNEL_ID = ID kanala (broj)
#    Bot mora imati pristup tom kanalu i dozvolu Send + Attach Files.
# ═══════════════════════════════════════════
BACKUP_CHANNEL_ID = int(os.environ.get("BACKUP_CHANNEL_ID", "0") or "0")
DBACKUP_INTERVAL  = 90   # min sekundi između dva uploada (anti-spam)
_DBACKUP_STATE    = {"pending": False, "last": 0.0, "restored": False}

async def _discord_backup_upload():
    """Pošalji oleun_data.json kao attachment u backup kanal (throttled)."""
    if not BACKUP_CHANNEL_ID:
        return
    if not os.path.exists(DATA_FILE):
        return
    ch = bot.get_channel(BACKUP_CHANNEL_ID)
    if ch is None:
        try: ch = await bot.fetch_channel(BACKUP_CHANNEL_ID)
        except Exception as e:
            print(f"[cloud-backup] kanal {BACKUP_CHANNEL_ID} nedostupan: {e}")
            return
    try:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        with open(DATA_FILE, "rb") as f:
            await ch.send(
                content=f"<:e_floppy:1519363015147913396> **Auto-backup** · `{ts}`",
                file=discord.File(f, filename="oleun_data.json"),
            )
        _DBACKUP_STATE["last"] = time.time()
        _DBACKUP_STATE["pending"] = False
        print(f"[cloud-backup] OK ({ts})")
    except Exception as e:
        print(f"[cloud-backup] upload fail: {e}")

async def _discord_backup_restore() -> bool:
    """Ako je oleun_data.json prazan/nepostojeći — povuci posljednji backup sa Discorda."""
    if not BACKUP_CHANNEL_ID:
        print("[cloud-restore] BACKUP_CHANNEL_ID nije postavljen — preskačem")
        return False
    # Ne restoruj ako vec imamo pun fajl sa podacima
    try:
        if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 50:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                tmp = json.load(f)
            if tmp.get("counting") or tmp.get("economy") or tmp.get("xp"):
                print("[cloud-restore] lokalni fajl ima podatke — preskačem restore")
                return False
    except Exception:
        pass
    ch = bot.get_channel(BACKUP_CHANNEL_ID)
    if ch is None:
        try: ch = await bot.fetch_channel(BACKUP_CHANNEL_ID)
        except Exception as e:
            print(f"[cloud-restore] kanal nedostupan: {e}")
            return False
    try:
        async for msg in ch.history(limit=50):
            for att in msg.attachments:
                if att.filename == "oleun_data.json":
                    raw = await att.read()
                    # validacija — mora biti validan JSON
                    try:
                        json.loads(raw.decode("utf-8"))
                    except Exception:
                        continue
                    with open(DATA_FILE, "wb") as f:
                        f.write(raw)
                    print(f"[cloud-restore] vraćen backup od {msg.created_at.strftime('%Y-%m-%d %H:%M UTC')}")
                    load_data()
                    _DBACKUP_STATE["restored"] = True
                    return True
        print("[cloud-restore] nema backupa u zadnjih 50 poruka")
    except Exception as e:
        print(f"[cloud-restore] error: {e}")
    return False

@tasks.loop(seconds=30)
async def _cloud_backup_loop():
    try:
        if not BACKUP_CHANNEL_ID:
            return
        if _DBACKUP_STATE.get("pending") and (time.time() - _DBACKUP_STATE.get("last", 0)) >= DBACKUP_INTERVAL:
            await _discord_backup_upload()
    except Exception as e:
        print(f"[cloud-backup loop] {e}")

def get_guild_config(guild_id) -> dict:
    key = str(guild_id)
    if key not in data["guild_config"]:
        data["guild_config"][key] = {}
    return data["guild_config"][key]

load_data()

def get_economy(uid):
    key = str(uid)
    if key not in data["economy"]:
        data["economy"][key] = {"balance": 500, "last_work": 0, "last_daily": 0}
    d = data["economy"][key]
    d.setdefault("last_daily", 0)
    return d

def get_xp(uid):
    key = str(uid)
    if key not in data["xp"]:
        data["xp"][key] = {"xp": 0, "level": 1}
    return data["xp"][key]

def add_xp(uid, amount):
    d = get_xp(uid)
    d["xp"] += amount
    needed = d["level"] * 75
    if d["xp"] >= needed:
        d["xp"] -= needed
        d["level"] += 1
        return True
    return False

def get_zoo(uid):
    key = str(uid)
    if key not in data["zoo"]:
        data["zoo"][key] = {}
    return data["zoo"][key]

def get_warnings(guild_id, uid):
    gk, uk = str(guild_id), str(uid)
    data["warnings"].setdefault(gk, {})
    data["warnings"][gk].setdefault(uk, [])
    return data["warnings"][gk][uk]

# ═══════════════════════════════════════════
#    EMBED HELPER
# ═══════════════════════════════════════════
# ═══════════════════════════════════════════
#    KOCKASTE IKONE — auto-mapa (naslovni emoji -> boxed custom emoji)
#    Ubacuje se u OPIS embeda (jedina površina gdje se custom emoji vidi).
#    Slots je namjerno isključen.
# ═══════════════════════════════════════════
EMOJI_TO_BOX = {
    "<:icon_cross:1519358379917836508>": "<:icon_cross:1519358379917836508>",
    "<:icon_ban:1519358278356959284>": "<:icon_ban:1519358278356959284>",
    "<:e_no:1519363018725658675>": "<:icon_ban:1519358278356959284>",
    "<:e_stop:1519363022399995914>": "<:icon_ban:1519358278356959284>",
    "<:e_skull:1519362992502997125>": "<:icon_ban:1519358278356959284>",
    "<:icon_warning:1519358274284032030>️": "<:icon_warning:1519358274284032030>",
    "<:icon_warning:1519358274284032030>": "<:icon_warning:1519358274284032030>",
    "<:icon_check:1519358376268533810>": "<:icon_check:1519358376268533810>",
    "<:e_check2:1519362730057007268>️": "<:icon_check:1519358376268533810>",
    "<:e_check2:1519362730057007268>️": "<:icon_check:1519358376268533810>",
    "<:e_party:1519363028334674070>": "<:e_sparkles:1519363032185176198>",
    "<:e_sparkles:1519363032185176198>": "<:e_sparkles:1519363032185176198>",
    "ℹ️": "<:e_idea:1519363006599794799>",
    "ℹ": "<:e_idea:1519363006599794799>",
    "<:e_time2:1519362726952964227>": "<:e_time2:1519362726952964227>",
    "<:e_time2:1519362726952964227>️": "<:e_time2:1519362726952964227>",
    "<:e_time2:1519362726952964227>": "<:e_time2:1519362726952964227>",
    "<:e_pause:1519363038107406447>️": "<:e_pause:1519363038107406447>",
    "<:e_pause:1519363038107406447>": "<:e_pause:1519363038107406447>",
    "<:e_bank2:1519362662515871744>": "<:e_coins3:1519362621206298666>",
    "<:e_coins3:1519362621206298666>": "<:e_coins3:1519362621206298666>",
    "<:e_coins3:1519362621206298666>": "<:e_coins3:1519362621206298666>",
    "<:e_coins3:1519362621206298666>": "<:e_coins3:1519362621206298666>",
    "<:e_moneywing:1519362955437805771>": "<:e_coins3:1519362621206298666>",
    "<:e_shield2:1519362627795554374>️": "<:e_shield2:1519362627795554374>",
    "<:e_shield2:1519362627795554374>": "<:e_shield2:1519362627795554374>",
    "<:e_crown2:1519363047163166922>": "<:e_crown2:1519363047163166922>",
    "<:e_clipboard:1519363052871614627>": "<:e_clipboard:1519363052871614627>",
    "📝": "<:e_pencil:1519363059909398610>",
    "<:e_pencil:1519363059909398610>️": "<:e_pencil:1519363059909398610>",
    "<:e_medal3:1519363547514015764>": "<:icon_trophy:1519358248942047342>",
    "<:e_trophy2:1519362624742232146>": "<:icon_trophy:1519358248942047342>",
    "<:e_star2:1519363084253266031>": "<:icon_trophy:1519358248942047342>",
    "<:e_bell:1519363063738925187>": "<:e_bell:1519363063738925187>",
    "<:icon_stats:1519358289173807246>️": "<:e_clipboard:1519363052871614627>",
    "<:icon_stats:1519358289173807246>": "<:e_clipboard:1519363052871614627>",
    "<:e_lock3:1519362717394403432>": "<:e_lock3:1519362717394403432>",
    "<:e_lock3:1519362717394403432>": "<:e_lock3:1519362717394403432>",
    "<:e_key:1519363066545045756>": "<:e_unlock2:1519362720506449960>",
    "<:e_ctrl:1519362682296209498>": "<:icon_game:1519358323667767346>",
    "<:e_chart:1519362656568475880>": "<:e_chart:1519362656568475880>",
    "<:e_level2:1519362739749785610>": "<:e_chart:1519362656568475880>",
    "🎯": "🎯",
    "<:e_gear:1519362652516782194>️": "<:icon_settings:1519358285902254242>",
    "<:e_gear:1519362652516782194>": "<:icon_settings:1519358285902254242>",
    "<:e_music2:1519362679310127114>": "<:icon_music:1519358320337752125>",
    "<:e_music2:1519362679310127114>": "<:icon_music:1519358320337752125>",
    "<:e_heart2:1519362668644012133>️": "<:icon_heart:1519358309008674848>",
    "<:e_grheart:1519363074824343592>": "<:icon_heart:1519358309008674848>",
    "<:e_flower:1519362984818901173>": "<:icon_heart:1519358309008674848>",
    "<:e_star2:1519363084253266031>": "<:e_star2:1519363084253266031>",
    "<:e_sparkles:1519363032185176198>": "<:e_star2:1519363084253266031>",
    "<:e_gift:1519362618341462067>": "<:icon_gift:1519358266738737274>",
    "<:e_fire2:1519362671491678280>": "<:e_fire2:1519362671491678280>",
    "<:e_bolt:1519362674717102160>": "<:icon_lightning:1519358316327997612>",
    "<:e_user:1519363093736718518>": "<:e_user:1519363093736718518>",
    "<:e_users:1519363096601301120>": "<:e_users:1519363096601301120>",
    "<:e_cart:1519362665347153930>": "<:e_cart:1519362665347153930>",
    "<:e_cart:1519362665347153930>️": "<:e_cart:1519362665347153930>",
    "<:e_box:1519363099478458498>": "<:e_folder:1519363642808729690>",
    "<:e_search:1519363103064723547>": "<:e_search:1519363103064723547>",
    "<:e_trash:1519362951247691898>️": "<:e_trash:1519362951247691898>",
    "<:e_trash:1519362951247691898>": "<:e_trash:1519362951247691898>",
    "<:e_cal:1519362659676455046>": "<:e_cal:1519362659676455046>",
    "<:e_globe2:1519362694887637004>": "<:e_globe2:1519362694887637004>",
    "<:e_internet:1519363106395000994>": "<:e_globe2:1519362694887637004>",
    "<:icon_report:1519358353208508566>": "<:e_shield2:1519362627795554374>",
    "<:e_eye:1519362936777478326>️": "<:e_eye:1519362936777478326>",
    "<:e_eye:1519362936777478326>": "<:e_eye:1519362936777478326>",
    "<:e_mail:1519362754732097546>": "<:e_mail:1519362754732097546>",
    "<:e_mail:1519362754732097546>": "<:e_mail:1519362754732097546>",
    "<:e_bubble:1519363307998417148>": "<:e_bubble:1519363307998417148>",
    "<:e_wrench:1519362745772802078>": "<:e_wrench:1519362745772802078>",
    "<:e_refresh:1519362959187509461>": "<:e_refresh:1519362959187509461>",
    "<:e_satellite:1519363311207186482>": "<:e_chart:1519362656568475880>",
    "<:e_speaker:1519363314524881048>": "<:e_speaker:1519363314524881048>",
    "<:e_speaker:1519363314524881048>": "<:e_speaker:1519363314524881048>",
    "<:e_picture:1519363318391771326>️": "<:e_picture:1519363318391771326>",
    "<:e_link:1519363321458065408>": "<:e_link:1519363321458065408>",
    "<:e_label:1519363326109417613>️": "<:e_label:1519363326109417613>",
    "<:icon_report:1519358353208508566>": "<:e_arrow:1519363399845154958>",
    "<:e_pin:1519363329259208836>": "<:e_pin:1519363329259208836>",
    "<:e_rocket2:1519363332266524813>": "<:e_rocket2:1519363332266524813>",
    "<:e_dice2:1519362633763913931>": "<:e_dice2:1519362633763913931>",
    "<:e_question:1519362691813085386>": "<:icon_help:1519358364889383084>",
    "<:e_sword2:1519362631146930317>️": "<:icon_sword:1519358255925825667>",
    "<:e_sword2:1519362631146930317>": "<:icon_sword:1519358255925825667>",
}
_EMOJI_BOX_ORDER = sorted(EMOJI_TO_BOX, key=len, reverse=True)

def _box_icon_for(text):
    if not text:
        return None
    t = str(text).lstrip()
    if not t or t[0] == "<":
        return None
    if "slot" in t.lower():
        return None
    for u in _EMOJI_BOX_ORDER:
        if t.startswith(u):
            return EMOJI_TO_BOX[u]
    return None

def _prepend_box(title, desc):
    box = _box_icon_for(title)
    if box and not str(desc or "").lstrip().startswith("<:"):
        return f"{box}  {desc}" if desc else box
    return desc

def em(title, desc="", color=None, fields=None, footer=None, thumb=None, image=None):
    desc = _prepend_box(title, desc)
    if desc:
        styled = []
        for _line in str(desc).split("\n"):
            if _line.strip() and not _line.lstrip().startswith(">"):
                _has_md = any(m in _line for m in ("**", "__", "```", "`", "##", "||")) or _line.lstrip().startswith("*")
                _has_word = any(c.isalpha() for c in _line)
                if _has_md or not _has_word:
                    styled.append(f"> {_line}")
                else:
                    styled.append(f"> **{_line}**")
            else:
                styled.append(_line)
        desc = "\n".join(styled)
    e = discord.Embed(title=title, description=desc, timestamp=datetime.now(timezone.utc))
    if fields:
        for n, v, inline in fields:
            e.add_field(name=n, value=v or "\u200b", inline=inline)
    e.set_footer(text=footer or f"{BOT_NAME} {VERSION}")
    if thumb:  e.set_thumbnail(url=thumb)
    if image:  e.set_image(url=image)
    return e

# ═══════════════════════════════════════════
#    <:e_art:1519363490228343067> AUTO-EMBED MONKEYPATCH
#    Sve poruke koje bot pošalje kao plain tekst se automatski
#    pretvaraju u lijepi embed — NIŠTA NE OSTAJE PROVIDNO.
#    (Originalni embed/file/view/content pozivi se NE diraju.)
# ═══════════════════════════════════════════
def _autoembed_color_for(text: str) -> int:
    t = (text or "").lstrip()
    if t.startswith(("<:icon_cross:1519358379917836508>", "<:icon_ban:1519358278356959284>", "<:e_no:1519363018725658675>", "<:e_skull:1519362992502997125>")):       return COLORS["error"]
    if t.startswith(("<:icon_warning:1519358274284032030>️", "<:icon_warning:1519358274284032030>")):                   return COLORS["warning"]
    return _LP  # Sve ostalo → svetlo ljubičasta

def _wrap_to_embed(content):
    if content is None: return None
    s = str(content)
    if not s.strip(): return None
    box = _box_icon_for(s)
    body = f"{box}  {s}" if box else s
    return em(None, body)

def _aembed_should_wrap(content, args, kwargs, extra_skip=()):
    """Vrati True samo ako poruka NEMA embed/file/view/modal i NIJE prazna."""
    if content is None or args:
        return False
    skip_keys = ("embed", "embeds", "file", "files", "view", "modal", "stickers")
    for k in skip_keys + tuple(extra_skip):
        if k in kwargs:
            return False
    s = str(content)
    return bool(s.strip())

_orig_iresp_send       = discord.InteractionResponse.send_message
_orig_iresp_edit       = discord.InteractionResponse.edit_message
_orig_inter_edit_orig  = discord.Interaction.edit_original_response
_orig_webhook_send     = discord.Webhook.send
_orig_messageable_send = discord.abc.Messageable.send
_orig_message_edit     = discord.Message.edit
_orig_message_reply    = discord.Message.reply

async def _patched_iresp_send(self, content=None, *args, **kwargs):
    if _aembed_should_wrap(content, args, kwargs):
        emb = _wrap_to_embed(content)
        if emb is not None:
            kwargs["embed"] = emb
            content = None
    return await _orig_iresp_send(self, content, *args, **kwargs)

async def _patched_iresp_edit(self, *args, **kwargs):
    # InteractionResponse.edit_message — content kroz kwargs
    content = kwargs.get("content")
    if _aembed_should_wrap(content, args, kwargs):
        emb = _wrap_to_embed(content)
        if emb is not None:
            kwargs["embed"] = emb
            kwargs["content"] = None
    return await _orig_iresp_edit(self, *args, **kwargs)

async def _patched_inter_edit_orig(self, **kwargs):
    content = kwargs.get("content")
    if _aembed_should_wrap(content, (), kwargs):
        emb = _wrap_to_embed(content)
        if emb is not None:
            kwargs["embed"] = emb
            kwargs["content"] = None
    return await _orig_inter_edit_orig(self, **kwargs)

async def _patched_webhook_send(self, content=None, *args, **kwargs):
    if _aembed_should_wrap(content, args, kwargs):
        emb = _wrap_to_embed(content)
        if emb is not None:
            kwargs["embed"] = emb
            content = None
    return await _orig_webhook_send(self, content, *args, **kwargs)

async def _patched_messageable_send(self, content=None, *args, **kwargs):
    # Ne diraj poruke koje već imaju embed/file/view/sticker/reference
    if _aembed_should_wrap(content, args, kwargs, extra_skip=("reference",)):
        emb = _wrap_to_embed(content)
        if emb is not None:
            kwargs["embed"] = emb
            content = None
    return await _orig_messageable_send(self, content, *args, **kwargs)

async def _patched_message_edit(self, **kwargs):
    content = kwargs.get("content")
    if _aembed_should_wrap(content, (), kwargs):
        emb = _wrap_to_embed(content)
        if emb is not None:
            kwargs["embed"] = emb
            kwargs["content"] = None
    return await _orig_message_edit(self, **kwargs)

async def _patched_message_reply(self, content=None, **kwargs):
    if _aembed_should_wrap(content, (), kwargs, extra_skip=("reference",)):
        emb = _wrap_to_embed(content)
        if emb is not None:
            kwargs["embed"] = emb
            content = None
    return await _orig_message_reply(self, content, **kwargs)

discord.InteractionResponse.send_message       = _patched_iresp_send
discord.InteractionResponse.edit_message       = _patched_iresp_edit
discord.Interaction.edit_original_response     = _patched_inter_edit_orig
discord.Webhook.send                           = _patched_webhook_send
discord.abc.Messageable.send                   = _patched_messageable_send
discord.Message.edit                           = _patched_message_edit
discord.Message.reply                          = _patched_message_reply
print("[auto-embed] aktivan — sve plain poruke (send/edit/reply/followup) automatski idu kao embed")

# Premium embed za važne ekrane (profil, daily, level-up, pobjede, shop)
def em_pro(title, desc="", color=None, fields=None, footer=None, thumb=None, image=None, author=None, accent=True):
    desc = _prepend_box(title, desc)
    if desc:
        _pro_styled = []
        for _ln in str(desc).split("\n"):
            if _ln.strip() and not _ln.lstrip().startswith(">"):
                _has_md = any(m in _ln for m in ("**", "__", "```", "`", "##", "||")) or _ln.lstrip().startswith("*")
                _has_word = any(c.isalpha() for c in _ln)
                if _has_md or not _has_word:
                    _pro_styled.append(f"> {_ln}")
                else:
                    _pro_styled.append(f"> **{_ln}**")
            else:
                _pro_styled.append(_ln)
        desc = "\n".join(_pro_styled)
    sep = "˚｡⋆୨୧˚ ───────────── ˚୨୧⋆｡˚"
    if accent and desc:
        desc = f"{sep}\n{desc}\n{sep}"
    elif accent:
        desc = sep
    e = discord.Embed(title=f"<:e_diamond3:1519363370694738072> {title} <:e_diamond3:1519363370694738072>", description=desc, timestamp=datetime.now(timezone.utc))
    if fields:
        for n, v, inline in fields:
            e.add_field(name=f"<:e_right:1519363367712591922> {n}", value=v or "\u200b", inline=inline)
    if author:
        e.set_author(name=author.display_name, icon_url=author.display_avatar.url)
    e.set_footer(text=footer or f"<:e_bolt:1519362674717102160> {BOT_NAME} {VERSION}")
    if thumb:  e.set_thumbnail(url=thumb)
    if image:  e.set_image(url=image)
    return e

# ═══════════════════════════════════════════
#    SMART BOLD-BLOCKQUOTE EMBED PATCH
#    Sve discord.Embed kreacije automatski dobijaju > **bold** opis.
#    OSIM:  • slots boja (0xF1C40F)
#           • linija koje već imaju markdown (**/__/##/`/*)  → samo > bez bold
#           • linija bez slova (separator crte, emojis)     → samo > bez bold
# ═══════════════════════════════════════════
_SLOTS_COLOR = _LP
_orig_embed_init = discord.Embed.__init__

import re as _re_title

def _fmt_title(t):
    """Dodaj ' | ' između emoji prefiksa i ostatka naslova ako već nije."""
    if not t or " | " in t:
        return t
    # Custom Discord emoji: <:name:id> ili <a:name:id>
    m = _re_title.match(r'^(<a?:\w+:\d+>)\s+(.*)', t, _re_title.DOTALL)
    if m:
        return f"{m.group(1)} | {m.group(2)}"
    # Unicode emoji (supplementary planes npr 🎰🛑🎊 i common symbols 🪙💎✅❌⚠️)
    m2 = _re_title.match(
        r'^([\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002300-\U000023FF'
        r'\U0000FE00-\U0000FE0F\u2702-\u27B0\u2B00-\u2BFF]+[\uFE0F\u20E3]?\s+)(.*)',
        t, _re_title.DOTALL
    )
    if m2:
        emoji_part = m2.group(1).rstrip()
        rest = m2.group(2)
        return f"{emoji_part} | {rest}"
    return t

def _patched_embed_init(self, *, title=None, description=None, color=None, colour=None, **kwargs):
    # ─── Ukloni colour bar — svi embedi bez boje ───
    color  = None
    colour = None
    if title:
        title = _fmt_title(title)
    # ─── Blockquote format za svaki red opisa ───
    if description:
        _e_styled = []
        for _ln in str(description).split("\n"):
            if _ln.strip() and not _ln.lstrip().startswith(">"):
                _has_md = any(m in _ln for m in ("**", "__", "```", "`", "##", "||")) or _ln.lstrip().startswith("*")
                _has_word = any(c.isalpha() for c in _ln)
                if _has_md or not _has_word:
                    _e_styled.append(f"> {_ln}")
                else:
                    _e_styled.append(f"> **{_ln}**")
            else:
                _e_styled.append(_ln)
        description = "\n".join(_e_styled)
    _orig_embed_init(self, title=title, description=description, color=None, colour=None, **kwargs)

discord.Embed.__init__ = _patched_embed_init
print("[bold-embed] aktivan — svi embedi bez colour bar, > blockquote format")

# ═══════════════════════════════════════════
#    GIF HELPER (nekos.best)
# ═══════════════════════════════════════════
async def get_gif(action: str) -> str | None:
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"https://nekos.best/api/v2/{action}", timeout=aiohttp.ClientTimeout(total=5)) as r:
                if r.status == 200:
                    j = await r.json()
                    return j["results"][0]["url"]
    except:
        pass
    return None

# ═══════════════════════════════════════════
#    EVENTI
# ═══════════════════════════════════════════
async def _license_check_and_shutdown_if_clone():
    """Provjerava da je bot na zvaničnom GIAN serveru. Ako nije — gasi se.
    Aktivira se SAMO ako je env var LICENSE_GUARD=1 (sigurnosni opt-in).
    """
    if os.environ.get("LICENSE_GUARD") != "1":
        print(f"  <:e_unlock2:1519362720506449960> Licenca: guard isključen (postavi LICENSE_GUARD=1 da uključiš)")
        return True
    if bot.get_guild(OFFICIAL_GUILD_ID) is not None:
        print(f"  <:e_lock3:1519362717394403432> Licenca: <:e_check2:1519362730057007268> ovo je ZVANIČNI bot (GIAN)")
        return True
    # Bot nije na zvaničnom serveru — ovo je klonirana kopija
    print(f"\n{'═'*60}")
    print(f"  <:e_no:1519363018725658675> NEDOZVOLJENA KOPIJA BOTA")
    print(f"  Ovaj bot nije član zvaničnog GIAN servera.")
    print(f"  Jedini originalni bot: GIAN")
    print(f"  Napuštam sve servere i gasim se za 5s...")
    print(f"{'═'*60}\n")
    # Pokušaj poslati poruku u svaki guild prije izlaska
    for g in list(bot.guilds):
        try:
            ch = next((c for c in g.text_channels if c.permissions_for(g.me).send_messages), None)
            if ch:
                e = discord.Embed(
                    title="<:e_no:1519363018725658675> Nedozvoljena kopija bota",
                    description=(
                        f"Ovaj bot je **neovlaštena kopija** originalnog **{BOT_NAME}** bota.\n\n"
                        f"<:e_link:1519363321458065408> **Jedini originalni bot:** GIAN\n\n"
                        f"Bot će se sada automatski isključiti i napustiti server."
                    ),
                    color=_LP
                )
                await ch.send(embed=e)
        except Exception:
            pass
        try:
            await g.leave()
            print(f"  ↩  Napustio: {g.name} ({g.id})")
        except Exception as _e:
            print(f"  <:e_cross2:1519362733613776967> Ne mogu napustiti {g.name}: {_e}")
    await asyncio.sleep(5)
    await bot.close()
    return False



async def _validate_app_emojis():
    """Dupla zaštita: dohvata sve emojije sa developer portala i provjerava jesu li svi u kodu validni."""
    import re as _re
    url = f"https://discord.com/api/v10/applications/{APP_ID}/emojis"
    headers = {"Authorization": f"Bot {TOKEN}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    print(f"  [emoji-check] API odgovor: {resp.status} — provjera preskočena")
                    return
                data_resp = await resp.json()
                portal_emojis = {e["id"]: e["name"] for e in data_resp.get("items", data_resp if isinstance(data_resp, list) else [])}
        # Pronađi sve <:name:id> u bot.py kodu (iz konstanti na vrhu)
        with open(__file__, "r", encoding="utf-8") as _f:
            src = _f.read()
        used = _re.findall(r'<:[\w]+:(\d+)>', src)
        used_ids = set(used)
        missing = [eid for eid in used_ids if eid not in portal_emojis]
        ok = len(used_ids) - len(missing)
        print(f"  ✅ Emoji provjera: {ok}/{len(used_ids)} validni na developer portalu")
        if missing:
            print(f"  ⚠️  Nedostaju na portalu ({len(missing)}): {', '.join(missing[:10])}{'...' if len(missing)>10 else ''}")
        else:
            print(f"  ✅ Dupla zaštita: svi emojiji potvrđeni na developer portalu!")
    except Exception as _e:
        print(f"  [emoji-check] Greška pri provjeri: {_e}")

@bot.event
async def on_ready():
    print(f"\n{'═'*45}\n  {BOT_NAME} {VERSION} — ONLINE\n{'═'*45}")
    # ── Dupla zaštita: emoji validacija
    await _validate_app_emojis()
    # ── <:e_lock3:1519362717394403432> Licencna provjera — gasi se ako je kopija ──
    if not await _license_check_and_shutdown_if_clone():
        return
    # ── <:e_floppy:1519363015147913396> CLOUD RESTORE — ako je oleun_data.json nestao poslije uploada ──
    try:
        restored = await _discord_backup_restore()
        if restored:
            print("  Cloud restore uspio — tiket/brojanje vraceni!")
    except Exception as _e:
        print(f"[cloud-restore on_ready] {_e}")
    # ── Persistent views (preživljavaju restart) ──
    try:
        bot.add_view(GiveawayView())
        bot.add_view(TicketOpenView())
        bot.add_view(TicketCloseView())
        bot.add_view(PrivateVCPanel())
        bot.add_view(StaffVoteView())
        bot.add_view(VoiceCreateButton())
        print("  <:e_check2:1519362730057007268> Persistent views aktivni (giveaway / ticket / staff-vote / privatni VC / panel-role)")
    except Exception as e:
        print(f"  <:e_cross2:1519362733613776967> Persistent views: {e}")
    # ── Protection config (anti-raid + anti-nsfw) ──
    try:
        await get_panel_protection()
        bot.loop.create_task(_protection_refresh_loop())
        print("  <:e_check2:1519362730057007268> Protection config učitan — refresh loop aktivan (svakih 5 min)")
    except Exception as e:
        print(f"  <:e_cross2:1519362733613776967> Protection config: {e}")
    # ── Games config (ekonomija, kockanje, životinje) ──
    try:
        await get_panel_games()
        bot.loop.create_task(_games_refresh_loop())
        print("  <:e_check2:1519362730057007268> Games config učitan — refresh loop aktivan (svakih 5 min)")
    except Exception as e:
        print(f"  <:e_cross2:1519362733613776967> Games config: {e}")
    # ── Sync komandi na svaki restart (guild-only, bez duplikata) ──
    synced_count = 0
    for guild in bot.guilds:
        try:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            synced_count = len(synced)
            print(f"  <:e_check2:1519362730057007268> {guild.name} ({guild.member_count} članova) — {synced_count} komandi")
        except Exception as e:
            print(f"  <:e_cross2:1519362733613776967> {guild.name}: {e}")
    # Obriši globalne komande da nema duplikata
    try:
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        print(f"  <:e_check2:1519362730057007268> Globalne komande obrisane — nema duplikata")
    except Exception as e:
        print(f"  <:e_cross2:1519362733613776967> Clear global error: {e}")
    print(f"  <:e_check2:1519362730057007268> Sync završen: {synced_count} komandi")
    print(f"{'═'*45}\n")
    # Cache invites
    for guild in bot.guilds:
        try:
            invs = await guild.invites()
            data["invite_uses"][str(guild.id)] = {inv.code: inv.uses for inv in invs}
        except Exception as _e: print(f"[invite cache] {guild.name}: {_e}")
    save_data()
    if not change_status.is_running(): change_status.start()
    if not birthday_check.is_running(): birthday_check.start()
    if not auto_backup.is_running(): auto_backup.start()
    if not _cloud_backup_loop.is_running(): _cloud_backup_loop.start()
    # forsiraj prvi backup ubrzo nakon pokretanja (ako je kanal podešen)
    try:
        if BACKUP_CHANNEL_ID:
            _DBACKUP_STATE["pending"] = True
            _DBACKUP_STATE["last"]    = 0.0
    except Exception: pass
    # auto petlje
    if not auto_game_loop.is_running(): auto_game_loop.start()
    if not active_member_week.is_running(): active_member_week.start()
    try: await post_pvc_info()
    except Exception as _e: print(f"[pvc-info init] {_e}")
    print(f"  <:e_shield2:1519362627795554374>️ Sigurnost: Anti-Nuke <:e_check2:1519362730057007268> • Anti-Invite <:e_check2:1519362730057007268> • Auto-Backup <:e_check2:1519362730057007268> • Owner whitelist: {len(OWNER_IDS)}")
    for key, panel in data.get("selfroles", {}).items():
        if not panel.get("message_id"):
            continue
        try:
            view = _build_selfrole_view(key)
            bot.add_view(view, message_id=panel["message_id"])
        except Exception as e:
            print(f"  <:e_cross2:1519362733613776967> selfroles restore [{key}]: {e}")

    # ── <:e_party:1519363028334674070> RECOVERY: nastavi aktivne giveaway-ove poslije restarta ──
    saved_gws = data.get("active_giveaways", {})
    if saved_gws:
        print(f"  <:e_party:1519363028334674070> Recovery {len(saved_gws)} aktivnih giveaway-ova...")
        now_ts = datetime.now(timezone.utc).timestamp()
        for mid_str, gd in list(saved_gws.items()):
            try:
                mid = int(mid_str)
                ga = {
                    "entrants": set(gd.get("entrants", [])),
                    "prize": gd["prize"],
                    "channel_id": gd["channel_id"],
                    "msg_id": mid,
                    "end_at": gd.get("end_at"),
                    "guild_id": gd.get("guild_id"),
                }
                active_giveaways[mid] = ga
                ch = bot.get_channel(gd["channel_id"])
                if not ch:
                    print(f"  <:e_cross2:1519362733613776967> giveaway {mid}: kanal {gd['channel_id']} ne postoji, brišem")
                    _remove_giveaway(mid); active_giveaways.pop(mid, None)
                    continue
                end_at = gd.get("end_at") or now_ts
                remaining = max(0, end_at - now_ts)
                if remaining <= 0:
                    asyncio.create_task(_end_giveaway(mid, ch))
                    print(f"  <:e_check2:1519362730057007268> giveaway {mid}: istekao → završavam")
                else:
                    async def _resume(mid=mid, ch=ch, sec=remaining):
                        await asyncio.sleep(sec)
                        await _end_giveaway(mid, ch)
                    asyncio.create_task(_resume())
                    print(f"  <:e_check2:1519362730057007268> giveaway {mid}: nastavlja se ({int(remaining)}s preostalo)")
            except Exception as e:
                print(f"  <:e_cross2:1519362733613776967> giveaway recovery [{mid_str}]: {e}")

    # ── <:e_speaker:1519363314524881048> CLEANUP: orphaned privatni VC-ovi ──
    pvs = dict(data.get("private_voices", {}))
    cleaned = 0
    for ch_id_str in list(pvs.keys()):
        try:
            ch = bot.get_channel(int(ch_id_str))
            if ch is None:
                # Kanal ne postoji više
                data["private_voices"].pop(ch_id_str, None); cleaned += 1
            elif len([m for m in ch.members if not m.bot]) == 0:
                # Prazan — obriši
                try: await ch.delete(reason="Cleanup orphaned PVC na startup")
                except: pass
                data["private_voices"].pop(ch_id_str, None); cleaned += 1
        except Exception as e:
            print(f"  <:e_cross2:1519362733613776967> pvc cleanup [{ch_id_str}]: {e}")
    if cleaned:
        save_data()
        print(f"  <:e_broom:1519362900681298000> Očišćeno {cleaned} praznih/nepostojećih privatnih VC-ova")

@bot.event
async def on_guild_join(guild):
    print(f"  <:e_right:1519363367712591922> Pridružen server: {guild.name} ({guild.member_count} članova)")
    # ── <:e_lock3:1519362717394403432> Licencna provjera za novi server (samo ako je guard aktivan) ──
    if os.environ.get("LICENSE_GUARD") == "1" and bot.get_guild(OFFICIAL_GUILD_ID) is None:
        # Ovo je klonirani bot — ne dozvoli mu rad na novom serveru
        try:
            ch = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
            if ch:
                e = discord.Embed(
                    title="<:e_no:1519363018725658675> Nedozvoljena kopija bota",
                    description=(
                        f"Ovaj bot je **neovlaštena kopija** originalnog **{BOT_NAME}** bota.\n\n"
                        f"<:e_link:1519363321458065408> **Jedini originalni bot:** GIAN\n\n"
                        f"Bot napušta server."
                    ),
                    color=_LP
                )
                await ch.send(embed=e)
        except Exception:
            pass
        try:
            await guild.leave()
            print(f"  <:e_lock3:1519362717394403432> Licenca: napustio nedozvoljeni server {guild.name}")
        except Exception as _e:
            print(f"  <:e_cross2:1519362733613776967> Ne mogu napustiti {guild.name}: {_e}")
        return
    try:
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"  <:e_check2:1519362730057007268> Komande sync-ane za {guild.name}")
    except Exception as e:
        print(f"  <:e_cross2:1519362733613776967> Sync error za {guild.name}: {e}")
    chan = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
    if chan:
        try:
            e = discord.Embed(
                title=f"<:e_shake:1519362947766554737> Zdravo, {guild.name}!",
                description=(
                    f"Ja sam **{BOT_NAME}** — Balkan Discord bot!\n\n"
                    f"<:e_help2:1519362723148726534> Ukucaj `/help` da vidiš sve komande.\n"
                    f"<:e_ctrl:1519362682296209498> Igraj igre, skupljaj životinje, zarađuj pare!\n\n"
                    f"*Verzija: {VERSION}*"
                ),
                color=COLORS["balkan"],
                timestamp=datetime.now(timezone.utc)
            )
            e.set_thumbnail(url=bot.user.display_avatar.url)
            e.set_footer(text=f"{BOT_NAME} {VERSION}")
            await chan.send(embed=e)
        except Exception:
            pass

@bot.event
async def on_member_join(member):
    cfg = get_guild_config(member.guild.id)

    # ── Anti-Raid (PAMETNI: ne lockuje, samo kickuje sumnjive) ──
    try:
        if await antiraid_check(member):
            return  # Kickovan, ne radi welcome
    except Exception as _e: print(f"[anti-raid] {_e}")


    # ── Invite Tracking ────────────────────────────────
    try:
        gkey = str(member.guild.id)
        old = data["invite_uses"].get(gkey, {})
        new_invites = await member.guild.invites()
        new_uses = {inv.code: inv.uses for inv in new_invites}
        used_code = None
        for code, uses in new_uses.items():
            if uses > old.get(code, 0):
                used_code = code
                break
        if used_code:
            inviter = next((inv.inviter for inv in new_invites if inv.code == used_code), None)
            if inviter and not inviter.bot:
                ikey = f"{member.guild.id}:{inviter.id}"
                rec = data["invites"].setdefault(ikey, {"count": 0, "code": used_code})
                rec["count"] += 1
                rec["code"] = used_code
        data["invite_uses"][gkey] = new_uses
        save_data()
    except Exception as _e: print(f"[invite-track join] {_e}")

    # ── Sumnjivi nalozi (mlađi od 7 dana) — upozorenje u log ──
    try:
        if is_suspicious_account(member):
            age_days = (datetime.now(timezone.utc) - member.created_at).days
            await audit_log(member.guild, "<:icon_warning:1519358274284032030>️ Sumnjiv nalog se pridružio",
                f"{member.mention} (`{member}`) — nalog je star samo **{age_days} dan/a**.\n"
                f"Mogući fake/spam nalog. Provjeriti aktivnost.",
                color=COLORS.get("warning", 0xFFA500))
    except Exception as _e: print(f"[suspicious] {_e}")

    # ── Server Milestones (50, 100, 200, 500, 1000…) ──
    try:
        cnt = sum(1 for m in member.guild.members if not m.bot)
        milestones = [25, 50, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 5000]
        if cnt in milestones:
            ms_ch = member.guild.get_channel(cfg.get("welcome_channel") or 1494687347558715543) or member.guild.system_channel
            if ms_ch:
                ms_e = discord.Embed(
                    title=f"<:e_confetti2:1519363348288901221> MILESTONE — {cnt} ČLANOVA! <:e_confetti2:1519363348288901221>",
                    description=(
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"<:e_trophy2:1519362624742232146> Upravo smo dostigli **{cnt}** članova!\n"
                        f"<:e_flower:1519362984818901173> Hvala svima koji su dio **× GIAN** porodice!\n"
                        f"<:e_rocket2:1519363332266524813> Nastavljamo dalje — sljedeća stanica još veća!\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━"
                    ),
                    color=_LP, timestamp=datetime.now(timezone.utc)
                )
                ms_e.set_image(url="https://media.tenor.com/M0vSf9CGHoEAAAAC/celebration.gif")
                ms_e.set_footer(text=f"{BOT_NAME} • Server raste! <:e_level2:1519362739749785610>")
                await ms_ch.send(content="@everyone", embed=ms_e,
                    allowed_mentions=discord.AllowedMentions(everyone=True))
    except Exception as _e: print(f"[milestone] {_e}")

    # ── Auto-Role ──────────────────────────────────────
    if auto_role_id := cfg.get("auto_role"):
        role = member.guild.get_role(auto_role_id)
        if role:
            try: await member.add_roles(role)
            except: pass

    # ── Log ────────────────────────────────────────────
    if log_ch := member.guild.get_channel(cfg.get("log_channel", 0)):
        le = discord.Embed(title="<:e_inbox:1519363351354937497> Novi Član", color=COLORS["success"], timestamp=datetime.now(timezone.utc))
        le.set_author(name=str(member), icon_url=member.display_avatar.url)
        le.add_field(name="ID", value=f"`{member.id}`", inline=True)
        le.add_field(name="Nalog kreiran", value=member.created_at.strftime("%d.%m.%Y."), inline=True)
        le.add_field(name="Ukupno članova", value=f"`{member.guild.member_count}`", inline=True)
        await log_ch.send(embed=le)


    # ── Welcome ────────────────────────────────────────
    ch_id = cfg.get("welcome_channel")
    chan = member.guild.get_channel(ch_id) if ch_id else discord.utils.get(member.guild.text_channels, name="welcome")
    if not chan: return


    # ── Kanali ──
    ch_chat = member.guild.get_channel(cfg.get("chat_channel",  1496860023706488884))
    ch_info = member.guild.get_channel(cfg.get("info_channel",  1496860023093989475))
    ch_news = member.guild.get_channel(cfg.get("news_channel",  1501973333195882696))
    ch_gws  = member.guild.get_channel(cfg.get("gws_channel",   1496860023480127505))
    ch_game = member.guild.get_channel(cfg.get("game_channel",  1496860023706488890))
    ch_mus  = member.guild.get_channel(cfg.get("music_channel", 1496860024121852088))

    chat_lnk = ch_chat.mention if ch_chat else "#chat"
    info_lnk = ch_info.mention if ch_info else "#info"
    news_lnk = ch_news.mention if ch_news else "#news"
    gws_lnk  = ch_gws.mention  if ch_gws  else "#gws"

    member_count = sum(1 for m in member.guild.members if not m.bot)

    # ── Welcome Embed (Panel API → fallback hardkod) ──
    _pw = await get_panel_embed("welcome")

    # Welcome-specific variable resolver — handles {accountAge}, {joinedAt}, {count} etc.
    _now_utc = datetime.now(timezone.utc)
    _created  = member.created_at if member.created_at.tzinfo else member.created_at.replace(tzinfo=timezone.utc)
    _delta    = _now_utc - _created
    _yrs, _rem = divmod(_delta.days, 365)
    _mos = _rem // 30
    _age_str = (f"{_yrs}g {_mos}m" if _yrs and _mos else
                f"{_yrs}g"         if _yrs           else
                f"{_mos}m"         if _mos           else "< 1m")
    _joined_str = (member.joined_at or _now_utc).strftime("%b %Y")

    def _wev(text: str) -> str:
        """Welcome embed variable expander — superset of _ev."""
        if not text: return text
        return (_ev(text, member, member_count)
                .replace("{accountAge}", _age_str)
                .replace("{joinedAt}",   _joined_str)
                .replace("{count}",      str(member_count))
                .replace("{user.avatar}", str(member.display_avatar.url))
                .replace("{memberCount}", str(member_count)))

    def _fmt_item(label: str, ch_id: str) -> str:
        return f"<#{ch_id}>" if ch_id else f"**{label}**"

    if _pw:
        _wc = int((_pw.get("color") or "#ec4899").lstrip("#") or "ec4899", 16)

        # Card list items (with optional channel links)
        _item1 = _pw.get("cardItem1") or "Procitaj pravila"
        _item2 = _pw.get("cardItem2") or "Odaberi role"
        _item3 = _pw.get("cardItem3") or "Predstavi se zajednici"
        _ch1   = _pw.get("item1ChannelId") or ""
        _ch2   = _pw.get("item2ChannelId") or ""
        _ch3   = _pw.get("item3ChannelId") or ""

        # Build description
        _desc_base = _pw.get("description") or ""
        if not _desc_base:
            _desc_base = (f"{_fmt_item(_item1, _ch1)}\n"
                          f"{_fmt_item(_item2, _ch2)}\n"
                          f"{_fmt_item(_item3, _ch3)}")
        else:
            _desc_base = (_desc_base
                .replace("{item1}", _fmt_item(_item1, _ch1))
                .replace("{item2}", _fmt_item(_item2, _ch2))
                .replace("{item3}", _fmt_item(_item3, _ch3)))

        e = discord.Embed(description=_wev(_desc_base), color=_wc, timestamp=_now_utc)

        if _pw.get("title"):
            e.title = _wev(_pw["title"])

        # Fields — with full variable substitution
        for _f in (_pw.get("fields") or []):
            _fn = _wev(str(_f.get("name") or ""))
            _fv = _wev(str(_f.get("value") or ""))
            if _fn or _fv:
                e.add_field(
                    name=_fn   or "\u200b",
                    value=_fv  or "\u200b",
                    inline=bool(_f.get("inline", True))
                )

        # Thumbnail
        _thumb_raw = _pw.get("thumbnail") or ""
        _thumb_url = _wev(_thumb_raw) if _thumb_raw else str(member.display_avatar.url)
        if _thumb_url and _thumb_url.startswith("http"):
            e.set_thumbnail(url=_thumb_url)

        # Footer
        _footer_text = _wev(_pw.get("footer") or f"{BOT_NAME} • Welcome")
        e.set_footer(text=_footer_text, icon_url=member.guild.icon.url if member.guild.icon else None)

    else:
        e = discord.Embed(
            title=f"<:e_diamond3:1519363370694738072> Dobrodošao/la, {member.display_name}! <:e_diamond3:1519363370694738072>",
            description=(
                f"```\n"
                f"  <:e_sparkles:1519363032185176198>  Novi član se pridružio serveru!  <:e_sparkles:1519363032185176198>\n"
                f"```\n"
                f"<:e_shake:1519362947766554737> Hej {member.mention}! Drago nam je što si tu!\n\n"
                f"<:e_pushpin:1519363357436543099> **Korisni kanali:**\n"
                f"┣ <:e_bubble:1519363307998417148> {chat_lnk}\n"
                f"┣ <:e_clipboard:1519363052871614627> {info_lnk}\n"
                f"┗ <:e_gift:1519362618341462067> {gws_lnk}\n\n"
                f"<:e_feather:1519363362322907218> Ti si **{member_count}.** član servera!"
            ),
            color=_LP,
            timestamp=_now_utc
        )
        e.set_thumbnail(url=member.display_avatar.url)
        e.set_footer(text=f"<:e_diamond3:1519363370694738072> {member.guild.name} • Welcome <:e_diamond3:1519363370694738072>",
                     icon_url=member.guild.icon.url if member.guild.icon else None)

    # ── Dugmadi ──
    wv = discord.ui.View()
    pw_buttons = (_pw or {}).get("buttons") or []
    _has_linked = any(pb.get("channelId") or pb.get("url") for pb in pw_buttons)
    if pw_buttons and _has_linked:
        for pb in pw_buttons:
            if not pb.get("label"):
                continue
            ch_id  = pb.get("channelId") or pb.get("channel_id")
            direct = pb.get("url")
            if ch_id:
                btn_url = f"https://discord.com/channels/{member.guild.id}/{ch_id}"
            elif direct:
                btn_url = direct
            else:
                continue
            wv.add_item(discord.ui.Button(
                label=pb["label"],
                emoji=pb.get("emoji") or None,
                url=btn_url,
                style=discord.ButtonStyle.link,
            ))
    else:
        # Fallback — hardkodovani game/music kanali
        if ch_game:
            wv.add_item(discord.ui.Button(
                label="game",
                emoji="<:icon_game:1519358323667767346>",
                url=f"https://discord.com/channels/{member.guild.id}/{ch_game.id}",
                style=discord.ButtonStyle.link
            ))
        if ch_mus:
            wv.add_item(discord.ui.Button(
                label="music",
                emoji="<:icon_music:1519358320337752125>",
                url=f"https://discord.com/channels/{member.guild.id}/{ch_mus.id}",
                style=discord.ButtonStyle.link
            ))

    await chan.send(content=member.mention, embed=e, view=wv)

def _find_boost_channel(guild: discord.Guild):
    """Vraća prvi tekstualni kanal koji u imenu sadrži 'boost' (case-insensitive),
    a u koji bot ima dozvolu da šalje poruke. Fallback: system_channel."""
    for c in guild.text_channels:
        if "boost" in c.name.lower() and c.permissions_for(guild.me).send_messages:
            return c
    sc = guild.system_channel
    if sc and sc.permissions_for(guild.me).send_messages:
        return sc
    return next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)

@bot.event
async def on_member_update(before, after):
    if before.premium_since is None and after.premium_since is not None:
        guild  = after.guild
        boosts = guild.premium_subscription_count or 0
        tier   = guild.premium_tier

        BOOST_REWARD = 2500
        get_economy(after.id)["balance"] += BOOST_REWARD
        save_data()

        chan = _find_boost_channel(guild)
        if not chan:
            return

        # ── MALI, ČIST EMBED ──
        e = discord.Embed(
            title="<:e_flower:1519362984818901173> Novi Boost!",
            description=(
                f"{after.mention} je upravo **boostovao server**! <:e_rocket2:1519363332266524813>\n"
                f"Hvala ti na podršci — server je sad još jači! <:e_muscle:1519362764244652122>"
            ),
            color=_LP,
            timestamp=datetime.now(timezone.utc)
        )
        e.add_field(name="<:e_rocket2:1519363332266524813> Boostova", value=f"`{boosts}`",        inline=True)
        e.add_field(name="<:e_medal3:1519363547514015764> Tier",     value=f"`Lvl {tier}`",      inline=True)
        e.add_field(name="<:e_gift:1519362618341462067> Nagrada",  value=f"`+{BOOST_REWARD:,} <:e_coins3:1519362621206298666>`", inline=True)
        e.set_thumbnail(url=after.display_avatar.url)
        e.set_footer(text=f"{BOT_NAME} • Hvala na podršci <:e_flower:1519362984818901173>")
        await chan.send(content=after.mention, embed=e)

@bot.event
async def on_message(message):
    if message.author.bot: return
    if not message.guild: return

    # ── Prefix bridge (.kpm radi kao /kpm) ──
    if message.content.startswith("."):
        if await try_prefix_command(message):
            return

    # ── WLCM auto-reakcije (svako ko napiše "wlcm" dobije <:e_globe2:1519362694887637004><:e_globe2:1519362694887637004><:e_globe2:1519362694887637004><:e_globe2:1519362694887637004>) ──
    if message.content.lower().strip() in ("wlcm", "wlcm all"):
        for emj in ["<:e_globe2:1519362694887637004>", "<:e_globe2:1519362694887637004>", "<:e_globe2:1519362694887637004>", "<:e_globe2:1519362694887637004>"]:
            try: await message.add_reaction(emj)
            except: pass
        return

    # ── Brojanje handler (PRIJE auto-mod-a, da se uvijek reaguje) ──
    cnt_cfg = data.get("counting", {}).get(str(message.guild.id))
    if cnt_cfg and message.channel.id == cnt_cfg.get("channel_id"):
        content = message.content.strip()
        try:
            num = int(content)
        except ValueError:
            try: await message.delete()
            except: pass
            return
        expected = cnt_cfg.get("current", 0) + 1
        last_user = cnt_cfg.get("last_user")
        if last_user == message.author.id:
            try: await message.add_reaction("<:e_no:1519363018725658675>")
            except Exception as e: print(f"[brojanje] reaction fail: {e}")
            warn_e = discord.Embed(
                title="<:e_no:1519363018725658675> OPOMENA — Ne možeš brojati iza sebe!",
                description=(
                    f"{message.author.mention}, **mora neko drugi nastaviti** prije nego što ti opet brojiš.\n\n"
                    f"<:e_right:1519363367712591922>️ Sljedeći broj je i dalje: **{expected}**"
                ),
                color=COLORS["warning"]
            )
            warn_e.set_footer(text=f"Pravilo: izmjenjivanje korisnika obavezno")
            await message.channel.send(content=message.author.mention, embed=warn_e, delete_after=8)
            try: await message.delete()
            except: pass
            return
        if num != expected:
            try: await message.add_reaction("<:icon_cross:1519358379917836508>")
            except Exception as e: print(f"[brojanje] reaction fail: {e}")
            try: await message.delete()
            except: pass
            # broji greške po korisniku (NE resetujemo brojanje!)
            mistakes = cnt_cfg.setdefault("mistakes", {})
            uid_str = str(message.author.id)
            mistakes[uid_str] = mistakes.get(uid_str, 0) + 1
            user_total = mistakes[uid_str]
            save_data()
            err_e = discord.Embed(
                title="<:e_bomb:1519363456334168255> OPOMENA — Pogrešan broj!",
                description=(
                    f"{message.author.mention}, **pogriješio/la** si!\n\n"
                    f"<:icon_cross:1519358379917836508> Tvoj odgovor: **{num}**\n"
                    f"<:icon_check:1519358376268533810> Trebalo je: **{expected}**\n\n"
                    f"<:icon_warning:1519358274284032030>️ Tvojih grešaka ukupno: **{user_total}**\n"
                    f"<:e_right:1519363367712591922>️ Brojanje **se nastavlja** — sljedeći broj je i dalje: **{expected}**"
                ),
                color=COLORS["error"], timestamp=datetime.now(timezone.utc)
            )
            err_e.set_footer(text=f"Pazi sljedeći put, {message.author.display_name}!")
            await message.channel.send(content=message.author.mention, embed=err_e, delete_after=10)
            return
        # tačan broj
        cnt_cfg["current"] = num
        cnt_cfg["last_user"] = message.author.id
        if num > cnt_cfg.get("high_score", 0):
            cnt_cfg["high_score"] = num
        save_data()
        try:
            await message.add_reaction("<:icon_check:1519358376268533810>")
        except Exception as e:
            print(f"[brojanje] reaction fail: {e}")
        # uokvireni label ispod broja
        try:
            label = discord.Embed(
                description=f"<:icon_check:1519358376268533810>  **#{num}**  ·  sljedeći: **{num+1}**",
                color=COLORS["success"]
            )
            label.set_footer(text=f"Brojao/la: {message.author.display_name}")
            await message.reply(embed=label, mention_author=False, silent=True)
        except Exception as e:
            print(f"[brojanje] reply fail: {e}")
        if num % 50 == 0:
            eco = get_economy(message.author.id)
            eco["balance"] += 100
            add_xp(message.author.id, 50); save_data()
            await message.channel.send(
                embed=em(f"🎯 Milestone {num}!",
                         f"{message.author.mention} dostigao broj **{num}**!\n`+100 <:e_coins3:1519362621206298666>` `+50 XP`",
                         color=COLORS["gold"]),
                delete_after=10
            )
        return

    # ── Auto-Mod ──────────────────────────────────────
    if await check_nsfw(message):
        return
    if await check_automod(message):
        return

    # ── AFK: clear if author was AFK ──────────────────
    uid_str = str(message.author.id)
    if uid_str in data["afk"]:
        afk_info = data["afk"].pop(uid_str)
        save_data()
        since = datetime.fromtimestamp(afk_info["since"], tz=timezone.utc)
        elapsed = datetime.now(timezone.utc) - since
        mins = int(elapsed.total_seconds() // 60)
        await message.channel.send(
            embed=em("<:e_shake:1519362947766554737> Dobro došao/la nazad!", f"Skinut AFK status. Bio/la si odsutan/na **{mins} min**.", color=COLORS["info"]),
            delete_after=8
        )

    # ── AFK: notify if mentioning AFK user ────────────
    for mentioned in message.mentions:
        m_str = str(mentioned.id)
        if m_str in data["afk"]:
            afk_r = data["afk"][m_str]
            await message.channel.send(
                embed=em(f"<:e_sleep:1519362785291669644> {mentioned.display_name} je AFK",
                         f"Razlog: *{afk_r.get('reason', 'nema razloga')}*",
                         color=COLORS["warning"]),
                delete_after=10
            )

    # ── Quest: msgs20 ─────────────────────────────────
    if not message.content.startswith("/") and not message.content.startswith("!"):
        completed = quest_progress(message.author.id, "msgs20")
        if completed:
            await message.channel.send(
                embed=em(f"<:icon_check:1519358376268533810> Quest završen! {completed['name']}", f"+**{completed['reward']} <:e_coins3:1519362621206298666>**!", color=COLORS["gold"]),
                delete_after=8
            )

    # ── Kaladont handler ──────────────────────────────
    if message.channel.id in kaladont_games and not message.content.startswith("/"):
        game = kaladont_games[message.channel.id]
        word = _kaladont_normalize(message.content)
        letters = game["letters"]
        req = game["word"][-letters:]

        # Ignoriši poruke koje nisu čiste jednorijeci
        if not word or not word.isalpha() or " " in message.content.strip():
            pass  # ignoriši
        elif (len(word) < 3
              or message.author.id == game.get("last_uid")
              or word[:letters] != req
              or word in game["used"]):
            # Format greška (pogrešna slova, prekratko, isti igrač, već korištena) → ❌ reakcija
            try: await message.add_reaction("<:icon_cross:1519358379917836508>")
            except: pass
        elif word != "KALADONT" and word not in KALADONT_DICT:
            # Rijec nije u rjecniku — samo ❌, a ember + dugme tek svake 10. greške
            try: await message.add_reaction("<:icon_cross:1519358379917836508>")
            except: pass
            cid = message.channel.id
            _kaladont_invalid_count[cid] = _kaladont_invalid_count.get(cid, 0) + 1
            if _kaladont_invalid_count[cid] >= 7:
                _kaladont_invalid_count[cid] = 0
                # Deaktiviraj prethodni invalid embed ako postoji
                old_msg = _kaladont_invalid_msgs.pop(cid, None)
                if old_msg:
                    try: await old_msg.edit(view=None)
                    except: pass
                inv_msg = await message.channel.send(
                    embed=kaladont_invalid_embed(word, req, game["letters"]),
                    view=KaladontInvalidView(cid, checkpoint_word=game["word"])
                )
                _kaladont_invalid_msgs[cid] = inv_msg
        else:
            # ── Validna riječ — prihvata se ───────────────────────
            # Resetuj invalid counter i deaktiviraj stari invalid embed
            _kaladont_invalid_count.pop(message.channel.id, None)
            old_inv = _kaladont_invalid_msgs.pop(message.channel.id, None)
            if old_inv:
                try: await old_inv.edit(view=None)
                except: pass
            game["word"]             = word
            game["last_uid"]         = message.author.id
            game["last_player_name"] = message.author.display_name
            game["used"].add(word)
            game["chain"].append((word, message.author.display_name))
            count   = len(game["chain"])
            new_req = word[-letters:]
            try: await message.add_reaction("<:icon_check:1519358376268533810>")
            except: pass
            # ── POBJEDA: magična riječ "KALADONT" ─────────────
            if word == "KALADONT":
                try: await message.add_reaction("<:e_crown2:1519363047163166922>")
                except: pass
                eco = get_economy(message.author.id)
                nagrada = 1500
                eco["balance"] = eco.get("balance", 0) + nagrada
                add_xp(message.author.id, 200)
                save_data()
                win_e = discord.Embed(
                    title=f"<:e_crown2:1519363047163166922>  K A L A D O N T  —  P O B J E D A !  {E_FIRE4}",
                    description=f"{E_FIRE1}{E_FIRE2}{E_FIRE3}  {message.author.mention} je izrekao/la magičnu riječ!  {E_FIRE3}{E_FIRE2}{E_FIRE1}",
                    color=_LP,
                    timestamp=datetime.now(timezone.utc)
                )
                win_e.add_field(name="<:e_trophy2:1519362624742232146>  Pobjednik/ca",  value=f"**{message.author.display_name}**", inline=True)
                win_e.add_field(name="<:e_chart:1519362656568475880>  Riječi u nizu", value=f"**{count}**",                       inline=True)
                win_e.add_field(name="<:e_coins3:1519362621206298666>  Nagrada",       value=f"**+{nagrada:,} <:e_coins3:1519362621206298666>**",               inline=True)
                win_e.add_field(name="<:e_star2:1519363084253266031>  XP",            value=f"**+200**",                          inline=True)
                win_e.set_thumbnail(url=message.author.display_avatar.url)
                win_e.set_footer(text=f"{BOT_NAME} • Kaladont pobjeda")
                await message.channel.send(content=message.author.mention, embed=win_e)
                del kaladont_games[message.channel.id]
                return
            await message.channel.send(embed=kaladont_word_card(word, message.author.mention, new_req, count), view=KaladontWordView(message.channel.id))
            if game["msg"]:
                try: await game["msg"].edit(embed=kaladont_active_embed(game))
                except: pass
        return  # ne procesuj XP za kaladont poruke

    # ── Wordle handler ────────────────────────────────
    if message.channel.id in wordle_games:
        wgame = wordle_games[message.channel.id]
        wcontent = message.content.strip()
        if message.author.id == wgame["uid"] and not wcontent.startswith("/"):
            guess = _kaladont_normalize(wcontent)
            if guess.isalpha() and len(guess) == 5:
                wgame["guesses"].append(guess)
                won  = (guess == wgame["word"])
                used = len(wgame["guesses"])
                try: await message.add_reaction("<:e_green:1519362769047126028>" if won else "<:icon_check:1519358376268533810>")
                except: pass
                if won:
                    wcfg   = _g_gamble("wordle")
                    reward = int(wcfg.get("reward", 1200))
                    xp     = 150
                    eco    = get_economy(message.author.id)
                    eco["balance"] = eco.get("balance", 0) + reward
                    add_xp(message.author.id, xp)
                    save_data()
                    win_e = _wordle_embed(wgame, message.author, finished=True, won=True, reward=reward, xp=xp)
                    if wgame.get("msg"):
                        try: await wgame["msg"].edit(embed=win_e)
                        except: pass
                    await message.channel.send(content=message.author.mention, embed=win_e)
                    del wordle_games[message.channel.id]
                    return
                if used >= wgame["max"]:
                    lose_e = _wordle_embed(wgame, message.author, finished=True, won=False)
                    if wgame.get("msg"):
                        try: await wgame["msg"].edit(embed=lose_e)
                        except: pass
                    await message.channel.send(embed=lose_e)
                    del wordle_games[message.channel.id]
                    return
                upd_e = _wordle_embed(wgame, message.author)
                if wgame.get("msg"):
                    try: await wgame["msg"].edit(embed=upd_e)
                    except: pass
                else:
                    try:
                        sent = await message.channel.send(embed=upd_e)
                        wgame["msg"] = sent
                    except: pass
                return  # ne procesuj XP za wordle pogodak

    # ── Msg Counter ───────────────────────────────────
    mkey = f"{message.guild.id}:{message.author.id}"
    data["msg_count"][mkey] = data["msg_count"].get(mkey, 0) + 1
    # Poo task: chat messages
    if message.guild:
        _poo_task_progress(message.guild.id, message.author.id, "chat")
    data.setdefault("msg_count_week", {})
    data["msg_count_week"][mkey] = data["msg_count_week"].get(mkey, 0) + 1


    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

@bot.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content: return
    if not before.guild: return
    cfg = get_guild_config(before.guild.id)
    log_ch = before.guild.get_channel(cfg.get("log_channel", 0))
    if not log_ch: return
    e = discord.Embed(title="<:e_pencil:1519363059909398610>️ Poruka Editovana", color=COLORS["warning"], timestamp=datetime.now(timezone.utc))
    e.set_author(name=str(before.author), icon_url=before.author.display_avatar.url)
    e.add_field(name="Kanal",   value=before.channel.mention,           inline=True)
    e.add_field(name="<:e_pin:1519363329259208836> Link", value=f"[Idi na poruku]({after.jump_url})", inline=True)
    e.add_field(name="Prije",   value=(before.content[:1000] or "*prazno*"), inline=False)
    e.add_field(name="Poslije", value=(after.content[:1000]  or "*prazno*"), inline=False)
    await log_ch.send(embed=e)

@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild: return
    cfg = get_guild_config(message.guild.id)
    log_ch = message.guild.get_channel(cfg.get("log_channel", 0))
    if not log_ch: return
    e = discord.Embed(title="<:e_trash:1519362951247691898>️ Poruka Obrisana", color=COLORS["error"], timestamp=datetime.now(timezone.utc))
    e.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
    e.add_field(name="Kanal",    value=message.channel.mention,                         inline=True)
    e.add_field(name="Sadržaj",  value=(message.content[:1000] or "*prilog/prazno*"),   inline=False)
    await log_ch.send(embed=e)

@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.emoji) != "<:e_star2:1519363084253266031>" or not payload.guild_id: return
    cfg = get_guild_config(payload.guild_id)
    sb_ch_id = cfg.get("starboard_channel")
    if not sb_ch_id: return
    if payload.channel_id == sb_ch_id: return
    threshold = cfg.get("starboard_threshold", 3)
    guild   = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(payload.channel_id)
    try:
        message = await channel.fetch_message(payload.message_id)
    except: return
    star_r = discord.utils.get(message.reactions, emoji="<:e_star2:1519363084253266031>")
    count  = star_r.count if star_r else 0
    if count < threshold: return
    sb_channel = guild.get_channel(sb_ch_id)
    if not sb_channel: return
    gkey   = str(payload.guild_id)
    mkey   = str(payload.message_id)
    done   = data["starboard_done"].setdefault(gkey, {})
    if mkey in done:
        try:
            sb_msg = await sb_channel.fetch_message(done[mkey])
            ne = sb_msg.embeds[0]
            ne.set_footer(text=f"<:e_star2:1519363084253266031> {count} | #{channel.name}")
            await sb_msg.edit(embed=ne)
        except: pass
        return
    e = discord.Embed(description=message.content or "", color=COLORS["gold"], timestamp=message.created_at)
    e.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    e.add_field(name="<:e_pin:1519363329259208836> Original", value=f"[Idi na poruku]({message.jump_url})", inline=False)
    if message.attachments: e.set_image(url=message.attachments[0].url)
    e.set_footer(text=f"<:e_star2:1519363084253266031> {count} | #{channel.name}")
    sb_msg = await sb_channel.send(f"<:e_star2:1519363084253266031> **{count}** | {channel.mention}", embed=e)
    done[mkey] = sb_msg.id
    save_data()

@tasks.loop(hours=1)
async def birthday_check():
    today = datetime.now(timezone.utc).strftime("%d-%m")
    for uid, bday in list(data.get("birthdays", {}).items()):
        if bday != today: continue
        for guild in bot.guilds:
            member = guild.get_member(int(uid))
            if not member: continue
            cfg   = get_guild_config(guild.id)
            ch_id = cfg.get("birthday_channel")
            if not ch_id: continue
            chan = guild.get_channel(ch_id)
            if not chan: continue
            e = discord.Embed(
                title="<:e_party:1519363028334674070> Sretan Rođendan!",
                description=f"Danas je rođendan od {member.mention}! <:e_party:1519363028334674070>\nSvi mu/joj čestitajte! <:e_party:1519363028334674070>",
                color=COLORS["fun"], timestamp=datetime.now(timezone.utc)
            )
            e.set_thumbnail(url=member.display_avatar.url)
            e.set_footer(text=f"{BOT_NAME} • Rođendani")
            try: await chan.send(content=member.mention, embed=e)
            except: pass

@bot.command(name="sync")
@commands.has_permissions(administrator=True)
async def sync_cmd(ctx):
    try:
        bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(embed=em("<:icon_check:1519358376268533810> Sinhronizovano!", f"`{len(synced)}` komandi registrovano.", color=COLORS["success"]))
    except Exception as e:
        await ctx.send(embed=em("<:icon_cross:1519358379917836508> Greška", str(e), color=COLORS["error"]))

# ═══════════════════════════════════════════
#    <:e_shield2:1519362627795554374>️ SIGURNOST: Anti-Nuke / Audit / Backup / Whitelist
# ═══════════════════════════════════════════
OWNER_IDS: set = {829552737322270731}  # Discord ID-evi koji su 100% sigurni (anti-nuke whitelist)
NUKE_WINDOW = 30        # sekundi
NUKE_BAN_LIMIT = 3      # max banova/kickova/brisanja u prozoru
nuke_tracker: dict = defaultdict(lambda: defaultdict(deque))

# ── PAMETNI Anti-Raid (NE LOCKUJE server, samo kickuje sumnjive) ───
RAID_WINDOW = 30            # sekundi (5+ joinova u 30s = raid lockdown 5 min)
RAID_JOIN_LIMIT = 5         # 5+ NOVIH naloga u 30s = raid
SUSPICIOUS_AGE_DAYS = 7     # nalozi mlađi od ovoliko dana = sumnjivi
join_tracker: dict = defaultdict(deque)   # guild_id -> deque[(timestamp, member_id, account_age_days)]
raid_mode: dict = {}        # guild_id -> until_timestamp (period gdje se sumnjivi auto-kickaju)

def is_suspicious_account(member) -> bool:
    """Nalog je sumnjiv ako je mlađi od konfiguriranog praga."""
    age_days = (datetime.now(timezone.utc) - member.created_at).days
    return age_days < _prot_raid().get("age_days", SUSPICIOUS_AGE_DAYS)

async def antiraid_check(member):
    """Prati joinove. Ako je raid, ulazi u raid mod. Koristi live panel config."""
    r = _prot_raid()
    if not r["enabled"]:
        return False
    now = time.time()
    gid = member.guild.id
    age_days = (datetime.now(timezone.utc) - member.created_at).days
    dq = join_tracker[gid]
    dq.append((now, member.id, age_days))
    while dq and dq[0][0] < now - r["window"]:
        dq.popleft()
    suspicious_recent = sum(1 for _, _, ad in dq if ad < r["age_days"])
    if suspicious_recent >= r["limit"]:
        lockdown_secs = r["lockdown_min"] * 60
        raid_mode[gid] = now + lockdown_secs
        await audit_log(member.guild, "<:e_report2:1519362714198347886> RAID DETEKTOVAN!",
            f"**{suspicious_recent}** sumnjivih naloga (mlađih od {r['age_days']} dana) u zadnjih {r['window']}s!\n"
            f"<:e_gear:1519362652516782194>️ **Raid mode AKTIVAN {r['lockdown_min']}min** — sumnjivi nalozi će biti automatski kickovani.\n"
            f"<:icon_check:1519358376268533810> Stari/legitimni nalozi prolaze normalno.")
    if gid in raid_mode and now < raid_mode[gid] and is_suspicious_account(member):
        try:
            await member.send(embed=em("<:e_shield2:1519362627795554374>️ Raid Zaštita", f"Server **{member.guild.name}** je trenutno pod raid zaštitom. Tvoj nalog je premlad ({age_days}d). Pokušaj ponovo kasnije.", color=COLORS["warning"]))
        except: pass
        action = r["action"]
        if action == "ban":
            try:
                await member.ban(reason="<:e_shield2:1519362627795554374>️ Anti-Raid: sumnjiv nalog tokom raida")
                await audit_log(member.guild, "<:e_shield2:1519362627795554374>️ Anti-Raid Ban", f"Banovan: `{member}` (`{member.id}`) — nalog star {age_days}d")
                return True
            except: pass
        elif action == "kick":
            try:
                await member.kick(reason="<:e_shield2:1519362627795554374>️ Anti-Raid: sumnjiv nalog tokom raida")
                await audit_log(member.guild, "<:e_shield2:1519362627795554374>️ Anti-Raid Kick", f"Kickovan: `{member}` (`{member.id}`) — nalog star {age_days}d")
                return True
            except: pass
        else:  # alert_only
            await audit_log(member.guild, "<:e_shield2:1519362627795554374>️ Anti-Raid Upozorenje", f"Sumnjiv nalog: `{member}` (`{member.id}`) — nalog star {age_days}d (akcija: samo upozori)")
    return False

async def audit_log(guild, title, desc):
    """Šalje sigurnosni log u log_channel + DM-uje OWNER_IDS."""
    try:
        cfg = get_guild_config(guild.id)
        if log_ch := guild.get_channel(cfg.get("log_channel", 0)):
            await log_ch.send(embed=em(title, desc, color=COLORS["error"]))
    except: pass
    for oid in OWNER_IDS:
        try:
            owner = await bot.fetch_user(oid)
            await owner.send(embed=em(f"<:e_bell:1519363063738925187> [{guild.name}] {title}", desc, color=COLORS["warning"]))
        except: pass

async def antinuke_check(guild, mod, action: str):
    """Vrati True ako moderator prelazi limit. Skida mu admin uloge i obavještava."""
    if mod.id in OWNER_IDS or mod.bot:
        return False
    now = time.time()
    dq = nuke_tracker[guild.id][mod.id]
    dq.append(now)
    while dq and dq[0] < now - NUKE_WINDOW:
        dq.popleft()
    if len(dq) >= NUKE_BAN_LIMIT:
        dq.clear()
        # Skini sve admin uloge
        try:
            removed = []
            for r in list(mod.roles):
                if r.permissions.administrator or r.permissions.ban_members or r.permissions.kick_members or r.permissions.manage_roles:
                    try:
                        await mod.remove_roles(r, reason="<:e_shield2:1519362627795554374>️ Anti-Nuke: prelazak limita")
                        removed.append(r.name)
                    except: pass
            await audit_log(guild, "<:e_report2:1519362714198347886> ANTI-NUKE AKTIVAN!",
                f"**Moderator:** {mod.mention} (`{mod}`)\n**Akcija:** {action}\n**Limit:** {NUKE_BAN_LIMIT} u {NUKE_WINDOW}s\n**Skinute uloge:** {', '.join(removed) if removed else 'nijedna'}")
        except Exception as _e: print(f"[anti-nuke] {_e}")
        return True
    return False

@bot.event
async def on_member_ban(guild, user):
    # ── Log u log_channel ───────────────────────────────
    try:
        cfg = get_guild_config(guild.id)
        if log_ch := guild.get_channel(cfg.get("log_channel", 0)):
            e = discord.Embed(title="<:e_hammer:1519362836671762494> Član Banovan", color=COLORS["error"], timestamp=datetime.now(timezone.utc))
            e.set_author(name=str(user), icon_url=user.display_avatar.url)
            e.add_field(name="ID", value=f"`{user.id}`", inline=True)
            await log_ch.send(embed=e)
    except Exception as _e: print(f"[on_member_ban log] {_e}")
    # ── Anti-Nuke provjera ──────────────────────────────
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                await antinuke_check(guild, entry.user, f"BAN korisnika `{user}`")
                await audit_log(guild, "<:e_hammer:1519362836671762494> BAN", f"**Moderator:** {entry.user.mention}\n**Korisnik:** `{user}` (`{user.id}`)\n**Razlog:** {entry.reason or '—'}")
                break
    except Exception as _e: print(f"[on_member_ban nuke] {_e}")

@bot.event
async def on_member_remove(member):
    # ── Sanity guards ───────────────────────────────────
    # Ako je guild nedostupan (bot je izbačen/napustio server) — izlaz
    if member.guild is None or bot.get_guild(member.guild.id) is None:
        return
    # Ako je član koji odlazi sam bot — izlaz
    if bot.user is not None and member.id == bot.user.id:
        return

    cfg = get_guild_config(member.guild.id)
    # ── Log ────────────────────────────────────────────
    try:
        if log_ch := member.guild.get_channel(cfg.get("log_channel", 0)):
            le = discord.Embed(title="<:e_box:1519363099478458498> Član Otišao", color=COLORS["warning"], timestamp=datetime.now(timezone.utc))
            le.set_author(name=str(member), icon_url=member.display_avatar.url)
            le.add_field(name="ID", value=f"`{member.id}`", inline=True)
            le.add_field(name="Pridružio se", value=member.joined_at.strftime("%d.%m.%Y.") if member.joined_at else "?", inline=True)
            await log_ch.send(embed=le)
    except (discord.NotFound, discord.Forbidden):
        pass
    except Exception as _e: print(f"[on_member_remove log] {_e}")
    # ── Leave message ───────────────────────────────────
    try:
        ch_id = cfg.get("leave_channel") or cfg.get("welcome_channel")
        chan = member.guild.get_channel(ch_id) if ch_id else discord.utils.get(member.guild.text_channels, name="welcome")
        if chan:
            VE_L = [
                "<:icon_fire:1519358312188088466>",
                "<:e_fire2:1519362671491678280>",
                "<:icon_fire:1519358312188088466>",
                "<:e_fire2:1519362671491678280>",
            ]
            member_count_l = sum(1 for m in member.guild.members if not m.bot)
            _pl = await get_panel_embed("leave")
            if _pl:
                _ld = _ev(_pl.get("description") or "", member, member_count_l)
                _lc = int(_pl.get("color", "#2B2D3A").lstrip("#") or "2B2D3A", 16)
                e = discord.Embed(description=_ld, color=_lc, timestamp=datetime.now(timezone.utc))
                if _pl.get("title"): e.title = _ev(_pl["title"], member, member_count_l)
            else:
                e = discord.Embed(
                    description=(
                        f"**bye {member.mention}** <:e_shake:1519362947766554737>\n\n"
                        f"{VE_L[0]} {member.display_name} **je napustio/la server**\n"
                        f"<:e_feather:1519363362322907218> **{member_count_l} member**"
                    ),
                    color=_LP,
                    timestamp=datetime.now(timezone.utc)
                )
            e.set_thumbnail(url=member.display_avatar.url)
            e.set_footer(
                text=f"{BOT_NAME} • Leave",
                icon_url=member.guild.icon.url if member.guild.icon else None
            )
            await chan.send(embed=e)
    except (discord.NotFound, discord.Forbidden):
        pass
    except Exception as _e: print(f"[on_member_remove leave] {_e}")
    # ── Anti-Nuke kick provjera ─────────────────────────
    try:
        # Provjeri ponovo prije API poziva (guild je možda nestao u međuvremenu)
        if bot.get_guild(member.guild.id) is None:
            return
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id and (time.time() - entry.created_at.timestamp()) < 5:
                await antinuke_check(member.guild, entry.user, f"KICK korisnika `{member}`")
                await audit_log(member.guild, "<:e_run:1519362884868636883> KICK", f"**Moderator:** {entry.user.mention}\n**Korisnik:** `{member}` (`{member.id}`)")
                break
    except (discord.NotFound, discord.Forbidden):
        # Guild ne postoji više ili nemamo View Audit Log permisiju — tiho ignoriši
        pass
    except Exception as _e: print(f"[on_member_remove nuke] {_e}")

@bot.event
async def on_guild_channel_delete(channel):
    try:
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if entry.target.id == channel.id:
                await antinuke_check(channel.guild, entry.user, f"BRISANJE kanala #{channel.name}")
                await audit_log(channel.guild, "<:e_trash:1519362951247691898>️ KANAL OBRISAN", f"**Moderator:** {entry.user.mention}\n**Kanal:** `#{channel.name}`")
                break
    except Exception as _e: print(f"[on_channel_delete] {_e}")

@bot.event
async def on_guild_role_delete(role):
    try:
        async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if entry.target.id == role.id:
                await antinuke_check(role.guild, entry.user, f"BRISANJE uloge {role.name}")
                await audit_log(role.guild, "<:e_label:1519363326109417613>️ ULOGA OBRISANA", f"**Moderator:** {entry.user.mention}\n**Uloga:** `{role.name}`")
                break
    except Exception as _e: print(f"[on_role_delete] {_e}")

# ── Auto-backup svakih 6 sati ────────────────────────
@tasks.loop(hours=6)
async def auto_backup():
    try:
        import shutil as _sh
        backup_dir = _os.path.join(_DATA_DIR, "backups")
        _os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dst = _os.path.join(backup_dir, f"oleun_data_{ts}.json")
        _sh.copy(DATA_FILE, dst)
        # Drži maksimum 20 backupa
        backups = sorted(_os.listdir(backup_dir))
        for old in backups[:-20]:
            try: _os.remove(_os.path.join(backup_dir, old))
            except: pass
        print(f"[backup] {dst}")
    except Exception as _e: print(f"[backup] {_e}")

@tasks.loop(seconds=30)
async def change_status():
    statuses = [
        discord.CustomActivity(name=".help - mrak i tjt"),
    ]
    await bot.change_presence(activity=random.choice(statuses))

# ═══════════════════════════════════════════
#    INFO & UTILS
# ═══════════════════════════════════════════
@bot.tree.command(name="ping", description="🎯 Provjeri brzinu bota")
async def ping(i: discord.Interaction):
    ms = round(bot.latency * 1000)
    status, color = ("<:e_green:1519362769047126028> Odlično", COLORS["success"]) if ms < 80 else ("<:e_green:1519362769047126028> Dobro", COLORS["warning"]) if ms < 180 else ("<:e_red:1519362782192210041> Sporo", COLORS["error"])
    await i.response.send_message(embed=em("🎯 Pong!", color=color, fields=[
        ("<:e_satellite:1519363311207186482> Latency", f"`{ms}ms`", True), ("<:e_chart:1519362656568475880> Status", status, True), ("<:e_gear:1519362652516782194> Bot", f"`{bot.user}`", True)
    ]))

@bot.tree.command(name="serverinfo", description="<:e_chart:1519362656568475880> Informacije o serveru")
async def serverinfo(i: discord.Interaction):
    g = i.guild
    bots, humans = sum(1 for m in g.members if m.bot), g.member_count - sum(1 for m in g.members if m.bot)
    await i.response.send_message(embed=em(f"<:e_castle:1519363568645177457> {g.name}", color=COLORS["purple"], thumb=g.icon.url if g.icon else None, fields=[
        ("<:e_crown2:1519363047163166922> Vlasnik",   g.owner.mention,                                        True),
        ("<:e_users:1519363096601301120> Članovi",   f"`{humans}` ljudi • `{bots}` botova",                 True),
        ("<:e_cal:1519362659676455046> Kreiran",   g.created_at.strftime("%d.%m.%Y."),                    True),
        ("<:e_bubble:1519363307998417148> Kanali",    f"`{len(g.text_channels)}` tekst • `{len(g.voice_channels)}` voice", True),
        ("<:e_label:1519363326109417613>️ Uloge",    f"`{len(g.roles)-1}`",                                  True),
        ("<:e_rocket2:1519363332266524813> Boostovi",  f"`{g.premium_subscription_count or 0}`",              True),
    ]))

@bot.tree.command(name="userinfo", description="<:e_user:1519363093736718518> Informacije o korisniku")
async def userinfo(i: discord.Interaction, korisnik: discord.Member = None):
    u = korisnik or i.user
    eco, xpd = get_economy(u.id), get_xp(u.id)
    warns = len(get_warnings(i.guild.id, u.id))
    await i.response.send_message(embed=em(f"<:e_user:1519363093736718518> {u.display_name}", color=u.accent_color or COLORS["default"], thumb=u.display_avatar.url, fields=[
        ("🆔 ID",          f"`{u.id}`",                                            True),
        ("<:e_cal:1519362659676455046> Pridružio",   u.joined_at.strftime("%d.%m.%Y.") if u.joined_at else "N/A", True),
        ("<:e_label:1519363326109417613>️ Top uloga",  u.top_role.mention,                                    True),
        ("<:e_coins3:1519362621206298666> Balans",      f"`{eco['balance']:,} <:e_coins3:1519362621206298666>`",                            True),
        ("<:e_level2:1519362739749785610> Level",       f"`{xpd['level']}`",                                   True),
        ("<:icon_warning:1519358274284032030>️ Upozorenja",  f"`{warns}`",                                           True),
    ]))

@bot.tree.command(name="spotify", description="<:e_music2:1519362679310127114> Pogledaj šta korisnik trenutno sluša na Spotifyu")
async def spotify_cmd(i: discord.Interaction, korisnik: discord.Member = None):
    u = korisnik or i.user
    spotify = next((a for a in u.activities if isinstance(a, discord.Spotify)), None)
    if not spotify:
        return await i.response.send_message(
            embed=em("<:e_music2:1519362679310127114> Spotify", f"{u.mention} trenutno **ne sluša ništa** na Spotifyu.\n\n<:e_idea:1519363006599794799> *Mora imati Spotify povezan sa Discord nalogom i pustiti pjesmu.*", color=COLORS["warning"]),
            ephemeral=False
        )
    duration = spotify.duration
    elapsed = datetime.now(timezone.utc) - spotify.start
    progress = min(elapsed.total_seconds() / duration.total_seconds(), 1.0)
    bar_len = 20
    filled = int(progress * bar_len)
    bar = "▰" * filled + "▱" * (bar_len - filled)
    def fmt_t(td):
        s = int(td.total_seconds()); return f"{s//60}:{s%60:02d}"
    e = discord.Embed(
        title=f"<:e_music2:1519362679310127114> {spotify.title}",
        url=f"https://open.spotify.com/track/{spotify.track_id}",
        description=f"**Izvođač:** {spotify.artist}\n**Album:** {spotify.album}\n\n`{fmt_t(elapsed)}` {bar} `{fmt_t(duration)}`",
        color=_LP,
        timestamp=datetime.now(timezone.utc)
    )
    e.set_author(name=f"{u.display_name} sluša", icon_url=u.display_avatar.url)
    if spotify.album_cover_url: e.set_thumbnail(url=spotify.album_cover_url)
    e.set_footer(text=f"Spotify • {BOT_NAME}")
    await i.response.send_message(embed=e)

@bot.tree.command(name="invite", description="<:e_chart:1519362656568475880> Statistika — poruke + invite-ovi")
async def invite_cmd(i: discord.Interaction, korisnik: discord.Member = None):
    u = korisnik or i.user
    mkey = f"{i.guild.id}:{u.id}"
    msg_n = data["msg_count"].get(mkey, 0)
    ikey = f"{i.guild.id}:{u.id}"
    inv_rec = data["invites"].get(ikey, {})
    inv_count = inv_rec.get("count", 0)
    invite_url = None
    invite_uses = 0
    try:
        invs = await i.guild.invites()
        user_invs = [inv for inv in invs if inv.inviter and inv.inviter.id == u.id]
        if user_invs:
            best = max(user_invs, key=lambda x: x.uses)
            invite_url = f"https://discord.gg/{best.code}"
            invite_uses = best.uses
            if not inv_rec:
                inv_count = best.uses
    except Exception as _e: print(f"[pump] {_e}")
    e = em(f"<:e_chart:1519362656568475880> Statistika — {u.display_name}",
        color=u.accent_color or COLORS["balkan"], thumb=u.display_avatar.url, fields=[
        ("<:e_pencil:1519363059909398610>️ Poruke poslato", f"`{msg_n:,}`", True),
        ("<:e_users:1519363096601301120> Doveo članova",   f"`{inv_count}`", True),
        ("<:e_cal:1519362659676455046> Pridružio",       u.joined_at.strftime("%d.%m.%Y.") if u.joined_at else "N/A", True),
        ("<:e_link:1519363321458065408> Tvoj invite",     f"`{invite_uses}` korišćenja" if invite_url else "*nemaš svoj invite link*", False),
    ])
    e.set_footer(text=f"Korisnik: {u} • ID: {u.id}")
    view = None
    if invite_url:
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Otvori invite", emoji="<:e_link:1519363321458065408>", url=invite_url, style=discord.ButtonStyle.link))
    await i.response.send_message(embed=e, view=view) if view else await i.response.send_message(embed=e)


@bot.tree.command(name="avatar", description="<:e_picture:1519363318391771326>️ Prikaži avatar korisnika")
async def avatar(i: discord.Interaction, korisnik: discord.Member = None):
    u = korisnik or i.user
    await i.response.send_message(embed=em(f"<:e_picture:1519363318391771326>️ {u.display_name}",
        f"[PNG]({u.display_avatar.with_format('png').url}) • [JPG]({u.display_avatar.with_format('jpg').url}) • [WEBP]({u.display_avatar.with_format('webp').url})",
        color=COLORS["info"], image=u.display_avatar.url))

# /say uklonjeno (v2.1) — rizik impersonacije/uznemiravanja kroz bota.

@set_group.command(name="brojanje", description="<:e_chart:1519362656568475880> Postavi kanal za brojanje [ADMIN]")
@app_commands.describe(kanal="Kanal u kojem će se brojati", pocetak="Od kog broja krenuti (default 0 → sljedeći je 1)")
async def brojanje_postavi(i: discord.Interaction, kanal: discord.TextChannel, pocetak: int = 0):
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Samo admin.", color=COLORS["error"]), ephemeral=True)
    data["counting"][str(i.guild.id)] = {
        "channel_id": kanal.id,
        "current": max(0, pocetak),
        "last_user": None,
        "high_score": data.get("counting", {}).get(str(i.guild.id), {}).get("high_score", 0)
    }
    save_data()
    nxt = max(0, pocetak) + 1
    e = em("<:icon_check:1519358376268533810> Kanal za brojanje postavljen!",
           f"Kanal: {kanal.mention}\n"
           f"Trenutno: **{max(0, pocetak)}**\n"
           f"Sljedeći broj: **{nxt}**\n\n"
           f"📝 **Pravila:**\n"
           f"• Pišite brojeve redom (1, 2, 3, …)\n"
           f"• Ne smiješ brojati dvaput zaredom\n"
           f"• Ko pogriješi → reset na 0\n"
           f"• Svaki **50.** broj = `+100 <:e_coins3:1519362621206298666>` `+50 XP` 🎯",
           color=COLORS["success"])
    await i.response.send_message(embed=e)

@set_group.command(name="brojanje-reset", description="<:e_chart:1519362656568475880> Resetuj brojanje na 0 [ADMIN]")
async def brojanje_reset(i: discord.Interaction):
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Samo admin.", color=COLORS["error"]), ephemeral=True)
    cfg = data.get("counting", {}).get(str(i.guild.id))
    if not cfg:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508>", "Brojanje nije postavljeno!", color=COLORS["error"]),
            ephemeral=True
        )
    cfg["current"] = 0
    cfg["last_user"] = None
    save_data()
    await i.response.send_message(embed=em("<:icon_check:1519358376268533810> Resetovano!", "Brojanje krene od **1**.", color=COLORS["success"]))

# /setname i /setavatar — uklonjeni (oslobađa slotove za 100-command limit)
# Bot ime/avatar mijenjaj ručno preko Discord Developer Portal-a.

# ═══════════════════════════════════════════
#    MODERACIJA
# ═══════════════════════════════════════════
def _find_role_by_names(guild: discord.Guild, names: list):
    """Pronađi ulogu po nazivu (case-insensitive, zanemari razmake i dekorativne separatore).
    Tolerira: 〢 ║ ┃ │ ┊ ╏ ▎ ▏ ▌ ▍ ︙ ⫶ • · ・ ｜ | ‖ ╎ ┋ ┆ ┇ ┈ ┉ ─ ━ ═ ▪ ▫ ◆ ◇ <:e_star2:1519363084253266031> <:e_star2:1519363084253266031>"""
    SEP_CHARS = "〢║┃│┊╏▎▏▌▍︙⫶•·・｜|‖╎┋┆┇┈┉─━═▪▫◆◇<:e_star2:1519363084253266031><:e_star2:1519363084253266031>◈◉○●◎◍◌«»‹›„""''‚‛*=+~-_."
    def norm(s: str) -> str:
        s = s.lower()
        # Skini sve dekorativne separatore i razmake
        s = "".join(ch for ch in s if ch not in SEP_CHARS)
        s = re.sub(r"\s+", "", s)
        return s
    targets = [norm(n) for n in names]
    for r in guild.roles:
        if norm(r.name) in targets:
            return r
    return None

@bot.tree.command(name="ban", description="<:e_hammer:1519362836671762494> [VLASNIK / 〢 /GIAN] Ban korisnika")
async def ban(i: discord.Interaction, korisnik: discord.Member, razlog: str = "Bez razloga"):
    # ── Provjera pristupa: samo OWNER ili 〢 /GIAN član kojeg je vlasnik odobrio ──
    if i.user.id not in OWNER_IDS:
        gianni_ban_role = _find_role_by_names(i.guild, ["〢 /GIAN", "/GIAN", "〢/GIAN", "〢 /GIANNI", "/GIANNI", "〢/GIANNI"])
        has_gianni = gianni_ban_role is not None and gianni_ban_role in i.user.roles
        if not has_gianni:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Pristup odbijen",
                         "Samo korisnici sa ulogom `〢 /GIAN` smiju koristiti `/ban`!",
                         color=COLORS["error"]),
                ephemeral=True)
        ban_allowed = str(i.user.id) in data.get("ban_allowed_ids", [])
        if not ban_allowed:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Pristup odbijen",
                         "Vlasnik te još **nije odobrio** za korištenje `/ban`.\n"
                         "Kontaktiraj vlasnika — on koristi `/ban-dozvola add @ti` da te odobri.",
                         color=COLORS["error"]),
                ephemeral=True)

    if korisnik.top_role >= i.user.top_role:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", "Ne možeš ovo nekome sa višom ili istom ulogom!", color=COLORS["error"]), ephemeral=True)

    # ── VLASNIK → pravi Discord ban ──
    if i.user.id in OWNER_IDS:
        await korisnik.ban(reason=f"[VLASNIK BAN] {razlog}")
        return await i.response.send_message(embed=em("<:e_hammer:1519362836671762494> Banovan (Vlasnik)", color=COLORS["error"], thumb=korisnik.display_avatar.url, fields=[
            ("<:e_user:1519363093736718518> Korisnik", f"{korisnik} (`{korisnik.id}`)", False),
            ("📝 Razlog", razlog, False), ("<:e_crown2:1519363047163166922> Vlasnik", i.user.mention, False),
        ]))

    # ── STAFF → soft-ban: dodaj ulogu "Banned Permisson" ──
    banned_role = _find_role_by_names(i.guild, ["Banned Permisson", "Banned Permission", "Banned"])
    if not banned_role:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", "Uloga `Banned Permisson` ne postoji na serveru!\nKreiraj je ili javi vlasniku.", color=COLORS["error"]), ephemeral=True)
    if banned_role >= i.guild.me.top_role:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", f"Bot ne može dodijeliti `{banned_role.name}` jer je iznad njegove uloge!\nPomakni GIAN bot ulogu iznad nje.", color=COLORS["error"]), ephemeral=True)

    # Sačuvaj sve njegove uloge (osim @everyone) za moguće vraćanje
    saved_roles = [r.id for r in korisnik.roles if r != i.guild.default_role and r != banned_role]
    data.setdefault("soft_bans", {})[str(korisnik.id)] = {
        "guild_id": i.guild.id, "roles": saved_roles,
        "razlog": razlog, "moderator": i.user.id,
        "vreme": datetime.now(timezone.utc).strftime("%d.%m.%Y. %H:%M")
    }
    save_data()

    try:
        # Skini sve uloge i dodaj banned
        roles_to_remove = [r for r in korisnik.roles if r != i.guild.default_role and r < i.guild.me.top_role]
        if roles_to_remove:
            await korisnik.remove_roles(*roles_to_remove, reason=f"Soft-ban od {i.user}: {razlog}")
        await korisnik.add_roles(banned_role, reason=f"Soft-ban od {i.user}: {razlog}")
    except discord.Forbidden:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", "Bot nema permisiju da mijenja uloge ovom korisniku!", color=COLORS["error"]), ephemeral=True)

    # View sa dugmadima za vlasnika (Vrati uloge / Pravi Ban)
    class SoftBanView(discord.ui.View):
        def __init__(self, target_id: int, banned_role_id: int):
            super().__init__(timeout=None)
            self.target_id = target_id
            self.banned_role_id = banned_role_id

        @discord.ui.button(label="<:icon_check:1519358376268533810> Vrati Uloge", style=discord.ButtonStyle.success, custom_id=f"softban_restore_{korisnik.id}")
        async def restore(self, ii: discord.Interaction, btn: discord.ui.Button):
            if ii.user.id not in OWNER_IDS:
                return await ii.response.send_message("<:icon_cross:1519358379917836508> Samo vlasnik može vratiti uloge.", ephemeral=True)
            target = ii.guild.get_member(self.target_id)
            if not target:
                return await ii.response.send_message("<:icon_cross:1519358379917836508> Korisnik više nije na serveru.", ephemeral=True)
            sb = data.get("soft_bans", {}).get(str(self.target_id))
            if not sb:
                return await ii.response.send_message("<:icon_cross:1519358379917836508> Nema sačuvanih uloga.", ephemeral=True)
            br = ii.guild.get_role(self.banned_role_id)
            try:
                if br and br in target.roles:
                    await target.remove_roles(br, reason=f"Restore od {ii.user}")
                roles_to_add = [ii.guild.get_role(rid) for rid in sb.get("roles", [])]
                roles_to_add = [r for r in roles_to_add if r and r < ii.guild.me.top_role]
                if roles_to_add:
                    await target.add_roles(*roles_to_add, reason=f"Restore od {ii.user}")
                data["soft_bans"].pop(str(self.target_id), None); save_data()
                await ii.response.send_message(f"<:icon_check:1519358376268533810> Vraćene uloge za {target.mention}", ephemeral=True)
            except Exception as e:
                await ii.response.send_message(f"<:icon_cross:1519358379917836508> Greška: `{e}`", ephemeral=True)

        @discord.ui.button(label="<:e_hammer:1519362836671762494> Pravi Ban", style=discord.ButtonStyle.danger, custom_id=f"softban_hardban_{korisnik.id}")
        async def hardban(self, ii: discord.Interaction, btn: discord.ui.Button):
            if ii.user.id not in OWNER_IDS:
                return await ii.response.send_message("<:icon_cross:1519358379917836508> Samo vlasnik može banovati.", ephemeral=True)
            target = ii.guild.get_member(self.target_id)
            if not target:
                return await ii.response.send_message("<:icon_cross:1519358379917836508> Korisnik više nije na serveru.", ephemeral=True)
            try:
                await target.ban(reason=f"[VLASNIK] Pravi ban iz soft-ban panela ({ii.user})")
                data.get("soft_bans", {}).pop(str(self.target_id), None); save_data()
                await ii.response.send_message(f"<:e_hammer:1519362836671762494> {target} pravi banovan.", ephemeral=True)
            except Exception as e:
                await ii.response.send_message(f"<:icon_cross:1519358379917836508> Greška: `{e}`", ephemeral=True)

    await i.response.send_message(embed=em("<:e_no:1519363018725658675> Soft-Ban (uloga Banned Permisson)", color=COLORS["error"], thumb=korisnik.display_avatar.url, fields=[
        ("<:e_user:1519363093736718518> Korisnik", f"{korisnik.mention} (`{korisnik.id}`)", False),
        ("📝 Razlog", razlog, False),
        ("<:e_shield2:1519362627795554374>️ Moderator", i.user.mention, True),
        ("ℹ️ Info", "Pravi Discord ban može uraditi **samo vlasnik** (dugmad ispod).", False),
    ]), view=SoftBanView(korisnik.id, banned_role.id))
    # DM vlasniku za odobrenje pravog bana
    for oid in OWNER_IDS:
        try:
            owner = await bot.fetch_user(oid)
            await owner.send(embed=em("<:e_bell:1519363063738925187> Soft-Ban zahtijeva pažnju", color=COLORS["warning"], fields=[
                ("<:e_user:1519363093736718518> Korisnik", f"{korisnik} (`{korisnik.id}`)", False),
                ("📝 Razlog", razlog, False),
                ("<:e_shield2:1519362627795554374>️ Moderator", f"{i.user} (`{i.user.id}`)", False),
                ("<:e_house:1519362841369378961> Server", i.guild.name, True),
                ("<:e_scales:1519362852853649439>️ Akcija", "Vrati uloge ili pravi ban — kroz panel u serveru.", False),
            ]))
        except: pass

@bot.tree.command(name="ban-dozvola", description="<:e_crown2:1519363047163166922> [VLASNIK] Dozvoli/oduzmi pravo na /ban za 〢 /GIAN člana")
async def ban_dozvola(i: discord.Interaction, akcija: str, korisnik: discord.Member):
    """
    akcija: "add" (dodaj dozvolu) ili "remove" (ukloni dozvolu)
    Samo vlasnici iz OWNER_IDS smiju koristiti ovu komandu.
    """
    if i.user.id not in OWNER_IDS:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Pristup odbijen", "Samo vlasnik može koristiti `/ban-dozvola`!", color=COLORS["error"]),
            ephemeral=True)
    akcija_norm = akcija.lower().strip()
    if akcija_norm not in ("add", "remove", "dodaj", "ukloni"):
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Greška", "Akcija mora biti `add` ili `remove`.\nPrimjer: `/ban-dozvola add @korisnik`", color=COLORS["error"]),
            ephemeral=True)
    allowed: list = data.setdefault("ban_allowed_ids", [])
    uid = str(korisnik.id)
    if akcija_norm in ("add", "dodaj"):
        if uid not in allowed:
            allowed.append(uid)
            save_data()
        return await i.response.send_message(
            embed=em("<:icon_check:1519358376268533810> Dozvola dodana",
                     f"{korisnik.mention} (`{korisnik}`) sada **može koristiti `/ban`**.\n"
                     f"<:icon_warning:1519358274284032030>️ Mora imati ulogu `〢 /GIAN` da bi komanda radila.",
                     color=COLORS["success"]),
            ephemeral=True)
    else:
        if uid in allowed:
            allowed.remove(uid)
            save_data()
        return await i.response.send_message(
            embed=em("<:icon_check:1519358376268533810> Dozvola uklonjena",
                     f"{korisnik.mention} (`{korisnik}`) više **ne može koristiti `/ban`**.",
                     color=COLORS["warning"]),
            ephemeral=True)

@bot.tree.command(name="kick", description="<:e_run:1519362884868636883> [VLASNIK] Pravi kick / [STAFF] dodjela /GIAN oznake")
@app_commands.default_permissions(kick_members=True)
@app_commands.checks.has_permissions(kick_members=True)
async def kick(i: discord.Interaction, korisnik: discord.Member, razlog: str = "Bez razloga"):
    if korisnik.top_role >= i.user.top_role:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", "Ne možeš ovo nekome sa višom ili istom ulogom!", color=COLORS["error"]), ephemeral=True)

    # ── VLASNIK → pravi kick ──
    if i.user.id in OWNER_IDS:
        await korisnik.kick(reason=f"[VLASNIK KICK] {razlog}")
        return await i.response.send_message(embed=em("<:e_run:1519362884868636883> Izbačen (Vlasnik)", color=COLORS["warning"], thumb=korisnik.display_avatar.url, fields=[
            ("<:e_user:1519363093736718518> Korisnik", f"{korisnik} (`{korisnik.id}`)", False),
            ("📝 Razlog", razlog, False), ("<:e_crown2:1519363047163166922> Vlasnik", i.user.mention, False),
        ]))

    # ── STAFF → dodaj /GIAN ulogu kao oznaku upozorenja ──
    gianni_role = _find_role_by_names(i.guild, ["/GIAN", "/Gianni", "GIAN", "/GIANNI", "GIANNI"])
    if not gianni_role:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", "Uloga `/GIAN` ne postoji na serveru!\nKreiraj je ili javi vlasniku.", color=COLORS["error"]), ephemeral=True)
    if gianni_role >= i.guild.me.top_role:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", f"Bot ne može dodijeliti `{gianni_role.name}` jer je iznad njegove uloge!", color=COLORS["error"]), ephemeral=True)

    try:
        await korisnik.add_roles(gianni_role, reason=f"Soft-kick (oznaka) od {i.user}: {razlog}")
    except discord.Forbidden:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", "Bot nema permisiju!", color=COLORS["error"]), ephemeral=True)

    await i.response.send_message(embed=em("<:icon_warning:1519358274284032030>️ Soft-Kick (oznaka /GIAN)", color=COLORS["warning"], thumb=korisnik.display_avatar.url, fields=[
        ("<:e_user:1519363093736718518> Korisnik", f"{korisnik.mention} (`{korisnik.id}`)", False),
        ("📝 Razlog", razlog, False),
        ("<:e_shield2:1519362627795554374>️ Moderator", i.user.mention, True),
        ("ℹ️ Info", "Pravi Discord kick može uraditi **samo vlasnik**. Dodijeljena oznaka `/GIAN`.", False),
    ]))
    for oid in OWNER_IDS:
        try:
            owner = await bot.fetch_user(oid)
            await owner.send(embed=em("<:e_bell:1519363063738925187> Soft-Kick (oznaka /GIAN)", color=COLORS["warning"], fields=[
                ("<:e_user:1519363093736718518> Korisnik", f"{korisnik} (`{korisnik.id}`)", False),
                ("📝 Razlog", razlog, False),
                ("<:e_shield2:1519362627795554374>️ Moderator", f"{i.user} (`{i.user.id}`)", False),
                ("<:e_house:1519362841369378961> Server", i.guild.name, True),
            ]))
        except: pass

@bot.tree.command(name="timeout", description="<:e_time2:1519362726952964227>️ Ućutkaj korisnika")
@app_commands.default_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout_cmd(i: discord.Interaction, korisnik: discord.Member, minuta: int = 10, razlog: str = "Bez razloga"):
    if not 1 <= minuta <= 1440:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", "Između 1 i 1440 minuta!", color=COLORS["error"]), ephemeral=True)
    await korisnik.timeout(discord.utils.utcnow() + timedelta(minutes=minuta), reason=razlog)
    await i.response.send_message(embed=em("<:e_time2:1519362726952964227>️ Ućutkan", color=COLORS["warning"], thumb=korisnik.display_avatar.url, fields=[
        ("<:e_user:1519363093736718518> Korisnik", korisnik.mention, True), ("<:e_time2:1519362726952964227> Trajanje", f"`{minuta}` min", True),
        ("📝 Razlog", razlog, False), ("<:e_shield2:1519362627795554374>️ Moderator", i.user.mention, True),
    ]))

@bot.tree.command(name="warn", description="<:icon_warning:1519358274284032030>️ Upozori korisnika")
@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_permissions(manage_messages=True)
async def warn(i: discord.Interaction, korisnik: discord.Member, razlog: str = "Kršenje pravila"):
    warns = get_warnings(i.guild.id, korisnik.id)
    warns.append({"razlog": razlog, "moderator": str(i.user), "vreme": datetime.now(timezone.utc).strftime("%d.%m.%Y. %H:%M")})
    save_data()
    await i.response.send_message(embed=em("<:icon_warning:1519358274284032030>️ Upozorenje", color=COLORS["warning"], thumb=korisnik.display_avatar.url, fields=[
        ("<:e_user:1519363093736718518> Korisnik", korisnik.mention, True), ("<:e_chart:1519362656568475880> Ukupno", f"`{len(warns)}`", True),
        ("📝 Razlog", razlog, False), ("<:e_shield2:1519362627795554374>️ Moderator", i.user.mention, True),
    ]))

@bot.tree.command(name="warnings", description="<:e_clipboard:1519363052871614627> Upozorenja korisnika")
@app_commands.checks.has_permissions(manage_messages=True)
async def warnings_cmd(i: discord.Interaction, korisnik: discord.Member):
    warns = get_warnings(i.guild.id, korisnik.id)
    if not warns:
        return await i.response.send_message(embed=em(f"<:e_clipboard:1519363052871614627> {korisnik.display_name}", "Nema upozorenja! <:icon_check:1519358376268533810>", color=COLORS["success"]), ephemeral=True)
    desc = "\n".join([f"`{n+1}.` **{w['razlog']}** — {w['vreme']}" for n, w in enumerate(warns)])
    await i.response.send_message(embed=em(f"<:e_clipboard:1519363052871614627> {korisnik.display_name} — Upozorenja", desc, color=COLORS["warning"], thumb=korisnik.display_avatar.url), ephemeral=True)

@bot.tree.command(name="clearwarnings", description="<:e_trash:1519362951247691898>️ Obriši upozorenja")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def clearwarnings(i: discord.Interaction, korisnik: discord.Member):
    data["warnings"].get(str(i.guild.id), {}).pop(str(korisnik.id), None)
    save_data()
    await i.response.send_message(embed=em("<:icon_check:1519358376268533810> Obrisano", f"Sva upozorenja za {korisnik.mention} su uklonjena.", color=COLORS["success"]), ephemeral=True)

@bot.tree.command(name="clear", description="<:e_broom:1519362900681298000> Obriši poruke")
@app_commands.default_permissions(manage_messages=True)
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(i: discord.Interaction, kolicina: int = 10):
    await i.response.defer(ephemeral=True)
    deleted = await i.channel.purge(limit=max(1, min(kolicina, 100)))
    await i.followup.send(embed=em("<:e_broom:1519362900681298000> Čišćenje završeno", color=COLORS["success"], fields=[
        ("<:e_trash:1519362951247691898>️ Obrisano", f"`{len(deleted)}` poruka", True), ("<:e_pushpin:1519363357436543099> Kanal", i.channel.mention, True),
    ]), ephemeral=True)

# ═══════════════════════════════════════════
#    EKONOMIJA & LEVEL
# ═══════════════════════════════════════════
@bot.tree.command(name="baki", description="<:e_coins3:1519362621206298666> Provjeri stanje novca")
async def baki(i: discord.Interaction, korisnik: discord.Member = None):
    u = korisnik or i.user
    d = get_economy(u.id)
    last = time.strftime("%H:%M", time.localtime(d["last_work"])) if d["last_work"] else "Nikad"
    await i.response.send_message(embed=em_pro(f"<:e_coins3:1519362621206298666> Novčanik", f"<:e_diamond2:1519362640961474601> Stanje računa za {u.mention}", color=COLORS["gold"], thumb=u.display_avatar.url, author=u, fields=[
        ("<:e_coins3:1519362621206298666> Balans", f"```yaml\n{d['balance']:,} <:e_coins3:1519362621206298666>\n```", True), ("<:e_job:1519362615069904977> Poslednji posao", f"`{last}`", True),
    ]))

@bot.tree.command(name="posao", description="<:e_job:1519362615069904977> Radi i zaradi (svakih 30 min)")
@app_commands.checks.cooldown(1, 1800, key=lambda i: i.user.id)
async def posao(i: discord.Interaction):
    cfg_p = _g_eco("posao")
    if not cfg_p.get("enabled", True):
        return await i.response.send_message(embed=em("<:e_pause:1519363038107406447>️ Isključeno", "Komanda `/posao` je trenutno isključena.", color=COLORS["warning"]), ephemeral=True)
    d = get_economy(i.user.id)
    earn = random.randint(int(cfg_p.get("reward_min", 150)), int(cfg_p.get("reward_max", 600)))
    d["balance"] += earn; d["last_work"] = time.time(); save_data()
    quest_progress(i.user.id, "work3")
    _poo_task_progress(i.guild.id if i.guild else 0, i.user.id, "work")
    await i.response.send_message(embed=em("<:e_job:1519362615069904977> Posao završen!", f"*{random.choice(JOBS)}*", color=COLORS["success"], fields=[
        ("<:e_coins3:1519362621206298666> Zarada", f"`+{earn} <:e_coins3:1519362621206298666>`", True), ("<:e_bank2:1519362662515871744> Balans", f"`{d['balance']:,} <:e_coins3:1519362621206298666>`", True), ("<:e_time2:1519362726952964227> Sledeći", "za 30 min", True),
    ]))

@bot.tree.command(name="daily", description="<:e_gift:1519362618341462067> Dnevna nagrada")
async def daily(i: discord.Interaction):
    cfg_d = _g_eco("daily")
    if not cfg_d.get("enabled", True):
        return await i.response.send_message(embed=em("<:e_pause:1519363038107406447>️ Isključeno", "Komanda `/daily` je trenutno isključena.", color=COLORS["warning"]), ephemeral=True)
    # <:e_lock3:1519362717394403432> PERZISTENTNI cooldown — preživljava restart bota
    cooldown_secs = int(cfg_d.get("cooldown_hours", 24)) * 3600
    d = get_economy(i.user.id)
    now = time.time()
    last = float(d.get("last_daily", 0) or 0)
    elapsed = now - last
    if elapsed < cooldown_secs:
        remaining = int(cooldown_secs - elapsed)
        hours, rem = divmod(remaining, 3600)
        mins, secs = divmod(rem, 60)
        if hours:   wait_text = f"{hours}h {mins}min"
        elif mins:  wait_text = f"{mins}min {secs}s"
        else:       wait_text = f"{secs}s"
        return await i.response.send_message(
            embed=em("<:e_time2:1519362726952964227> Cooldown!", f"Već si uzeo daily!\n\n<:e_time2:1519362726952964227> Sačekaj još **{wait_text}**.", color=COLORS["warning"]),
            ephemeral=True
        )
    reward = random.randint(int(cfg_d.get("reward_min", 300)), int(cfg_d.get("reward_max", 800)))
    d["balance"] += reward
    d["last_daily"] = now
    save_data()
    quest_progress(i.user.id, "daily1")
    _poo_task_progress(i.guild.id if i.guild else 0, i.user.id, "daily")
    cd_label = f"za {cfg_d.get('cooldown_hours', 24)}h"
    await i.response.send_message(embed=em(
        "<:e_gift:1519362618341462067> Daily Nagrada",
        f"<:e_sparkles:1519363032185176198>  Tvoj poklon je stigao!",
        color=COLORS["gold"],
        fields=[
            ("<:e_coins3:1519362621206298666> Nagrada", f"`+{reward:,} <:e_coins3:1519362621206298666>`", True),
            ("<:e_bank2:1519362662515871744> Balans",   f"`{d['balance']:,} <:e_coins3:1519362621206298666>`", True),
            ("<:e_time2:1519362726952964227> Sljedeći", f"`{cd_label}`", True),
        ]
    ))

@bot.tree.command(name="daj", description="<:e_shake:1519362947766554737> Pošalji pare drugaru")
async def daj(i: discord.Interaction, korisnik: discord.Member, iznos: int):
    if iznos <= 0: return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", "Iznos mora biti pozitivan!", color=COLORS["error"]), ephemeral=True)
    if korisnik.id == i.user.id: return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Greška", "Ne možeš sebi slati!", color=COLORS["error"]), ephemeral=True)
    s, r = get_economy(i.user.id), get_economy(korisnik.id)
    if s["balance"] < iznos: return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Nemaš dovoljno", f"Imaš samo `{s['balance']:,} <:e_coins3:1519362621206298666>`!", color=COLORS["error"]), ephemeral=True)
    s["balance"] -= iznos; r["balance"] += iznos; save_data()
    await i.response.send_message(embed=em("<:e_shake:1519362947766554737> Transakcija uspešna", color=COLORS["success"], fields=[
        ("<:e_box:1519363099478458498> Od", i.user.mention, True), ("<:e_inbox:1519363351354937497> Za", korisnik.mention, True), ("<:e_coins3:1519362621206298666> Iznos", f"`{iznos:,} <:e_coins3:1519362621206298666>`", True),
    ]))

@bot.tree.command(name="kradi", description="<:e_search:1519363103064723547>️ Pokušaj ukrasti (rizično!)")
@app_commands.checks.cooldown(1, 7200, key=lambda i: i.user.id)
async def kradi(i: discord.Interaction, korisnik: discord.Member):
    cfg_k = _g_eco("kradi")
    if not cfg_k.get("enabled", True):
        return await i.response.send_message(embed=em("<:e_pause:1519363038107406447>️ Isključeno", "Komanda `/kradi` je trenutno isključena.", color=COLORS["warning"]), ephemeral=True)
    if korisnik.id == i.user.id: return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Ne možeš krasti sam sebe!", color=COLORS["error"]), ephemeral=True)
    if korisnik.bot: return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Botovi nemaju para!", color=COLORS["error"]), ephemeral=True)
    s, r = get_economy(i.user.id), get_economy(korisnik.id)
    if r["balance"] < 100: return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Siromašna žrtva, nema šta ukrasti.", color=COLORS["error"]), ephemeral=True)
    await i.response.defer()
    await asyncio.sleep(2)
    steal_max = int(cfg_k.get("steal_max", 300))
    steal_min = int(cfg_k.get("steal_min", 50))
    success_rate = float(cfg_k.get("success_rate", 38)) / 100.0
    amount = random.randint(steal_min, min(steal_max, r["balance"]))
    if random.random() < success_rate:
        r["balance"] -= amount; s["balance"] += amount
        e = em("<:e_search:1519363103064723547>️ Krađa uspješna!", "Niko te nije video. Za sad... <:e_eyes:1519362845970530577>", color=COLORS["gold"], fields=[
            ("<:e_coins3:1519362621206298666> Ukradeno", f"`{amount:,} <:e_coins3:1519362621206298666>`", True), ("<:e_user:1519363093736718518> Žrtva", korisnik.mention, True), ("<:e_bank2:1519362662515871744> Balans", f"`{s['balance']:,} <:e_coins3:1519362621206298666>`", True),
        ])
    else:
        fine = random.randint(100, 350)
        s["balance"] = max(0, s["balance"] - fine)
        e = em("<:e_taxi:1519363380513603615> Uhvaćen si!", f"{korisnik.mention} te je prijavio policiji! <:e_devil:1519362989470253187>", color=COLORS["error"], fields=[
            ("<:e_moneywing:1519362955437805771> Kazna", f"`{fine:,} <:e_coins3:1519362621206298666>`", True), ("<:e_bank2:1519362662515871744> Balans", f"`{s['balance']:,} <:e_coins3:1519362621206298666>`", True),
        ])
    save_data(); await i.followup.send(embed=e)

@bot.tree.command(name="rank", description="<:e_level2:1519362739749785610> Level i XP")
async def rank(i: discord.Interaction, korisnik: discord.Member = None):
    u = korisnik or i.user
    d = get_xp(u.id)
    needed = max(d["level"] * 75, 1)
    filled = min(d["xp"] * 10 // needed, 10)
    empty  = 10 - filled
    bar    = "█" * filled + "░" * empty
    pct    = min(round(d["xp"] / needed * 100), 100)
    rank_e = discord.Embed(
        description=(
            f"**{u.display_name}**\n"
            f"```\n[{bar}] {pct}%\n```"
        ),
        color=COLORS["purple"],
        timestamp=datetime.now(timezone.utc)
    )
    rank_e.set_thumbnail(url=u.display_avatar.url)
    rank_e.add_field(name="<:e_trophy2:1519362624742232146>  Level",   value=f"**{d['level']}**",           inline=True)
    rank_e.add_field(name="<:e_star2:1519363084253266031>  XP",        value=f"**{d['xp']:,} / {needed:,}**", inline=True)
    rank_e.add_field(name="<:e_chart:1519362656568475880>  Progres",   value=f"**{pct}%**",                 inline=True)
    rank_e.set_author(name=f"🏆  Rank — {u.display_name}", icon_url=u.display_avatar.url)
    rank_e.set_footer(text=f"{BOT_NAME} {VERSION}  •  Rank sistem")
    await i.response.send_message(embed=rank_e)

# ═══════════════════════════════════════════
# /aktivnost — prikaz LVL / XP / poruke
# ═══════════════════════════════════════════
@bot.tree.command(name="aktivnost", description="<:e_chart:1519362656568475880> Tvoja aktivnost: level, XP i broj poruka")
@discord.app_commands.describe(korisnik="Čija statistika? (default: ti)")
async def aktivnost(i: discord.Interaction, korisnik: discord.Member = None):
    u = korisnik or i.user
    gid = i.guild.id if i.guild else 0
    mkey = f"{gid}:{u.id}"
    msgs = int(data.get("msg_count", {}).get(mkey, 0))
    xp_d = get_xp(u.id)
    lvl  = int(xp_d.get("level", 1))
    xp   = int(xp_d.get("xp", 0))
    # Napredak do sljedećeg levela (svakih 100 poruka)
    do_sljedeceg = 100 - (msgs % 100) if msgs % 100 != 0 else 100
    proslo = msgs % 100
    filled = min(proslo // 10, 10)
    bar = "<:e_sun:1519362860218843399>" * filled + "<:e_stop:1519363022399995914>" * (10 - filled)
    sep = "━━━━━━━━━━━━━━━━━━━━"
    desc = (
        f"{sep}\n"
        f"<:e_user:1519363093736718518> **{u.display_name}**\n"
        f"{sep}\n"
        f"{bar}  `{proslo}/100`\n"
        f"<:e_time2:1519362726952964227> Još **`{do_sljedeceg}`** poruka do sljedećeg levela!\n"
    )
    e = discord.Embed(
        title="<:e_chart:1519362656568475880> ᴀᴋᴛɪᴠɴᴏsᴛ",
        description=desc,
        color=_LP,
        timestamp=datetime.now(timezone.utc)
    )
    e.set_thumbnail(url=u.display_avatar.url)
    e.add_field(name="<:e_trophy2:1519362624742232146> Level",  value=f"```fix\n<:e_star2:1519363084253266031> {lvl} <:e_star2:1519363084253266031>\n```", inline=True)
    e.add_field(name="<:e_star2:1519363084253266031> XP",     value=f"```py\n{xp:,}\n```",      inline=True)
    e.add_field(name="<:e_bubble:1519363307998417148> Poruke", value=f"```css\n{msgs:,}\n```",   inline=True)
    e.add_field(name="<:e_level2:1519362739749785610> Sistem", value="```ini\n[100 poruka = 1 LVL + 100 XP]\n```", inline=True)
    e.set_footer(text=f"<:e_bolt:1519362674717102160> {BOT_NAME} • Aktivnost • Svakih 100 poruka novi level!")
    await i.response.send_message(embed=e)

# ═══════════════════════════════════════════
#    /vers — hip-hop rima u stylish embedu
# ═══════════════════════════════════════════
VERS_CHANNEL_ID = 1498983966005268520

@bot.tree.command(name="leaderboard", description="<:e_medal3:1519363547514015764> Top lista servera")
@app_commands.choices(tip=[app_commands.Choice(name="XP & Leveli", value="xp"), app_commands.Choice(name="Novac <:e_coins3:1519362621206298666>", value="novac")])
async def leaderboard(i: discord.Interaction, tip: str = "xp"):
    await i.response.defer()
    medals = ["<:e_star2:1519363084253266031>", "<:icon_rank2:1519358512336212091>", "<:icon_rank3:1519358517633355919>"]
    if tip == "xp":
        srt = sorted(data["xp"].items(), key=lambda x: (x[1]["level"], x[1]["xp"]), reverse=True)[:10]
        lines = []
        for n, (uid, d) in enumerate(srt):
            try: user = await bot.fetch_user(int(uid)); name = user.display_name
            except: name = f"#{uid[:4]}"
            lines.append(f"{medals[n] if n<3 else f'`{n+1}.`'} **{name}** — Level `{d['level']}` • `{d['xp']} XP`")
        e = em("<:e_medal3:1519363547514015764> Top Lista — XP", "\n".join(lines) or "Nema podataka.", color=COLORS["purple"])
    else:
        srt = sorted(data["economy"].items(), key=lambda x: x[1]["balance"], reverse=True)[:10]
        lines = []
        for n, (uid, d) in enumerate(srt):
            try: user = await bot.fetch_user(int(uid)); name = user.display_name
            except: name = f"#{uid[:4]}"
            lines.append(f"{medals[n] if n<3 else f'`{n+1}.`'} **{name}** — `{d['balance']:,} <:e_coins3:1519362621206298666>`")
        e = em("<:e_medal3:1519363547514015764> Top Lista — Bogatstvo", "\n".join(lines) or "Nema podataka.", color=COLORS["gold"])
    await i.followup.send(embed=e)

# ═══════════════════════════════════════════
#    IGRE
# ═══════════════════════════════════════════
class KPM(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=30); self.user = user; self.msg = None

    async def on_timeout(self):
        for c in self.children: c.disabled = True
        if self.msg: await self.msg.edit(embed=em("<:e_time2:1519362726952964227>️ Vreme isteklo!", "Igra otkazana.", color=COLORS["error"]), view=self)

    async def play(self, i, choice):
        if i.user != self.user: return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Nije tvoja igra!", color=COLORS["error"]), ephemeral=True)
        bot_c = random.choice(["<:e_hammer:1519362836671762494> Kamen", "📝 Papir", "<:e_sword2:1519362631146930317> Makaze"])
        win_map = {("Kamen","Makaze"),("Papir","Kamen"),("Makaze","Papir")}
        cw, bw = choice.split()[1], bot_c.split()[1]
        if choice == bot_c:   res, color = "<:e_shake:1519362947766554737> Nerješeno!", COLORS["warning"]
        elif (cw, bw) in win_map: res, color = "<:e_trophy2:1519362624742232146> Pobijedio si!", COLORS["success"]
        else:                 res, color = "<:e_skull:1519362992502997125> Izgubio si!", COLORS["error"]
        for c in self.children: c.disabled = True
        _kpm_res = discord.Embed(
            title=f"<:e_ctrl:1519362682296209498>  Kamen — Papir — Makaze",
            description=f"{res}",
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        _kpm_res.add_field(name="<:e_user:1519363093736718518>  Ti",            value=choice, inline=True)
        _kpm_res.add_field(name="<:e_gear:1519362652516782194>  Bot",           value=bot_c,  inline=True)
        _kpm_res.add_field(name="<:e_chart:1519362656568475880>  Rezultat",     value=res,    inline=False)
        _kpm_res.set_footer(text=f"{BOT_NAME} {VERSION}")
        await i.response.edit_message(embed=_kpm_res, view=self); self.stop()

    @discord.ui.button(label="Kamen",  emoji="<:e_hammer:1519362836671762494>", style=discord.ButtonStyle.primary)
    async def r(self, i, b): await self.play(i, "<:e_hammer:1519362836671762494> Kamen")
    @discord.ui.button(label="Papir",  emoji="📝", style=discord.ButtonStyle.success)
    async def p(self, i, b): await self.play(i, "📝 Papir")
    @discord.ui.button(label="Makaze", emoji="<:e_sword2:1519362631146930317>️", style=discord.ButtonStyle.danger)
    async def s(self, i, b): await self.play(i, "<:e_sword2:1519362631146930317>️ Makaze")

@bot.tree.command(name="kpm", description="<:e_ctrl:1519362682296209498> Kamen-Papir-Makaze")
async def kpm(i: discord.Interaction):
    v = KPM(i.user)
    _kpm_e = discord.Embed(
        title="<:e_ctrl:1519362682296209498>  Kamen — Papir — Makaze",
        description=f"<:e_shake:1519362947766554737>  {i.user.mention}, odaberi potez!",
        color=COLORS["balkan"],
        timestamp=datetime.now(timezone.utc)
    )
    _kpm_e.add_field(name="<:e_hammer:1519362836671762494>  Kamen", value="Pobjeđuje Makaze",  inline=True)
    _kpm_e.add_field(name="📝  Papir",  value="Pobjeđuje Kamen",   inline=True)
    _kpm_e.add_field(name="<:e_sword2:1519362631146930317>  Makaze", value="Pobjeđuju Papir", inline=True)
    _kpm_e.set_footer(text=f"{BOT_NAME} {VERSION}  •  Imaš 30 sekundi")
    await i.response.send_message(embed=_kpm_e, view=v)
    v.msg = await i.original_response()

@bot.tree.command(name="slots", description="🎰 Slot mašina — uloži i zavrti!")
@app_commands.describe(ulog="Iznos uloga (min 20 — max 1.000.000.000)")
@app_commands.checks.cooldown(1, 15, key=lambda i: i.user.id)
async def slots(i: discord.Interaction, ulog: int = 100):
    _poo_task_progress(i.guild.id if i.guild else 0, i.user.id, "slots")
    SLOTS_MIN = 20
    SLOTS_MAX = 1_000_000_000

    if ulog < SLOTS_MIN:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Premali ulog", f"Minimalan ulog je **{SLOTS_MIN:,} <:e_coins3:1519362621206298666>**.", color=COLORS["error"]),
            ephemeral=True
        )
    if ulog > SLOTS_MAX:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Preveliki ulog", f"Maksimalan ulog je **{SLOTS_MAX:,} <:e_coins3:1519362621206298666>**.", color=COLORS["error"]),
            ephemeral=True
        )

    d = get_economy(i.user.id)
    if d["balance"] < ulog:
        return await i.response.send_message(
            embed=em(
                "<:icon_cross:1519358379917836508> Nemaš dovoljno",
                f"Trebaš **{ulog:,} <:e_coins3:1519362621206298666>** a imaš samo **{d['balance']:,} <:e_coins3:1519362621206298666>**.",
                color=COLORS["error"]
            ),
            ephemeral=True
        )

    await i.response.defer()

    # ─── Simboli (isti kao OWO: lakši simboli češći) ─────────────────────
    SLOT_DATA = [
        ("🍒", 30, 2.0,  "×2",   0xE74C3C),
        ("🍉", 25, 3.0,  "×3",   0x2ECC71),
        ("🔔", 18, 4.0,  "×4",   0xF39C12),
        ("💎", 10, 5.0,  "×5",   0x3498DB),
        ("🌟",  6, 7.0,  "×7",   0xF1C40F),
        ("🍀",  4, 9.0,  "×9",   0x27AE60),
        ("7️⃣",  1, 15.0, "×15",  0xFFD700),
    ]
    SYM      = [s[0] for s in SLOT_DATA]
    WEIGHTS  = [s[1] for s in SLOT_DATA]
    MULTI    = {s[0]: s[2] for s in SLOT_DATA}
    LABEL    = {s[0]: s[3] for s in SLOT_DATA}

    reels = random.choices(SYM, weights=WEIGHTS, k=3)
    SPIN  = "🎰"

    def _embed(r1, r2, r3, status: str = "", title: str = "", ts=None) -> discord.Embed:
        reels_line = f"> `[ {r1} ]`  `[ {r2} ]`  `[ {r3} ]`"
        desc = f"\n{reels_line}"
        if status:
            desc += f"\n\n> {status}"
        e = discord.Embed(
            title=title or "🎰 | SLOTS | 🎰",
            description=desc,
            color=_LP,
        )
        e.set_author(name=i.user.display_name, icon_url=i.user.display_avatar.url)
        if ts:
            e.timestamp = ts
        e.set_footer(text=f"🪙 | Ulog: {ulog:,}  •  💰 | Balans: {d['balance']:,}")
        return e

    # ── Frame 0: svi reelovi se vrte (~0.7s) — status prazan, animacija u reelovima ──
    msg = await i.followup.send(embed=_embed(SPIN, SPIN, SPIN, title="🎰 | SLOTS | 🎰"), wait=True)
    await asyncio.sleep(0.7)

    # ── Frame 1: lijevi staje (~0.65s) ───────────────────────────────────
    try: await msg.edit(embed=_embed(reels[0], SPIN, SPIN, title="🎰 | SLOTS | 🎰"))
    except: pass
    await asyncio.sleep(0.65)

    # ── Frame 2: desni staje (~0.65s) ────────────────────────────────────
    try: await msg.edit(embed=_embed(reels[0], SPIN, reels[2], title="🎰 | SLOTS | 🎰"))
    except: pass
    await asyncio.sleep(0.65)

    # ── Odluka ───────────────────────────────────────────────────────────
    all_same  = reels[0] == reels[1] == reels[2]
    two_same  = (reels[0]==reels[1]) or (reels[1]==reels[2]) or (reels[0]==reels[2])
    sym       = reels[1]

    if all_same:
        multiplier   = MULTI[sym]
        win          = int(ulog * multiplier)
        d["balance"] += win - ulog
        if sym == "7️⃣":
            title    = "🎰 | 7 7 7 MEGA JACKPOT 🎉 | 🎰"
            status   = f"🏆 **JACKPOT!**  +**{win:,}** <:e_coins3:1519362621206298666>  `{LABEL[sym]}`"
        else:
            title    = f"🎰 | {sym}{sym}{sym} JACKPOT! | 🎰"
            status   = f"🎊 **Pogotak!**  +**{win:,}** <:e_coins3:1519362621206298666>  `{LABEL[sym]}`"

    elif two_same:
        win          = ulog
        d["balance"] += 0
        title        = "🎰 | Par — ulog vraćen | 🎰"
        status       = f"✨ **Dva ista!**  **{win:,}** <:e_coins3:1519362621206298666>  `×1.0`"

    else:
        d["balance"] = max(0, d["balance"] - ulog)
        title        = "🎰 | Nema sreće | 🎰"
        status       = f"💸 **Promašaj!**  −**{ulog:,}** <:e_coins3:1519362621206298666>"

    save_data()

    try:
        await msg.edit(embed=_embed(reels[0], reels[1], reels[2], status=status, title=title, ts=datetime.now(timezone.utc)))
    except Exception:
        pass

# /rulet uklonjeno (na zahtjev) — /flip i /8ball uklonjeni (v2.2) — pravimo mjesto za /mafia igru.
# /meme uklonjeno (v2.1) — vanjski sadržaj može vratiti NSFW u SFW kanal.

# ═══════════════════════════════════════════
#    VJEŠALA (Hangman)
# ═══════════════════════════════════════════
class VjesalaModal(discord.ui.Modal, title="Unesi slovo"):
    slovo = discord.ui.TextInput(label="Slovo (jedno)", min_length=1, max_length=1, placeholder="Npr: A")

    def __init__(self, hangman_view):
        super().__init__()
        self.hv = hangman_view

    async def on_submit(self, i: discord.Interaction):
        await self.hv.guess(i, self.slovo.value.upper().strip())

class VjesalaView(discord.ui.View):
    def __init__(self, user: discord.Member, word: str):
        super().__init__(timeout=300)
        self.user    = user
        self.word    = word.upper()
        self.guessed: set = set()
        self.wrong   = 0
        self.max_w   = 6
        self.over    = False

    def display_word(self):
        return " ".join(c if c in self.guessed else "\\_ " for c in self.word)

    def make_embed(self, title=None, color=None):
        wrong_letters = [l for l in sorted(self.guessed) if l not in self.word]
        right_letters = [l for l in sorted(self.guessed) if l in self.word]
        t = title or "<:e_ctrl:1519362682296209498> Vješala"
        c = color or COLORS["balkan"]
        e = discord.Embed(title=t, description="<:icon_game:1519358323667767346>  **Pogodi skrivenu riječ slovo po slovo!**", color=c, timestamp=datetime.now(timezone.utc))
        e.add_field(name="📝 Riječ", value=f"`{self.display_word()}`", inline=False)
        e.add_field(name="<:e_skull:1519362992502997125> Vješalo", value=VJASALA_FAZE[self.wrong], inline=True)
        e.add_field(name="<:icon_cross:1519358379917836508> Pogrešna", value=" ".join(wrong_letters) or "—", inline=True)
        e.add_field(name="<:icon_check:1519358376268533810> Tačna", value=" ".join(right_letters) or "—", inline=True)
        e.add_field(name="<:e_heart2:1519362668644012133>️ Životi", value=f"`{self.max_w - self.wrong}/{self.max_w}`", inline=True)
        e.set_footer(text=f"{BOT_NAME} {VERSION} • Pogodi slovo klikom!")
        return e

    async def guess(self, i: discord.Interaction, letter: str):
        if i.user != self.user:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Nije tvoja igra!", color=COLORS["error"]), ephemeral=True)
        if not letter.isalpha():
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Unesi samo slovo!", color=COLORS["error"]), ephemeral=True)
        if letter in self.guessed:
            return await i.response.send_message(embed=em("<:icon_warning:1519358274284032030>️", f"Slovo **{letter}** si već pokušao!", color=COLORS["warning"]), ephemeral=True)
        self.guessed.add(letter)
        if letter not in self.word:
            self.wrong += 1
        won  = all(c in self.guessed for c in self.word)
        lost = self.wrong >= self.max_w
        if won:
            self.over = True; self.children[0].disabled = True
            await i.response.edit_message(embed=self.make_embed(f"<:e_trophy2:1519362624742232146> Pobijedio si! Riječ: **{self.word}**", COLORS["success"]), view=self)
            self.stop()
        elif lost:
            self.over = True; self.children[0].disabled = True
            await i.response.edit_message(embed=self.make_embed(f"<:e_skull:1519362992502997125> Izgubio si! Bila je: **{self.word}**", COLORS["error"]), view=self)
            self.stop()
        else:
            await i.response.edit_message(embed=self.make_embed(), view=self)

    async def on_timeout(self):
        if not self.over:
            self.children[0].disabled = True
            try:
                await self.message.edit(embed=self.make_embed(f"⏱️ Vreme isteklo! Bila je: **{self.word}**", COLORS["error"]), view=self)
            except: pass

    @discord.ui.button(label="Unesi slovo", style=discord.ButtonStyle.primary, emoji="<:e_pencil:1519363059909398610>️")
    async def enter(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user != self.user:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Nije tvoja igra!", color=COLORS["error"]), ephemeral=True)
        await i.response.send_modal(VjesalaModal(self))

    @discord.ui.button(label="Predaj se", emoji="<:e_check2:1519362730057007268>️", style=discord.ButtonStyle.danger)
    async def give_up(self, i: discord.Interaction, b: discord.ui.Button):
        if i.user != self.user:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Nije tvoja igra!", color=COLORS["error"]), ephemeral=True)
        self.over = True
        for c in self.children: c.disabled = True
        await i.response.edit_message(embed=self.make_embed(f"<:e_check2:1519362730057007268>️ Predao si! Bila je: **{self.word}**", COLORS["warning"]), view=self)
        self.stop()

@bot.tree.command(name="vjasala", description="<:e_ctrl:1519362682296209498> Igra Vješala — pogodi skrivenu riječ!")
async def vjasala(i: discord.Interaction):
    _poo_task_progress(i.guild.id if i.guild else 0, i.user.id, "vjasala")
    word = random.choice(VJASALA_RJECNIK)
    v    = VjesalaView(i.user, word)
    await i.response.send_message(embed=v.make_embed(), view=v)
    v.message = await i.original_response()

# ═══════════════════════════════════════════
#    KALADONT
# ═══════════════════════════════════════════
_KALADONT_START_RAW = [
    "BALKON","RAKIJA","KAFANA","FUDBAL","TANJIR","SUNCE","ZIVOT","RIJEKA",
    "PLANINA","DRVO","KAMEN","VATRA","ZEMLJA","VJETAR","OBLAK","JEZERO",
    "MOST","GRAD","SELO","POLJE","BRDO","DOLINA","SPILJA","OCEAN",
    "MAJKA","OTAC","BRAT","SESTRA","BAKA","DJED","PRIJATELJ","KOMŠIJA",
    "GITARA","MUZIKA","PJESMA","PLES","RADIO","POZORIŠTE","BIOSKOP",
    "AUTOMOBIL","AVION","BROD","VAGON","BICIKL","MOTOCIKL","TRAKTOR",
    "JABUKA","KRUŠKA","ŠLJIVA","TREŠNJA","BANANA","NARANDZA","GROŽĐE",
    "CEVAPI","BUREK","SARMA","KAJMAK","PITA","PALAČINKA","KOLAC",
    "ŠKOLA","BOLNICA","CRKVA","DŽAMIJA","STADION","BIBLIOTEKA","MUZEJ",
]
# Normaliziraj sve start-words (skidanje dijakritika) i osiguraj da su u rječniku
KALADONT_START_WORDS = [_kaladont_normalize(w) for w in _KALADONT_START_RAW]
for _w in KALADONT_START_WORDS:
    KALADONT_DICT.add(_w)

kaladont_games: dict = {}  # channel_id -> {word, used, starter, letters, chain, msg}

KALADONT_ICONS = ["<:e_sparkles:1519363032185176198>","<:e_bolt:1519362674717102160>","<:e_fire2:1519362671491678280>","<:e_sparkles:1519363032185176198>","<:e_dolphin:1519363432615510078>","<:e_clover:1519363694549667881>","🎯","<:e_bomb:1519363456334168255>","<:e_sparkles:1519363032185176198>","<:e_circus:1519363558809272371>","<:e_diamond2:1519362640961474601>","<:e_masks:1519363003424706671>","<:e_rocket2:1519363332266524813>","<:e_feather:1519363362322907218>","<:e_dragon:1519363409421008987>","<:e_music2:1519362679310127114>"]
# Kockaste (boxed) ikone — koriste se SAMO u opisu kartice (description),
# gdje se custom emoji renderuje. NE koristiti u naslovima/field-name-ovima.
KALADONT_BOX_ICONS = [
    "<:e_sparkles:1519363032185176198>",
    "<:icon_lightning:1519358316327997612>",
    "<:e_fire2:1519362671491678280>",
    "<:e_star2:1519363084253266031>",
    "<:icon_trophy:1519358248942047342>",
    "<:e_diamond2:1519362640961474601>",
    "<:e_crown2:1519363047163166922>",
    "<:icon_gift:1519358266738737274>",
    "🎯",
    "<:e_books:1519363612978839642>",
    "<:icon_music:1519358320337752125>",
    "<:icon_heart:1519358309008674848>",
]
KALADONT_COLOR = _LP

def kaladont_start_embed(game: dict, mention: str):
    word    = game["word"]
    letters = game["letters"]
    req     = word[-letters:]
    tezina_map = {1: "Lako · **1 slovo**", 2: "Normalno · **2 slova**", 3: "Teško · **3 slova**"}
    tezina_label = tezina_map.get(letters, f"**{letters} slova**")
    tezina_icon  = {1: "<:e_green:1519362769047126028>", 2: "<:e_green:1519362769047126028>", 3: "<:e_red:1519362782192210041>"}.get(letters, "<:e_gear:1519362652516782194>")
    e = discord.Embed(
        title="📝  K A L A D O N T",
        description=(
            f"Igra je počela! Prva riječ:\n"
            f"## <:e_bubble:1519363307998417148>  **{word}**\n\n"
            f"<:e_right:1519363367712591922>️  Sljedeća počinje sa : **`{req}`**\n"
            f"{tezina_icon}  Težina — {tezina_label}\n"
            f"<:e_link:1519363321458065408>  **Niz** #1\n\n"
            f"<:e_help2:1519362723148726534>  **Pravila igre**\n"
            f"<:icon_check:1519358376268533810>  Svaka riječ počinje traženim slovima\n"
            f"<:icon_ban:1519358278356959284>  Ista osoba **ne može** igrati iza sebe\n"
            f"<:e_repeat:1519363009883934740>  Ponavljanje iste riječi nije dozvoljeno\n"
            f"<:e_pencil:1519363059909398610>  Minimalno **3 slova** po riječi\n"
            f"<:icon_help:1519358364889383084>  Pritisni **Pomoć** za primjer riječi\n"
            f"<:icon_trophy:1519358248942047342>  Upiši **`KALADONT`** i osvoji **1500** <:e_coins3:1519362621206298666> + **200** <:e_sparkles:1519363032185176198> **XP**!"
        ),
        color=KALADONT_COLOR,
        timestamp=datetime.now(timezone.utc)
    )
    e.set_footer(text=f"Pokrenuo/la: {mention}  •  Pritisni dugme za kraj")
    return e

def kaladont_active_embed(game: dict):
    word    = game["word"]
    letters = game["letters"]
    req     = word[-letters:]
    count   = len(game["chain"])
    last_player = game.get("last_player_name", "—")
    icon    = KALADONT_ICONS[(count - 1) % len(KALADONT_ICONS)]
    streak_fx = E_FIRE1 if count < 5 else (E_FIRE2 if count < 10 else (E_FIRE3 if count < 20 else E_FIRE4))
    e = discord.Embed(
        title=f"{E_GAME}  K A L A D O N T  {E_GAME}",
        description=f"{E_FIRE1}{E_FIRE2}{E_FIRE3}{E_FIRE4}  **aktivna igra**  {E_FIRE4}{E_FIRE3}{E_FIRE2}{E_FIRE1}",
        color=KALADONT_COLOR,
        timestamp=datetime.now(timezone.utc)
    )
    e.add_field(name=f"{icon}  Zadnja riječ",    value=f"**`{word}`**",     inline=True)
    e.add_field(name="<:e_speaker:1519363314524881048>️  Odigrao/la",           value=last_player,         inline=True)
    e.add_field(name=f"{streak_fx}  Niz",        value=f"**#{count}**",     inline=True)
    e.add_field(name="<:e_right:1519363367712591922>️  Sljedeća počinje sa",  value=f"## **`{req}`**",   inline=False)
    e.set_footer(text="🎯 Pritisni dugme za kraj igre")
    return e

# ── Kaladont slike — uploadaj slike iz images/ foldera na Discord CDN ili Imgur,
#    zatim zamijeni URL-ove ispod sa tvojim linkovima ──────────────────────────
KALADONT_PENGUIN_GIFS = [
    "https://i.imgur.com/NcMzy4B.png",
    "https://i.imgur.com/XzLe6aT.png",
    "https://i.imgur.com/nsZcLzn.png",
]

def kaladont_word_card(word: str, player: str, req: str, count: int):
    icon = KALADONT_BOX_ICONS[(count - 1) % len(KALADONT_BOX_ICONS)]
    streak_fx = E_FIRE1 if count < 5 else (E_FIRE2 if count < 10 else (E_FIRE3 if count < 20 else E_FIRE4))
    e = discord.Embed(
        description=f"{icon}  **{word}**  ·  <:e_speaker:1519363314524881048>️ {player}  ·  {streak_fx} **#{count}**",
        color=KALADONT_COLOR,
    )
    e.add_field(name="<:e_right:1519363367712591922>️  Sljedeća", value=f"**`{req}`**", inline=False)
    _img = random.choice(KALADONT_PENGUIN_GIFS)
    if _img.startswith("http"):
        e.set_thumbnail(url=_img)
    e.set_footer(text=f"🐧 {BOT_NAME} Kaladont  •  #{count}")
    return e


def kaladont_invalid_embed(word: str, req: str, letters: int) -> discord.Embed:
    """Embed koji se prikazuje kada rijec nije u rjecniku."""
    e = discord.Embed(
        description=(
            f"<:icon_cross:1519358379917836508>  **{word}** nije u rječniku\n"
            f"<:e_right:1519363367712591922>️  Treba počinjati sa  **`{req}`**  ·  klikni za novu startnu riječ"
        ),
        color=COLORS["error"],
    )
    e.set_footer(text=f"🐧 {BOT_NAME} Kaladont  •  Nova Riječ resetuje startnu poziciju")
    return e

# ── Kaladont pomoć cooldown: uid -> timestamp zadnjeg klika ──
_kaladont_help_cd: dict = {}
KALADONT_HELP_CD = 15 * 60  # 15 minuta u sekundama

async def _send_kaladont_help(i: discord.Interaction, channel_id: int):
    """Zajednička logika za Pomoć dugme — koristi se i u KaladontView i KaladontWordView."""
    # ── 15-minuta cooldown po korisniku ──
    now = time.time()
    last = _kaladont_help_cd.get(i.user.id, 0)
    remaining = KALADONT_HELP_CD - (now - last)
    if remaining > 0 and i.user.id not in OWNER_IDS:
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        wait = f"{mins}m {secs}s" if mins else f"{secs}s"
        return await i.response.send_message(
            embed=em("<:e_time2:1519362726952964227> Cooldown", f"Možeš ponovo kliknuti Pomoć za **{wait}**.", color=COLORS["warning"]),
            ephemeral=True
        )
    _kaladont_help_cd[i.user.id] = now

    game = kaladont_games.get(channel_id)
    if not game:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508>", "Nema aktivne igre.", color=COLORS["error"]), ephemeral=True
        )
    req   = game["word"][-game["letters"]:]
    used  = game.get("used", set())
    hints = get_kaladont_hint(req, used)
    if hints:
        hint_text = "  ·  ".join(f"`{w}`" for w in hints)
        desc = (
            f"Sljedeća mora početi sa **`{req}`**\n\n"
            f"<:e_idea:1519363006599794799> **Primjeri iz baze:**\n{hint_text}\n\n"
            f"*Možeš koristiti i bilo koju drugu imenicu/glagol/pridjev!*"
        )
    else:
        desc = (
            f"Sljedeća mora početi sa **`{req}`**\n\n"
            f"<:e_idea:1519363006599794799> Nema primjera u bazi za **`{req}`**, ali probaj:\n"
            f"Imenice, glagoli, pridjevi koji počinju sa `{req}`.\n"
            f"*(Npr. ako je `{req}` → razmisli o riječima koje počinju tim slovima)*"
        )
    e = discord.Embed(
        title=f"<:icon_warning:1519358274284032030> Pomoć — počni sa `{req}`",
        description=desc,
        color=_LP,
        timestamp=datetime.now(timezone.utc)
    )
    e.set_footer(text="📝 Kaladont Pomoć • samo ti vidiš ovo • cooldown 15 min")
    await i.response.send_message(embed=e, ephemeral=True)


class KaladontView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="Pomoć", emoji="<:icon_warning:1519358274284032030>", style=discord.ButtonStyle.secondary, row=0)
    async def pomoc(self, i: discord.Interaction, b: discord.ui.Button):
        await _send_kaladont_help(i, self.channel_id)

    @discord.ui.button(label="Završi igru", emoji="🎯", style=discord.ButtonStyle.danger, row=0)
    async def zavrsi(self, i: discord.Interaction, b: discord.ui.Button):  # type: ignore
        game = kaladont_games.get(self.channel_id)
        if not game:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Nema aktivne igre.", color=COLORS["error"]), ephemeral=True)
        if i.user.id != game["starter"] and not i.user.guild_permissions.manage_messages:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Samo pokretač ili mod može završiti igru!", color=COLORS["error"]), ephemeral=True)
        count = len(game["chain"])
        del kaladont_games[self.channel_id]
        b.disabled = True
        e = discord.Embed(
            title="🎯 Kaladont završen!",
            description=f"Igra gotova! Ukupno izgovoreno **{count}** rijeci. <:e_party:1519363028334674070>",
            color=COLORS["gold"], timestamp=datetime.now(timezone.utc)
        )
        e.set_footer(text=f"{BOT_NAME} {VERSION}")
        await i.response.edit_message(embed=e, view=self)
        self.stop()


class KaladontWordView(discord.ui.View):
    """Mala view ispod svakog word-card embeda — samo dugme Pomoć sa 15-min cooldownom."""
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="Pomoć", emoji="<:icon_warning:1519358274284032030>", style=discord.ButtonStyle.secondary)
    async def pomoc(self, i: discord.Interaction, b: discord.ui.Button):
        await _send_kaladont_help(i, self.channel_id)


_kaladont_invalid_msgs: dict = {}   # channel_id -> discord.Message (zadnji invalid embed)
_kaladont_invalid_count: dict = {}  # channel_id -> int (broj uzastopnih nevalidnih rijeci)

class KaladontInvalidView(discord.ui.View):
    """View ispod invalid-word embeda — dugme Nova Rijec resetuje startnu poziciju.
    Čuva checkpoint_word kako bismo detektirali je li igra već nastavila bez nas."""
    def __init__(self, channel_id: int, checkpoint_word: str):
        super().__init__(timeout=120)
        self.channel_id     = channel_id
        self.checkpoint_word = checkpoint_word  # game["word"] u trenutku greške

    @discord.ui.button(label="Nova Riječ", emoji="<:e_refresh:1519362959187509461>", style=discord.ButtonStyle.primary)
    async def nova_rijec(self, i: discord.Interaction, b: discord.ui.Button):
        game = kaladont_games.get(self.channel_id)
        if not game:
            for c in self.children: c.disabled = True
            return await i.response.edit_message(
                embed=em("<:icon_cross:1519358379917836508>", "Igra je završena.", color=COLORS["error"]), view=self)

        # ── Provjera: je li igra već nastavila od kad je ova greška prikazana? ──
        if game["word"] != self.checkpoint_word:
            # Neko je već odigrao valjanu riječ — ne resetujemo, samo deaktiviramo dugme
            for c in self.children: c.disabled = True
            letters = game["letters"]
            req = game["word"][-letters:]
            zakasnio_e = discord.Embed(
                description=(
                    f"<:icon_warning:1519358274284032030>  Igra je već nastavila!\n"
                    f"<:e_right:1519363367712591922>️  Trenutna riječ: **{game['word']}**  ·  Sljedeća počinje sa **`{req}`**"
                ),
                color=COLORS["warning"],
            )
            zakasnio_e.set_footer(text=f"GIAN Kaladont  •  #{len(game['chain'])}")
            return await i.response.edit_message(embed=zakasnio_e, view=self)

        # ── Resetuj na novu startnu riječ ──
        available = [w for w in KALADONT_START_WORDS if w not in game["used"]]
        if not available:
            available = list(KALADONT_START_WORDS)
        new_word = random.choice(available)
        game["word"] = new_word
        game["used"].add(new_word)
        game["last_uid"] = None  # Reset — svako može igrati
        letters = game["letters"]
        new_req = new_word[-letters:]
        count = len(game["chain"])
        for c in self.children: c.disabled = True
        nova_e = discord.Embed(
            description=(
                f"<:e_refresh:1519362959187509461>  Nova startna riječ: **{new_word}**\n"
                f"<:e_right:1519363367712591922>️  Sljedeća počinje sa  **`{new_req}`**"
            ),
            color=KALADONT_COLOR,
        )
        nova_e.set_footer(text=f"GIAN Kaladont  •  #{count}")
        _kaladont_invalid_msgs.pop(self.channel_id, None)
        await i.response.edit_message(embed=nova_e, view=self)
        self.stop()


@bot.tree.command(name="kaladont", description="📝 Pokretanje igre Kaladont — ulančaj riječi!")
@app_commands.describe(slova="Koliko zadnjih slova mora nova rijec početi (1, 2 ili 3)")
@app_commands.choices(slova=[
    app_commands.Choice(name="1 slovo (lakše)", value=1),
    app_commands.Choice(name="2 slova (normalno)", value=2),
    app_commands.Choice(name="3 slova (teže)", value=3),
])
async def kaladont(i: discord.Interaction, slova: int = 2):
    if i.channel.id in kaladont_games:
        return await i.response.send_message(
            embed=em("<:icon_warning:1519358274284032030>️ Igra već teče!", "U ovom kanalu je već aktivan Kaladont. Završi prvu!", color=COLORS["warning"]), ephemeral=True)
    start_word = random.choice(KALADONT_START_WORDS)
    game = {
        "word":             start_word,
        "used":             {start_word},
        "starter":          i.user.id,
        "letters":          slova,
        "chain":            [(start_word, "<:e_gear:1519362652516782194> Bot")],
        "msg":              None,
        "last_uid":         None,        # ko je zadnji odigrao (None = bot, svi mogu)
        "last_player_name": "<:e_gear:1519362652516782194> Bot",
    }
    kaladont_games[i.channel.id] = game
    v = KaladontView(i.channel.id)
    await i.response.send_message(embed=kaladont_start_embed(game, i.user.display_name), view=v)
    resp = await i.original_response()
    game["msg"] = resp

@bot.tree.command(name="kaladont-stop", description="📝 Zaustavi trenutnu Kaladont igru u ovom kanalu")
async def kaladont_stop(i: discord.Interaction):
    game = kaladont_games.get(i.channel.id)
    if not game:
        return await i.response.send_message(
            embed=em("ℹ️", "Nema aktivne Kaladont igre u ovom kanalu.", color=COLORS["info"]),
            ephemeral=True
        )
    is_admin = i.user.guild_permissions.administrator
    if i.user.id != game["starter"] and not is_admin:
        return await i.response.send_message(
            embed=em("<:icon_ban:1519358278356959284>", "Samo onaj ko je pokrenuo igru ili admin može zaustaviti!", color=COLORS["error"]),
            ephemeral=True
        )
    chain = game.get("chain", [])
    count = len(chain)
    last_word = game.get("word", "—")
    del kaladont_games[i.channel.id]
    e = discord.Embed(
        title="<:e_stop:1519363022399995914> Kaladont zaustavljen",
        description=f"Igru zaustavio: {i.user.mention}",
        color=COLORS["warning"], timestamp=datetime.now(timezone.utc)
    )
    e.add_field(name="<:e_chart:1519362656568475880>  Riječi u nizu", value=f"**{count}**",        inline=True)
    e.add_field(name="📝  Zadnja riječ",   value=f"**`{last_word}`**",  inline=True)
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await i.response.send_message(embed=e)

# ═══════════════════════════════════════════
#    WORDLE — pogodi skrivenu riječ od 5 slova
#    Riječi: UPPERCASE, bez dijakritika (ista normalizacija kao kaladont)
# ═══════════════════════════════════════════
WORDLE_WORDS = [
    # Ljudi / porodica / profesije
    "MAJKA","TETKA","STRIC","KUHAR","PEKAR","RIBAR","LOVAC","ZUBAR",
    # Hrana / piće
    "LIMUN","DINJA","KUPUS","SECER","BIBER","MLEKO",
    # Životinje
    "KAJAK","JELEN","MACKA","KRAVA","PETAO","PATKA","GUSKA","HRCAK",
    "ZMIJA","PCELA","MRAVI","VRANA","GOLUB",
    # Priroda
    "POTOK","IZVOR","VRELO","POLJE","OKEAN","KAMEN","OBALA","PLAZA",
    "MAGLA","MUNJA","OLUJA","HRAST","BUKVA","JAVOR","BREZA","PALMA",
    "TRAVA","SUNCE","OBLAK","LJETO","JESEN","JUTRO","PODNE","VECER",
    # Tijelo
    "GLAVA","JEZIK","VRATA","PRSTI","NOKAT","LAKAT","GRUDI","TRBUH",
    "KICMA","REBRO","PLUCA","MOZAK","KOSTI","MISIC",
    # Kuća / predmeti / odjeća
    "ORMAR","TEPIH","SLIKA","LAMPA","SOLJA","LONAC","TORBA","RANAC",
    "KOFER","JAKNA","KAPUT","HLACE","CIZME",
    # Tehnika / vozila
    "MODEM","EKRAN","RADIO","ROBOT","KOMBI","JAHTA","CAMAC","SPLAV","BALON",
    # Geografija
    "ULICA","TUNEL","CESTA","STAZA","SPLIT","ZADAR","TUZLA","BIHAC",
    "JAJCE","JAPAN","GRCKA","AZIJA",
    # Pojmovi
    "VJERA",
]

wordle_games: dict = {}  # channel_id -> {word, guesses, uid, max, starter_name, msg}

def _wordle_feedback(secret: str, guess: str) -> str:
    """Vrati niz <:e_green:1519362769047126028>/<:e_green:1519362769047126028>/<:e_stop:1519363022399995914> za pogodak (ispravno rješava duple slova)."""
    res = ["<:e_stop:1519363022399995914>"] * 5
    rest = list(secret)
    # prvo zelena polja (tačno mjesto)
    for idx in range(5):
        if guess[idx] == rest[idx]:
            res[idx] = "<:e_green:1519362769047126028>"
            rest[idx] = None
    # zatim žuta polja (slovo u riječi, pogrešno mjesto)
    for idx in range(5):
        if res[idx] == "<:e_green:1519362769047126028>":
            continue
        ch = guess[idx]
        if ch in rest:
            res[idx] = "<:e_green:1519362769047126028>"
            rest[rest.index(ch)] = None
    return "".join(res)

def _wordle_embed(game: dict, user, *, finished: bool = False, won: bool = False,
                  reward: int = 0, xp: int = 0):
    used = len(game["guesses"])
    maxg = game["max"]
    rows = []
    for g in game["guesses"]:
        fb = _wordle_feedback(game["word"], g)
        letters = "  ".join(g)
        rows.append(f"{fb}\n`  {letters}  `")
    board = "\n\n".join(rows) if rows else "*Upiši riječ od **5 slova** u chat!*"
    legend = "<:e_green:1519362769047126028> tačno mjesto  •  <:e_green:1519362769047126028> pogrešno mjesto  •  <:e_stop:1519363022399995914> nema slova"
    if finished and won:
        color = GAME_COLORS["wordle"]
        title = f"{E_GAME}  W O R D L E  —  P O B J E D A !  {E_FIRE4}"
        footer = f"<:e_trophy2:1519362624742232146> Pogodio/la {user.display_name} • {used}/{maxg} pokušaja"
        extra = (f"\n\n{E_FIRE1}{E_FIRE2}{E_FIRE3} Riječ je bila **{game['word']}**!\n"
                 f"<:e_coins3:1519362621206298666> Nagrada: **+{reward:,} <:e_coins3:1519362621206298666>**   •   <:e_star2:1519363084253266031> XP: **+{xp}**")
    elif finished:
        color = COLORS["error"]
        title = "<:e_red:1519362782192210041>  W O R D L E  —  K R A J"
        footer = "Pokušaj ponovo sa /wordle"
        extra = (f"\n\n<:e_skull:1519362992502997125> Iskoristio/la si svih **{maxg}** pokušaja!\n"
                 f"<:e_key:1519363066545045756> Skrivena riječ je bila **{game['word']}**")
    else:
        color = GAME_COLORS["wordle"]
        title = f"{E_GAME}  W O R D L E"
        footer = f"Pokušaj {used}/{maxg} • upiši riječ od 5 slova"
        extra = ""
    e = discord.Embed(
        title=title,
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{board}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{legend}{extra}"
        ),
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    e.set_footer(text=footer)
    return e

@bot.tree.command(name="wordle", description="<:e_green:1519362769047126028> Pogodi skrivenu riječ od 5 slova u 6 pokušaja!")
async def wordle(i: discord.Interaction):
    cfg = _g_gamble("wordle")
    if not cfg.get("enabled", True):
        return await i.response.send_message(
            embed=em("<:icon_ban:1519358278356959284> Wordle je isključen", "Administrator je privremeno onemogućio ovu igru.", color=COLORS["error"]),
            ephemeral=True
        )
    if i.channel.id in wordle_games:
        return await i.response.send_message(
            embed=em("<:icon_warning:1519358274284032030>️ Igra već teče!", "U ovom kanalu je već aktivan Wordle. Završi prvi!", color=COLORS["warning"]),
            ephemeral=True
        )
    secret = random.choice(WORDLE_WORDS)
    game = {
        "word":         secret,
        "guesses":      [],
        "uid":          i.user.id,
        "max":          6,
        "starter_name": i.user.display_name,
        "msg":          None,
    }
    wordle_games[i.channel.id] = game
    await i.response.send_message(embed=_wordle_embed(game, i.user))
    try:
        resp = await i.original_response()
        game["msg"] = resp
    except Exception:
        pass

@bot.tree.command(name="wordle-stop", description="<:e_green:1519362769047126028> Zaustavi trenutnu Wordle igru u ovom kanalu")
async def wordle_stop(i: discord.Interaction):
    game = wordle_games.get(i.channel.id)
    if not game:
        return await i.response.send_message(
            embed=em("ℹ️", "Nema aktivne Wordle igre u ovom kanalu.", color=COLORS["info"]),
            ephemeral=True
        )
    is_admin = i.user.guild_permissions.administrator
    if i.user.id != game["uid"] and not is_admin:
        return await i.response.send_message(
            embed=em("<:icon_ban:1519358278356959284>", "Samo onaj ko je pokrenuo igru ili admin može zaustaviti!", color=COLORS["error"]),
            ephemeral=True
        )
    secret = game["word"]
    del wordle_games[i.channel.id]
    await i.response.send_message(
        embed=em("<:e_stop:1519363022399995914> Wordle zaustavljen", f"Igra je prekinuta.\n<:e_key:1519363066545045756> Skrivena riječ je bila **{secret}**", color=COLORS["warning"])
    )

# ═══════════════════════════════════════════
#    TOPLO-HLADNO
# ═══════════════════════════════════════════
toplo_games: dict = {}  # channel_id -> {"secret": int, "guesses": int, "starter": int, "min": int, "max": int}

TEMPERATURE = [
    (0,  0,   "🎯 TAČNO!",       COLORS["gold"]),
    (1,  5,   "<:e_fire2:1519362671491678280> VRELO je!",    0xFF4500),
    (6,  15,  "<:e_fire2:1519362671491678280>️ Jako toplo!",  COLORS["error"]),
    (16, 30,  "<:e_sun:1519362860218843399>️ Toplo...",     COLORS["warning"]),
    (31, 60,  "<:e_user:1519363093736718518> Mlako...",     COLORS["info"]),
    (61, 120, "<:e_snow:1519362801703977110>️ Hladno!",      0x87CEEB),
    (121,999, "<:e_snow:1519362801703977110> Ledeno!",      0x4169E1),
]

def get_temperature(diff: int):
    for lo, hi, label, color in TEMPERATURE:
        if lo <= diff <= hi:
            return label, color
    return "<:e_snow:1519362801703977110> Ledeno!", 0x4169E1

class ToploModal(discord.ui.Modal, title="Toplo-Hladno — Pogodi broj!"):
    broj = discord.ui.TextInput(label="Tvoj broj", min_length=1, max_length=5, placeholder="Unesi broj...")

    def __init__(self, view):
        super().__init__(); self.tv = view

    async def on_submit(self, i: discord.Interaction):
        try:
            guess = int(self.broj.value.strip())
        except ValueError:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Unesi cijeli broj!", color=COLORS["error"]), ephemeral=True)
        await self.tv.process_guess(i, guess)

class ToploView(discord.ui.View):
    def __init__(self, channel_id: int, starter: discord.Member, secret: int, max_num: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.max_num    = max_num
        toplo_games[channel_id] = {"secret": secret, "guesses": 0, "starter": starter.id, "history": []}

    def make_embed(self, result: str = "", color=None, solved=False):
        game = toplo_games.get(self.channel_id, {})
        guesses = game.get("guesses", 0)
        history = game.get("history", [])[-5:]
        c = color or COLORS["info"]
        e = discord.Embed(title="<:e_sun:1519362860218843399>️ Toplo-Hladno", description="<:e_fire2:1519362671491678280>  **Pogodi tajni broj — toplije ili hladnije!**", color=c, timestamp=datetime.now(timezone.utc))
        e.add_field(name="🎯 Raspon", value=f"`1 — {self.max_num}`", inline=True)
        e.add_field(name="<:e_chart:1519362656568475880> Pokušaji", value=f"`{guesses}`", inline=True)
        if result: e.add_field(name="<:e_satellite:1519363311207186482> Signal", value=result, inline=False)
        if history and not solved:
            e.add_field(name="📝 Zadnji pokušaji", value="\n".join(history), inline=False)
        e.set_footer(text=f"{BOT_NAME} {VERSION} • Klikni i pogodi broj!")
        return e

    async def process_guess(self, i: discord.Interaction, guess: int):
        game = toplo_games.get(self.channel_id)
        if not game:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Igra nije aktivna!", color=COLORS["error"]), ephemeral=True)
        if not 1 <= guess <= self.max_num:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Van raspona!", f"Unesi broj između `1` i `{self.max_num}`!", color=COLORS["error"]), ephemeral=True)
        game["guesses"] += 1
        secret = game["secret"]
        diff   = abs(guess - secret)
        label, color = get_temperature(diff)
        direction = "<:e_level2:1519362739749785610>️ više" if guess < secret else "<:e_down:1519363345252090081>️ manje" if guess > secret else ""
        hint = f"`{guess}` → {label}" + (f" ({direction})" if direction else "")
        game["history"].append(hint)
        if diff == 0:
            for c in self.children: c.disabled = True
            del toplo_games[self.channel_id]
            e = discord.Embed(
                title=f"🎯 {i.user.mention} pogodio/la!",
                description=f"Tajna je bila **`{secret}`**!\n<:e_trophy2:1519362624742232146> Pogođeno za **{game['guesses']}** pokušaja!",
                color=COLORS["gold"], timestamp=datetime.now(timezone.utc)
            )
            e.set_footer(text=f"{BOT_NAME} {VERSION}")
            await i.response.edit_message(embed=e, view=self)
            self.stop()
        else:
            await i.response.edit_message(embed=self.make_embed(hint, color), view=self)

    @discord.ui.button(label="Pogodi broj", emoji="<:e_sun:1519362860218843399>️", style=discord.ButtonStyle.primary)
    async def guess_btn(self, i: discord.Interaction, b: discord.ui.Button):
        if self.channel_id not in toplo_games:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Igra nije aktivna.", color=COLORS["error"]), ephemeral=True)
        await i.response.send_modal(ToploModal(self))

    @discord.ui.button(label="Završi igru", emoji="🎯", style=discord.ButtonStyle.danger)
    async def zavrsi(self, i: discord.Interaction, b: discord.ui.Button):
        game = toplo_games.get(self.channel_id)
        if not game:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Nema aktivne igre.", color=COLORS["error"]), ephemeral=True)
        if i.user.id != game["starter"] and not i.user.guild_permissions.manage_messages:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Samo pokretač ili mod može završiti igru!", color=COLORS["error"]), ephemeral=True)
        secret = game["secret"]
        del toplo_games[self.channel_id]
        for c in self.children: c.disabled = True
        e = discord.Embed(title="🎯 Igra završena!",
            description=f"Tajna je bila **`{secret}`**!\nNiko nije pogodio ovaj put. <:e_dizzy:1519362812554510509>",
            color=COLORS["warning"], timestamp=datetime.now(timezone.utc))
        e.set_footer(text=f"{BOT_NAME} {VERSION}")
        await i.response.edit_message(embed=e, view=self)
        self.stop()

@bot.tree.command(name="toplo-hladno", description="<:e_sun:1519362860218843399>️ Pogodi tajni broj — Toplo ili Hladno!")
@app_commands.describe(maksimum="Maksimalni broj (default 100, max 1000)")
async def toplo_hladno(i: discord.Interaction, maksimum: int = 100):
    if i.channel.id in toplo_games:
        return await i.response.send_message(
            embed=em("<:icon_warning:1519358274284032030>️ Igra već teče!", "U ovom kanalu je već aktivna igra. Završi prvu!", color=COLORS["warning"]), ephemeral=True)
    maksimum = max(10, min(maksimum, 1000))
    secret = random.randint(1, maksimum)
    v = ToploView(i.channel.id, i.user, secret, maksimum)
    await i.response.send_message(
        embed=v.make_embed(f"<:e_ctrl:1519362682296209498> {i.user.mention} pokrenuo igru!\nPogodi broj od `1` do `{maksimum}`!", COLORS["info"]),
        view=v
    )

# ═══════════════════════════════════════════
#    <:e_ctrl:1519362682296209498> PER-USER COOLDOWN za GAME komande
#    Regularan član može pokrenuti svaku igru jednom u 30 minuta.
#    Owner i admin (manage_messages) zaobilaze cooldown.
# ═══════════════════════════════════════════
GAME_USER_COOLDOWN_SEC = 30 * 60  # 30 minuta
_game_user_cooldowns: dict = {}   # (gid, uid, cmd) -> last_use_ts

def _is_game_admin(member) -> bool:
    """Owner ili korisnik s manage_messages zaobilazi cooldown."""
    try:
        if int(getattr(member, "id", 0)) in OWNER_IDS:
            return True
    except Exception:
        pass
    try:
        return bool(member.guild_permissions.manage_messages)
    except Exception:
        return False

def _check_game_cooldown(member, gid: int, cmd: str):
    """Vrati (ok: bool, sec_left: int). Owner/admin = uvijek ok."""
    if _is_game_admin(member):
        return True, 0
    key  = (gid or 0, getattr(member, "id", 0), cmd)
    last = _game_user_cooldowns.get(key, 0.0)
    now  = time.time()
    diff = now - last
    if diff < GAME_USER_COOLDOWN_SEC:
        return False, int(GAME_USER_COOLDOWN_SEC - diff)
    return True, 0

def _set_game_cooldown(member, gid: int, cmd: str):
    if _is_game_admin(member):
        return
    _game_user_cooldowns[((gid or 0), getattr(member, "id", 0), cmd)] = time.time()

async def _send_cooldown_msg(i: discord.Interaction, cmd: str, secs_left: int):
    mins, secs = divmod(secs_left, 60)
    e = em(
        "<:e_time2:1519362726952964227> Cooldown — sačekaj!",
        f"Možeš ponovo pokrenuti **/{cmd}** za **{mins}m {secs}s**.\n"
        f"*(Cooldown za regularne članove: 30 min — admin/owner zaobilazi.)*",
        color=COLORS["warning"]
    )
    return await i.response.send_message(embed=e, ephemeral=True)

# ═══════════════════════════════════════════
#    AMONG US — AMOGUS
# ═══════════════════════════════════════════
PLAYER_COLORS   = ["<:e_red:1519362782192210041>","<:e_sun:1519362860218843399>","<:e_green:1519362769047126028>","<:e_green:1519362769047126028>","<:e_internet:1519363106395000994>","<:e_flower:1519362984818901173>","<:e_stop:1519363022399995914>","<:e_user:1519363093736718518>","<:e_globe2:1519362694887637004>","<:e_heart2:1519362668644012133>"]
IMPOSTOR_COUNTS = {4:1, 5:1, 6:1, 7:2, 8:2, 9:2, 10:3}
TASKS_PER_PLAYER = 3
KILL_COOLDOWN_SEC = 30

#  ── DINAMIČKI GENERATOR ZADATAKA (6 kategorija) ──
#  Tipovi: math / typing / logic / memory / speed / repair
#  Svaki zadatak je dict: {q, a, type, fake}
#   - real (crewmate)  → uvećava done_tasks pri tačnom odgovoru
#   - fake (impostor)  → izgleda isto, ali NE broji se u napredak

AMOGUS_TASK_TYPES = ["math", "typing", "logic", "memory", "speed", "repair"]

_AG_LOGIC_TEMPLATES = [
    # (formula, opis za prikaz)
    (lambda x: x*x,         "n²",        "Niz kvadrata: {a}, {b}, {c}, __?"),
    (lambda x: x*2,         "n·2",       "Niz duplih: {a}, {b}, {c}, __?"),
    (lambda x: x*3,         "n·3",       "Niz: {a}, {b}, {c}, __?"),
    (lambda x: x+x*2,       "n + 2n",    "Niz: {a}, {b}, {c}, __?"),
    (lambda x: x*x - 1,     "n²-1",      "Niz: {a}, {b}, {c}, __?"),
]
_AG_TYPE_WORDS  = ["REACTOR","ENGINE","SHIELD","SCAN","UPLOAD","O2","COMMS","ADMIN",
                   "MEDBAY","CAFE","NAV","WEAPONS","STORAGE","ELECTRIC","CAMS"]
_AG_TYPE_SUFFIX = ["ON","OFF","OK","CORE","BAY","ROOM","42","X9","BETA","ZONE"]
_AG_REPAIR_WORDS = ["KABEL","REAKTOR","KAMERE","O2VENT","NAVIGAT","STITOVI"]
_AG_SPEED_WORDS  = ["GO","NOW","FAST","HIT","TAP","RUN","CLICK","ZAP"]

def generate_amogus_task(fake: bool = False) -> dict:
    """Generiše random zadatak iz jedne od 6 kategorija."""
    ttype = random.choice(AMOGUS_TASK_TYPES)

    if ttype == "math":
        op = random.choice(["+","-","×","÷"])
        if op == "+":
            a, b = random.randint(15, 99), random.randint(15, 99)
            q, ans = f"<:e_ruler:1519363621912576191> Koliko je {a} + {b}?", str(a+b)
        elif op == "-":
            a = random.randint(50, 199); b = random.randint(10, a-1)
            q, ans = f"<:e_ruler:1519363621912576191> Koliko je {a} − {b}?", str(a-b)
        elif op == "×":
            a, b = random.randint(6, 19), random.randint(3, 12)
            q, ans = f"<:e_ruler:1519363621912576191> Koliko je {a} × {b}?", str(a*b)
        else:
            b = random.randint(2, 12); ans_v = random.randint(3, 25); a = b * ans_v
            q, ans = f"<:e_ruler:1519363621912576191> Koliko je {a} ÷ {b}?", str(ans_v)

    elif ttype == "typing":
        word = f"{random.choice(_AG_TYPE_WORDS)}_{random.choice(_AG_TYPE_SUFFIX)}_{random.randint(10,99)}"
        q, ans = f"<:e_keyboard:1519363499875242104>️ Upiši TAČNO: `{word}`", word

    elif ttype == "logic":
        fn, label, desc_tpl = random.choice(_AG_LOGIC_TEMPLATES)
        start = random.randint(2, 7)
        seq = [fn(start), fn(start+1), fn(start+2)]
        nxt = fn(start+3)
        q   = f"🎯 {desc_tpl.format(a=seq[0], b=seq[1], c=seq[2])}  *(formula: {label})*"
        ans = str(nxt)

    elif ttype == "memory":
        num = "".join(str(random.randint(0,9)) for _ in range(random.choice([4,5,6])))
        q   = f"<:e_brain:1519362849548406975> Zapamti i upiši: **{num}**"
        ans = num

    elif ttype == "speed":
        word = random.choice(_AG_SPEED_WORDS)
        q    = f"<:e_bolt:1519362674717102160> BRZINA! Upiši **{word}** što prije!"
        ans  = word

    else:  # repair
        word = random.choice(_AG_REPAIR_WORDS)
        scrambled = list(word); random.shuffle(scrambled)
        q   = f"<:e_wrench:1519362745772802078> POPRAVKA — sastavi riječ iz: `{'-'.join(scrambled)}`"
        ans = word

    return {"q": q, "a": ans, "type": ttype, "fake": bool(fake), "done": False}

# Zadržano za kompatibilnost (nije korišteno aktivno)
AMOGUS_TASKS = [generate_amogus_task() for _ in range(15)]

amogus_games: dict = {}  # channel_id -> state

def _ag(cid):
    return amogus_games.get(cid)

def _task_bar(done, total):
    filled = int((done / total) * 10) if total else 0
    return "<:e_green:1519362769047126028>"*filled + "<:e_check2:1519362730057007268>"*(10-filled) + f" `{done}/{total}`"

def _ag_player_list(players, show_roles=False):
    lines = []
    for uid, p in players.items():
        dead = "<:e_skull:1519362992502997125> ~~" if not p["alive"] else ""
        end  = "~~" if not p["alive"] else ""
        role = f" — **{'<:e_red:1519362782192210041> IMP' if p['role']=='impostor' else '<:e_internet:1519363106395000994> CREW'}**" if show_roles else ""
        td   = f" [{p['tasks_done']}/{TASKS_PER_PLAYER}]" if p["alive"] and not show_roles else ""
        lines.append(f"{dead}{p['color']} {p['name']}{td}{role}{end}")
    return "\n".join(lines) or "*Nema igrača*"

def _ag_lobby_embed(state):
    players = state["players"]
    e = discord.Embed(title="<:e_rocket2:1519363332266524813> Among Us — Lobby", color=_LP,
                      description="Pridruži se i čekaj da host pokrene igru!\n**Min 4 • Max 10 igrača**",
                      timestamp=datetime.now(timezone.utc))
    e.add_field(name=f"<:e_users:1519363096601301120> Igrači ({len(players)}/10)",
                value="\n".join(f"{p['color']} {p['name']}" for p in players.values()) or "*Čekamo...*",
                inline=False)
    e.set_footer(text="Host: klikni <:e_right:1519363367712591922>️ Pokreni igru kad ste svi tu!")
    return e

def _ag_game_embed(state):
    alive = [p for p in state["players"].values() if p["alive"]]
    ac = sum(1 for p in alive if p["role"]=="crewmate")
    ai = sum(1 for p in alive if p["role"]=="impostor")
    e = discord.Embed(title="<:e_rocket2:1519363332266524813> Among Us — U Toku", color=_LP, timestamp=datetime.now(timezone.utc))
    e.add_field(name="<:e_users:1519363096601301120> Igrači", value=_ag_player_list(state["players"]), inline=False)
    e.add_field(name="<:e_clipboard:1519363052871614627> Zadaci", value=_task_bar(state["done_tasks"], state["total_tasks"]), inline=True)
    e.add_field(name="<:e_masks:1519363003424706671> Živi", value=f"<:e_internet:1519363106395000994> {ac} crew | <:e_red:1519362782192210041> {ai} imp", inline=True)
    if state.get("reactor"):
        n_fix = len(state["reactor"]["fixers"])
        e.add_field(name="<:e_bomb:1519363456334168255> SABOTAŽA AKTIVNA!", value=f"Reaktor — `{n_fix}/{REACTOR_FIXES_NEEDED}` popravača! <:e_time2:1519362726952964227>️", inline=False)
    e.set_footer(text="<:e_clipboard:1519363052871614627> Zadatak • <:e_report2:1519362714198347886> Alarm • <:e_sword2:1519362631146930317> Akcija • <:e_stop:1519363022399995914> Sabotiraj • <:e_masks:1519363003424706671> Lažni alarm • <:e_arrow:1519363399845154958> Šerif • <:e_skull:1519362992502997125> Ghost")
    return e

async def _ag_check_win(state, channel) -> bool:
    alive = [p for p in state["players"].values() if p["alive"]]
    ac = [p for p in alive if p["role"]=="crewmate"]
    ai = [p for p in alive if p["role"]=="impostor"]
    if not ai:
        await _ag_end(state, channel, "<:e_internet:1519363106395000994> CREWMATI POBIJEDE!", "Svi impostori eliminirani! <:icon_check:1519358376268533810>", COLORS["success"])
        return True
    if len(ai) >= len(ac):
        await _ag_end(state, channel, "<:e_red:1519362782192210041> IMPOSTORI POBIJEDE!", "Impostori preuzeli brod! <:e_skull2:1519362997443629186>️", COLORS["error"])
        return True
    if state["done_tasks"] >= state["total_tasks"] > 0:
        await _ag_end(state, channel, "<:e_internet:1519363106395000994> CREWMATI POBIJEDE!", "Svi zadaci završeni! <:e_party:1519363028334674070>", COLORS["success"])
        return True
    return False

async def _ag_end(state, channel, title, desc, color):
    state["phase"] = "ended"
    reveal = "\n".join(
        f"{'<:e_red:1519362782192210041>' if p['role']=='impostor' else '<:e_internet:1519363106395000994>'} {p['color']} **{p['name']}** — {p['role'].upper()}"
        for p in state["players"].values()
    )
    e = discord.Embed(title=f"🎯 {title}", description=desc, color=color, timestamp=datetime.now(timezone.utc))
    e.add_field(name="<:e_masks:1519363003424706671> Otkrivene uloge", value=reveal, inline=False)
    e.set_footer(text=f"{BOT_NAME} • Among Us")
    await channel.send(embed=e)
    amogus_games.pop(channel.id, None)

async def _ag_tally(channel, state):
    tally = Counter(v for v in state["votes"].values() if v is not None)
    if not tally:
        state["phase"] = "playing"; state["votes"] = {}
        await channel.send(embed=em("<:e_right:1519363367712591922>️ Niko nije eliminisan", "Svi su preskočili — igra se nastavlja!", color=COLORS["warning"]))
        gv = state.get("game_view")
        if gv: await channel.send(embed=_ag_game_embed(state), view=gv)
        return
    max_v   = max(tally.values())
    winners = [uid for uid, c in tally.items() if c == max_v]
    if len(winners) > 1:
        state["phase"] = "playing"; state["votes"] = {}
        await channel.send(embed=em("<:e_scales:1519362852853649439>️ Izjednačeno!", "Glasanje neodlučeno — niko nije eliminisan!", color=COLORS["warning"]))
        gv = state.get("game_view")
        if gv: await channel.send(embed=_ag_game_embed(state), view=gv)
        return
    ejected_id = winners[0]
    ejected_p  = state["players"][ejected_id]
    ejected_p["alive"] = False
    role_txt = "<:e_red:1519362782192210041> **IMPOSTOR**" if ejected_p["role"] == "impostor" else "<:e_internet:1519363106395000994> **CREWMATE**"
    e = discord.Embed(
        title=f"<:e_rocket2:1519363332266524813> {ejected_p['name']} je izbačen/a!",
        description=f"{ejected_p['color']} **{ejected_p['name']}** eliminisan/a sa **{max_v}** glasova.\nBio/la je: {role_txt}",
        color=COLORS["error"] if ejected_p["role"]=="impostor" else COLORS["warning"],
        timestamp=datetime.now(timezone.utc)
    )
    await channel.send(embed=e)
    if not await _ag_check_win(state, channel):
        state["phase"] = "playing"; state["votes"] = {}
        gv = state.get("game_view")
        if gv: await channel.send(embed=_ag_game_embed(state), view=gv)

# ── Views ──────────────────────────────────────────────────

class AmogusLobbyView(discord.ui.View):
    def __init__(self, cid):
        super().__init__(timeout=300)
        self.cid = cid

    @discord.ui.button(label="Pridruži se", emoji="<:e_rocket2:1519363332266524813>", style=discord.ButtonStyle.success)
    async def join(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state or state["phase"] != "lobby":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Lobby je zatvoren!",color=COLORS["error"]),ephemeral=True)
        uid = str(i.user.id)
        if uid in state["players"]:
            return await i.response.send_message(embed=em("<:icon_check:1519358376268533810>","Već si tu!",color=COLORS["warning"]),ephemeral=True)
        if len(state["players"]) >= 10:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Lobby pun (10/10)!",color=COLORS["error"]),ephemeral=True)
        idx = len(state["players"]) % len(PLAYER_COLORS)
        state["players"][uid] = {"name":i.user.display_name,"alive":True,"role":None,
                                  "color":PLAYER_COLORS[idx],"tasks":[],"tasks_done":0,"kill_cd":0}
        await i.response.edit_message(embed=_ag_lobby_embed(state), view=self)

    @discord.ui.button(label="Napusti", emoji="<:e_door:1519363657404776661>", style=discord.ButtonStyle.secondary)
    async def leave(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state or state["phase"] != "lobby":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Lobby zatvoren!",color=COLORS["error"]),ephemeral=True)
        uid = str(i.user.id)
        if uid not in state["players"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nisi u lobby-u!",color=COLORS["error"]),ephemeral=True)
        del state["players"][uid]
        if not state["players"]:
            amogus_games.pop(self.cid, None)
            return await i.response.edit_message(embed=em("<:e_door:1519363657404776661>","Lobby zatvoren.",color=COLORS["error"]),view=None)
        if state["host"] == i.user.id:
            state["host"] = int(next(iter(state["players"])))
        await i.response.edit_message(embed=_ag_lobby_embed(state), view=self)

    @discord.ui.button(label="Pokreni igru", emoji="<:e_right:1519363367712591922>️", style=discord.ButtonStyle.primary)
    async def start(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nema lobby-a!",color=COLORS["error"]),ephemeral=True)
        if i.user.id != state["host"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Samo host može pokrenuti!",color=COLORS["error"]),ephemeral=True)
        if len(state["players"]) < 4:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>",f"Treba min **4 igrača**! Sad: `{len(state['players'])}`",color=COLORS["error"]),ephemeral=True)
        await i.response.defer()
        n     = len(state["players"])
        n_imp = IMPOSTOR_COUNTS.get(n, 1)
        ids   = list(state["players"].keys())
        random.shuffle(ids)
        for idx, uid in enumerate(ids):
            role = "impostor" if idx < n_imp else "crewmate"
            state["players"][uid]["role"] = role
            state["players"][uid]["is_sheriff"] = False
            state["players"][uid]["shot_used"]  = False
            # Crewmate dobija prave zadatke; impostor dobija LAŽNE (da glumi rad)
            is_imp = (role == "impostor")
            state["players"][uid]["tasks"] = [generate_amogus_task(fake=is_imp) for _ in range(TASKS_PER_PLAYER)]
        # Jedan random crewmate postaje <:icon_report:1519358353208508566> ŠERIF
        crew_uids = [uid for uid in ids if state["players"][uid]["role"] == "crewmate"]
        if crew_uids:
            sheriff_uid = random.choice(crew_uids)
            state["players"][sheriff_uid]["is_sheriff"] = True
        state["total_tasks"]         = (n - n_imp) * TASKS_PER_PLAYER
        state["done_tasks"]          = 0
        state["phase"]               = "playing"
        state["sabotage_cd"]         = 0
        state["reactor"]             = None
        state["last_alarm_was_fake"] = False
        # DMs
        bad_dm = []
        for uid, p in state["players"].items():
            member = i.guild.get_member(int(uid))
            if not member: continue
            is_imp = p["role"] == "impostor"
            dm_e = discord.Embed(
                title=f"{'<:e_red:1519362782192210041> IMPOSTOR' if is_imp else '<:e_internet:1519363106395000994> CREWMATE'} — Tvoja uloga!",
                description=("<:e_red:1519362782192210041> **Eliminiši crewmate-e, ne budi uhvaćen!**\nKoristi dugme <:e_sword2:1519362631146930317> **Akcija** za ubijanje."
                             if is_imp else
                             "<:e_internet:1519363106395000994> **Završi zadatke, pronađi impostora!**\nKoristi dugme <:e_clipboard:1519363052871614627> **Zadatak** za rad."),
                color=COLORS["error"] if is_imp else COLORS["info"]
            )
            if is_imp:
                partners = [state["players"][x]["name"] for x in ids[:n_imp] if x != uid]
                if partners: dm_e.add_field(name="<:e_red:1519362782192210041> Saimpostori", value="\n".join(partners))
                dm_e.add_field(name="<:e_stop:1519363022399995914> Sabotaža",  value=f"Klikni **<:e_stop:1519363022399995914> Sabotiraj** u kanalu — reaktor će eksplodirati za `{REACTOR_TIME_SEC}s` ako ga ne stabilizuju!", inline=False)
                dm_e.add_field(name="<:e_masks:1519363003424706671> Lažni alarm", value="Klikni **<:e_masks:1519363003424706671> Lažni alarm** da sazoveš FAKE meeting i zbunjš ekipu.", inline=False)
            if p.get("is_sheriff"):
                dm_e.add_field(name="<:icon_report:1519358353208508566> SPECIJALNA ULOGA: ŠERIF",
                               value="Imaš **1 hitac** za cijelu igru!\n• Pogodi **impostora** → on/ona umire\n• Pogodi **civila** → TI umireš (kazna)\n→ Dugme: **<:e_arrow:1519363399845154958> Šerif Pucaj**",
                               inline=False)
            dm_e.add_field(name="<:e_skull:1519362992502997125> Ghost Chat", value="Kad umreš, klikni **<:e_skull:1519362992502997125> Ghost Chat** u kanalu da pišeš drugim duhovima.", inline=False)
            dm_e.set_footer(text=f"{BOT_NAME} • Samo ti vidiš ovo!")
            try: await member.send(embed=dm_e)
            except: bad_dm.append(p["name"])
        gv = AmogusGameView(self.cid)
        state["game_view"] = gv
        extra = f"\n<:icon_warning:1519358274284032030>️ Nije mogao primiti DM: {', '.join(bad_dm)}" if bad_dm else ""
        start_e = discord.Embed(title="<:e_rocket2:1519363332266524813> Igra počinje!", description=f"Uloge podijeljene! Provjeri **DM** za svoju ulogu.{extra}",
                                color=_LP, timestamp=datetime.now(timezone.utc))
        await i.edit_original_response(embed=start_e, view=None)
        await i.channel.send(embed=_ag_game_embed(state), view=gv)

class AmogusTaskModal(discord.ui.Modal, title="<:e_clipboard:1519363052871614627> Zadatak"):
    odgovor = discord.ui.TextInput(label="Odgovor:", placeholder="Upiši odgovor...", max_length=60)
    def __init__(self, cid, uid, tidx):
        super().__init__()
        self.cid  = cid
        self.uid  = uid
        self.tidx = tidx
        state = _ag(cid)
        if state and uid in state["players"]:
            q = state["players"][uid]["tasks"][tidx]["q"]
            self.odgovor.label = q[:45]
    async def on_submit(self, i: discord.Interaction):
        state = _ag(self.cid)
        if not state or state["phase"] != "playing":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!",color=COLORS["error"]),ephemeral=True)
        p    = state["players"][self.uid]
        task = p["tasks"][self.tidx]
        if self.odgovor.value.strip().lower() == task["a"].strip().lower():
            task["done"] = True
            p["tasks_done"] += 1
            is_fake = task.get("fake", False)
            # Lažni zadaci NE povećavaju globalni napredak
            if not is_fake:
                state["done_tasks"] += 1
            rem = TASKS_PER_PLAYER - p["tasks_done"]
            msg = f"<:icon_check:1519358376268533810> Tačno! Ostalo zadataka: **{rem}**" if rem else "<:icon_check:1519358376268533810> Svi zadaci završeni! <:e_party:1519363028334674070>"
            # Igraču NE govorimo da je task fake (zato impostor i može da glumi)
            await i.response.send_message(embed=em("<:e_clipboard:1519363052871614627> Zadatak završen!", msg, color=COLORS["success"]), ephemeral=True)
            gv = state.get("game_view")
            try: await i.message.edit(embed=_ag_game_embed(state), view=gv)
            except: pass
            if not is_fake:
                await _ag_check_win(state, i.channel)
        else:
            await i.response.send_message(embed=em("<:icon_cross:1519358379917836508> Pogrešno!","Pokušaj ponovo!", color=COLORS["error"]), ephemeral=True)

class AmogusKillSelect(discord.ui.View):
    def __init__(self, cid, killer_id):
        super().__init__(timeout=20)
        self.cid       = cid
        self.killer_id = killer_id
        state = _ag(cid)
        if not state: return
        opts = [discord.SelectOption(label=p["name"], value=uid, emoji=p["color"])
                for uid, p in state["players"].items()
                if p["alive"] and uid != str(killer_id) and p["role"] == "crewmate"]
        if opts:
            s = discord.ui.Select(placeholder="Odaberi žrtvu...", options=opts[:25])
            s.callback = self.do_kill
            self.add_item(s)
    async def do_kill(self, i: discord.Interaction):
        state = _ag(self.cid)
        if not state or state["phase"] != "playing":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!",color=COLORS["error"]),ephemeral=True)
        ks  = str(self.killer_id)
        kp  = state["players"].get(ks)
        if not kp or not kp["alive"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Ne možeš ubijati!",color=COLORS["error"]),ephemeral=True)
        now = time.time()
        if now - kp.get("kill_cd",0) < KILL_COOLDOWN_SEC:
            left = int(KILL_COOLDOWN_SEC-(now-kp["kill_cd"]))
            return await i.response.send_message(embed=em("<:e_time2:1519362726952964227>",f"Cooldown! Čekaj još `{left}s`",color=COLORS["warning"]),ephemeral=True)
        vid = i.data["values"][0]
        vp  = state["players"].get(vid)
        if not vp or not vp["alive"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Taj igrač nije dostupan!",color=COLORS["error"]),ephemeral=True)
        vp["alive"] = False
        kp["kill_cd"] = now
        # reduce total tasks
        state["total_tasks"] = max(0, state["total_tasks"] - (TASKS_PER_PLAYER - vp["tasks_done"]))
        await i.response.send_message(embed=em("<:e_sword2:1519362631146930317> Eliminirano!",f"**{vp['name']}** je eliminisan/a! Niko ne zna...",color=COLORS["error"]),ephemeral=True)
        vm = i.guild.get_member(int(vid))
        if vm:
            try: await vm.send(embed=em("<:e_skull:1519362992502997125> Eliminisan/a si!",f"**{kp['name']}** te je eliminisao/la. Možeš promatrati igru.",color=COLORS["error"]))
            except: pass
        gv = state.get("game_view")
        try: await i.message.edit(embed=_ag_game_embed(state), view=gv)
        except: pass
        await _ag_check_win(state, i.channel)
        self.stop()

# ── REAKTOR (sabotaža mini-igra) ──
SABOTAGE_COOLDOWN_SEC = 60
REACTOR_TIME_SEC      = 30
REACTOR_FIXES_NEEDED  = 2

class AmogusReactorView(discord.ui.View):
    """Crewmate-i moraju 2x kliknuti '<:e_wrench:1519362745772802078> Stabilizuj' u 30s ili impostori pobjeđuju."""
    def __init__(self, cid):
        super().__init__(timeout=REACTOR_TIME_SEC)
        self.cid = cid

    @discord.ui.button(label="<:e_wrench:1519362745772802078> Stabilizuj reaktor", style=discord.ButtonStyle.success)
    async def fix(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state or not state.get("reactor"):
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nema aktivne sabotaže!",color=COLORS["error"]),ephemeral=True)
        uid = str(i.user.id)
        p   = state["players"].get(uid)
        if not p or not p["alive"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Mrtvi ne mogu popravljati!",color=COLORS["error"]),ephemeral=True)
        if p["role"] == "impostor":
            return await i.response.send_message(embed=em("<:icon_ban:1519358278356959284>","Impostori NE mogu popravljati! <:e_devil:1519362989470253187>",color=COLORS["error"]),ephemeral=True)
        state["reactor"]["fixers"].add(uid)
        n = len(state["reactor"]["fixers"])
        await i.response.send_message(embed=em("<:e_wrench:1519362745772802078> Popravljaš!", f"Klik registrovan: **{n}/{REACTOR_FIXES_NEEDED}** popravača.", color=COLORS["success"]), ephemeral=True)
        if n >= REACTOR_FIXES_NEEDED:
            state["reactor"] = None
            self.stop()
            try: await i.message.edit(view=None)
            except: pass
            await i.channel.send(embed=em("<:icon_check:1519358376268533810> REAKTOR STABILIZOVAN!", "Crewmate-i su uspjeli popraviti reaktor na vrijeme! <:e_shield2:1519362627795554374>️", color=COLORS["success"]))

    async def on_timeout(self):
        state = _ag(self.cid)
        if not state or not state.get("reactor"):
            return  # već je popravljen
        state["reactor"] = None
        ch = bot.get_channel(self.cid)
        if ch and state["phase"] == "playing":
            await ch.send(embed=em("<:e_bomb:1519363456334168255> REAKTOR EKSPLODIRAO!","Crewmate-i nisu uspjeli popraviti reaktor! <:e_skull:1519362992502997125>", color=COLORS["error"]))
            await _ag_end(state, ch, "<:e_red:1519362782192210041> IMPOSTORI POBJEDJUJU!", "Reaktor eksplodirao zbog sabotaže <:e_bomb:1519363456334168255>", COLORS["error"])

# ── ŠERIF SELECT (specijalna crewmate uloga, 1 hitac) ──
class AmogusSheriffSelect(discord.ui.View):
    def __init__(self, cid, sheriff_id):
        super().__init__(timeout=20)
        self.cid        = cid
        self.sheriff_id = sheriff_id
        state = _ag(cid)
        if not state: return
        opts = [discord.SelectOption(label=p["name"], value=uid, emoji=p["color"])
                for uid, p in state["players"].items()
                if p["alive"] and uid != str(sheriff_id)]
        if opts:
            s = discord.ui.Select(placeholder="<:e_arrow:1519363399845154958> Pucaj na...", options=opts[:25])
            s.callback = self.do_shot
            self.add_item(s)

    async def do_shot(self, i: discord.Interaction):
        state = _ag(self.cid)
        if not state or state["phase"] != "playing":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!",color=COLORS["error"]),ephemeral=True)
        ss = str(self.sheriff_id)
        sp = state["players"].get(ss)
        if not sp or not sp.get("is_sheriff") or sp.get("shot_used") or not sp["alive"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Ne možeš sad pucati!",color=COLORS["error"]),ephemeral=True)
        tid = i.data["values"][0]
        tp  = state["players"].get(tid)
        if not tp or not tp["alive"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Meta nije dostupna!",color=COLORS["error"]),ephemeral=True)
        sp["shot_used"] = True
        if tp["role"] == "impostor":
            tp["alive"] = False
            state["total_tasks"] = max(0, state["total_tasks"])  # impostor nema realne zadatke
            await i.response.send_message(embed=em("🎯 POGODAK!", f"Eliminisao/la si **IMPOSTORA** {tp['name']}!", color=COLORS["success"]), ephemeral=True)
            await i.channel.send(embed=em("<:icon_report:1519358353208508566> ŠERIF DJELUJE!", f"<:e_bomb:1519363456334168255> **{tp['name']}** je upucan/a — bio/la je **IMPOSTOR**! <:e_party:1519363028334674070>", color=COLORS["success"]))
        else:
            sp["alive"] = False
            state["total_tasks"] = max(0, state["total_tasks"] - (TASKS_PER_PLAYER - sp["tasks_done"]))
            await i.response.send_message(embed=em("<:e_skull:1519362992502997125> Pogriješio si!", f"**{tp['name']}** nije bio impostor — UMIREŠ od kazne!", color=COLORS["error"]), ephemeral=True)
            await i.channel.send(embed=em("<:icon_report:1519358353208508566> ŠERIF PROMAŠIO!", f"<:e_scales:1519362852853649439>️ Šerif **{sp['name']}** pucao u civila — sam je pao! <:e_skull:1519362992502997125>", color=COLORS["error"]))
        gv = state.get("game_view")
        try: await i.message.edit(view=None)
        except: pass
        await _ag_check_win(state, i.channel)
        self.stop()

# ── GHOST CHAT (mrtvi pričaju u DM-u) ──
class AmogusGhostModal(discord.ui.Modal, title="<:e_skull:1519362992502997125> Ghost Chat"):
    poruka = discord.ui.TextInput(label="Poruka ostalim duhovima:", placeholder="Pisi ovde...", max_length=200, style=discord.TextStyle.paragraph)
    def __init__(self, cid, uid):
        super().__init__()
        self.cid = cid
        self.uid = uid

    async def on_submit(self, i: discord.Interaction):
        state = _ag(self.cid)
        if not state:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nema igre!",color=COLORS["error"]),ephemeral=True)
        sender = state["players"].get(self.uid)
        if not sender:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nisi u igri!",color=COLORS["error"]),ephemeral=True)
        text = self.poruka.value.strip()
        if not text:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Prazna poruka!",color=COLORS["error"]),ephemeral=True)
        e = em(f"<:e_skull:1519362992502997125> {sender['name']} (DUH)", text, color=COLORS["purple"])
        e.set_footer(text="<:e_lock3:1519362717394403432> Samo mrtvi vide ovo (Ghost Chat)")
        sent = 0
        for puid, p in state["players"].items():
            if not p["alive"]:
                try:
                    m = i.guild.get_member(int(puid))
                    if m:
                        await m.send(embed=e)
                        sent += 1
                except: pass
        await i.response.send_message(embed=em("<:e_skull:1519362992502997125> Poslato!", f"Vidjelo te je **{sent}** duhova.", color=COLORS["success"]), ephemeral=True)

class AmogusGameView(discord.ui.View):
    def __init__(self, cid):
        super().__init__(timeout=None)
        self.cid = cid

    @discord.ui.button(label="Zadatak", emoji="<:e_clipboard:1519363052871614627>", style=discord.ButtonStyle.primary)
    async def task_btn(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state or state["phase"] != "playing":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!",color=COLORS["error"]),ephemeral=True)
        uid = str(i.user.id)
        if uid not in state["players"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nisi u igri!",color=COLORS["error"]),ephemeral=True)
        p = state["players"][uid]
        if not p["alive"]:
            return await i.response.send_message(embed=em("<:e_skull:1519362992502997125>","Mrtvi ne mogu raditi zadatke!",color=COLORS["error"]),ephemeral=True)
        tidx = next((idx for idx,t in enumerate(p["tasks"]) if not t["done"]), None)
        if tidx is None:
            return await i.response.send_message(embed=em("<:icon_check:1519358376268533810> Sve završeno!","Čekaj ostatak tima! <:e_party:1519363028334674070>",color=COLORS["success"]),ephemeral=True)
        await i.response.send_modal(AmogusTaskModal(self.cid, uid, tidx))

    @discord.ui.button(label="Alarm!", emoji="<:e_report2:1519362714198347886>", style=discord.ButtonStyle.danger)
    async def alarm_btn(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state or state["phase"] != "playing":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!",color=COLORS["error"]),ephemeral=True)
        uid = str(i.user.id)
        if uid not in state["players"] or not state["players"][uid]["alive"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Ne možeš sazvati meeting!",color=COLORS["error"]),ephemeral=True)
        state["phase"]      = "meeting"
        state["votes"]      = {}
        state["meeting_by"] = i.user.id
        alive_pl = [(k, v["name"]) for k,v in state["players"].items() if v["alive"]]
        mv = AmogusMeetingView(self.cid, alive_pl)
        state["meeting_view"] = mv
        me = _ag_meeting_embed(state, state["players"][uid]["name"], "Emergency Meeting <:e_report2:1519362714198347886>")
        await i.response.send_message(embed=me, view=mv)

    @discord.ui.button(label="Akcija", emoji="<:e_sword2:1519362631146930317>", style=discord.ButtonStyle.secondary)
    async def action_btn(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state or state["phase"] != "playing":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!",color=COLORS["error"]),ephemeral=True)
        uid = str(i.user.id)
        if uid not in state["players"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nisi u igri!",color=COLORS["error"]),ephemeral=True)
        p = state["players"][uid]
        if not p["alive"]:
            return await i.response.send_message(embed=em("<:e_skull:1519362992502997125>","Mrtvi ništa ne mogu!",color=COLORS["error"]),ephemeral=True)
        if p["role"] != "impostor":
            return await i.response.send_message(embed=em("<:e_internet:1519363106395000994> Ti si Crewmate!","Samo impostori mogu koristiti Akciju.",color=COLORS["info"]),ephemeral=True)
        kv = AmogusKillSelect(self.cid, i.user.id)
        if not kv.children:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nema živih crewmate-a!",color=COLORS["error"]),ephemeral=True)
        await i.response.send_message(embed=em("<:e_sword2:1519362631146930317> Odaberi žrtvu","Samo ti vidiš ovo!",color=COLORS["error"]),view=kv,ephemeral=True)

    # ── <:e_stop:1519363022399995914> SABOTAŽA (samo impostor) ──
    @discord.ui.button(label="Sabotiraj", emoji="<:e_stop:1519363022399995914>", style=discord.ButtonStyle.danger, row=1)
    async def sabotage_btn(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state or state["phase"] != "playing":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!",color=COLORS["error"]),ephemeral=True)
        uid = str(i.user.id)
        p   = state["players"].get(uid)
        if not p or not p["alive"] or p["role"] != "impostor":
            return await i.response.send_message(embed=em("<:icon_ban:1519358278356959284>","Samo živi impostori sabotiraju!",color=COLORS["error"]),ephemeral=True)
        if state.get("reactor"):
            return await i.response.send_message(embed=em("<:icon_warning:1519358274284032030>️","Sabotaža je već aktivna!",color=COLORS["warning"]),ephemeral=True)
        now = time.time()
        last = state.get("sabotage_cd", 0)
        if now - last < SABOTAGE_COOLDOWN_SEC:
            left = int(SABOTAGE_COOLDOWN_SEC - (now - last))
            return await i.response.send_message(embed=em("<:e_time2:1519362726952964227> Cooldown",f"Sačekaj još `{left}s` da opet sabotiraš.",color=COLORS["warning"]),ephemeral=True)
        state["sabotage_cd"] = now
        state["reactor"]     = {"started": now, "fixers": set()}
        rv = AmogusReactorView(self.cid)
        await i.response.send_message(embed=em("<:e_stop:1519363022399995914> Sabotaža pokrenuta!","Reaktor će eksplodirati za 30s ako ga ne stabilizuju!",color=COLORS["error"]),ephemeral=True)
        await i.channel.send(embed=em("<:e_bomb:1519363456334168255> ALARM — REAKTOR SE TOPI!",
            f"<:icon_warning:1519358274284032030>️ Sabotirano!\n**Treba `{REACTOR_FIXES_NEEDED}` različita crewmate-a da kliknu '<:e_wrench:1519362745772802078> Stabilizuj' u **`{REACTOR_TIME_SEC}s`!**",
            color=COLORS["error"]), view=rv)

    # ── <:e_masks:1519363003424706671> LAŽNI ALARM (samo impostor) ──
    @discord.ui.button(label="Lažni alarm", emoji="<:e_masks:1519363003424706671>", style=discord.ButtonStyle.secondary, row=1)
    async def fake_alarm_btn(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state or state["phase"] != "playing":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!",color=COLORS["error"]),ephemeral=True)
        uid = str(i.user.id)
        p   = state["players"].get(uid)
        if not p or not p["alive"] or p["role"] != "impostor":
            return await i.response.send_message(embed=em("<:icon_ban:1519358278356959284>","Samo živi impostori!",color=COLORS["error"]),ephemeral=True)
        state["phase"]              = "meeting"
        state["votes"]              = {}
        state["meeting_by"]         = i.user.id
        state["last_alarm_was_fake"] = True
        alive_pl = [(k, v["name"]) for k,v in state["players"].items() if v["alive"]]
        mv = AmogusMeetingView(self.cid, alive_pl)
        state["meeting_view"] = mv
        me = _ag_meeting_embed(state, p["name"], "<:e_masks:1519363003424706671> Lažna prijava — neko je 'navodno' vidio tijelo (ali da li je istina?)")
        await i.response.send_message(embed=em("<:e_masks:1519363003424706671> Lažni alarm postavljen!","Niko ne zna da si TI to lažirao/la! <:e_devil:1519362989470253187>",color=COLORS["error"]),ephemeral=True)
        await i.channel.send(embed=me, view=mv)

    # ── <:e_arrow:1519363399845154958> ŠERIF (specijalna crewmate uloga, 1 hitac) ──
    @discord.ui.button(label="Šerif Pucaj", emoji="<:e_arrow:1519363399845154958>", style=discord.ButtonStyle.danger, row=2)
    async def sheriff_btn(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state or state["phase"] != "playing":
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!",color=COLORS["error"]),ephemeral=True)
        uid = str(i.user.id)
        p   = state["players"].get(uid)
        if not p or not p["alive"]:
            return await i.response.send_message(embed=em("<:e_skull:1519362992502997125>","Mrtvi ne pucaju!",color=COLORS["error"]),ephemeral=True)
        if not p.get("is_sheriff"):
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nisi šerif!","Samo jedan crewmate ima ovu sposobnost.",color=COLORS["error"]),ephemeral=True)
        if p.get("shot_used"):
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Već si potrošio svoj hitac!",color=COLORS["error"]),ephemeral=True)
        sv = AmogusSheriffSelect(self.cid, i.user.id)
        if not sv.children:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nema dostupnih meta!",color=COLORS["error"]),ephemeral=True)
        await i.response.send_message(embed=em("<:e_arrow:1519363399845154958> Šerif — biraj metu","<:icon_warning:1519358274284032030>️ Pažljivo! Ako pogriješiš — UMIREŠ od kazne!",color=COLORS["gold"]),view=sv,ephemeral=True)

    # ── <:e_skull:1519362992502997125> GHOST CHAT (samo mrtvi) ──
    @discord.ui.button(label="Ghost Chat", emoji="<:e_skull:1519362992502997125>", style=discord.ButtonStyle.secondary, row=2)
    async def ghost_btn(self, i: discord.Interaction, b):
        state = _ag(self.cid)
        if not state:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nema aktivne igre!",color=COLORS["error"]),ephemeral=True)
        uid = str(i.user.id)
        p   = state["players"].get(uid)
        if not p:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nisi u igri!",color=COLORS["error"]),ephemeral=True)
        if p["alive"]:
            return await i.response.send_message(embed=em("<:e_skull:1519362992502997125>","Ghost Chat je SAMO za mrtve!",color=COLORS["error"]),ephemeral=True)
        await i.response.send_modal(AmogusGhostModal(self.cid, uid))

def _ag_meeting_embed(state, caller, reason):
    e = discord.Embed(title="<:e_report2:1519362714198347886> EMERGENCY MEETING!", color=_LP,
                      description=f"**{caller}** je sazvao/la meeting!\n*{reason}*\n\n**Glasajte koga eliminišete!**",
                      timestamp=datetime.now(timezone.utc))
    alive = {k:v for k,v in state["players"].items() if v["alive"]}
    e.add_field(name="<:e_users:1519363096601301120> Živi igrači", value=_ag_player_list(alive), inline=False)
    total_alive = len(alive)
    e.add_field(name="<:icon_stats:1519358289173807246>️ Glasanje", value=f"`0` od `{total_alive}` glasalo", inline=True)
    e.set_footer(text="Glasajte mudro! Eliminisani igrač otkrije svoju ulogu.")
    return e

class AmogusMeetingView(discord.ui.View):
    def __init__(self, cid, alive_players):
        super().__init__(timeout=90)
        self.cid           = cid
        self.alive_players = alive_players
        for uid, name in alive_players:
            btn = discord.ui.Button(label=name[:20], custom_id=f"agv_{uid}", style=discord.ButtonStyle.secondary)
            btn.callback = self._vote_cb(uid, name)
            self.add_item(btn)
        skip = discord.ui.Button(label="Preskoči", emoji="<:e_right:1519363367712591922>️", custom_id="agv_skip", style=discord.ButtonStyle.secondary)
        skip.callback = self._vote_cb(None, "Preskoči")
        self.add_item(skip)

    def _vote_cb(self, tid, tname):
        async def cb(i: discord.Interaction):
            state = _ag(self.cid)
            if not state or state["phase"] != "meeting":
                return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Meeting završen!",color=COLORS["error"]),ephemeral=True)
            uid = str(i.user.id)
            if uid not in state["players"] or not state["players"][uid]["alive"]:
                return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Ne možeš glasati!",color=COLORS["error"]),ephemeral=True)
            if uid in state["votes"]:
                return await i.response.send_message(embed=em("<:icon_warning:1519358274284032030>️","Već si glasao/la!",color=COLORS["warning"]),ephemeral=True)
            state["votes"][uid] = tid
            label = f"**{tname}**" if tid else "Preskoči"
            await i.response.send_message(embed=em("<:icon_stats:1519358289173807246>️ Glas zabilježen!",f"Glasao/la si za: {label}",color=COLORS["success"]),ephemeral=True)
            alive_cnt = sum(1 for p in state["players"].values() if p["alive"])
            # Update meeting embed vote count
            try:
                me = i.message.embeds[0]
                me.set_field_at(1, name="<:icon_stats:1519358289173807246>️ Glasanje", value=f"`{len(state['votes'])}` od `{alive_cnt}` glasalo", inline=True)
                await i.message.edit(embed=me)
            except: pass
            if len(state["votes"]) >= alive_cnt:
                self.stop()
                await _ag_tally(i.channel, state)
        return cb

    async def on_timeout(self):
        state = _ag(self.cid)
        if not state or state["phase"] != "meeting": return
        for guild in bot.guilds:
            chan = guild.get_channel(self.cid)
            if chan:
                await chan.send(embed=em("<:e_time2:1519362726952964227>️ Glasanje isteklo!","Premalo glasova — niko nije eliminisan.", color=COLORS["warning"]))
                await _ag_tally(chan, state)
                break

@bot.tree.command(name="amogus", description="<:e_rocket2:1519363332266524813> Pokreni Among Us igru!")
async def amogus_cmd(i: discord.Interaction):
    ok, left = _check_game_cooldown(i.user, i.guild_id, "amogus")
    if not ok:
        return await _send_cooldown_msg(i, "amogus", left)
    if i.channel.id in amogus_games:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Igra je već aktivna! Koristi `/amogus-stop` za kraj.",color=COLORS["error"]),ephemeral=True)
    _set_game_cooldown(i.user, i.guild_id, "amogus")
    state = {"phase":"lobby","host":i.user.id,"channel_id":i.channel.id,
             "players":{},"total_tasks":0,"done_tasks":0,"votes":{},"game_view":None,"meeting_view":None}
    state["players"][str(i.user.id)] = {
        "name":i.user.display_name,"alive":True,"role":None,
        "color":PLAYER_COLORS[0],"tasks":[],"tasks_done":0,"kill_cd":0
    }
    amogus_games[i.channel.id] = state
    await i.response.send_message(embed=_ag_lobby_embed(state), view=AmogusLobbyView(i.channel.id))

@bot.tree.command(name="amogus-stop", description="<:e_rocket2:1519363332266524813> Zaustavi Among Us igru [HOST/ADMIN]")
async def amogus_stop(i: discord.Interaction):
    state = _ag(i.channel.id)
    if not state:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Nema aktivne igre!",color=COLORS["error"]),ephemeral=True)
    if i.user.id != state["host"] and not i.user.guild_permissions.manage_messages:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>","Samo host ili admin može zaustaviti igru!",color=COLORS["error"]),ephemeral=True)
    amogus_games.pop(i.channel.id, None)
    await i.response.send_message(embed=em("<:e_rocket2:1519363332266524813> Igra zaustavljena","Among Us igra je prekinuta.", color=COLORS["warning"]))

# ═══════════════════════════════════════════
#    <:e_cards2:1519362702835712010> POKER — Texas Hold'em za pravi novac
# ═══════════════════════════════════════════

_PK_RANKS  = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
_PK_SUITS  = ["<:e_cards2:1519362702835712010>","<:e_heart2:1519362668644012133>","<:e_diamond2:1519362640961474601>","<:e_cards2:1519362702835712010>"]
_PK_SE     = {"<:e_cards2:1519362702835712010>":"<:e_cards2:1519362702835712010>️","<:e_heart2:1519362668644012133>":"<:e_heart2:1519362668644012133>️","<:e_diamond2:1519362640961474601>":"<:e_diamond2:1519362640961474601>️","<:e_cards2:1519362702835712010>":"<:e_cards2:1519362702835712010>️"}
_PK_RV     = {r: i+2 for i, r in enumerate(_PK_RANKS)}
_PK_HNAMES = [
    "Visoka karta","Par","Dva para","Tri iste","Strit",
    "Flush","Full house","Četiri iste","Strit flush","Rojal flush"
]

def _pk_deck():
    d = [(r, s) for s in _PK_SUITS for r in _PK_RANKS]
    random.shuffle(d)
    return d

def _pk_card(c):
    return f"`{c[0]}{_PK_SE[c[1]]}`"

def _pk_cards(cards):
    return " ".join(_pk_card(c) for c in cards) if cards else "`?` `?`"

def _pk_hand_rank(five):
    vals  = sorted([_PK_RV[c[0]] for c in five], reverse=True)
    suits = [c[1] for c in five]
    flush = len(set(suits)) == 1
    straight = (vals == list(range(vals[0], vals[0]-5, -1)))
    if not straight and sorted(vals) == [2, 3, 4, 5, 14]:
        straight = True; vals = [5, 4, 3, 2, 1]
    cnt = Counter(vals)
    grp = sorted(cnt.items(), key=lambda x: (x[1], x[0]), reverse=True)
    gc  = [g[1] for g in grp]
    gv  = [g[0] for g in grp]
    if flush and straight:
        return (9 if vals[0] == 14 and vals[1] == 13 else 8, vals)
    if gc[0] == 4:                return (7, gv)
    if gc[:2] == [3, 2]:          return (6, gv)
    if flush:                     return (5, vals)
    if straight:                  return (4, vals)
    if gc[0] == 3:                return (3, gv)
    if gc[:2] == [2, 2]:          return (2, gv)
    if gc[0] == 2:                return (1, gv)
    return (0, vals)

def _pk_best(hole, community):
    all7 = hole + community
    if len(all7) < 5:
        return (_pk_hand_rank(all7), all7)
    return max(((_pk_hand_rank(list(c)), list(c)) for c in _pk_comb(all7, 5)), key=lambda x: x[0])

poker_games: dict = {}  # channel_id -> game dict

def _pk_get_bal(guild_id, user_id):
    mkey = f"{guild_id}:{user_id}"
    return data["money"].get(mkey, data["economy"].get(str(user_id), {}).get("balance", 0))

def _pk_set_bal(guild_id, user_id, amount):
    data["money"][f"{guild_id}:{user_id}"] = max(0, int(amount))

def _pk_lobby_embed(g):
    plist = "\n".join(f"▸ **{p['name']}**" for p in g["players"].values()) or "_Niko još nije ušao_"
    e = discord.Embed(
        title="<:e_cards2:1519362702835712010> POKER — Texas Hold'em",
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<:e_coins3:1519362621206298666> **Ulog po igraču:** `{g['ulog']:,} <:e_coins3:1519362621206298666>`\n"
            f"<:e_trophy2:1519362624742232146> **Trenutni pot:** `{g['pot']:,} <:e_coins3:1519362621206298666>`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<:e_users:1519363096601301120> **Igrači ({len(g['players'])}/9):**\n{plist}\n\n"
            f"▸ Klikni **Ulazi u igru** da se pridružiš\n"
            f"▸ Domaćin klika **Počni igru** kad je spreman\n"
            f"▸ Igra automatski kreće za **60 sekundi**"
        ),
        color=_LP,
        timestamp=datetime.now(timezone.utc)
    )
    e.set_footer(text=f"<:e_cards2:1519362702835712010> {BOT_NAME} • Poker • Min 2, Max 9 igrača")
    return e

def _pk_game_embed(g):
    phase_titles = {
        "preflop": "<:e_cards2:1519362702835712010> Pre-Flop — Kartice podijeljene",
        "flop":    "<:e_dolphin:1519363432615510078> Flop — 3 zajedničke kartice",
        "turn":    "<:e_refresh:1519362959187509461> Turn — 4. zajednička kartica",
        "river":   "<:e_dolphin:1519363432615510078> River — 5. zajednička kartica",
    }
    community_str = _pk_cards(g["community"]) if g["community"] else "`?` `?` `?` `?` `?`"
    active = [(uid, p) for uid, p in g["players"].items() if not p["folded"]]
    folded = [(uid, p) for uid, p in g["players"].items() if p["folded"]]
    act_str  = "\n".join(f"<:icon_check:1519358376268533810> **{p['name']}**" for _, p in active) or "_nema_"
    fold_str = "\n".join(f"<:icon_cross:1519358379917836508> ~~{p['name']}~~" for _, p in folded)
    needs = g.get("needs_action", set())
    wait_str = "\n".join(f"<:e_time2:1519362726952964227> {g['players'][uid]['name']}" for uid in needs if uid in g["players"]) or "_Svi su djelovali_"
    desc = (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<:e_cards2:1519362702835712010> **Zajedničke kartice:**\n{community_str}\n"
        f"<:e_coins3:1519362621206298666> **Pot:** `{g['pot']:,} <:e_coins3:1519362621206298666>`\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<:e_users:1519363096601301120> **Aktivni:**\n{act_str}\n"
    )
    if fold_str:
        desc += f"<:icon_cross:1519358379917836508> **Foldali:**\n{fold_str}\n"
    desc += f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n<:e_time2:1519362726952964227> **Čekamo potez:**\n{wait_str}"
    e = discord.Embed(
        title=phase_titles.get(g["phase"], "<:e_cards2:1519362702835712010> POKER"),
        description=desc,
        color=_LP,
        timestamp=datetime.now(timezone.utc)
    )
    e.set_footer(text=f"<:e_cards2:1519362702835712010> {BOT_NAME} • Klikni 'Vidi kartice' za svoju ruku • Pot: {g['pot']:,} <:e_coins3:1519362621206298666>")
    return e

class PokerLobbyView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=60)
        self.channel_id = channel_id
        self._started   = False

    @discord.ui.button(label="Ulazi u igru <:e_cards2:1519362702835712010>", style=discord.ButtonStyle.success, row=0)
    async def join_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = poker_games.get(self.channel_id)
        if not g or g["phase"] != "join":
            return await interaction.response.send_message("<:icon_cross:1519358379917836508> Prijava je zatvorena.", ephemeral=True)
        uid = interaction.user.id
        if uid in g["players"]:
            return await interaction.response.send_message("Već si u igri!", ephemeral=True)
        if len(g["players"]) >= 9:
            return await interaction.response.send_message("<:icon_cross:1519358379917836508> Igra je puna (max 9)!", ephemeral=True)
        ulog = g["ulog"]
        bal  = _pk_get_bal(g["guild_id"], uid)
        if bal < ulog:
            return await interaction.response.send_message(
                f"<:icon_cross:1519358379917836508> Nemaš dovoljno! Trebaš `{ulog:,} <:e_coins3:1519362621206298666>`, a imaš `{bal:,} <:e_coins3:1519362621206298666>`.", ephemeral=True)
        _pk_set_bal(g["guild_id"], uid, bal - ulog)
        save_data()
        g["players"][uid] = {"name": interaction.user.display_name, "hole": [], "folded": False}
        g["pot"] += ulog
        try:
            await interaction.message.edit(embed=_pk_lobby_embed(g))
        except Exception:
            pass
        await interaction.response.send_message(
            f"<:icon_check:1519358376268533810> Ušao/la si u igru! Skinuto `{ulog:,} <:e_coins3:1519362621206298666>`. Pot: `{g['pot']:,} <:e_coins3:1519362621206298666>`", ephemeral=True)

    @discord.ui.button(label="Počni igru <:e_right:1519363367712591922>️", style=discord.ButtonStyle.primary, row=0)
    async def start_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = poker_games.get(self.channel_id)
        if not g:
            return await interaction.response.send_message("Nema aktivne igre.", ephemeral=True)
        if interaction.user.id != g["host_id"] and interaction.user.id not in OWNER_IDS:
            return await interaction.response.send_message("<:icon_cross:1519358379917836508> Samo domaćin može pokrenuti igru!", ephemeral=True)
        if len(g["players"]) < 2:
            return await interaction.response.send_message("<:icon_cross:1519358379917836508> Trebaju minimalno **2 igrača**!", ephemeral=True)
        if self._started:
            return await interaction.response.send_message("Igra već počinje...", ephemeral=True)
        self._started = True
        await interaction.response.defer()
        await _pk_begin(self.channel_id)

    async def on_timeout(self):
        g = poker_games.get(self.channel_id)
        if not g or g["phase"] != "join":
            return
        if len(g["players"]) >= 2:
            await _pk_begin(self.channel_id)
        else:
            for uid in g["players"]:
                _pk_set_bal(g["guild_id"], uid, _pk_get_bal(g["guild_id"], uid) + g["ulog"])
            save_data()
            del poker_games[self.channel_id]
            ch = bot.get_channel(self.channel_id)
            if ch:
                try:
                    msg = g.get("msg")
                    if msg:
                        await msg.edit(embed=discord.Embed(
                            title="<:icon_cross:1519358379917836508> Poker otkazan",
                            description="Nema dovoljno igrača (min 2). Ulozi vraćeni.",
                            color=COLORS["error"]
                        ), view=None)
                except Exception:
                    pass

class PokerRaiseModal(discord.ui.Modal, title="<:e_coins3:1519362621206298666> Raise / Podigni ulog"):
    iznos = discord.ui.TextInput(label="Koliko podižeš (<:e_coins3:1519362621206298666>)?", placeholder="npr. 100", max_length=10)

    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        g = poker_games.get(self.channel_id)
        if not g or g["phase"] in ("join", "showdown"):
            return await interaction.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!", color=COLORS["error"]), ephemeral=True)
        uid = interaction.user.id
        if uid not in g["players"] or g["players"][uid]["folded"]:
            return await interaction.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>","Nisi u igri ili si foldo!", color=COLORS["error"]), ephemeral=True)
        if uid not in g.get("needs_action", set()):
            return await interaction.response.send_message(
                embed=em("<:e_time2:1519362726952964227>","Već si djelovao/la!", color=COLORS["warning"]), ephemeral=True)
        try:
            amt = int(self.iznos.value.strip())
        except Exception:
            return await interaction.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>","Mora biti broj!", color=COLORS["error"]), ephemeral=True)
        if amt < 10:
            return await interaction.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>","Min raise je `10 <:e_coins3:1519362621206298666>`!", color=COLORS["error"]), ephemeral=True)
        bal = _pk_get_bal(g["guild_id"], uid)
        if bal < amt:
            return await interaction.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>","Nemaš dovoljno!", f"Imaš `{bal:,} <:e_coins3:1519362621206298666>`, treba `{amt:,} <:e_coins3:1519362621206298666>`.", color=COLORS["error"]),
                ephemeral=True)
        _pk_set_bal(g["guild_id"], uid, bal - amt)
        g["pot"] += amt
        save_data()
        # Resetuj needs_action: svi ostali aktivni MORAJU reagovati
        active = [u for u, p in g["players"].items() if not p["folded"] and u != uid]
        g["needs_action"] = set(active)
        await interaction.response.send_message(
            embed=em("<:e_coins3:1519362621206298666> Raise!", f"Podigao/la si **`{amt:,} <:e_coins3:1519362621206298666>`**!\n<:e_trophy2:1519362624742232146> Novi pot: **`{g['pot']:,} <:e_coins3:1519362621206298666>`**\n<:e_time2:1519362726952964227> Ostali igrači moraju reagovati.",
                     color=COLORS.get("gold", 0xFFD700)),
            ephemeral=False
        )
        # Update embed
        try:
            msg = g.get("msg")
            if msg:
                await msg.edit(embed=_pk_game_embed(g), view=PokerActionView(self.channel_id))
        except Exception:
            pass

class PokerActionView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=120)
        self.channel_id = channel_id

    @discord.ui.button(label="<:e_cards2:1519362702835712010> Vidi kartice", style=discord.ButtonStyle.secondary, row=0)
    async def see_cards(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = poker_games.get(self.channel_id)
        if not g:
            return await interaction.response.send_message("Nema aktivne igre.", ephemeral=True)
        uid = interaction.user.id
        if uid not in g["players"]:
            return await interaction.response.send_message("Nisi u ovoj igri!", ephemeral=True)
        p      = g["players"][uid]
        hole   = p["hole"]
        status = "<:icon_cross:1519358379917836508> **FOLDO si**" if p["folded"] else "<:icon_check:1519358376268533810> **Aktivno igraš**"
        community = g.get("community", [])
        if community and len(hole) == 2:
            rank_t, best5 = _pk_best(hole, community)
            best_str = f"\n<:e_trophy2:1519362624742232146> Tvoja trenutna ruka: **{_PK_HNAMES[rank_t[0]]}**\n→ {_pk_cards(best5)}"
        else:
            best_str = ""
        await interaction.response.send_message(
            f"<:e_cards2:1519362702835712010> **Tvoje kartice:** {_pk_cards(hole)}\n{status}{best_str}", ephemeral=True)

    @discord.ui.button(label="<:icon_check:1519358376268533810> Prati", style=discord.ButtonStyle.success, row=1)
    async def check_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = poker_games.get(self.channel_id)
        if not g:
            return await interaction.response.send_message("Nema igre.", ephemeral=True)
        uid = interaction.user.id
        if uid not in g["players"]:
            return await interaction.response.send_message("Nisi u igri!", ephemeral=True)
        if g["players"][uid]["folded"]:
            return await interaction.response.send_message("Već si foldo!", ephemeral=True)
        if uid not in g.get("needs_action", set()):
            return await interaction.response.send_message("Već si djelovao/la u ovoj rundi.", ephemeral=True)
        g["needs_action"].discard(uid)
        await interaction.response.send_message(
            embed=em("<:icon_check:1519358376268533810> Pratiš!", "Tvoja akcija je registrovana.", color=COLORS["success"]),
            ephemeral=True
        )
        await _pk_check_advance(self.channel_id)

    @discord.ui.button(label="<:icon_cross:1519358379917836508> Fold", style=discord.ButtonStyle.danger, row=1)
    async def fold_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = poker_games.get(self.channel_id)
        if not g:
            return await interaction.response.send_message("Nema igre.", ephemeral=True)
        uid = interaction.user.id
        if uid not in g["players"]:
            return await interaction.response.send_message("Nisi u igri!", ephemeral=True)
        if g["players"][uid]["folded"]:
            return await interaction.response.send_message("Već si foldo!", ephemeral=True)
        if uid not in g.get("needs_action", set()):
            return await interaction.response.send_message("Već si djelovao/la u ovoj rundi.", ephemeral=True)
        g["players"][uid]["folded"] = True
        g["needs_action"].discard(uid)
        active_left = [u for u, p in g["players"].items() if not p["folded"]]
        await interaction.response.send_message(
            f"<:icon_cross:1519358379917836508> Foldo/la si! Ostalo **{len(active_left)}** aktivnih igrača.", ephemeral=True)
        await _pk_check_advance(self.channel_id)

    @discord.ui.button(label="<:e_coins3:1519362621206298666> Raise", style=discord.ButtonStyle.primary, row=1)
    async def raise_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = poker_games.get(self.channel_id)
        if not g or g["phase"] in ("join", "showdown"):
            return await interaction.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!", color=COLORS["error"]), ephemeral=True)
        uid = interaction.user.id
        if uid not in g["players"] or g["players"][uid]["folded"]:
            return await interaction.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>","Nisi u igri ili si foldo!", color=COLORS["error"]), ephemeral=True)
        if uid not in g.get("needs_action", set()):
            return await interaction.response.send_message(
                embed=em("<:e_time2:1519362726952964227>","Već si djelovao/la!", color=COLORS["warning"]), ephemeral=True)
        await interaction.response.send_modal(PokerRaiseModal(self.channel_id))

    @discord.ui.button(label="<:e_fire2:1519362671491678280> ALL-IN", style=discord.ButtonStyle.danger, row=2)
    async def allin_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        g = poker_games.get(self.channel_id)
        if not g or g["phase"] in ("join", "showdown"):
            return await interaction.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>","Igra nije aktivna!", color=COLORS["error"]), ephemeral=True)
        uid = interaction.user.id
        if uid not in g["players"] or g["players"][uid]["folded"]:
            return await interaction.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>","Nisi u igri ili si foldo!", color=COLORS["error"]), ephemeral=True)
        if uid not in g.get("needs_action", set()):
            return await interaction.response.send_message(
                embed=em("<:e_time2:1519362726952964227>","Već si djelovao/la!", color=COLORS["warning"]), ephemeral=True)
        bal = _pk_get_bal(g["guild_id"], uid)
        if bal <= 0:
            return await interaction.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>","Nemaš novca za all-in!", color=COLORS["error"]), ephemeral=True)
        _pk_set_bal(g["guild_id"], uid, 0)
        g["pot"] += bal
        save_data()
        active = [u for u, p in g["players"].items() if not p["folded"] and u != uid]
        g["needs_action"] = set(active)
        await interaction.response.send_message(
            embed=em("<:e_fire2:1519362671491678280> ALL-IN!", f"**{interaction.user.display_name}** ide ALL-IN sa **`{bal:,} <:e_coins3:1519362621206298666>`**!\n<:e_trophy2:1519362624742232146> Pot: **`{g['pot']:,} <:e_coins3:1519362621206298666>`**",
                     color=COLORS["error"]),
            ephemeral=False
        )
        try:
            msg = g.get("msg")
            if msg:
                await msg.edit(embed=_pk_game_embed(g), view=PokerActionView(self.channel_id))
        except Exception:
            pass

    async def on_timeout(self):
        g = poker_games.get(self.channel_id)
        if not g or g["phase"] in ("join", "showdown"):
            return
        for uid in list(g.get("needs_action", set())):
            if uid in g["players"] and not g["players"][uid]["folded"]:
                g["players"][uid]["folded"] = True
        g["needs_action"] = set()
        await _pk_check_advance(self.channel_id)

async def _pk_begin(channel_id: int):
    g = poker_games.get(channel_id)
    if not g:
        return
    g["phase"]     = "preflop"
    deck           = _pk_deck()
    g["deck"]      = deck
    g["community"] = []
    for uid in g["players"]:
        g["players"][uid]["hole"]   = [deck.pop(), deck.pop()]
        g["players"][uid]["folded"] = False
    g["needs_action"] = set(g["players"].keys())
    ch = bot.get_channel(channel_id)
    if not ch:
        return
    e    = _pk_game_embed(g)
    view = PokerActionView(channel_id)
    try:
        msg = g.get("msg")
        if msg:
            await msg.edit(embed=e, view=view)
        else:
            msg = await ch.send(embed=e, view=view)
            g["msg"] = msg
    except Exception:
        msg = await ch.send(embed=e, view=view)
        g["msg"] = msg
    await ch.send(
        "<:e_cards2:1519362702835712010> **Kartice su podijeljene!**\n"
        "▸ Klikni **Vidi kartice** da vidiš svoju ruku (samo ti vidiš)\n"
        "▸ Klikni **Prati** da ostaneš u igri ili **Fold** da odustaneš."
    )

async def _pk_check_advance(channel_id: int):
    g = poker_games.get(channel_id)
    if not g:
        return
    active = [uid for uid, p in g["players"].items() if not p["folded"]]
    if len(active) <= 1:
        await _pk_end_game(channel_id, active)
        return
    if not g.get("needs_action"):
        await _pk_next_phase(channel_id)

async def _pk_next_phase(channel_id: int):
    g = poker_games.get(channel_id)
    if not g:
        return
    ch = bot.get_channel(channel_id)
    if not ch:
        return
    active = [uid for uid, p in g["players"].items() if not p["folded"]]
    phase  = g["phase"]
    if phase == "preflop":
        g["community"] = [g["deck"].pop(), g["deck"].pop(), g["deck"].pop()]
        g["phase"]     = "flop"
        ann_title = "<:e_dolphin:1519363432615510078> FLOP"
        ann_desc  = f"Zajedničke kartice:\n{_pk_cards(g['community'])}"
        ann_color = COLORS["info"]
    elif phase == "flop":
        g["community"].append(g["deck"].pop())
        g["phase"] = "turn"
        ann_title = "<:e_refresh:1519362959187509461> TURN"
        ann_desc  = f"Kartice:\n{_pk_cards(g['community'])}"
        ann_color = COLORS["purple"]
    elif phase == "turn":
        g["community"].append(g["deck"].pop())
        g["phase"] = "river"
        ann_title = "<:e_dolphin:1519363432615510078> RIVER"
        ann_desc  = f"Kartice:\n{_pk_cards(g['community'])}"
        ann_color = COLORS["gold"]
    elif phase == "river":
        await _pk_showdown(channel_id)
        return
    else:
        return
    g["needs_action"] = set(active)
    e    = _pk_game_embed(g)
    view = PokerActionView(channel_id)
    try:
        msg = g.get("msg")
        if msg:
            await msg.edit(embed=e, view=view)
    except Exception:
        pass
    await ch.send(embed=em(ann_title, ann_desc, color=ann_color))

async def _pk_showdown(channel_id: int):
    g = poker_games.get(channel_id)
    if not g:
        return
    g["phase"] = "showdown"
    ch = bot.get_channel(channel_id)
    if not ch:
        return
    active = [(uid, p) for uid, p in g["players"].items() if not p["folded"]]
    if not active:
        del poker_games[channel_id]
        return
    if len(active) == 1:
        await _pk_end_game(channel_id, [active[0][0]])
        return
    community = g["community"]
    results   = []
    for uid, p in active:
        rank_t, best5 = _pk_best(p["hole"], community)
        results.append((uid, p["name"], rank_t, best5, p["hole"]))
    results.sort(key=lambda x: x[2], reverse=True)
    best_rank  = results[0][2]
    winners    = [r for r in results if r[2] == best_rank]
    winner_ids = [r[0] for r in winners]
    pot        = g["pot"]
    split      = pot // len(winners)
    lines = []
    for uid, name, rank_t, best5, hole in results:
        crown = "<:e_trophy2:1519362624742232146>" if uid in winner_ids else "  "
        lines.append(
            f"{crown} **{name}**\n"
            f"   Ruka: {_pk_cards(hole)}\n"
            f"   → **{_PK_HNAMES[rank_t[0]]}** | {_pk_cards(best5)}"
        )
    winner_str = " & ".join(r[1] for r in winners)
    tie_note   = " *(Split pot)*" if len(winners) > 1 else ""
    e = discord.Embed(
        title="<:e_trophy2:1519362624742232146> SHOWDOWN — Poker",
        description=(
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<:e_cards2:1519362702835712010> **Zajedničke kartice:**\n{_pk_cards(community)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            + "\n\n".join(lines) +
            f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<:e_trophy2:1519362624742232146> **Pobjednik:** {winner_str}{tie_note}\n"
            f"<:e_coins3:1519362621206298666> **Dobitak:** `{split:,} <:e_coins3:1519362621206298666>` po pobjedniku"
        ),
        color=COLORS.get("gold", 0xFFD700),
        timestamp=datetime.now(timezone.utc)
    )
    e.set_footer(text=f"<:e_cards2:1519362702835712010> {BOT_NAME} • Poker završen • Ukupni pot: {pot:,} <:e_coins3:1519362621206298666>")
    try:
        msg = g.get("msg")
        if msg:
            await msg.edit(embed=e, view=None)
        else:
            await ch.send(embed=e)
    except Exception:
        await ch.send(embed=e)
    await _pk_end_game(channel_id, winner_ids, skip_embed=True)

async def _pk_end_game(channel_id: int, winner_ids: list, skip_embed: bool = False):
    g = poker_games.get(channel_id)
    if not g:
        return
    pot      = g["pot"]
    guild_id = g["guild_id"]
    ch       = bot.get_channel(channel_id)
    if winner_ids:
        split     = pot // len(winner_ids)
        remainder = pot % len(winner_ids)
        for idx, uid in enumerate(winner_ids):
            amt = split + (remainder if idx == 0 else 0)
            _pk_set_bal(guild_id, uid, _pk_get_bal(guild_id, uid) + amt)
        save_data()
        if not skip_embed and ch:
            name = g["players"].get(winner_ids[0], {}).get("name", "Pobjednik")
            e = discord.Embed(
                title="<:e_trophy2:1519362624742232146> Poker — Pobjednik!",
                description=(
                    f"<:e_trophy2:1519362624742232146> **{name}** pobijedio/la jer su svi ostali foldali!\n"
                    f"<:e_coins3:1519362621206298666> **Dobitak:** `{pot:,} <:e_coins3:1519362621206298666>`"
                ),
                color=COLORS.get("gold", 0xFFD700),
                timestamp=datetime.now(timezone.utc)
            )
            try:
                msg = g.get("msg")
                if msg:
                    await msg.edit(embed=e, view=None)
                else:
                    await ch.send(embed=e)
            except Exception:
                await ch.send(embed=e)
    poker_games.pop(channel_id, None)

@bot.tree.command(name="poker", description="<:e_cards2:1519362702835712010> Pokreni Texas Hold'em Poker za pravi novac (2–9 igrača)")
@app_commands.describe(ulog="Iznos uloga po igraču u <:e_coins3:1519362621206298666> (default: 200, min: 50, max: 50000)")
async def poker_cmd(i: discord.Interaction, ulog: int = 200):
    ok, left = _check_game_cooldown(i.user, i.guild_id, "poker")
    if not ok:
        return await _send_cooldown_msg(i, "poker", left)
    if poker_games.get(i.channel_id):
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508>", "Poker igra je već aktivna u ovom kanalu!", color=COLORS["error"]), ephemeral=True)
    if ulog < 50:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508>", "Minimalni ulog je `50 <:e_coins3:1519362621206298666>`.", color=COLORS["error"]), ephemeral=True)
    if ulog > 50000:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508>", "Maksimalni ulog je `50,000 <:e_coins3:1519362621206298666>`.", color=COLORS["error"]), ephemeral=True)
    uid = i.user.id
    bal = _pk_get_bal(i.guild.id, uid)
    if bal < ulog:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508>", f"Nemaš dovoljno! Trebaš `{ulog:,} <:e_coins3:1519362621206298666>`, a imaš `{bal:,} <:e_coins3:1519362621206298666>`.", color=COLORS["error"]),
            ephemeral=True)
    _pk_set_bal(i.guild.id, uid, bal - ulog)
    save_data()
    _set_game_cooldown(i.user, i.guild_id, "poker")
    g = {
        "guild_id":    i.guild.id,
        "channel_id":  i.channel_id,
        "host_id":     uid,
        "ulog":        ulog,
        "pot":         ulog,
        "phase":       "join",
        "players":     {uid: {"name": i.user.display_name, "hole": [], "folded": False}},
        "deck":        [],
        "community":   [],
        "needs_action": set(),
        "msg":         None,
    }
    poker_games[i.channel_id] = g
    view = PokerLobbyView(i.channel_id)
    e    = _pk_lobby_embed(g)
    await i.response.send_message(embed=e, view=view)
    msg  = await i.original_response()
    g["msg"] = msg

# ═══════════════════════════════════════════
#    LJUBAVNE / SOCIJALNE KOMANDE
# ═══════════════════════════════════════════
async def social_cmd(i: discord.Interaction, target: discord.Member, action: str, txt: str, color_key: str = "love"):
    await i.response.defer()
    gif = await get_gif(action)
    opis = txt.replace("{from}", i.user.mention).replace("{to}", target.mention)
    e = discord.Embed(description=opis, color=COLORS[color_key], timestamp=datetime.now(timezone.utc))
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    if gif: e.set_image(url=gif)
    await i.followup.send(embed=e)

@bot.tree.command(name="zagrljaj", description="<:e_shake:1519362947766554737> Zagrli nekog na serveru")
async def zagrljaj(i: discord.Interaction, korisnik: discord.Member):
    await social_cmd(i, korisnik, "hug", "<:e_shake:1519362947766554737> {from} grli {to}! Aww, tako slatko! <:e_heart2:1519362668644012133>", "love")

@bot.tree.command(name="poljubac", description="<:e_heart2:1519362668644012133> Pošalji poljubac nekome")
async def poljubac(i: discord.Interaction, korisnik: discord.Member):
    await social_cmd(i, korisnik, "kiss", "<:e_heart2:1519362668644012133> {from} šalje poljubac {to}! <:e_heart2:1519362668644012133>", "pink")

@bot.tree.command(name="mazi", description="<:e_heart2:1519362668644012133> Pomazi nekoga nježno")
async def mazi(i: discord.Interaction, korisnik: discord.Member):
    await social_cmd(i, korisnik, "pat", "<:e_heart2:1519362668644012133> {from} mazi {to} po glavi! Predobro! <:e_sparkles:1519363032185176198>", "love")

@bot.tree.command(name="tapsi", description="<:e_shake:1519362947766554737> Tapši nekoga prijateljski")
async def tapsi(i: discord.Interaction, korisnik: discord.Member):
    await social_cmd(i, korisnik, "handshake", "<:e_shake:1519362947766554737> {from} tapše {to}! Aj, brate! <:e_shake:1519362947766554737>", "teal")

@bot.tree.command(name="high5", description="<:e_shake:1519362947766554737> Daj peticu nekome")
async def high5(i: discord.Interaction, korisnik: discord.Member):
    await social_cmd(i, korisnik, "highfive", "<:e_shake:1519362947766554737> {from} daje peticu {to}! Dobra ekipa! <:e_bolt:1519362674717102160>", "success")

@bot.tree.command(name="cudan", description="<:e_devil:1519362989470253187> Budi ćudan prema nekome")
async def cudan(i: discord.Interaction, korisnik: discord.Member):
    await social_cmd(i, korisnik, "poke", "<:e_devil:1519362989470253187> {from} je ćudan prema {to}! Ajde, brate... <:e_muscle:1519362764244652122>", "warning")

@bot.tree.command(name="srce", description="<:e_heart2:1519362668644012133>️ Pošalji srce nekome")
async def srce(i: discord.Interaction, korisnik: discord.Member):
    poruke = [
        "<:e_heart2:1519362668644012133>️ {from} šalje srce {to}! Aww! <:e_cry:1519362944717160530>",
        "<:e_heart2:1519362668644012133> {from} voli {to}! Toliko slatko! <:e_heart2:1519362668644012133>",
        "<:e_rose:1519363697728815175> {from} poklanja ruže {to}! Romantično! <:e_rose:1519363697728815175>",
        "<:e_heart2:1519362668644012133> {from} šalje ljubav {to}! Neka traje! <:e_heart2:1519362668644012133>",
    ]
    e = discord.Embed(description=random.choice(poruke).replace("{from}", i.user.mention).replace("{to}", korisnik.mention), color=COLORS["love"], timestamp=datetime.now(timezone.utc))
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await i.response.send_message(embed=e)

@bot.tree.command(name="brak", description="<:e_ring:1519362941617438750> Zaprosio nekoga (za fun)")
async def brak(i: discord.Interaction, korisnik: discord.Member):
    if korisnik.id == i.user.id:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Ne možeš se zarositi sam sebi!", color=COLORS["error"]), ephemeral=True)
    odgovori = [
        f"<:e_ring:1519362941617438750> {i.user.mention} zaprosio {korisnik.mention}! <:e_heart2:1519362668644012133> Hoćeš li? <:e_coffee:1519362856884371526>",
        f"<:e_ring:1519362941617438750> {i.user.mention} klekne pred {korisnik.mention} i kaže: 'Hoćeš li biti moj/moja?' <:e_ring:1519362941617438750>",
        f"<:e_rose:1519363697728815175> {i.user.mention} donosi ruže i prsten {korisnik.mention}! Romantika! <:e_heart2:1519362668644012133>",
    ]
    e = discord.Embed(description=random.choice(odgovori), color=COLORS["love"], timestamp=datetime.now(timezone.utc))
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await i.response.send_message(embed=e)

# ═══════════════════════════════════════════
#    POZDRAVI & MUVANJE
# ═══════════════════════════════════════════
_fun_cd: dict = {}  # (user_id, cmd) -> expires_at

async def fun_cooldown(i: discord.Interaction, cmd: str) -> bool:
    """Vrati True (i pošalji grešku) ako je korisnik na cooldownu."""
    key = (i.user.id, cmd)
    now = time.time()
    if key in _fun_cd and now < _fun_cd[key]:
        left = round(_fun_cd[key] - now, 1)
        await i.response.send_message(
            embed=em("<:e_time2:1519362726952964227> Polako!", f"Čekaj još `{left}s` pa pošalji ponovo! <:e_dizzy:1519362812554510509>", color=COLORS["warning"]),
            ephemeral=True
        )
        return True
    _fun_cd[key] = now + random.randint(5, 7)
    return False

POZZ_PORUKE = [
    "{user} je toliko nesretan/nesretna da bi kiša padala samo na njega/nju! <:e_rain:1519362881756336168><:e_sparkles:1519363032185176198>",
    "{user} se pojavio/la! Svima odmah postalo malo bolje. Ili gore. Još ne znamo. <:e_brain:1519362849548406975>",
    "{user} je stigao/la! Server je upravo dobio +1 na kaos. <:e_dice2:1519362633763913931>",
    "Oh, {user} je tu! Čak i WiFi malo usporio od uzbuđenja. <:e_signal:1519362931689525422><:e_sparkles:1519363032185176198>",
    "{user} je ušao/la kao da nosi sav teret Balkana na leđima. Budi jači/a, brate/sestro! <:e_muscle:1519362764244652122>",
    "{user} se pojavio/la, oblaci su se razišli... al samo da ga/je bolje vide. <:e_cloud:1519363450084786376>️<:e_eyes:1519362845970530577>",
    "{user} je stigao/la! Temperatura u sobi pala za 2 stepena. Brrr. <:e_snow:1519362801703977110>",
    "{user} je tu! Neko je trebao doći kasno, i evo ga/je. <:e_time2:1519362726952964227><:e_sparkles:1519363032185176198>",
    "{user} je ušao/la onako kako ulaze heroji — tiho, neopaženo, i malo zbunjeno. <:e_shield2:1519362627795554374>",
    "{user} se pojavio/la! Baba bi rekla: 'Ajde sine/ćeri, jesil jeo/jela?' <:e_grandma:1519362798189150370><:e_plate:1519362791591378975>️",
    "{user} je stigao/la! Google Maps kaže da si trebao/la biti tu prije 45 minuta. <:e_map:1519363571815809179>️<:e_dizzy:1519362812554510509>",
    "{user} se prijavio/la na server! Anđeli plaču, a đavoli aplaudiraju. <:e_devil:1519362989470253187><:e_sparkles:1519363032185176198>",
    "{user} je tu! Čak i mačke na ulici znale da nešto nije u redu. <:e_tiger:1519363422716825600>",
    "Alarm! {user} je online! Sklanjajte sve vrijedno! <:e_report2:1519362714198347886><:e_sparkles:1519363032185176198>",
    "{user} je ušao/la onako tiho kao slon u prodavnici porculana. <:e_bear:1519363418790822029>",
]

KOMPLI_PORUKE = [
    "<:e_rose:1519363697728815175> {from} kaže {to}: 'Ti si razlog zašto dan počinje sa osmijehom. <:e_heart2:1519362668644012133>'",
    "<:e_sparkles:1519363032185176198> {from} za {to}: 'Tvoje oči sjaje više nego moj monitor u 3 ujutru. <:e_heart2:1519362668644012133>'",
    "<:e_cherry:1519363439385116812> {from} {to}: 'Kad se smiješiš, čak i bots-ovi izgube koncentraciju. <:e_heart2:1519362668644012133>'",
    "<:e_sparkles:1519363032185176198> {from} kaže {to}: 'Ti si jedina osoba zbog koje bih zatvorio YouTube. I to je PUNO. <:e_dizzy:1519362812554510509><:e_heart2:1519362668644012133>'",
    "<:e_feather:1519363362322907218> {from} za {to}: 'Pored tebe, sve ostale zvezde izgledaju kao noćne lampice. <:e_sparkles:1519363032185176198>'",
    "<:e_clover:1519363694549667881> {from} {to}: 'Ako si ti greška, onda je svemir trebao praviti više grešaka. <:e_heart2:1519362668644012133>'",
    "<:e_moon:1519363445466595522> {from} kaže {to}: 'Ti si razlog zašto pjesnici još uvijek pišu stihove. 📝<:e_heart2:1519362668644012133>'",
    "<:e_fire2:1519362671491678280> {from} za {to}: 'Toliko si cool da ni klima u mom sobi ne može da te dostigne. <:e_snow:1519362801703977110>️<:e_heart2:1519362668644012133>'",
    "<:e_sparkles:1519363032185176198> {from} {to}: 'Kad si ti tu, cio server osjeti razliku. Kao sunce posle kiše. <:e_rainbow:1519363453347696821>'",
    "<:e_mail:1519362754732097546> {from} kaže {to}: 'Nisi savršen/na, ali si savršen/na za mene. I to je sve što treba. <:e_heart2:1519362668644012133>'",
    "<:e_flower:1519362984818901173> {from} za {to}: 'Tvoj smijeh zvuči kao melodija koje bi slušao/la cio dan. <:e_music2:1519362679310127114><:e_heart2:1519362668644012133>'",
    "<:e_star2:1519363084253266031> {from} {to}: 'Ti si dokaz da Bog ponekad ima dobrog dana. <:e_sparkles:1519363032185176198><:e_sparkles:1519363032185176198>'",
]

FORA_PORUKE = [
    "<:e_sparkles:1519363032185176198> {from} je pogledao/la {to} i shvatio/la: 'Brate/sestro, ti si dokaz da evolucija nije uvijek napredak.' <:e_bear:1519363418790822029>",
    "<:e_masks:1519363003424706671> {from} za {to}: 'Tražiš razlog da se smiješ? Pogledaj se u ogledalo!' <:e_cry:1519362944717160530><:e_sparkles:1519363032185176198>",
    "<:e_skull:1519362992502997125> {from} {to}: 'Toliko si prosječan/na da Google ne zna ni da te indexuje.' <:e_search:1519363103064723547>",
    "<:e_muscle:1519362764244652122> {from} za {to}: 'Tvoja ex je bila u pravu za jedno — čekanje nije uvijek vrijedno.' <:e_heart2:1519362668644012133><:e_sparkles:1519363032185176198>",
    "<:e_brain:1519362849548406975> {from} {to}: 'Mislio/la sam da si pametan/na... al to bi mi bila prva greška.' <:e_brain:1519362849548406975>",
    "<:e_circus:1519363558809272371> {from} za {to}: 'Jedina stvar koja radi brže od tebe je moj internet kad ga fakturiram.' <:e_satellite:1519363311207186482><:e_sparkles:1519363032185176198>",
    "<:e_dizzy:1519362812554510509> {from} {to}: 'Rekli su mi da budem ljubazan/na... al ni ja ne znam kako.' <:e_skull:1519362992502997125>",
    "<:e_eyes:1519362845970530577> {from} za {to}: 'Svaki put kad pišeš, autocorrect se zapita je li vredno popraviti.' <:e_phone:1519362788462559323><:e_sparkles:1519363032185176198>",
    "<:e_dizzy:1519362812554510509> {from} {to}: 'IQ ti je manji od temp u frižideru. I to zimski frižider.' <:e_snow:1519362801703977110>️",
    "<:e_trophy2:1519362624742232146> {from} za {to}: 'Nagradu za originalnost si propustio/la zajedno sa svakom drugom nagradom.' <:e_sparkles:1519363032185176198>",
]

# /pozz uklonjeno (v2.2) — pravimo mjesto za /mafia igru.

@bot.tree.command(name="kompli", description="<:e_rose:1519363697728815175> Pošalji slatki kompliment nekome")
@discord.app_commands.describe(korisnik="Kome šalješ kompliment")
async def kompli(i: discord.Interaction, korisnik: discord.Member):
    if await fun_cooldown(i, "kompli"): return
    if korisnik.id == i.user.id:
        poruka = "<:e_devil:1519362989470253187> Hm, komplimentiraš samog/samu sebe? Ajde, prihvatamo to!"
    else:
        poruka = random.choice(KOMPLI_PORUKE).replace("{from}", i.user.mention).replace("{to}", korisnik.mention)
    e = discord.Embed(description=poruka, color=COLORS["pink"], timestamp=datetime.now(timezone.utc))
    e.set_thumbnail(url=korisnik.display_avatar.url)
    e.set_footer(text=f"{BOT_NAME} • Muvanje 101 <:e_heart2:1519362668644012133>")
    await i.response.send_message(embed=e)

@bot.tree.command(name="fora", description="<:e_sparkles:1519363032185176198> Ubaci foru na račun nekoga (sve u šali!)")
@discord.app_commands.describe(korisnik="Ko prima foru")
async def fora(i: discord.Interaction, korisnik: discord.Member):
    if await fun_cooldown(i, "fora"): return
    if korisnik.id == i.user.id:
        poruka = "<:e_sparkles:1519363032185176198> Fora na vlastiti račun? Poštujemo samokritiku!"
    else:
        poruka = random.choice(FORA_PORUKE).replace("{from}", i.user.mention).replace("{to}", korisnik.mention)
    e = discord.Embed(description=poruka, color=COLORS["fun"], timestamp=datetime.now(timezone.utc))
    e.set_thumbnail(url=korisnik.display_avatar.url)
    e.set_footer(text=f"{BOT_NAME} • Sve u šali! <:e_sparkles:1519363032185176198>")
    await i.response.send_message(embed=e)

@bot.tree.command(name="muv", description="<:e_crystal:1519362965558657146> Muvaj nekoga Balkan stilom")
@discord.app_commands.describe(korisnik="Ko je sretan/na da ga/ju muvaš")
async def muv(i: discord.Interaction, korisnik: discord.Member):
    if await fun_cooldown(i, "muv"): return
    if korisnik.id == i.user.id:
        return await i.response.send_message(embed=em("<:e_dizzy:1519362812554510509>", "Ne možeš muvati samog/samu sebe, brate/sestro!", color=COLORS["error"]), ephemeral=True)
    muv_poruke = [
        f"<:e_crystal:1519362965558657146> {i.user.mention} {korisnik.mention}: 'Jesi li ti WiFi? Jer osjećam konekciju između nas.' <:e_signal:1519362931689525422><:e_heart2:1519362668644012133>",
        f"<:e_rose:1519363697728815175> {i.user.mention} {korisnik.mention}: 'Daj mi broj, hoću te zvati svaki dan... osim kad nemam kredit.' <:e_sparkles:1519363032185176198><:e_heart2:1519362668644012133>",
        f"<:e_fire2:1519362671491678280> {i.user.mention} {korisnik.mention}: 'Ti si kao kebab u 3 ujutru — ne znam zašto, ali baš te trebam.' <:e_wrap:1519363373748195502><:e_heart2:1519362668644012133>",
        f"<:e_sparkles:1519363032185176198> {i.user.mention} kaže {korisnik.mention}: 'Slika ti se hvata svuda — čak i u mojim snovima. <:e_camera:1519363493701091348><:e_heart2:1519362668644012133>'",
        f"<:e_heart2:1519362668644012133> {i.user.mention} {korisnik.mention}: 'Da sam Google, stavil/la bih te na prvu stranicu. <:e_search:1519363103064723547><:e_heart2:1519362668644012133>'",
        f"🎯 {i.user.mention} {korisnik.mention}: 'Znaš šta te razlikuje od ostalih? Sve. <:e_heart2:1519362668644012133><:e_sparkles:1519363032185176198>'",
        f"<:e_arrow:1519363399845154958> {i.user.mention} {korisnik.mention}: 'Cupid me pogodio strelicom, ali mislim da si ti sljedeća meta. <:e_dizzy:1519362812554510509><:e_heart2:1519362668644012133>'",
        f"<:e_moon:1519363445466595522> {i.user.mention} {korisnik.mention}: 'Astronomija je dokazala da zvijezde padaju. Ali ti... ti nikad ne padaš s mog uma. <:e_sparkles:1519363032185176198>'",
        f"<:e_coffee:1519362856884371526> {i.user.mention} {korisnik.mention}: 'Ti si mi kao kafa ujutru — ne mogu bez tebe ni dan. <:e_crystal:1519362965558657146><:e_coffee:1519362856884371526>'",
        f"<:e_music2:1519362679310127114> {i.user.mention} {korisnik.mention}: 'Svaka pjesma koju čujem podsjeti me na tebe. Čak i folk. <:e_music2:1519362679310127114><:e_heart2:1519362668644012133>'",
    ]
    e = discord.Embed(description=random.choice(muv_poruke), color=COLORS["love"], timestamp=datetime.now(timezone.utc))
    e.set_thumbnail(url=korisnik.display_avatar.url)
    e.set_footer(text=f"{BOT_NAME} • Balkan Muvanje™ <:e_crystal:1519362965558657146>")
    await i.response.send_message(embed=e)

@bot.tree.command(name="crush", description="<:e_heart2:1519362668644012133> Otkrij ko je tvoj tajni crush na serveru!")
async def crush(i: discord.Interaction):
    if await fun_cooldown(i, "crush"): return
    members = [m for m in i.guild.members if not m.bot and m.id != i.user.id]
    if not members:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Nema dovoljno članova!", color=COLORS["error"]), ephemeral=True)
    random.seed(i.user.id + i.guild.id)
    picked = random.choice(members)
    random.seed()
    poruke = [
        f"<:e_heart2:1519362668644012133> Po zvijezdama i kafanskim računima, tvoj tajni crush je... **{picked.display_name}**! <:e_dizzy:1519362812554510509>",
        f"<:e_crystal:1519362965558657146> Kristalna kugla kaže: **{picked.display_name}** ti se sviđa više nego što priznaješ! <:e_heart2:1519362668644012133>",
        f"<:e_mail:1519362754732097546> Baka bi rekla: 'Idi, pitaj ga/je na kafu!' — tvoj crush: **{picked.display_name}** <:e_coffee:1519362856884371526><:e_heart2:1519362668644012133>",
    ]
    e = discord.Embed(description=random.choice(poruke), color=COLORS["love"], timestamp=datetime.now(timezone.utc))
    e.set_thumbnail(url=picked.display_avatar.url)
    e.set_footer(text=f"{BOT_NAME} • Crush Otkrivač™ | Samo za zabavu!")
    await i.response.send_message(embed=e)

# ═══════════════════════════════════════════
#    OWO — ŽIVOTINJE SISTEM
# ═══════════════════════════════════════════
ANIMALS = {
    # ime: (emoji, rarity, power, value)
    "Riba":            ("<:e_fish2:1519362685957963940>", "common",    1,   5),
    "Ptica":           ("<:e_eagle:1519363429394153633>", "common",    1,   5),
    "Patka":           ("<:e_eagle:1519363429394153633>", "common",    1,   6),
    "Kokoška":         ("<:e_eagle:1519363429394153633>", "common",    1,   6),
    "Zec":             ("<:e_sheep:1519363388789227611>", "common",    2,   8),
    "Vjeverica":       ("<:e_deer2:1519362689212874883>️","common",    2,   8),
    "Gušter":          ("<:e_dragon:1519363409421008987>", "common",    2,   8),
    "Puž":             ("<:e_herb:1519363706243387573>", "common",    1,   5),
    "Miš":             ("<:e_deer2:1519362689212874883>", "common",    2,   7),
    "Lisica":          ("<:e_fox:1519363415871590420>", "uncommon",  5,  25),
    "Jazavac":         ("<:e_bear:1519363418790822029>", "uncommon",  4,  22),
    "Vuk":             ("<:e_wolf:1519363412625326161>", "uncommon",  7,  40),
    "Rakun":           ("<:e_fox:1519363415871590420>", "uncommon",  5,  30),
    "Kornjača":        ("<:e_dragon:1519363409421008987>", "uncommon",  3,  28),
    "Majmun":          ("<:e_bear:1519363418790822029>", "uncommon",  5,  32),
    "Medvjed":         ("<:e_bear:1519363418790822029>", "rare",     12,  90),
    "Lav":             ("<:e_lion:1519363402890346658>", "rare",     14, 110),
    "Tigar":           ("<:e_tiger:1519363422716825600>", "rare",     13, 105),
    "Orao":            ("<:e_eagle:1519363429394153633>", "rare",     10, 100),
    "Ajkula":          ("<:e_fish2:1519362685957963940>", "rare",     13, 115),
    "Nilski konj":     ("<:e_bear:1519363418790822029>", "rare",     11,  95),
    "Zmaj":            ("<:e_dragon:1519363409421008987>", "epic",     28, 320),
    "Jednorog":        ("<:e_crystal:1519362965558657146>", "epic",     22, 270),
    "Krokodil":        ("<:e_dragon:1519363409421008987>", "epic",     25, 290),
    "Gorila":          ("<:e_bear:1519363418790822029>", "epic",     20, 260),
    "Feniks":          ("<:e_fire2:1519362671491678280>", "legendary",55, 900),
    "Morski Lav":      ("<:e_dolphin:1519363432615510078>", "legendary",50, 820),
    "Noćni Zmaj":      ("<:e_dragon:1519363409421008987>", "legendary",60, 980),
    "Kristalni Jednorog":("<:e_diamond2:1519362640961474601>","mythical",110,5000),
    "Dugin Feniks":    ("<:e_rainbow:1519363453347696821>", "mythical", 130,7000),
    "Nebeski Zmaj":    ("<:e_sparkles:1519363032185176198>", "mythical", 150,9999),
}

RARITY_ORDER  = ["common","uncommon","rare","epic","legendary","mythical"]
RARITY_EMOJI  = {"common":"<:e_user:1519363093736718518>","uncommon":"<:e_green:1519362769047126028>","rare":"<:e_internet:1519363106395000994>","epic":"<:e_flower:1519362984818901173>","legendary":"<:e_green:1519362769047126028>","mythical":"<:e_cherry:1519363439385116812>"}
RARITY_COLORS = {"common":0x9B9B9B,"uncommon":0x2ECC71,"rare":0x3498DB,"epic":0x9B59B6,"legendary":0xF1C40F,"mythical":0xFF69B4}
RARITY_WEIGHTS= {"common":50,"uncommon":26,"rare":15,"epic":7,"legendary":2,"mythical":0.3}

HUNT_MISS = [
    "Ništa nisi uhvatio... životinja je pobjegla! <:e_wind:1519362878300229883>",
    "Prazne ruke! Vrati se kad si odmorniji. <:e_sleep:1519362785291669644>",
    "Tišina u šumi... nema ničega danas. <:e_palm:1519363442597695600>",
    "Promašio si! Trebao si ići lijevo. <:e_refresh:1519362959187509461>️",
    "Životinja te vidjela prije nego ti nju. <:e_eyes:1519362845970530577>",
]

def pick_animal() -> str | None:
    if random.random() < 0.12:
        return None  # miss
    rarities = list(RARITY_WEIGHTS.keys())
    weights  = [RARITY_WEIGHTS[r] for r in rarities]
    chosen   = random.choices(rarities, weights=weights, k=1)[0]
    pool     = [n for n, (_, r, _, _) in ANIMALS.items() if r == chosen]
    return random.choice(pool) if pool else None

def zoo_power(uid) -> int:
    zoo  = get_zoo(uid)
    total = 0
    for name, cnt in zoo.items():
        if name in ANIMALS and cnt > 0:
            total += ANIMALS[name][2] * cnt
    return total

HUNT_COOLDOWNS: dict = {}

@bot.tree.command(name="hunt", description="<:e_arrow:1519363399845154958> Idi u lov na životinje! (kao owo hunt)")
async def hunt(i: discord.Interaction):
    now = time.time()
    last = HUNT_COOLDOWNS.get(i.user.id, 0)
    remaining = 7 - (now - last)
    if remaining > 0:
        return await i.response.send_message(
            embed=em("<:e_time2:1519362726952964227> Previše si lovio!", f"Čekaj još `{remaining:.1f}s`", color=COLORS["warning"]),
            ephemeral=True
        )
    HUNT_COOLDOWNS[i.user.id] = now
    await i.response.defer()
    await asyncio.sleep(1.2)

    animal = pick_animal()
    if not animal:
        e = discord.Embed(description=f"<:e_arrow:1519363399845154958>  {random.choice(HUNT_MISS)}", color=_LP, timestamp=datetime.now(timezone.utc))
        e.set_footer(text=f"{BOT_NAME} {VERSION} • Pokušaj ponovo za 7s")
        return await i.followup.send(embed=e)

    emoji, rarity, power, value = ANIMALS[animal]
    zoo = get_zoo(i.user.id)
    zoo[animal] = zoo.get(animal, 0) + 1
    save_data()
    quest_progress(i.user.id, "hunt5")
    quest_progress(i.user.id, "hunt10")

    color = RARITY_COLORS[rarity]
    ri    = RARITY_EMOJI[rarity]
    e = discord.Embed(
        title=f"<:e_arrow:1519363399845154958>  Uhvatio si životinje!",
        description=f"🎯  **Uspješan lov!**\n## {emoji}  {animal}\n{ri} **{rarity.capitalize()}**  ·  <:e_sword2:1519362631146930317>️ Snaga `{power}`",
        color=color,
        timestamp=datetime.now(timezone.utc)
    )
    e.add_field(name="<:e_chart:1519362656568475880> Imaš ukupno", value=f"`{zoo[animal]}x {emoji} {animal}`", inline=True)
    e.add_field(name="<:e_coins3:1519362621206298666> Vrijednost",   value=f"`{value} <:e_coins3:1519362621206298666>`",                       inline=True)
    e.set_footer(text=f"{i.user.display_name} • {BOT_NAME} {VERSION}")
    await i.followup.send(embed=e)

@bot.tree.command(name="zoo", description="<:e_lion:1519363402890346658> Pogledaj svoju zbirku životinja (kao owo zoo)")
async def zoo_cmd(i: discord.Interaction, korisnik: discord.Member = None):
    u   = korisnik or i.user
    zoo = get_zoo(u.id)
    if not zoo or all(v == 0 for v in zoo.values()):
        return await i.response.send_message(
            embed=em(f"<:e_lion:1519363402890346658> {u.display_name} — Zoo", "Prazno! Idi u `/hunt` i uhvati neku životinje. <:e_arrow:1519363399845154958>", color=COLORS["info"]), ephemeral=True
        )

    sections = []
    for rarity in RARITY_ORDER:
        animals = [(n, cnt) for n, cnt in zoo.items() if n in ANIMALS and ANIMALS[n][1] == rarity and cnt > 0]
        if not animals:
            continue
        ri   = RARITY_EMOJI[rarity]
        rows = [f"{ANIMALS[n][0]} **{n}** `×{cnt}`" for n, cnt in sorted(animals)]
        sections.append(f"{ri} **{rarity.capitalize()}**\n" + "  ".join(rows))

    total   = sum(zoo.values())
    power   = zoo_power(u.id)
    e = discord.Embed(
        title=f"<:e_lion:1519363402890346658> {u.display_name} — Zoo",
        description="\n\n".join(sections),
        color=COLORS["purple"],
        timestamp=datetime.now(timezone.utc)
    )
    e.add_field(name="<:e_box:1519363099478458498> Ukupno",   value=f"`{total}` životinja", inline=True)
    e.add_field(name="<:e_sword2:1519362631146930317>️ Snaga",    value=f"`{power}`",           inline=True)
    e.set_thumbnail(url=u.display_avatar.url)
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await i.response.send_message(embed=e)

@bot.tree.command(name="battle", description="<:e_sword2:1519362631146930317>️ Bori se sa nekim (kao owo battle)")
async def battle(i: discord.Interaction, korisnik: discord.Member):
    if korisnik.id == i.user.id:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Ne možeš se boriti sam sa sobom!", color=COLORS["error"]), ephemeral=True)
    if korisnik.bot:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Botovi ne znaju se boriti!", color=COLORS["error"]), ephemeral=True)

    await i.response.defer()
    await asyncio.sleep(2)

    p1 = zoo_power(i.user.id) + random.randint(1, 30)
    p2 = zoo_power(korisnik.id) + random.randint(1, 30)

    if p1 == p2:
        p1 += 1

    winner = i.user if p1 > p2 else korisnik
    loser  = korisnik if p1 > p2 else i.user
    wp, lp = (p1, p2) if p1 > p2 else (p2, p1)

    reward = random.randint(80, 300)
    get_economy(winner.id)["balance"] += reward
    save_data()

    bar_total = 20
    p1_fill = round((p1 / (p1 + p2)) * bar_total)
    p2_fill = bar_total - p1_fill
    bar = f"`{'█' * p1_fill}{'░' * p2_fill}`"

    e = discord.Embed(
        title="<:e_sword2:1519362631146930317>️  BITKA!",
        description=(
            f"<:icon_sword:1519358255925825667>  **{i.user.display_name}** vs **{korisnik.display_name}**\n"
            f"{bar}\n"
            f"<:e_sword2:1519362631146930317>️ `{p1}` vs `{p2}` <:e_sword2:1519362631146930317>️"
        ),
        color=COLORS["gold"],
        timestamp=datetime.now(timezone.utc)
    )
    e.add_field(name="<:e_trophy2:1519362624742232146> Pobjednik",  value=f"**{winner.mention}**",      inline=True)
    e.add_field(name="<:e_skull:1519362992502997125> Poražen",    value=f"{loser.mention}",           inline=True)
    e.add_field(name="<:e_coins3:1519362621206298666> Nagrada",    value=f"`+{reward} <:e_coins3:1519362621206298666>`",            inline=False)
    e.set_thumbnail(url=winner.display_avatar.url)
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await i.followup.send(embed=e)

@bot.tree.command(name="sell", description="<:e_coins3:1519362621206298666> Prodaj životinje iz zoo-a (kao owo sell)")
@app_commands.describe(zivotinja="Ime životinje (npr. Riba)", kolicina="Koliko prodaješ (default 1)")
async def sell(i: discord.Interaction, zivotinja: str, kolicina: int = 1):
    name = zivotinja.strip().capitalize()
    if name not in ANIMALS:
        names = ", ".join(f"`{n}`" for n in list(ANIMALS.keys())[:15])
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Nepoznata životinja", f"Provjeri `/zoo` za listu svojih životinja.\nPrimjeri: {names}", color=COLORS["error"]), ephemeral=True
        )
    zoo = get_zoo(i.user.id)
    owned = zoo.get(name, 0)
    if owned < kolicina or kolicina < 1:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Nemaš dovoljno", f"Imaš samo `{owned}x {ANIMALS[name][0]} {name}`.", color=COLORS["error"]), ephemeral=True
        )
    emoji, rarity, power, value = ANIMALS[name]
    total_earn = value * kolicina
    zoo[name]  = owned - kolicina
    get_economy(i.user.id)["balance"] += total_earn
    save_data()
    await i.response.send_message(embed=em(
        f"<:e_coins3:1519362621206298666> Prodato!",
        f"Prodao si `{kolicina}x {emoji} {name}` za **{total_earn} <:e_coins3:1519362621206298666>**!",
        color=COLORS["success"],
        fields=[("<:e_bank2:1519362662515871744> Balans", f"`{get_economy(i.user.id)['balance']:,} <:e_coins3:1519362621206298666>`", True)]
    ))

@bot.tree.command(name="animals", description="<:e_clipboard:1519363052871614627> Listu svih životinja i raritet (kao owo animals)")
async def animals_cmd(i: discord.Interaction):
    e = discord.Embed(title="<:e_clipboard:1519363052871614627> Sve životinje — Raritetna lista", color=COLORS["purple"], timestamp=datetime.now(timezone.utc))
    for rarity in RARITY_ORDER:
        ri    = RARITY_EMOJI[rarity]
        pool  = [(n, d[0], d[2], d[3]) for n, d in ANIMALS.items() if d[1] == rarity]
        lines = [f"{em2} **{n}** — <:e_sword2:1519362631146930317>️`{pw}` <:e_coins3:1519362621206298666>`{val}`" for n, em2, pw, val in pool]
        e.add_field(name=f"{ri} {rarity.capitalize()}", value="\n".join(lines), inline=True)
    e.set_footer(text=f"{BOT_NAME} {VERSION} • /hunt za loviti!")
    await i.response.send_message(embed=e)

@bot.tree.command(name="pray", description="<:e_pray:1519363406078021863> Pomoli se za nekoga (kao owo pray)")
async def pray(i: discord.Interaction, korisnik: discord.Member):
    if korisnik.id == i.user.id:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Ne možeš moliti za sebe!", color=COLORS["error"]), ephemeral=True)
    bonus = random.randint(20, 100)
    get_economy(korisnik.id)["balance"] += bonus
    save_data()
    msgs = [
        f"<:e_pray:1519363406078021863> {i.user.mention} moli se za {korisnik.mention}! Nebo čuje — `+{bonus} <:e_coins3:1519362621206298666>` palo s neba!",
        f"<:e_sparkles:1519363032185176198> {i.user.mention} šalje dobre vibracije {korisnik.mention}! `+{bonus} <:e_coins3:1519362621206298666>` u džep!",
        f"<:e_feather:1519363362322907218>️ Zbog molitve {i.user.mention}, {korisnik.mention} je blagosloven sa `{bonus} <:e_coins3:1519362621206298666>`!",
    ]
    e = discord.Embed(description=random.choice(msgs), color=_LP, timestamp=datetime.now(timezone.utc))
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await i.response.send_message(embed=e)

# /curse uklonjeno (v2.1) — semantika "prokletstva" rizična za content moderaciju.

# ═══════════════════════════════════════════
#    AUTO-MOD (Anti-Spam + Bad Words)
# ═══════════════════════════════════════════
SPAM_WINDOW = 5
SPAM_LIMIT  = 7
BAD_WORDS: set = set()  # add bad words here: BAD_WORDS = {"rijec1", "rijec2"}
user_msg_times: dict = defaultdict(deque)

# ── Anti-NSFW (pornografija, slike) ─────────────────────
# <:icon_warning:1519358274284032030>️  Psovke u tekstu su DOZVOLJENE — filtriramo samo NSFW linkove i slike

# Pornografski sajtovi — blokirani kao linkovi/embeds
NSFW_SITES = [
    "pornhub", "xvideos", "xnxx", "redtube", "youporn", "onlyfans",
    "rule34", "e-hentai", "xhamster", "spankbang", "chaturbate",
    "pornpics", "porn.com", "xtube", "4tube", "tube8", "sex.com",
]

# Eksplicitni nazivi fajlova (slike kurca/picke) — blokirani u uploadima
NSFW_FILENAMES = [
    "dick", "cock", "penis", "pussy", "vagina", "kurac", "picka", "pička",
    "pizda", "nude", "nudes", "naked", "cumshot", "blowjob", "anal",
    "hentai", "xxx", "porn", "nsfw", "boobs", "tits",
]

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov", ".avi", ".webm"}

# Sigurni domeni — GIF-ovi s ovih servisa su uvijek OK (Discord GIF picker, Tenor, Giphy)
SAFE_DOMAINS = (
    "tenor.com", "media.tenor.com", "tenor.googleapis.com",
    "giphy.com", "media.giphy.com", "media0.giphy.com",
    "media1.giphy.com", "media2.giphy.com",
    "cdn.discordapp.com", "media.discordapp.net",
    "discord.com/channels",
)

def _contains_nsfw_site(text: str) -> str | None:
    if not text: return None
    t = text.lower()
    for w in NSFW_SITES:
        if w in t:
            return w
    return None

def _contains_nsfw_filename(text: str) -> str | None:
    if not text: return None
    t = text.lower()
    for w in NSFW_FILENAMES:
        if w in t:
            return w
    return None

async def check_nsfw(message) -> bool:
    """Briše NSFW sadržaj (slike/linkovi). Vraća True ako je obrisao.
    NAPOMENA: Psovke u tekstu su DOZVOLJENE — ne filtriramo tekst poruke."""
    n = _prot_nsfw()
    if not n["enabled"]:
        return False
    if message.channel.is_nsfw():  # NSFW kanal je dozvoljen
        return False
    # Merge ugrađene + panel extra liste
    all_sites    = list(NSFW_SITES)    + n["extra_sites"]
    all_keywords = list(NSFW_FILENAMES) + n["extra_keywords"]

    def _site_hit(text: str) -> str | None:
        if not text: return None
        t = text.lower()
        for w in all_sites:
            if w in t: return w
        return None

    def _kw_hit(text: str) -> str | None:
        if not text: return None
        t = text.lower()
        for w in all_keywords:
            if w in t: return w
        return None

    found = None

    # 1) Pornografski sajtovi u tekstu/linkovima poruke
    found = _site_hit(message.content)

    # 2) Attachmenti (slike/videi) — provjeri naziv fajla
    if not found:
        for att in message.attachments:
            if any(d in att.url.lower() for d in SAFE_DOMAINS):
                continue
            ext = _os.path.splitext(att.filename.lower())[1]
            if ext in IMAGE_EXTS:
                found = _kw_hit(att.filename)
                if not found:
                    found = _site_hit(att.url)
            if found: break

    # 3) Embeds — provjeri URL i title za NSFW sajtove
    if not found:
        for emb in message.embeds:
            url = emb.url or ""
            if any(d in url.lower() for d in SAFE_DOMAINS):
                continue
            for field in [url, emb.title, emb.description]:
                if field and (found := _site_hit(str(field))): break
            if found: break

    if not found: return False
    # OBRIŠI
    try:
        await message.delete()
    except: pass
    # Upozorenje korisniku
    try:
        await message.channel.send(
            embed=em("<:icon_ban:1519358278356959284> NSFW Sadržaj Zabranjen",
                     f"{message.author.mention} — pornografija/eksplicitan sadržaj nije dozvoljen!\n"
                     f"<:icon_warning:1519358274284032030>️ Detektovano: `{found}`\n"
                     f"<:e_idea:1519363006599794799> Za NSFW koristi posebne **age-restricted** kanale.",
                     color=COLORS["error"]),
            delete_after=10
        )
    except: pass
    # Auto-warn + log
    try:
        await audit_log(message.guild, "<:icon_ban:1519358278356959284> Anti-NSFW",
                        f"{message.author.mention} pokušao slati NSFW u {message.channel.mention}\n**Trigger:** `{found}`")
    except: pass
    # Dinamičan strikes limit i timeout iz panel konfiguracije
    nsfw_cfg = _prot_nsfw()
    strike_limit  = nsfw_cfg["strikes"]
    timeout_mins  = nsfw_cfg["timeout_min"]
    nsfw_strikes = data.setdefault("nsfw_strikes", {})
    skey = f"{message.guild.id}:{message.author.id}"
    nsfw_strikes[skey] = nsfw_strikes.get(skey, 0) + 1
    save_data()
    if nsfw_strikes[skey] >= strike_limit:
        try:
            await message.author.timeout(timedelta(minutes=timeout_mins), reason=f"Anti-NSFW: {strike_limit}+ pokušaja")
            await message.channel.send(
                embed=em("<:e_mute2:1519362648972595289> Timeout", f"{message.author.mention} dobio **{timeout_mins}min timeout** zbog ponovljenog NSFW sadržaja!", color=COLORS["error"]),
                delete_after=15
            )
            nsfw_strikes[skey] = 0; save_data()
        except: pass
    return True

# ── Anti-Invite (drugi serveri) ─────────────────────────
INVITE_REGEX = re.compile(
    r"(?:"
    r"discord\s*\.\s*(?:gg|io|me|li)\s*\/\s*[a-zA-Z0-9-]+"
    r"|discord(?:app)?\s*\.\s*com\s*\/\s*invite\s*\/\s*[a-zA-Z0-9-]+"
    r"|dsc\s*\.\s*gg\s*\/\s*[a-zA-Z0-9-]+"
    r"|(?<![a-zA-Z0-9])\.gg\/[a-zA-Z0-9-]+"
    r")",
    re.I
)

ALLOWED_UPLOAD_EXTS = {".gif", ".png", ".jpg", ".jpeg", ".webp", ".apng"}

# ── Globalna anti-invite zaštita za SVE slash (/) komande ─────────────────
# Svaki tekstualni argument na slash komandi se skenira; ako ima invite link,
# komanda se odbija sa ephemeral upozorenjem. (Vlasnici su izuzeti.)
async def _global_invite_check(interaction: discord.Interaction) -> bool:
    try:
        if interaction.type != discord.InteractionType.application_command:
            return True
        u = interaction.user
        if u and getattr(u, "id", None) in OWNER_IDS:
            return True
        ns = getattr(interaction, "namespace", None)
        if ns is None:
            return True
        for _k, _v in vars(ns).items():
            if isinstance(_v, str) and INVITE_REGEX.search(_v):
                try:
                    await interaction.response.send_message(
                        embed=em(
                            "<:icon_ban:1519358278356959284> Reklama zabranjena",
                            f"{u.mention if u else ''} — **invite linkovi nisu dozvoljeni** ni na slash komandama!\n"
                            f"Probaj ponovo bez `discord.gg/...` / `.gg/...` linka.",
                            color=COLORS["error"]
                        ),
                        ephemeral=True
                    )
                except Exception:
                    try:
                        await interaction.followup.send(
                            embed=em("<:icon_ban:1519358278356959284> Reklama zabranjena",
                                     "Invite linkovi nisu dozvoljeni!",
                                     color=COLORS["error"]),
                            ephemeral=True
                        )
                    except Exception: pass
                return False
    except Exception as _e:
        print(f"[global-invite-check] {_e}")
    return True

bot.tree.interaction_check = _global_invite_check

# ── Per-server isključene komande (panel → bot) ──────────────────────────
# Vlasnik servera na panelu (giann.uk) može isključiti pojedine komande za
# SVOJ server. Ovdje ih provjeravamo i blokiramo prije izvršavanja.
_guild_features_cache: dict = {}   # guild_id(str) -> (fetched_at, set(disabled))

async def get_guild_disabled(guild_id) -> set:
    """Vrati set isključenih komandi za dati server (cache 60s)."""
    gkey = str(guild_id)
    now = time.time()
    cached = _guild_features_cache.get(gkey)
    if cached and now - cached[0] < 60:
        return cached[1]
    disabled = cached[1] if cached else set()
    try:
        async with aiohttp.ClientSession() as _s:
            async with _s.get(f"{PANEL_API_URL}/api/guild/{gkey}/features",
                              timeout=aiohttp.ClientTimeout(total=3)) as _r:
                if _r.status == 200:
                    _data = await _r.json()
                    disabled = set(_data.get("disabled", []) or [])
    except Exception as _fe:
        print(f"[guild-features] Fetch error guild={gkey}: {_fe}")
    _guild_features_cache[gkey] = (now, disabled)
    return disabled

async def _combined_interaction_check(interaction: discord.Interaction) -> bool:
    # 1) zadrži postojeću anti-invite zaštitu
    if not await _global_invite_check(interaction):
        return False
    # 2) per-server isključene komande
    try:
        if interaction.type != discord.InteractionType.application_command:
            return True
        if not interaction.guild:
            return True
        cmd = interaction.command.name if interaction.command else None
        if not cmd:
            return True
        disabled = await get_guild_disabled(interaction.guild.id)
        if cmd in disabled:
            try:
                await interaction.response.send_message(
                    embed=em("<:e_pause:1519363038107406447>️ Isključeno",
                             f"Komanda `/{cmd}` je **isključena na ovom serveru**.\n"
                             f"Vlasnik je može ponovo uključiti na panelu (giann.uk).",
                             color=COLORS["warning"]),
                    ephemeral=True
                )
            except Exception:
                pass
            return False
    except Exception as _ce:
        print(f"[guild-features-check] {_ce}")
    return True

bot.tree.interaction_check = _combined_interaction_check

async def check_automod(message) -> bool:
    # ── Anti-Invite filter — vrijedi za SVE (admini, staff, svi) ──
    # Jedini izuzetak su vlasnici u OWNER_IDS.
    if message.author.id not in OWNER_IDS:
        invite_found = INVITE_REGEX.search(message.content or "")
        # Provjeri i u embedima koje je korisnik uključio (embed preview od linkova)
        if not invite_found and message.embeds:
            for _emb in message.embeds:
                _check_texts = [
                    _emb.title or "", _emb.description or "", _emb.url or "",
                    getattr(_emb.footer, "text", "") or "",
                    getattr(_emb.author, "name", "") or "",
                    getattr(_emb.author, "url", "") or "",
                ]
                for _fld in (_emb.fields or []):
                    _check_texts.append(str(_fld.name) + " " + str(_fld.value))
                if any(INVITE_REGEX.search(t) for t in _check_texts):
                    invite_found = True
                    break
        if invite_found:
            try:
                await message.delete()
                await message.channel.send(
                    embed=em("<:icon_ban:1519358278356959284> Reklama zabranjena",
                             f"{message.author.mention} — invite linkovi nisu dozvoljeni ni u porukama ni u embedima!",
                             color=COLORS["error"]),
                    delete_after=8
                )
                await audit_log(message.guild, "<:icon_ban:1519358278356959284> Anti-Invite", f"{message.author.mention} pokušao reklamirati drugi server u {message.channel.mention}")
            except: pass
            return True

    if message.author.guild_permissions.administrator:
        return False

    # ── Upload filter: dozvoli samo slike/GIF-ove (.gif/.png/.jpg/.jpeg/.webp) ──
    # NAPOMENA: NSFW filter postoji odvojeno (check_nsfw) — radi ranije u on_message
    if message.attachments:
        for att in message.attachments:
            fname = (att.filename or "").lower()
            ext = "." + fname.rsplit(".", 1)[-1] if "." in fname else ""
            ctype = (att.content_type or "").lower()
            is_image = ext in ALLOWED_UPLOAD_EXTS or ctype.startswith("image/")
            if not is_image:
                try:
                    await message.delete()
                    await message.channel.send(
                        embed=em("<:e_link:1519363321458065408> Upload Zabranjen",
                                 f"{message.author.mention} — dozvoljene su **samo slike i GIF-ovi** (.gif, .png, .jpg, .jpeg, .webp).\n"
                                 f"<:icon_cross:1519358379917836508> Datoteka: `{att.filename}` blokirana.\n\n"
                                 f"<:e_idea:1519363006599794799> GIF-ovi preko Discord GIF picker-a (Tenor/GIPHY) rade normalno.",
                                 color=COLORS["error"]),
                        delete_after=10
                    )
                    await audit_log(message.guild, "<:e_link:1519363321458065408> Upload Block", f"{message.author.mention} pokušao uploadati `{att.filename}` u {message.channel.mention}")
                except: pass
                return True
    content_lower = message.content.lower()
    for word in BAD_WORDS:
        if word in content_lower:
            try:
                await message.delete()
                await message.channel.send(
                    embed=em("<:e_shield2:1519362627795554374>️ Auto-Mod", f"{message.author.mention} — zabranjene riječi!", color=COLORS["warning"]),
                    delete_after=5
                )
            except Exception:
                pass
            return True
    uid = message.author.id
    now = time.time()
    dq  = user_msg_times[uid]
    dq.append(now)
    while dq and dq[0] < now - SPAM_WINDOW:
        dq.popleft()
    if len(dq) >= SPAM_LIMIT:
        dq.clear()
        try:
            await message.author.timeout(timedelta(seconds=30), reason="Auto-Mod: Spam")
            await message.channel.send(
                embed=em("<:e_shield2:1519362627795554374>️ Anti-Spam", f"{message.author.mention} dobio/la timeout od **30s** zbog spama! <:e_mute2:1519362648972595289>", color=COLORS["warning"]),
                delete_after=8
            )
        except Exception:
            pass
    return False

# ═══════════════════════════════════════════
#    BLACKJACK
# ═══════════════════════════════════════════
_RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']
_VALS  = {'A':11,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10}
_SUITS = ['<:e_cards2:1519362702835712010>','<:e_heart2:1519362668644012133>','<:e_diamond2:1519362640961474601>','<:e_cards2:1519362702835712010>']

def _new_deck():
    d = [(r, s) for r in _RANKS for s in _SUITS]
    random.shuffle(d)
    return d

def _bj_val(hand):
    val  = sum(_VALS[r] for r, _ in hand)
    aces = sum(1 for r, _ in hand if r == 'A')
    while val > 21 and aces:
        val -= 10; aces -= 1
    return val

def _bj_str(hand, hide=False):
    if hide:
        return f"`{hand[0][0]}{hand[0][1]}`  `🂠`"
    return "  ".join(f"`{r}{s}`" for r, s in hand)

def _bj_embed(player, dealer, oklada, note="", hide=True):
    e = discord.Embed(title="<:e_cards2:1519362702835712010> Blackjack", description="<:e_diamond2:1519362640961474601>  **Pobijedi dilera — cilj je 21!**", color=COLORS["dark"], timestamp=datetime.now(timezone.utc))
    e.add_field(name=f"Tvoje karte  ({_bj_val(player)})", value=_bj_str(player),         inline=False)
    e.add_field(name=f"Dealer  {'(?)' if hide else f'({_bj_val(dealer)})'}", value=_bj_str(dealer, hide), inline=False)
    if note:
        e.add_field(name="Rezultat", value=note, inline=False)
    e.set_footer(text=f"Oklada: {oklada:,} <:e_coins3:1519362621206298666> • {BOT_NAME}")
    return e

class BjView(discord.ui.View):
    def __init__(self, deck, player, dealer, oklada, uid):
        super().__init__(timeout=30)
        self.deck = deck; self.player = player; self.dealer = dealer
        self.oklada = oklada; self.uid = uid

    async def _finish(self, i, note, delta, color):
        eco = get_economy(self.uid)
        eco["balance"] = max(0, eco["balance"] + delta)
        save_data()
        self.clear_items()
        e = _bj_embed(self.player, self.dealer, self.oklada, note, hide=False)
        e.color = color
        await i.response.edit_message(embed=e, view=self)

    @discord.ui.button(label="Hit", emoji="<:e_cards2:1519362702835712010>", style=discord.ButtonStyle.primary)
    async def hit(self, i: discord.Interaction, b):
        if i.user.id != self.uid:
            return await i.response.send_message("Ovo nije tvoja igra!", ephemeral=True)
        self.player.append(self.deck.pop())
        val = _bj_val(self.player)
        if val > 21:
            await self._finish(i, f"<:e_bomb:1519363456334168255> **BUST!** Izgubio/la si `{self.oklada:,} <:e_coins3:1519362621206298666>`", -self.oklada, COLORS["error"])
        elif val == 21:
            await self.stand.callback(self, i, b)
        else:
            await i.response.edit_message(embed=_bj_embed(self.player, self.dealer, self.oklada), view=self)

    @discord.ui.button(label="Stand", emoji="<:e_shake:1519362947766554737>", style=discord.ButtonStyle.secondary)
    async def stand(self, i: discord.Interaction, b):
        if i.user.id != self.uid:
            return await i.response.send_message("Ovo nije tvoja igra!", ephemeral=True)
        while _bj_val(self.dealer) < 17:
            self.dealer.append(self.deck.pop())
        pv, dv = _bj_val(self.player), _bj_val(self.dealer)
        if dv > 21 or pv > dv:
            await self._finish(i, f"<:e_trophy2:1519362624742232146> **Pobijedio/la si!** `+{self.oklada:,} <:e_coins3:1519362621206298666>`", self.oklada, COLORS["success"])
        elif pv == dv:
            await self._finish(i, "<:e_shake:1519362947766554737> **Nerješeno!** Oklada vraćena.", 0, COLORS["warning"])
        else:
            await self._finish(i, f"<:e_cry:1519362944717160530> **Dealer pobijedio!** `-{self.oklada:,} <:e_coins3:1519362621206298666>`", -self.oklada, COLORS["error"])

    async def on_timeout(self):
        self.clear_items()

@bot.tree.command(name="blackjack", description="<:e_cards2:1519362702835712010> Igraj Blackjack protiv dilera!")
@app_commands.describe(oklada="Koliko <:e_coins3:1519362621206298666> ulažeš (min 10)")
async def blackjack(i: discord.Interaction, oklada: int):
    eco = get_economy(i.user.id)
    if oklada < 10:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Minimum oklada je `10 <:e_coins3:1519362621206298666>`!", color=COLORS["error"]), ephemeral=True)
    if eco["balance"] < oklada:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", f"Nemaš dovoljno! Imaš `{eco['balance']:,} <:e_coins3:1519362621206298666>`.", color=COLORS["error"]), ephemeral=True)
    deck = _new_deck()
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]
    if _bj_val(player) == 21:
        won = int(oklada * 1.5)
        eco["balance"] += won
        save_data()
        e = _bj_embed(player, dealer, oklada, f"<:e_party:1519363028334674070> **BLACKJACK!** `+{won:,} <:e_coins3:1519362621206298666>`!", hide=False)
        e.color = COLORS["gold"]
        return await i.response.send_message(embed=e)
    view = BjView(deck, player, dealer, oklada, i.user.id)
    await i.response.send_message(embed=_bj_embed(player, dealer, oklada), view=view)

# ═══════════════════════════════════════════
#    TRIVIA / KVIZ
# ═══════════════════════════════════════════
TRIVIA_QS = [
    ("Koji grad je glavni grad Bosne i Hercegovine?", "Sarajevo", ["Mostar","Banja Luka","Tuzla"]),
    ("Koja rijeka teče kroz Beograd?", "Sava", ["Dunav","Drina","Morava"]),
    ("U kojoj godini je Hrvatska ušla u EU?", "2013.", ["2007.","2004.","2015."]),
    ("Ko je napisao 'Na Drini ćuprija'?", "Ivo Andrić", ["Meša Selimović","Branko Ćopić","Dobrica Ćosić"]),
    ("Koliko država je nastalo raspadom Jugoslavije?", "6", ["5","7","4"]),
    ("Koji je najveći grad u Srbiji?", "Beograd", ["Novi Sad","Niš","Kragujevac"]),
    ("Koja je najpopularnija hrana u BiH?", "Ćevapi", ["Sarma","Burek","Pita"]),
    ("Koliko Grand Slam titula ima Novak Đoković?", "24", ["20","22","21"]),
    ("Koji planinski vrh je najviši u Bosni?", "Maglić", ["Bjelašnica","Jahorina","Treskavica"]),
    ("Koji grad je poznat po Guča trubačkom festivalu?", "Guča", ["Niš","Beograd","Čačak"]),
    ("Što znači 'merhaba' na bosanskom?", "Zdravo", ["Hvala","Molim","Doviđenja"]),
    ("Koja je zastava Srbije?", "Crvena, plava, bijela", ["Zelena, bijela, crvena","Plava, žuta, crvena","Bijela, zelena, plava"]),
    ("Koji je broj igrača u ekipi fudbala?", "11", ["10","12","9"]),
    ("Koja zemlja je domaćin Eurosonga 2024?", "Švicarska", ["Švedska","Italija","Hrvatska"]),
    ("Ko je pjevao 'Dragana' na Balkanu?", "Ceca", ["Lepa Brena","Jelena Karleuša","Zorana"]),
    ("Koji je glavni grad Hrvatske?", "Zagreb", ["Split","Rijeka","Osijek"]),
    ("Koliko km² ima Srbija?", "77,474", ["88,000","65,000","92,000"]),
    ("Šta je 'kajmak'?", "Mlječni proizvod", ["Vrsta sira","Vrsta mesa","Vrsta hljeba"]),
    ("Koji je najstariji grad na Balkanu?", "Plovdiv", ["Beograd","Sarajevo","Skoplje"]),
    ("Ko je 'Kralj Balkana' u košarci?", "Novak Đoković", ["Nikola Jokić","Goran Dragić","Predrag Stojaković"]),
]

class TriviaView(discord.ui.View):
    def __init__(self, correct, wrong, oklada, uid, pool=None, title="<:e_brain:1519362849548406975> Balkan Trivia", combo=1, total_won=0):
        super().__init__(timeout=20)
        self.correct = correct; self.oklada = oklada; self.uid = uid
        self.pool = pool; self.title = title
        self.combo = combo; self.total_won = total_won
        opts = wrong[:3] + [correct]
        random.shuffle(opts)
        for opt in opts:
            btn = discord.ui.Button(label=opt[:80], style=discord.ButtonStyle.primary)
            btn.callback = self._make_cb(opt)
            self.add_item(btn)

    def _make_cb(self, choice):
        async def cb(i: discord.Interaction):
            if i.user.id != self.uid:
                return await i.response.send_message("Ovo nije tvoja igra!", ephemeral=True)
            self.clear_items()
            eco = get_economy(self.uid)
            if choice == self.correct:
                # combo multiplier — više tačnih = veća nagrada
                reward = int(self.oklada * self.combo)
                xp_gain = 25 * self.combo
                eco["balance"] += reward
                add_xp(self.uid, xp_gain); save_data()
                new_total = self.total_won + reward
                # nastavi sa novim pitanjem
                if self.pool:
                    q, c, w = random.choice(self.pool)
                    new_view = TriviaView(c, w, self.oklada, self.uid,
                                          pool=self.pool, title=self.title,
                                          combo=self.combo + 1, total_won=new_total)
                    combo_fx = E_FIRE1 if self.combo < 3 else (E_FIRE2 if self.combo < 6 else (E_FIRE3 if self.combo < 10 else E_FIRE4))
                    e = discord.Embed(
                        title=f"{E_GAME} {self.title}",
                        description=(
                            f"<:icon_check:1519358376268533810> **Tačno!** `+{reward:,} <:e_coins3:1519362621206298666>` `+{xp_gain} XP`\n"
                            f"{combo_fx} **Combo:** `x{self.combo}` → sljedeće `x{self.combo+1}`\n"
                            f"<:e_coins3:1519362621206298666> **Ukupno osvojeno:** `{new_total:,} <:e_coins3:1519362621206298666>`\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"**{q}**"
                        ),
                        color=GAME_COLORS["kviz"], timestamp=datetime.now(timezone.utc)
                    )
                    e.add_field(name="<:e_coins3:1519362621206298666> Oklada", value=f"`{self.oklada}`", inline=True)
                    e.add_field(name=f"{combo_fx} Combo", value=f"`x{self.combo+1}`", inline=True)
                    e.add_field(name="<:e_time2:1519362726952964227>️ Vrijeme", value="`20s`", inline=True)
                    e.set_footer(text=f"{BOT_NAME} • Nastavi nizom!")
                    return await i.response.edit_message(embed=e, view=new_view)
                # fallback bez pool-a
                result = em("<:icon_check:1519358376268533810> Tačno!", f"**{self.correct}**\n`+{reward} <:e_coins3:1519362621206298666>` i `+{xp_gain} XP`!", color=COLORS["success"])
            else:
                eco["balance"] = max(0, eco["balance"] - self.oklada)
                save_data()
                desc = f"Tačan odgovor: **{self.correct}**\n`-{self.oklada} <:e_coins3:1519362621206298666>`"
                if self.combo > 1:
                    desc += f"\n\n<:e_fire2:1519362671491678280> Combo prekinut na `x{self.combo}`!\n<:e_coins3:1519362621206298666> Osvojeno u nizu: `{self.total_won:,} <:e_coins3:1519362621206298666>`"
                result = em("<:icon_cross:1519358379917836508> Netačno!", desc, color=COLORS["error"])
            await i.response.edit_message(embed=result, view=self)
        return cb

    async def on_timeout(self):
        self.clear_items()

@bot.tree.command(name="kviz", description="<:e_brain:1519362849548406975> Odgovori na Balkan pitanje i osvoji pare!")
@app_commands.describe(oklada="Koliko <:e_coins3:1519362621206298666> ulažeš (default 50)")
async def kviz(i: discord.Interaction, oklada: int = 50):
    eco = get_economy(i.user.id)
    if oklada < 10:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Minimum je `10 <:e_coins3:1519362621206298666>`!", color=COLORS["error"]), ephemeral=True)
    if eco["balance"] < oklada:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", f"Nemaš dovoljno! Imaš `{eco['balance']:,} <:e_coins3:1519362621206298666>`.", color=COLORS["error"]), ephemeral=True)
    question, correct, wrong = random.choice(TRIVIA_QS)
    view = TriviaView(correct, wrong, oklada, i.user.id, pool=TRIVIA_QS, title="<:e_brain:1519362849548406975> Balkan Trivia")
    e = em_pro(
        f"{E_GAME} Balkan Trivia",
        f"<:icon_help:1519358364889383084>  **{question}**",
        color=GAME_COLORS["kviz"],
        author=i.user,
        fields=[
            ("<:e_coins3:1519362621206298666> Oklada",        f"`{oklada:,} <:e_coins3:1519362621206298666>`", True),
            (f"{E_FIRE2} Combo", "`x1`",            True),
            ("<:e_time2:1519362726952964227>️ Vrijeme",       "`20 sekundi`",     True),
        ],
        footer=f"{BOT_NAME} • Biraj pažljivo — combo raste sa svakim tačnim!"
    )
    await i.response.send_message(embed=e, view=view)

# ═══════════════════════════════════════════
#    GEOGRAFIJA
# ═══════════════════════════════════════════
GEOGRAFIJA_QS = [
    # ── Balkan ──
    ("🇷🇸 Glavni grad Srbije?", "Beograd", ["Novi Sad", "Niš", "Kragujevac"]),
    ("🇭🇷 Glavni grad Hrvatske?", "Zagreb", ["Split", "Rijeka", "Osijek"]),
    ("🇧🇦 Glavni grad Bosne i Hercegovine?", "Sarajevo", ["Mostar", "Banja Luka", "Tuzla"]),
    ("<:e_globe2:1519362694887637004>🇪 Glavni grad Crne Gore?", "Podgorica", ["Cetinje", "Nikšić", "Budva"]),
    ("<:e_globe2:1519362694887637004>🇰 Glavni grad Sjeverne Makedonije?", "Skoplje", ["Bitola", "Ohrid", "Tetovo"]),
    ("🇸🇮 Glavni grad Slovenije?", "Ljubljana", ["Maribor", "Celje", "Koper"]),
    ("🇦<:e_globe2:1519362694887637004> Glavni grad Albanije?", "Tirana", ["Drač", "Skadar", "Vlora"]),
    ("🇧🇬 Glavni grad Bugarske?", "Sofija", ["Plovdiv", "Varna", "Burgas"]),
    ("🇬🇷 Glavni grad Grčke?", "Atina", ["Solun", "Patras", "Pirej"]),
    ("🇷🇴 Glavni grad Rumunije?", "Bukurešt", ["Kluž", "Brašov", "Temišvar"]),
    ("🇽🇰 Glavni grad Kosova?", "Priština", ["Prizren", "Peć", "Đakovica"]),
    ("Najduža rijeka kroz Srbiju?", "Dunav", ["Sava", "Morava", "Drina"]),
    ("Najviši vrh na Balkanu?", "Musala", ["Triglav", "Olimp", "Đeravica"]),
    ("U kojoj državi se nalazi Plitvička jezera?", "Hrvatska", ["BiH", "Slovenija", "Crna Gora"]),
    ("Koje more okružuje Crnu Goru?", "Jadransko", ["Egejsko", "Crno", "Sredozemno"]),
    ("Najveći grad u Bosni i Hercegovini?", "Sarajevo", ["Banja Luka", "Tuzla", "Mostar"]),
    ("Rijeka koja teče kroz Mostar?", "Neretva", ["Bosna", "Vrbas", "Una"]),
    ("Koja rijeka razdvaja Srbiju i Rumuniju?", "Dunav", ["Tisa", "Sava", "Drina"]),
    ("Najveće jezero na Balkanu?", "Skadarsko", ["Ohridsko", "Prespansko", "Plavsko"]),
    # ── Svijet ──
    ("Glavni grad Francuske?", "Pariz", ["Lion", "Marseilles", "Nica"]),
    ("Glavni grad Njemačke?", "Berlin", ["Minhen", "Hamburg", "Frankfurt"]),
    ("Glavni grad Italije?", "Rim", ["Milano", "Napulj", "Venecija"]),
    ("Glavni grad Španije?", "Madrid", ["Barcelona", "Sevilja", "Valensija"]),
    ("Glavni grad Engleske?", "London", ["Liverpul", "Mančester", "Oksford"]),
    ("Glavni grad SAD-a?", "Washington", ["New York", "Los Angeles", "Chicago"]),
    ("Glavni grad Rusije?", "Moskva", ["Sankt Peterburg", "Kazan", "Soči"]),
    ("Glavni grad Japana?", "Tokio", ["Kjoto", "Osaka", "Hirošima"]),
    ("Glavni grad Kine?", "Peking", ["Šangaj", "Hong Kong", "Guangžou"]),
    ("Glavni grad Australije?", "Canberra", ["Sydney", "Melbourne", "Perth"]),
    ("Glavni grad Brazila?", "Brasilia", ["Rio de Janeiro", "São Paulo", "Salvador"]),
    ("Glavni grad Argentine?", "Buenos Aires", ["Kordoba", "Rosario", "Mendoza"]),
    ("Glavni grad Egipta?", "Kairo", ["Aleksandrija", "Luksor", "Giza"]),
    ("Glavni grad Turske?", "Ankara", ["Istanbul", "Izmir", "Antalija"]),
    ("Najduža rijeka na svijetu?", "Nil", ["Amazon", "Misisipi", "Jangcekjang"]),
    ("Najviši vrh na svijetu?", "Mount Everest", ["K2", "Kangčendžunga", "Lhotse"]),
    ("Najveći okean?", "Tihi", ["Atlantski", "Indijski", "Arktički"]),
    ("Najveće jezero na svijetu?", "Kaspijsko", ["Bajkalsko", "Gornje", "Viktorijino"]),
    ("Najveći kontinent po površini?", "Azija", ["Afrika", "Sjeverna Amerika", "Evropa"]),
    ("Najveća pustinja na svijetu?", "Sahara", ["Gobi", "Kalahari", "Atakama"]),
    ("U kojoj zemlji je Eiffelov toranj?", "Francuska", ["Italija", "Njemačka", "Belgija"]),
    ("U kojoj zemlji je Coloseum?", "Italija", ["Grčka", "Španija", "Francuska"]),
    ("U kojoj zemlji se nalazi Statua slobode?", "SAD", ["Francuska", "Kanada", "Meksiko"]),
    ("Koja zemlja ima najviše stanovnika?", "Indija", ["Kina", "SAD", "Indonezija"]),
    ("Koliko kontinenata postoji?", "7", ["5", "6", "8"]),
    ("U kojem oceanu se nalaze Maldivi?", "Indijski", ["Tihi", "Atlantski", "Arktički"]),
    ("Glavni grad Holandije?", "Amsterdam", ["Hag", "Roterdam", "Utreht"]),
    ("Glavni grad Švicarske?", "Bern", ["Zurih", "Ženeva", "Bazel"]),
    ("Glavni grad Norveške?", "Oslo", ["Bergen", "Trondheim", "Stavanger"]),
    ("Glavni grad Švedske?", "Stockholm", ["Geteborg", "Malme", "Upsala"]),
    ("Glavni grad Finske?", "Helsinki", ["Tampere", "Turku", "Espoo"]),
]

@bot.tree.command(name="geografija", description="<:e_globe2:1519362694887637004> Geografski kviz — pogodi i osvoji pare!")
@app_commands.describe(oklada="Koliko <:e_coins3:1519362621206298666> ulažeš (default 50)")
async def geografija(i: discord.Interaction, oklada: int = 50):
    eco = get_economy(i.user.id)
    if oklada < 10:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Minimum je `10 <:e_coins3:1519362621206298666>`!", color=COLORS["error"]), ephemeral=True)
    if eco["balance"] < oklada:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", f"Nemaš dovoljno! Imaš `{eco['balance']:,} <:e_coins3:1519362621206298666>`.", color=COLORS["error"]), ephemeral=True)
    question, correct, wrong = random.choice(GEOGRAFIJA_QS)
    view = TriviaView(correct, wrong, oklada, i.user.id, pool=GEOGRAFIJA_QS, title="<:e_globe2:1519362694887637004> Geografija")
    e = discord.Embed(title="<:e_globe2:1519362694887637004> Geografija", description=f"<:e_globe2:1519362694887637004>  **{question}**", color=COLORS["info"], timestamp=datetime.now(timezone.utc))
    e.add_field(name="<:e_coins3:1519362621206298666> Oklada", value=f"`{oklada}`", inline=True)
    e.add_field(name="<:e_time2:1519362726952964227>️ Vrijeme", value="`20 sekundi`", inline=True)
    e.set_footer(text=f"{BOT_NAME} • Putuj svijetom!")
    await i.response.send_message(embed=e, view=view)

# ═══════════════════════════════════════════
#    KOCKA (DICE)
# ═══════════════════════════════════════════
_DICE_FACES = {1:"<:e_dice2:1519362633763913931>",2:"<:e_dice2:1519362633763913931>",3:"<:e_dice2:1519362633763913931>",4:"<:e_dice2:1519362633763913931>",5:"<:e_dice2:1519362633763913931>",6:"<:e_dice2:1519362633763913931>"}

# /kocka uklonjeno (na zahtjev)

# ═══════════════════════════════════════════
#    SHOP + KUPI
# ═══════════════════════════════════════════
SHOP_ITEMS = {
    "lucky_hunter": {"name": "<:e_clover:1519363694549667881> Srećni Lovac", "desc":"2× šansa za lov na životinju (1h)",  "price":800,  "duration":3600},
    "xp_boost":     {"name": "<:e_bolt:1519362674717102160> XP Boost",      "desc":"2× XP od poruka (1h)",               "price":1000, "duration":3600},
    "shield":       {"name": "<:e_shield2:1519362627795554374>️ Štit",         "desc":"Zaštita od krađe (24h)",             "price":600,  "duration":86400},
    "double_steal": {"name": "<:e_bomb:1519363456334168255> Bomba",         "desc":"Sljedeća krađa donosi duplo",        "price":400,  "duration":None},
    "daily_boost":  {"name": "<:e_cal:1519362659676455046> Daily Boost",   "desc":"+500 <:e_coins3:1519362621206298666> bonusa na sljedeći /daily",  "price":350,  "duration":None},
}

def get_items(uid):
    eco = get_economy(uid)
    eco.setdefault("items", {})
    return eco["items"]

def has_item(uid, key):
    items = get_items(uid)
    if key not in items:
        return False
    item = SHOP_ITEMS.get(key, {})
    if item.get("duration"):
        if time.time() > items[key]:
            del items[key]; return False
        return True
    return bool(items.get(key))

@bot.tree.command(name="shop", description="<:e_cart:1519362665347153930> Pogledaj šta možeš kupiti")
async def shop(i: discord.Interaction):
    e = discord.Embed(title="<:e_cart:1519362665347153930> GIAN Shop", description="Kupi predmete sa `/kupi <id>` komandom:", color=COLORS["purple"], timestamp=datetime.now(timezone.utc))
    for key, item in SHOP_ITEMS.items():
        dur = "Jednom" if not item["duration"] else f"{item['duration']//3600}h" if item["duration"] >= 3600 else f"{item['duration']//60}min"
        e.add_field(name=item["name"], value=f"**ID:** `{key}`\n{item['desc']}\n<:e_time2:1519362726952964227> `{dur}` • <:e_coins3:1519362621206298666> `{item['price']:,}`", inline=True)
    e.set_footer(text=f"{BOT_NAME} • /kupi <id> za kupovinu")
    await i.response.send_message(embed=e)

@bot.tree.command(name="kupi", description="<:e_bank2:1519362662515871744> Kupi predmet iz shopa")
@app_commands.describe(predmet="ID predmeta iz /shop")
async def kupi(i: discord.Interaction, predmet: str):
    if predmet not in SHOP_ITEMS:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Nepoznat predmet! Provjeri `/shop` za listu.", color=COLORS["error"]), ephemeral=True)
    item = SHOP_ITEMS[predmet]
    eco  = get_economy(i.user.id)
    if eco["balance"] < item["price"]:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", f"Nemaš dovoljno! Trebaš `{item['price']:,} <:e_coins3:1519362621206298666>`.", color=COLORS["error"]), ephemeral=True)
    eco["balance"] -= item["price"]
    items = get_items(i.user.id)
    items[predmet] = (time.time() + item["duration"]) if item["duration"] else True
    save_data()
    await i.response.send_message(embed=em_pro(
        f"<:icon_check:1519358376268533810> Kupovina Uspješna",
        f"<:e_gift:1519362618341462067> Nabavio si **{item['name']}**!\n*{item['desc']}*",
        color=COLORS["success"], author=i.user, thumb=i.user.display_avatar.url, fields=[
            ("<:e_moneywing:1519362955437805771> Cijena", f"```diff\n- {item['price']:,} <:e_coins3:1519362621206298666>\n```", True),
            ("<:e_bank2:1519362662515871744> Balans", f"```yaml\n{eco['balance']:,} <:e_coins3:1519362621206298666>\n```", True),
        ]
    ))

# ═══════════════════════════════════════════
#    QUESTS / DNEVNI ZADACI
# ═══════════════════════════════════════════
QUEST_POOL = [
    {"id":"hunt5",   "name": "<:e_arrow:1519363399845154958> Lovac",      "desc":"Ulovi 5 životinja",           "target":5,  "reward":200},
    {"id":"work3",   "name": "<:e_job:1519362615069904977> Radnik",      "desc":"Radi posao 3 puta",           "target":3,  "reward":300},
    {"id":"msgs20",  "name": "<:e_bubble:1519363307998417148> Pričalo",     "desc":"Pošalji 20 poruka",           "target":20, "reward":150},
    {"id":"bj_win",  "name": "<:e_cards2:1519362702835712010> Kockar",      "desc":"Pobijedi u Blackjacku",       "target":1,  "reward":500},
    {"id":"kviz3",   "name": "<:e_brain:1519362849548406975> Znalac",      "desc":"Tačno odgovori na 3 kviz pitanja","target":3,"reward":400},
    {"id":"hunt10",  "name": "🎯 Pro Lovac",   "desc":"Ulovi 10 životinja",          "target":10, "reward":500},
    {"id":"daily1",  "name": "<:e_cal:1519362659676455046> Redovan",     "desc":"Uzmi /daily nagradu",         "target":1,  "reward":250},
]

def get_quests(uid):
    key   = str(uid)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data["quests"].setdefault(key, {})
    if data["quests"][key].get("date") != today:
        chosen = random.sample(QUEST_POOL, 3)
        data["quests"][key] = {
            "date":     today,
            "assigned": [q["id"] for q in chosen],
            "progress": {q["id"]: 0 for q in chosen},
            "done":     {q["id"]: False for q in chosen},
        }
    return data["quests"][key]

def quest_progress(uid, quest_id, amount=1):
    qd = get_quests(uid)
    if quest_id not in qd["progress"] or qd["done"].get(quest_id):
        return None
    qd["progress"][quest_id] += amount
    quest = next((q for q in QUEST_POOL if q["id"] == quest_id), None)
    if quest and qd["progress"][quest_id] >= quest["target"]:
        qd["done"][quest_id] = True
        get_economy(uid)["balance"] += quest["reward"]
        save_data()
        return quest
    save_data()
    return None

@bot.tree.command(name="quests", description="<:e_clipboard:1519363052871614627> Pogledaj svoje dnevne zadatke")
async def quests_cmd(i: discord.Interaction):
    qd    = get_quests(i.user.id)
    save_data()
    lines = []
    for qid in qd["assigned"]:
        quest = next(q for q in QUEST_POOL if q["id"] == qid)
        prog  = qd["progress"].get(qid, 0)
        done  = qd["done"].get(qid, False)
        check = "<:icon_check:1519358376268533810>" if done else "<:e_check2:1519362730057007268>"
        fill  = min(prog, quest["target"])
        bar   = f"`{'█' * fill}{'░' * (quest['target'] - fill)}`"
        lines.append(f"{check} **{quest['name']}** — {quest['desc']}\n{bar} `{prog}/{quest['target']}` • <:e_coins3:1519362621206298666> `+{quest['reward']}`")
    done_count = sum(1 for qid in qd["assigned"] if qd["done"].get(qid))
    e = discord.Embed(
        title="<:e_clipboard:1519363052871614627> Dnevni Zadaci",
        description="\n\n".join(lines),
        color=COLORS["info"], timestamp=datetime.now(timezone.utc)
    )
    e.add_field(name="<:icon_check:1519358376268533810> Završeno", value=f"`{done_count}/3`", inline=True)
    e.set_footer(text=f"Resetuju se u ponoć UTC • {BOT_NAME}")
    await i.response.send_message(embed=e)

# ═══════════════════════════════════════════
#    GIVEAWAY
# ═══════════════════════════════════════════
active_giveaways: dict = {}

def _save_giveaway(msg_id, ga):
    """Persistira giveaway u data fajl (preživljava restart)."""
    data.setdefault("active_giveaways", {})[str(msg_id)] = {
        "entrants": list(ga["entrants"]),
        "prize": ga["prize"],
        "channel_id": ga["channel_id"],
        "msg_id": ga["msg_id"],
        "end_at": ga.get("end_at"),
        "guild_id": ga.get("guild_id"),
    }
    save_data()

def _remove_giveaway(msg_id):
    data.get("active_giveaways", {}).pop(str(msg_id), None)
    save_data()

class GiveawayView(discord.ui.View):
    def __init__(self, msg_id=None):
        super().__init__(timeout=None)
        self.msg_id = msg_id

    @discord.ui.button(label="Učestvuj", emoji="<:e_party:1519363028334674070>", style=discord.ButtonStyle.success, custom_id="ga_enter")
    async def enter(self, i: discord.Interaction, b):
        # Pronađi giveaway preko msg_id (interaction message ako self.msg_id None)
        mid = self.msg_id or i.message.id
        ga = active_giveaways.get(mid)
        if not ga:
            return await i.response.send_message("Nagradna igra je završena!", ephemeral=True)
        if i.user.id in ga["entrants"]:
            ga["entrants"].discard(i.user.id)
            await i.response.send_message("Odjavljen/a si sa nagradne igre.", ephemeral=True)
        else:
            ga["entrants"].add(i.user.id)
            await i.response.send_message("<:icon_check:1519358376268533810> Prijavljen/a si! Sretno! <:e_clover:1519363694549667881>", ephemeral=True)
        _save_giveaway(mid, ga)
        try:
            msg = await i.channel.fetch_message(mid)
            e   = msg.embeds[0]
            e.set_field_at(1, name="<:e_users:1519363096601301120> Učesnici", value=f"`{len(ga['entrants'])}`", inline=True)
            await msg.edit(embed=e)
        except Exception:
            pass

giveaway_group = app_commands.Group(name="giveaway", description="<:e_party:1519363028334674070> Nagradne igre")

def _gw_fmt_duration(minuta: int) -> str:
    """Pretvori minute u 'Xh Ymin' string."""
    if minuta <= 0: return "0min"
    h, m = divmod(int(minuta), 60)
    if h and m: return f"{h}h {m}min"
    if h:       return f"{h}h"
    return f"{m}min"

async def _gw_timer(msg_id: int, channel: discord.TextChannel, seconds: float):
    """Pozadinski timer — preživljava jer je odvojen od interaction context-a."""
    try:
        await asyncio.sleep(max(1.0, seconds))
        await _end_giveaway(msg_id, channel)
    except asyncio.CancelledError:
        pass
    except Exception as ex:
        print(f"[giveaway timer] msg={msg_id} error: {ex}")

@giveaway_group.command(name="start", description="<:e_party:1519363028334674070> Pokreni nagradnu igru")
@app_commands.describe(nagrada="Šta se osvaja", minuta="Koliko minuta traje (npr. 60 = 1h, 120 = 2h)", kanal="Kanal (default ovaj)")
@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.has_permissions(manage_guild=True)
async def giveaway_start(i: discord.Interaction, nagrada: str, minuta: int = 60, kanal: discord.TextChannel = None):
    if minuta < 1:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508>", "Minimalno trajanje je **1 minut**.", color=COLORS["error"]), ephemeral=True)
    if minuta > 60 * 24 * 14:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508>", "Maksimalno trajanje je **14 dana** (20160 minuta).", color=COLORS["error"]), ephemeral=True)
    chan = kanal or i.channel
    end  = datetime.now(timezone.utc) + timedelta(minutes=minuta)
    end_ts = int(end.timestamp())
    duration_txt = _gw_fmt_duration(minuta)
    e = discord.Embed(
        title="<:e_party:1519363028334674070> NAGRADNA IGRA!",
        description=f"## <:e_trophy2:1519362624742232146>  {nagrada}\n\nKlikni dugme **<:e_party:1519363028334674070> Učestvuj** da se prijaviš!",
        color=COLORS["gold"], timestamp=end
    )
    e.add_field(name="<:e_time2:1519362726952964227> Trajanje",  value=f"`{duration_txt}` ({minuta} min)",       inline=True)
    e.add_field(name="<:e_users:1519363096601301120> Učesnici",  value="`0`",                                    inline=True)
    e.add_field(name="<:e_ticket3:1519362637534597221>️ Domaćin",   value=i.user.mention,                           inline=True)
    e.add_field(name="<:e_cal:1519362659676455046> Završava",  value=f"<t:{end_ts}:F>\n<:e_time2:1519362726952964227> <t:{end_ts}:R>",     inline=False)
    e.set_footer(text=f"Završava se automatski • {BOT_NAME}")
    await i.response.send_message(
        embed=em("<:icon_check:1519358376268533810> Pokrenuto!",
                 f"Nagradna igra **{nagrada}** poslata u {chan.mention}.\n<:e_time2:1519362726952964227> Trajanje: **{duration_txt}**\n<:e_cal:1519362659676455046> Kraj: <t:{end_ts}:F>",
                 color=COLORS["success"]),
        ephemeral=True
    )
    msg = await chan.send(embed=e)
    ga  = {
        "entrants": set(), "prize": nagrada, "channel_id": chan.id,
        "msg_id": msg.id, "end_at": end.timestamp(), "guild_id": chan.guild.id,
    }
    active_giveaways[msg.id] = ga
    _save_giveaway(msg.id, ga)
    await msg.edit(view=GiveawayView(msg.id))
    # Timer u POZADINI — interaction se zatvara odmah, giveaway nastavlja
    asyncio.create_task(_gw_timer(msg.id, chan, minuta * 60))

@giveaway_group.command(name="end", description="🎯 Završi nagradnu igru odmah")
@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.has_permissions(manage_guild=True)
async def giveaway_end(i: discord.Interaction):
    for mid, ga in list(active_giveaways.items()):
        if ga["channel_id"] == i.channel_id:
            await i.response.send_message("Završavam nagradnu igru...", ephemeral=True)
            await _end_giveaway(mid, i.channel)
            return
    await i.response.send_message("Nema aktivnih nagradnih igara u ovom kanalu!", ephemeral=True)

async def _end_giveaway(msg_id, channel):
    ga = active_giveaways.pop(msg_id, None)
    _remove_giveaway(msg_id)
    if not ga: return
    try: msg = await channel.fetch_message(msg_id)
    except: return
    if not ga["entrants"]:
        e = discord.Embed(title="<:e_party:1519363028334674070> Nagradna igra završena", description="Niko se nije prijavio! <:e_cry:1519362944717160530>", color=COLORS["error"])
        await msg.edit(embed=e, view=None); return
    winner_id = random.choice(list(ga["entrants"]))
    winner    = channel.guild.get_member(winner_id)
    e = discord.Embed(
        title="<:e_party:1519363028334674070> Nagradna igra ZAVRŠENA!",
        description=f"## <:e_trophy2:1519362624742232146> {ga['prize']}\n\n<:e_party:1519363028334674070> Pobjednik: **{winner.mention if winner else f'<@{winner_id}>'}**!",
        color=COLORS["gold"], timestamp=datetime.now(timezone.utc)
    )
    e.add_field(name="<:e_users:1519363096601301120> Učesnici", value=f"`{len(ga['entrants'])}`", inline=True)
    e.set_footer(text=f"{BOT_NAME} • Čestitamo!")
    await msg.edit(embed=e, view=None)
    await channel.send(f"<:e_confetti2:1519363348288901221> Čestitamo {winner.mention if winner else f'<@{winner_id}>'}! Pobijedio/la si **{ga['prize']}**! <:e_trophy2:1519362624742232146>")

bot.tree.add_command(giveaway_group)

# ═══════════════════════════════════════════
#    <:e_refresh:1519362959187509461> RESET GIVEAWAY (5 min)
# ═══════════════════════════════════════════
async def _reset_gw_worker(chan: discord.TextChannel, host: discord.Member, nagrada: str):
    """Pozadinski radnik — sačeka 5 min, pa pokrene giveaway na 60min."""
    try:
        await asyncio.sleep(300)
        end    = datetime.now(timezone.utc) + timedelta(minutes=60)
        end_ts = int(end.timestamp())
        ga_e = discord.Embed(
            title="<:e_party:1519363028334674070> NAGRADNA IGRA!",
            description=f"## <:e_trophy2:1519362624742232146>  {nagrada}\n\nKlikni dugme **<:e_party:1519363028334674070> Učestvuj** da se prijaviš!",
            color=COLORS["gold"], timestamp=end
        )
        ga_e.add_field(name="<:e_time2:1519362726952964227> Trajanje",  value="`1h` (60 min)",               inline=True)
        ga_e.add_field(name="<:e_users:1519363096601301120> Učesnici", value="`0`",                          inline=True)
        ga_e.add_field(name="<:e_ticket3:1519362637534597221>️ Domaćin", value=host.mention,                   inline=True)
        ga_e.add_field(name="<:e_cal:1519362659676455046> Završava", value=f"<t:{end_ts}:F>\n<:e_time2:1519362726952964227> <t:{end_ts}:R>", inline=False)
        ga_e.set_footer(text=f"Završava se automatski • {BOT_NAME}")
        msg = await chan.send(embed=ga_e)
        ga = {"entrants": set(), "prize": nagrada, "channel_id": chan.id,
              "msg_id": msg.id, "end_at": end.timestamp(), "guild_id": chan.guild.id}
        active_giveaways[msg.id] = ga
        _save_giveaway(msg.id, ga)
        await msg.edit(view=GiveawayView(msg.id))
        asyncio.create_task(_gw_timer(msg.id, chan, 60 * 60))
    except Exception as ex:
        print(f"[reset_gw worker] error: {ex}")

@bot.tree.command(name="reset-gw", description="<:e_refresh:1519362959187509461> [ADMIN] Resetuj i ponovo pokreni giveaway za 5 minuta")
@app_commands.describe(nagrada="Nagrada za novi giveaway", kanal="Kanal (default ovaj)")
@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.has_permissions(manage_guild=True)
async def reset_gw_cmd(i: discord.Interaction, nagrada: str, kanal: discord.TextChannel = None):
    chan = kanal or i.channel
    for mid, ga in list(active_giveaways.items()):
        if ga["channel_id"] == chan.id:
            active_giveaways.pop(mid, None)
            _remove_giveaway(mid)
    start_ts = int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp())
    sep = "═══════════════════════════"
    countdown_e = discord.Embed(
        title="<:e_refresh:1519362959187509461> ɢɪᴠᴇᴀᴡᴀʏ ʀᴇꜱᴇᴛ!",
        description=(
            f"```ansi\n\u001b[1;36m{sep}\u001b[0m\n```"
            f"<:e_time2:1519362726952964227> **Novi giveaway počinje za 5 minuta!** (<t:{start_ts}:R>)\n\n"
            f"```yaml\n"
            f"Nagrada  : {nagrada}\n"
            f"Trajanje : 1h (60 min)\n"
            f"Kanal    : #{chan.name}\n"
            f"Pokrece  : {i.user.display_name}\n"
            f"Pocinje  : za 5 min\n"
            f"```"
        ),
        color=COLORS["aqua"], timestamp=datetime.now(timezone.utc)
    )
    countdown_e.set_footer(text=f"<:e_party:1519363028334674070> {BOT_NAME} • Giveaway Reset")
    await i.response.send_message(embed=countdown_e)
    asyncio.create_task(_reset_gw_worker(chan, i.user, nagrada))

# ═══════════════════════════════════════════
#    <:e_coins3:1519362621206298666> OWNER-ONLY: DODAJ / ODUZMI NOVAC
# ═══════════════════════════════════════════
@bot.tree.command(name="novac", description="<:e_coins3:1519362621206298666> [OWNER] Dodaj ili oduzmi coina korisniku")
@app_commands.describe(akcija="dodaj ili oduzmi", korisnik="Kome mijenjamo balans", iznos="Koliko coina")
async def novac_cmd(i: discord.Interaction, akcija: str, korisnik: discord.Member, iznos: int):
    if i.user.id not in OWNER_IDS:
        return await i.response.send_message(
            embed=em("<:e_no:1519363018725658675> Zabranjen pristup!", "Ova komanda je samo za **Vlasnika** bota.", color=COLORS["error"]),
            ephemeral=True
        )
    akcija_norm = akcija.lower().strip()
    if akcija_norm not in ("dodaj", "oduzmi", "add", "remove"):
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Greška", "Akcija mora biti `dodaj` ili `oduzmi`.\nPrimjer: `/novac dodaj @korisnik 500`", color=COLORS["error"]),
            ephemeral=True
        )
    if iznos <= 0:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Iznos mora biti pozitivan!", color=COLORS["error"]), ephemeral=True)
    eco = get_economy(korisnik.id)
    if akcija_norm in ("dodaj", "add"):
        eco["balance"] += iznos
        save_data()
        await i.response.send_message(embed=discord.Embed(
            title="<:e_coins3:1519362621206298666> ᴅᴏᴅᴀɴᴏ ᴄᴏɪɴᴀ!",
            description=(
                f"```yaml\n"
                f"Korisnik : {korisnik.display_name}\n"
                f"Dodano   : +{iznos:,} coina\n"
                f"Novi bal : {eco['balance']:,} coina\n"
                f"Vlasnik  : {i.user.display_name}\n"
                f"```"
            ),
            color=COLORS["aqua"], timestamp=datetime.now(timezone.utc)
        ).set_footer(text=f"<:e_coins3:1519362621206298666> {BOT_NAME} • Owner Komanda"), ephemeral=True)
    else:
        eco["balance"] = max(0, eco["balance"] - iznos)
        save_data()
        await i.response.send_message(embed=discord.Embed(
            title="<:e_moneywing:1519362955437805771> ᴏᴅᴜᴢᴇᴛᴏ ᴄᴏɪɴᴀ!",
            description=(
                f"```yaml\n"
                f"Korisnik : {korisnik.display_name}\n"
                f"Oduzeto  : -{iznos:,} coina\n"
                f"Novi bal : {eco['balance']:,} coina\n"
                f"Vlasnik  : {i.user.display_name}\n"
                f"```"
            ),
            color=COLORS["warning"], timestamp=datetime.now(timezone.utc)
        ).set_footer(text=f"<:e_moneywing:1519362955437805771> {BOT_NAME} • Owner Komanda"), ephemeral=True)

# ═══════════════════════════════════════════
#    POLL / GLASANJE
# ═══════════════════════════════════════════
@bot.tree.command(name="poll", description="<:e_chart:1519362656568475880> Napravi glasanje sa reakcijama")
@app_commands.describe(pitanje="Pitanje", opcija1="1. opcija", opcija2="2. opcija", opcija3="3. opcija (opcionalno)", opcija4="4. opcija (opcionalno)")
async def poll(i: discord.Interaction, pitanje: str, opcija1: str, opcija2: str, opcija3: str = None, opcija4: str = None):
    opts   = [o for o in [opcija1, opcija2, opcija3, opcija4] if o]
    emojis = ["1️⃣","2️⃣","3️⃣","4️⃣"]
    desc   = "\n".join(f"{emojis[idx]}  **{opt}**" for idx, opt in enumerate(opts))
    e = discord.Embed(title=f"<:e_chart:1519362656568475880> {pitanje}", description=desc, color=COLORS["info"], timestamp=datetime.now(timezone.utc))
    e.set_footer(text=f"Glasaj sa emoji reakcijama • {BOT_NAME}")
    e.set_author(name=i.user.display_name, icon_url=i.user.display_avatar.url)
    await i.response.send_message(embed=e)
    msg = await i.original_response()
    for idx in range(len(opts)):
        await msg.add_reaction(emojis[idx])

# ═══════════════════════════════════════════
#    TICKET SISTEM
# ═══════════════════════════════════════════
class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zatvori Ticket", emoji="<:e_lock3:1519362717394403432>", style=discord.ButtonStyle.danger, custom_id="ticket_close")
    async def close(self, i: discord.Interaction, b):
        await i.response.send_message("<:e_lock3:1519362717394403432> Ticket se zatvara za 5 sekundi...", ephemeral=False)
        await asyncio.sleep(5)
        try:
            await i.channel.delete(reason=f"Ticket zatvorio {i.user}")
        except discord.Forbidden:
            await i.channel.send("<:icon_cross:1519358379917836508> Nemam permisiju da obrišem kanal. Obriši ručno.")
        except Exception:
            pass

class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Otvori Ticket", emoji="<:e_ticket3:1519362637534597221>", style=discord.ButtonStyle.primary, custom_id="ticket_open")
    async def open_ticket(self, i: discord.Interaction, b):
        await i.response.defer(ephemeral=True)
        guild    = i.guild
        safe_name = "".join(c for c in i.user.name.lower() if c.isalnum() or c in "-_")[:20] or str(i.user.id)
        existing  = discord.utils.get(guild.text_channels, name=f"ticket-{safe_name}")
        if existing:
            return await i.followup.send(f"Već imaš otvoren ticket: {existing.mention}", ephemeral=True)

        # Check bot has Manage Channels
        if not guild.me.guild_permissions.manage_channels:
            return await i.followup.send("<:icon_cross:1519358379917836508> Bot nema **Manage Channels** permisiju. Daj mu je u Server Settings!", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            i.user:             discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }
        for role in guild.roles:
            if role.permissions.administrator:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        try:
            # Try to put tickets in a "tickets" category if it exists
            category = discord.utils.get(guild.categories, name="Tickets") or \
                       discord.utils.get(guild.categories, name="tickets")
            chan = await guild.create_text_channel(
                f"ticket-{safe_name}",
                overwrites=overwrites,
                category=category,
                reason=f"Ticket od {i.user}",
                topic=f"Ticket od {i.user} ({i.user.id})"
            )
        except discord.Forbidden:
            return await i.followup.send("<:icon_cross:1519358379917836508> Bot nema permisiju da kreira kanale! Dodaj **Manage Channels** u server settings.", ephemeral=True)
        except Exception as ex:
            return await i.followup.send(f"<:icon_cross:1519358379917836508> Greška: `{ex}`", ephemeral=True)

        e = discord.Embed(
            title="<:e_ticket3:1519362637534597221> Ticket Otvoren",
            description=(
                f"Zdravo {i.user.mention}! <:e_shake:1519362947766554737>\n\n"
                f"Opiši problem ili pitanje i tim će ti odgovoriti uskoro. <:e_pray:1519363406078021863>\n\n"
                f"Kad završiš, klikni **Zatvori Ticket** ispod."
            ),
            color=COLORS["info"], timestamp=datetime.now(timezone.utc)
        )
        e.set_thumbnail(url=i.user.display_avatar.url)
        e.set_footer(text=f"{BOT_NAME} • Ticket Sistem")
        await chan.send(content=i.user.mention, embed=e, view=TicketCloseView())
        await i.followup.send(f"<:icon_check:1519358376268533810> Ticket otvoren: {chan.mention}", ephemeral=True)

@bot.tree.command(name="ticket-setup", description="<:e_ticket3:1519362637534597221> Postavi ticket sistem u ovaj kanal")
@app_commands.default_permissions(manage_channels=True)
@app_commands.checks.has_permissions(administrator=True)
async def ticket_setup(i: discord.Interaction):
    # Respond FIRST, then send the panel
    await i.response.defer(ephemeral=True)

    # Check bot permissions
    missing = []
    perms = i.guild.me.guild_permissions
    if not perms.manage_channels: missing.append("`Manage Channels`")
    if not perms.manage_roles:    missing.append("`Manage Roles`")
    if not perms.send_messages:   missing.append("`Send Messages`")
    if missing:
        return await i.followup.send(
            f"<:icon_cross:1519358379917836508> Botu nedostaju permisije: {', '.join(missing)}\n"
            f"Dodaj ih u **Server Settings → Roles → GIAN (Custom)** (bot) pa pokušaj ponovo.",
            ephemeral=True
        )

    BAR = "━━━━━━━━━━━━━━━━━━━━"
    e = discord.Embed(
        title="<:e_ticket3:1519362637534597221>  Otvori Tiket",
        description=(
            f"{BAR}\n"
            f"📚  Trebaš pomoć? **Otvori tiket!**\n\n"
            f"🎀  Popuni formu i naš staff će ti odgovoriti što prije.\n"
            f"🔘  Prosječno vrijeme odgovora: **< 30 minuta**\n"
            f"{BAR}\n\n"
            f"🎁  **Šta ćeš dobiti**\n"
            f"🎀  Privatni kanal samo za tebe i staff\n"
            f"✅  Pomoć od iskusnog tima\n"
            f"📸  Možeš priložiti slike/screenshote"
        ),
        color=_LP,
    )
    e.set_footer(text=f"{BOT_NAME} Ticket Sistem")
    try:
        await i.channel.send(embed=e, view=TicketOpenView())
        await i.followup.send("<:icon_check:1519358376268533810> Ticket sistem postavljen uspješno!", ephemeral=True)
    except discord.Forbidden:
        await i.followup.send("<:icon_cross:1519358379917836508> Nemam permisiju da pišem u ovaj kanal!", ephemeral=True)

class SupportTicketModal(discord.ui.Modal, title="🎫 Otvori Tiket za Podršku"):
    razlog = discord.ui.TextInput(
        label="Razlog tiketa (kratko)",
        placeholder="Npr: Problem sa ulogom, ban žalba, pitanje...",
        min_length=3, max_length=100,
        style=discord.TextStyle.short,
    )
    opis = discord.ui.TextInput(
        label="Opiši problem detaljno",
        placeholder="Reci nam što preciznije šta se dešava...",
        min_length=10, max_length=800,
        style=discord.TextStyle.paragraph,
    )
    pokusao = discord.ui.TextInput(
        label="Šta si već pokušao/la?",
        placeholder="Npr: Kontaktirao/la sam moda, čitao/la pravila...",
        min_length=3, max_length=400,
        style=discord.TextStyle.paragraph,
        required=False,
    )

    async def on_submit(self, i: discord.Interaction):
        guild     = i.guild
        safe_name = "".join(c for c in i.user.name.lower() if c.isalnum() or c in "-_")[:20] or str(i.user.id)
        existing  = discord.utils.get(guild.text_channels, name=f"ticket-{safe_name}")
        if existing:
            return await i.response.send_message(
                embed=em("<:icon_check:1519358376268533810> Već otvoren", f"Imaš već otvoren tiket: {existing.mention}", color=COLORS["warning"]),
                ephemeral=True
            )
        if not guild.me.guild_permissions.manage_channels:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Permisija", "Bot nema **Manage Channels** permisiju! Javi adminu.", color=COLORS["error"]),
                ephemeral=True
            )
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            i.user:             discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }
        for role in guild.roles:
            if role.permissions.administrator:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        try:
            category = discord.utils.get(guild.categories, name="Tickets") or \
                       discord.utils.get(guild.categories, name="tickets")
            chan = await guild.create_text_channel(
                f"ticket-{safe_name}",
                overwrites=overwrites,
                category=category,
                reason=f"Ticket od {i.user}",
                topic=f"Ticket od {i.user} ({i.user.id})"
            )
        except discord.Forbidden:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Permisija", "Bot nema dozvolu da kreira kanale!", color=COLORS["error"]),
                ephemeral=True
            )
        except Exception as ex:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Greška", f"`{ex}`", color=COLORS["error"]),
                ephemeral=True
            )

        BAR = "━━━━━━━━━━━━━━━━━━━━━"
        e = discord.Embed(
            title="<:e_ticket3:1519362637534597221>  Novi Tiket za Podršku",
            description=(
                f"{BAR}\n"
                f"<:e_user:1519363093736718518> **{i.user.display_name}** ({i.user.mention})\n"
                f"🆔 ID: `{i.user.id}`\n"
                f"<:e_cal:1519362659676455046> Nalog: <t:{int(i.user.created_at.timestamp())}:R>\n"
                f"{BAR}"
            ),
            color=_LP,
            timestamp=datetime.now(timezone.utc),
        )
        e.set_thumbnail(url=i.user.display_avatar.url)
        e.add_field(name="<:e_pushpin:1519363357436543099>  Razlog tiketa",       value=self.razlog.value,                        inline=False)
        e.add_field(name="📝  Opis problema",        value=self.opis.value,                          inline=False)
        e.add_field(name="<:e_search:1519363103064723547>  Što je pokušano",      value=self.pokusao.value or "*(nije navedeno)*", inline=False)
        e.add_field(
            name="<:e_gear:1519362652516782194>️  Upute za Staff",
            value=(
                "<:icon_check:1519358376268533810> Odgovori što prije i pomozi članu\n"
                "<:icon_check:1519358376268533810> Postavi pitanja ako treba više info\n"
                "<:icon_check:1519358376268533810> Kad je riješeno — zatvori ticket\n"
                "<:e_lock3:1519362717394403432> Klikni **Zatvori Ticket** kad završiš"
            ),
            inline=False,
        )
        e.set_footer(text=f"<:e_ticket3:1519362637534597221> GIAN Ticket Sistem  •  {guild.name}")

        await chan.send(content=i.user.mention, embed=e, view=TicketCloseView())

        potvrda = discord.Embed(
            title="<:icon_check:1519358376268533810>  Tiket otvoren!",
            description=(
                f"## <:e_party:1519363028334674070> Tvoj tiket je kreiran!\n"
                f"Privatni kanal: {chan.mention}\n\n"
                f"<:e_time2:1519362726952964227> Staff će ti odgovoriti uskoro. Budemo te obavijestili! <:e_invite2:1519362710469476405>"
            ),
            color=_LP,
            timestamp=datetime.now(timezone.utc),
        )
        potvrda.add_field(
            name="<:e_clipboard:1519363052871614627>  Šta dalje?",
            value=(
                "<:e_bubble:1519363307998417148> Idi u kanal i čekaj odgovor staffa\n"
                "<:e_link:1519363321458065408> Možeš priložiti slike/screenshote\n"
                "<:e_lock3:1519362717394403432> Kanal je **privatan** — samo ti i staff\n"
                "<:icon_check:1519358376268533810> Ticket se zatvara kad je problem riješen"
            ),
            inline=False,
        )
        potvrda.set_footer(text="<:e_ticket3:1519362637534597221> GIAN  •  Hvala na strpljenju! <:e_pray:1519363406078021863>")
        await i.response.send_message(embed=potvrda)


@bot.tree.command(name="tiket", description="<:e_ticket3:1519362637534597221> Otvori tiket za podršku")
async def tiket_cmd(i: discord.Interaction):
    BAR = "━━━━━━━━━━━━━━━━━━━━"
    e = discord.Embed(
        title="<:e_ticket3:1519362637534597221>  Otvori Tiket",
        description=(
            f"{BAR}\n"
            f"📚  Trebaš pomoć? **Otvori tiket!**\n\n"
            f"🎀  Popuni formu i naš staff će ti odgovoriti što prije.\n"
            f"🔘  Prosječno vrijeme odgovora: **< 30 minuta**\n"
            f"{BAR}\n\n"
            f"🎁  **Šta ćeš dobiti**\n"
            f"🎀  Privatni kanal samo za tebe i staff\n"
            f"✅  Pomoć od iskusnog tima\n"
            f"📸  Možeš priložiti slike/screenshote"
        ),
        color=_LP,
    )
    e.set_footer(text=f"{BOT_NAME} Ticket Sistem")
    await i.response.send_message(embed=e, view=TicketOpenView())

# ═══════════════════════════════════════════
#    STAFF PRIJAVA SISTEM
# ═══════════════════════════════════════════

class StaffApplyModal(discord.ui.Modal, title="📋 Staff Prijava"):
    godine = discord.ui.TextInput(
        label="👤 Godine — koliko imaš godina?",
        placeholder="Npr: 17",
        min_length=1, max_length=20,
        style=discord.TextStyle.short,
    )
    iskustvo = discord.ui.TextInput(
        label="🎖️ Iskustvo — prethodno iskustvo?",
        placeholder="Npr: Bio sam mod na 2 servera, vodio sam tim od 10+ ljudi...",
        min_length=5, max_length=500,
        style=discord.TextStyle.paragraph,
    )
    motivacija = discord.ui.TextInput(
        label="💡 Motivacija — zašto želiš staff?",
        placeholder="Npr: Želim pomoći zajednici i radim dobro pod pritiskom...",
        min_length=10, max_length=500,
        style=discord.TextStyle.paragraph,
    )
    igraci = discord.ui.TextInput(
        label="👥 Igrači — koliko ljudi možeš dovesti?",
        placeholder="Npr: 10-20 prijatelja iz moje stare grupe",
        min_length=1, max_length=200,
        style=discord.TextStyle.short,
    )
    aktivnost = discord.ui.TextInput(
        label="⏰ Aktivnost — sati dnevno + timezone",
        placeholder="Npr: 4-6h dnevno, CET (Balkan)",
        min_length=3, max_length=100,
        style=discord.TextStyle.short,
    )

    async def on_submit(self, i: discord.Interaction):
        guild = i.guild
        safe_name = "".join(c for c in i.user.name.lower() if c.isalnum() or c in "-_")[:20] or str(i.user.id)
        existing = discord.utils.get(guild.text_channels, name=f"staff-{safe_name}")
        if existing:
            return await i.response.send_message(
                embed=em("<:icon_warning:1519358274284032030>", f"Već imaš poslanu prijavu: {existing.mention}", color=COLORS["warning"]),
                ephemeral=True
            )
        if not guild.me.guild_permissions.manage_channels:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>", "Bot nema **Manage Channels** permisiju!", color=COLORS["error"]),
                ephemeral=True
            )
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            i.user:             discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me:           discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True),
        }
        for role in guild.roles:
            if role.permissions.administrator:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        try:
            category = discord.utils.get(guild.categories, name="Staff") or \
                       discord.utils.get(guild.categories, name="Tickets") or \
                       discord.utils.get(guild.categories, name="tickets")
            chan = await guild.create_text_channel(
                f"staff-{safe_name}",
                overwrites=overwrites,
                category=category,
                reason=f"Staff prijava od {i.user}",
                topic=f"Staff prijava — {i.user} ({i.user.id})"
            )
        except discord.Forbidden:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>", "Bot nema dozvolu da kreira kanale!", color=COLORS["error"]),
                ephemeral=True
            )
        except Exception as ex:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>", f"`{ex}`", color=COLORS["error"]),
                ephemeral=True
            )

        prijava_e = discord.Embed(
            title="📋  Nova Staff Prijava",
            description=f"👤  **{i.user.display_name}** ({i.user.mention})  ·  🆔 `{i.user.id}`",
            color=_LP,
            timestamp=datetime.now(timezone.utc)
        )
        prijava_e.add_field(name="👤  Godine",       value=self.godine.value,     inline=True)
        prijava_e.add_field(name="⏰  Aktivnost",    value=self.aktivnost.value,  inline=True)
        prijava_e.add_field(name="👥  Igrači",       value=self.igraci.value,     inline=True)
        prijava_e.add_field(name="🎖️  Iskustvo",    value=self.iskustvo.value,   inline=False)
        prijava_e.add_field(name="💡  Motivacija",   value=self.motivacija.value, inline=False)
        prijava_e.set_thumbnail(url=i.user.display_avatar.url)
        prijava_e.set_footer(text=f"{BOT_NAME} • Staff Prijava")
        await chan.send(content=i.user.mention, embed=prijava_e)
        await i.response.send_message(
            embed=em("<:icon_check:1519358376268533810>", f"Prijava poslana! {chan.mention}", color=COLORS["success"]),
            ephemeral=True
        )


class StaffApplyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Staff Apply", emoji="📋", style=discord.ButtonStyle.primary, custom_id="staff_apply_btn")
    async def apply(self, i: discord.Interaction, b: discord.ui.Button):
        await i.response.send_modal(StaffApplyModal())


@bot.tree.command(name="staff", description="📋 Postavi Staff Prijava panel u ovaj kanal [ADMIN]")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def staff_cmd(i: discord.Interaction):
    await i.response.defer(ephemeral=True)
    e = discord.Embed(
        title="> STAFF PRIJAVA",
        description=(
            "Otvorene su prijave za **Staff tim** servera!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "📌 **Kako se prijaviti:**\n"
            "🎀  Klikni redom na **5 dugmadi** ispod i upiši svoje podatke\n"
            "🎀  Kad popuniš **sva polja**, klikni 📋 **Pošalji prijavu**\n"
            "🎀  Bot će ti otvoriti **privatni kanal** sa staff timom\n\n"
            "⚠️  Tvoji odgovori se vide samo tebi dok ne pošalješ prijavu.\n"
            "📢  **Discord invite linkovi nisu dozvoljeni** u poljima!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "🎀  **Rubrike**\n"
            "🔴  **Godine** — koliko imaš godina\n"
            "🎖️  **Iskustvo** — prethodno iskustvo\n"
            "🌸  **Motivacija** — zašto želiš staff\n"
            "💥  **Igrači** — koliko ljudi možeš dovesti\n"
            "👤  **Aktivnost** — sati dnevno + timezone"
        ),
        color=_LP,
        timestamp=datetime.now(timezone.utc)
    )
    e.set_footer(text=f"{BOT_NAME} (Custom)  •  Staff Prijava")
    try:
        await i.channel.send(embed=e, view=StaffApplyView())
        await i.followup.send("<:icon_check:1519358376268533810> Staff prijava panel postavljen!", ephemeral=True)
    except discord.Forbidden:
        await i.followup.send("<:icon_cross:1519358379917836508> Nemam permisiju da pišem u ovaj kanal!", ephemeral=True)

# ═══════════════════════════════════════════
#    SETUP ROLES — GIAN
# ═══════════════════════════════════════════
PERM_ADMIN = discord.Permissions(administrator=True)
PERM_MOD = discord.Permissions(
    ban_members=True, kick_members=True,
    manage_messages=True, moderate_members=True,
    view_channel=True, send_messages=True,
    read_message_history=True, manage_threads=True
)
PERM_MEMBER = discord.Permissions(
    view_channel=True, send_messages=True,
    read_message_history=True, connect=True, speak=True,
    attach_files=True, embed_links=True, add_reactions=True
)
PERM_BOT = discord.Permissions(
    view_channel=True, send_messages=True,
    read_message_history=True, manage_messages=True,
    embed_links=True, attach_files=True, add_reactions=True,
    connect=True, speak=True
)
PERM_BASIC = discord.Permissions(
    view_channel=True, send_messages=True,
    read_message_history=True, add_reactions=True
)
PERM_VOICE = discord.Permissions(
    view_channel=True, connect=True, speak=True,
    use_voice_activation=True, stream=True
)

GIAN_ROLES = [
    # ═══ JEDINA ULOGA SA POWER-OM (ban/kick/admin) ═══
    {"name": "〢 /GIAN",                     "color": discord.Color.from_str("#FFD700"), "permissions": PERM_ADMIN,  "hoist": True,  "desc": "Glavni admin — ban/kick/sve"},
    # ═══ DEKORATIVNE TOP ULOGE ═══
    {"name": "〢 Cryptid Gianni ( Vlasnik )", "color": discord.Color.from_str("#FF3B3B"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Vlasnik (dekorativna)"},
    {"name": "〢 High Masculinity",            "color": discord.Color.from_str("#1F2A44"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "High Masculinity"},
    {"name": "〢 Cristal De Gianni",           "color": discord.Color.from_str("#A569FF"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Cristal De Gianni"},
    {"name": "〢 Toxic Command ™",             "color": discord.Color.from_str("#00E676"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Toxic Command"},
    # ═══ STAFF (dekorativno) ═══
    {"name": "〢 Owners",                      "color": discord.Color.from_str("#FFC400"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Vlasnici"},
    {"name": "〢 Founders",                    "color": discord.Color.from_str("#FF8A00"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Osnivači"},
    {"name": "〢 Creators",                    "color": discord.Color.from_str("#5DADE2"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Kreatori"},
    {"name": "〢 Administrator",               "color": discord.Color.from_str("#EC407A"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Administrator (dekorativna)"},
    {"name": "〢 Hello Kitty Moderator",       "color": discord.Color.from_str("#FF85C8"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Hello Kitty Moderator"},
    {"name": "〢 Moderator",                   "color": discord.Color.from_str("#42A5F5"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Moderator (dekorativna)"},
    {"name": "〢 StaffTeam",                   "color": discord.Color.from_str("#26C6A4"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Staff Team"},
    # ═══ SPECIJALNE ULOGE ═══
    {"name": "〢 Mjauch",                      "color": discord.Color.from_str("#FF9ECF"), "permissions": PERM_MEMBER, "hoist": False, "desc": "Mjauch <:e_sparkles:1519363032185176198>"},
    {"name": "〢 Samo Njoj",                   "color": discord.Color.from_str("#FF4FA3"), "permissions": PERM_MEMBER, "hoist": False, "desc": "Samo Njoj"},
    {"name": "〢 Girly Pop",                   "color": discord.Color.from_str("#FFB7D5"), "permissions": PERM_MEMBER, "hoist": False, "desc": "Girly Pop"},
    {"name": "〢 Slay Queen",                  "color": discord.Color.from_str("#E91EFF"), "permissions": PERM_MEMBER, "hoist": False, "desc": "Slay Queen"},
    {"name": "〢 67 Pookie",                   "color": discord.Color.from_str("#C58CFF"), "permissions": PERM_MEMBER, "hoist": False, "desc": "67 Pookie"},
    {"name": "〢 Sexy",                        "color": discord.Color.from_str("#D81B60"), "permissions": PERM_MEMBER, "hoist": False, "desc": "Sexy"},
    {"name": "〢 Hello Kitty",                 "color": discord.Color.from_str("#FFC9DD"), "permissions": PERM_MEMBER, "hoist": False, "desc": "Hello Kitty"},
    # ═══ ČLANSTVO & PERMISIJE ═══
    {"name": "〢 Members for /Gianni !",       "color": discord.Color.from_str("#8E44AD"), "permissions": PERM_MEMBER, "hoist": True,  "desc": "Verificirani članovi"},
    {"name": "〢 Chatter",                     "color": discord.Color.from_str("#3DDC97"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Aktivni chatter"},
    {"name": "〢 Main Permission",             "color": discord.Color.from_str("#B0BEC5"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Glavna permisija"},
    {"name": "〢 Voice Permission",            "color": discord.Color.from_str("#78909C"), "permissions": PERM_VOICE,  "hoist": False, "desc": "Voice permisija"},
    # ═══ POL & KATEGORIJE ═══
    {"name": "〢 Musko",                       "color": discord.Color.from_str("#4FC3F7"), "permissions": PERM_MEMBER, "hoist": False, "desc": "Muški članovi"},
    {"name": "〢 Zensko",                      "color": discord.Color.from_str("#F48FB1"), "permissions": PERM_MEMBER, "hoist": False, "desc": "Ženski članovi"},
    {"name": "〢 Radio",                       "color": discord.Color.from_str("#FF5252"), "permissions": PERM_VOICE,  "hoist": False, "desc": "Radio uloga"},
    {"name": "〢 Bots",                        "color": discord.Color.from_str("#90A4AE"), "permissions": PERM_BOT,    "hoist": False, "desc": "Bot uloga"},
    {"name": "〢 Streaks",                     "color": discord.Color.from_str("#AB47BC"), "permissions": PERM_MEMBER, "hoist": False, "desc": "Streak uloga"},
    # ═══ DRŽAVE ═══
    {"name": "〢 Bosnia and Herzegovina",      "color": discord.Color.from_str("#FFCE00"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Bosna i Hercegovina"},
    {"name": "〢 Croatia",                     "color": discord.Color.from_str("#E53935"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Hrvatska"},
    {"name": "〢 Serbia",                      "color": discord.Color.from_str("#1E88E5"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Srbija"},
    {"name": "〢 Macedonia",                   "color": discord.Color.from_str("#FB8C00"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Makedonija"},
    {"name": "〢 Europe",                      "color": discord.Color.from_str("#26A69A"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Europa"},
    # ═══ GODINE ═══
    {"name": "〢 20+",                         "color": discord.Color.from_str("#00897B"), "permissions": PERM_BASIC,  "hoist": False, "desc": "20+ godina"},
    {"name": "〢 18+",                         "color": discord.Color.from_str("#43A047"), "permissions": PERM_BASIC,  "hoist": False, "desc": "18+ godina"},
    {"name": "〢 15+",                         "color": discord.Color.from_str("#FB8C00"), "permissions": PERM_BASIC,  "hoist": False, "desc": "15+ godina"},
    {"name": "〢 14+",                         "color": discord.Color.from_str("#E65100"), "permissions": PERM_BASIC,  "hoist": False, "desc": "14+ godina"},
    # ═══ BOJE (Color Roles) ═══
    {"name": "〢 Bela",                      "color": discord.Color.from_str("#F5F5F5"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Bijela boja"},
    {"name": "〢 Zelena",                    "color": discord.Color.from_str("#4CAF50"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Zelena boja"},
    {"name": "〢 Aqea",                      "color": discord.Color.from_str("#00BCD4"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Aqua boja"},
    {"name": "〢 Žuta",                      "color": discord.Color.from_str("#FFEB3B"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Žuta boja"},
    {"name": "〢 Plava",                     "color": discord.Color.from_str("#2196F3"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Plava boja"},
    {"name": "〢 Roza",                      "color": discord.Color.from_str("#FF4081"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Roza boja"},
    {"name": "〢 Crvena",                    "color": discord.Color.from_str("#F44336"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Crvena boja"},
    {"name": "〢 Crna",                      "color": discord.Color.from_str("#1A1B1E"), "permissions": PERM_BASIC,  "hoist": False, "desc": "Crna boja"},
]

@bot.command(name="sort-roles")
async def sort_roles(ctx: commands.Context):
    if not ctx.author.guild_permissions.administrator and ctx.author.id not in OWNER_IDS:
        return await ctx.send(embed=em("<:icon_cross:1519358379917836508> Nemaš pristup", "Samo admin može koristiti `.sort-roles`.", color=COLORS["error"]))
    guild = ctx.guild
    desired_order = [r["name"] for r in GIAN_ROLES]
    role_map = {r.name: r for r in guild.roles}
    found, missing = [], []
    for name in desired_order:
        if name in role_map:
            found.append((name, role_map[name]))
        else:
            missing.append(name)
    if not found:
        return await ctx.send(embed=em("<:icon_cross:1519358379917836508>", "Nema GIAN uloga! Prvo pokreni `.setup-roles`.", color=COLORS["error"]))
    try:
        positions = {}
        base = 1
        for idx, (name, role) in enumerate(reversed(found)):
            positions[role] = base + idx
        await guild.edit_role_positions(positions=positions)
        ordered_txt = "\n".join(f"`{idx+1}.` {name}" for idx, (name, _) in enumerate(found))
        e = discord.Embed(title="<:icon_check:1519358376268533810> Uloge poređane!", color=COLORS["success"], timestamp=datetime.now(timezone.utc))
        e.add_field(name="<:e_clipboard:1519363052871614627> Novi redoslijed (gore → dolje)", value=ordered_txt, inline=False)
        if missing:
            e.add_field(name="<:icon_warning:1519358274284032030>️ Nisu pronađene na serveru", value="\n".join(missing), inline=False)
        e.set_footer(text=f"{BOT_NAME} • GIAN Role Sort")
        await ctx.send(embed=e)
    except discord.Forbidden:
        await ctx.send(embed=em("<:icon_cross:1519358379917836508>", "Bot nema permisiju da mjenja redoslijed uloga!\nDaj botu **Administrator** permisiju.", color=COLORS["error"]))
    except Exception as ex:
        await ctx.send(embed=em("<:icon_cross:1519358379917836508>", f"Greška: `{ex}`", color=COLORS["error"]))

# ═══════════════════════════════════════════
#    /set GRUPA — sve setup/config komande na jednom mjestu
# ═══════════════════════════════════════════
set_group = app_commands.Group(
    name="set",
    description="<:e_gear:1519362652516782194>️ Server postavke — kanali, uloge, konfiguracija [ADMIN]",
    default_permissions=discord.Permissions(manage_guild=True),
)

@set_group.command(name="roles", description="<:e_label:1519363326109417613>️ Kreiraj sve GIAN uloge odjednom [ADMIN]")
@app_commands.default_permissions(administrator=True)
async def setup_roles(i: discord.Interaction):
    await i.response.defer(ephemeral=True)
    guild = i.guild
    existing = [r.name for r in guild.roles]
    created, skipped = [], []

    for role_data in GIAN_ROLES:
        if role_data["name"] in existing:
            skipped.append(role_data["name"])
            continue
        try:
            await guild.create_role(
                name=role_data["name"],
                color=role_data["color"],
                permissions=role_data["permissions"],
                hoist=role_data["hoist"],
                reason=f"GIAN setup — kreirao {i.user}"
            )
            created.append(role_data["name"])
        except Exception as ex:
            skipped.append(f"{role_data['name']} <:icon_cross:1519358379917836508> ({ex})")

    e = discord.Embed(
        title="<:e_label:1519363326109417613>️ GIAN Uloge — Setup Završen!",
        color=COLORS["gold"],
        timestamp=datetime.now(timezone.utc)
    )
    if created:
        e.add_field(
            name=f"<:icon_check:1519358376268533810> Kreirano ({len(created)})",
            value="\n".join(created),
            inline=False
        )
    if skipped:
        e.add_field(
            name=f"<:e_right:1519363367712591922>️ Preskočeno ({len(skipped)}) — već postoje",
            value="\n".join(skipped),
            inline=False
        )
    e.add_field(
        name="<:e_clipboard:1519363052871614627> Slijedeći korak",
        value=(
            "**Server Settings → Roles** — Povuci uloge u željeni redosljed!\n"
            "Dodijeli `〢 Cryptid Gianni ( Vlasnik )` sebi, `〢 Bots` botu."
        ),
        inline=False
    )
    e.set_footer(text=f"{BOT_NAME} • GIAN Server Setup")
    await i.followup.send(embed=e, ephemeral=True)

# ═══════════════════════════════════════════
#    SERVER SETUP KOMANDE
# ═══════════════════════════════════════════
@set_group.command(name="all", description="<:e_gear:1519362652516782194>️ Postavi sve kanale i uloge servera odjednom [ADMIN]")
@discord.app_commands.describe(
    welcome="Kanal za dobrodošlicu novih članova",
    leave="Kanal za odlaske (ako se ne postavi, koristi welcome kanal)",
    log="Kanal za logove (edit, delete, join, ban...)",
    starboard="Starboard kanal (popularne poruke sa <:e_star2:1519363084253266031>)",
    birthday="Kanal za čestitanje rođendana",
    autorole="Uloga koja se automatski daje svim novim članovima",
    welcome_poruka="Custom welcome poruka ({user} = mention, {server} = ime servera)",
    starboard_zvjezdice="Broj <:e_star2:1519363084253266031> potrebnih za starboard (default: 3)"
)
@discord.app_commands.default_permissions(manage_guild=True)
async def setup_all(
    i: discord.Interaction,
    welcome:             discord.TextChannel = None,
    leave:               discord.TextChannel = None,
    log:                 discord.TextChannel = None,
    starboard:           discord.TextChannel = None,
    birthday:            discord.TextChannel = None,
    autorole:            discord.Role        = None,
    welcome_poruka:      str = "",
    starboard_zvjezdice: int = 3,
):
    cfg = get_guild_config(i.guild.id)
    lines = []

    if welcome:
        cfg["welcome_channel"] = welcome.id
        lines.append(f"<:e_shake:1519362947766554737> **Welcome:** {welcome.mention}")
    if welcome_poruka:
        cfg["welcome_message"] = welcome_poruka
        lines.append(f"📝 **Welcome poruka:** *{welcome_poruka[:80]}*")
    if leave:
        cfg["leave_channel"] = leave.id
        lines.append(f"<:e_shake:1519362947766554737> **Leave:** {leave.mention}")
    if log:
        cfg["log_channel"] = log.id
        lines.append(f"<:e_clipboard:1519363052871614627> **Log:** {log.mention}")
    if starboard:
        cfg["starboard_channel"]   = starboard.id
        cfg["starboard_threshold"] = max(1, starboard_zvjezdice)
        lines.append(f"<:e_star2:1519363084253266031> **Starboard:** {starboard.mention} (min {starboard_zvjezdice}<:e_star2:1519363084253266031>)")
    if birthday:
        cfg["birthday_channel"] = birthday.id
        lines.append(f"<:e_party:1519363028334674070> **Rođendani:** {birthday.mention}")
    if autorole:
        if autorole >= i.guild.me.top_role:
            lines.append(f"<:icon_cross:1519358379917836508> **Auto-uloga:** `{autorole.name}` je viša od moje — preskočeno!")
        else:
            cfg["auto_role"] = autorole.id
            lines.append(f"<:e_label:1519363326109417613>️ **Auto-uloga:** {autorole.mention}")

    if not lines:
        return await i.response.send_message(
            embed=em("<:icon_warning:1519358274284032030>️ Ništa nije postavljeno",
                     "Proslijedi barem jedan parametar!\nPrimjer:\n`/setup welcome:#dobrodošlica log:#logs autorole:@Member`",
                     color=COLORS["warning"]),
            ephemeral=True
        )

    save_data()
    e = discord.Embed(
        title="<:icon_check:1519358376268533810> Server konfigurisan!",
        description="\n".join(lines),
        color=COLORS["success"],
        timestamp=datetime.now(timezone.utc)
    )
    e.set_footer(text=f"Pregled svih postavki: /set config | {BOT_NAME}")
    await i.response.send_message(embed=e, ephemeral=True)

@set_group.command(name="welcome", description="<:e_gear:1519362652516782194>️ Postavi welcome kanal [ADMIN]")
@discord.app_commands.describe(kanal="Kanal gdje bot šalje welcome embed novim članovima")
async def setup_welcome(i: discord.Interaction, kanal: discord.TextChannel):
    cfg = get_guild_config(i.guild.id)
    cfg["welcome_channel"] = kanal.id
    save_data()
    e_out = discord.Embed(
        title="<:icon_check:1519358376268533810> Welcome kanal postavljen!",
        description=(
            f"**Kanal:** {kanal.mention}\n\n"
            f"Svaki novi član će dobiti embed sa:\n"
            f"<:icon_fire:1519358312188088466> chat · <:e_fire2:1519362671491678280> info · "
            f"<:icon_fire:1519358312188088466> news · <:e_fire2:1519362671491678280> gws\n"
            f"<:e_feather:1519363362322907218> broj članova\n"
            f"Dugmad: <:icon_game:1519358323667767346> game · <:icon_music:1519358320337752125> music"
        ),
        color=COLORS["success"],
        timestamp=datetime.now(timezone.utc)
    )
    e_out.set_footer(text=f"{BOT_NAME} • Welcome Setup")
    await i.response.send_message(embed=e_out, ephemeral=True)

@set_group.command(name="aktivnost", description="<:e_gear:1519362652516782194>️ Postavi kanal za XP level-up i aktivnost [ADMIN]")
@discord.app_commands.describe(
    levelup_kanal="Kanal gdje bot objavljuje level-up notifikacije",
    xp_kanal="Kanal za XP/rank prikaz (/rank, /leaderboard komande)"
)
async def aktivnost_setup(
    i: discord.Interaction,
    levelup_kanal: discord.TextChannel = None,
    xp_kanal: discord.TextChannel = None
):
    cfg = get_guild_config(i.guild.id)
    linije = []
    if levelup_kanal:
        cfg["levelup_channel"]   = levelup_kanal.id
        cfg["aktivnost_channel"] = levelup_kanal.id
        linije.append(f"<:e_chart:1519362656568475880> **Level-up / Aktivnost:** {levelup_kanal.mention}")
    if xp_kanal:
        cfg["xp_kanal"] = xp_kanal.id
        linije.append(f"<:e_level2:1519362739749785610> **XP / Rank prikaz:** {xp_kanal.mention}")
    if not linije:
        return await i.response.send_message(
            embed=em("<:icon_warning:1519358274284032030>️ Ništa nije postavljeno", "Proslijedi barem jedan kanal:\n`/set aktivnost levelup_kanal:#aktivnost xp_kanal:#rank`", color=COLORS["warning"]),
            ephemeral=True
        )
    save_data()
    e_out = discord.Embed(
        title="<:icon_check:1519358376268533810> Aktivnost Setup — Sačuvano!",
        description="\n".join(linije),
        color=_LP,
        timestamp=datetime.now(timezone.utc)
    )
    e_out.set_footer(text="GIAN (Custom) • Aktivnost Setup")
    await i.response.send_message(embed=e_out, ephemeral=True)

@set_group.command(name="leave", description="<:e_gear:1519362652516782194>️ Postavi leave kanal [ADMIN]")
@discord.app_commands.describe(kanal="Kanal gdje bot šalje poruku kad član napusti server")
async def setup_leave(i: discord.Interaction, kanal: discord.TextChannel):
    get_guild_config(i.guild.id)["leave_channel"] = kanal.id
    save_data()
    e_out = discord.Embed(
        title="<:icon_check:1519358376268533810> Leave kanal postavljen!",
        description=(
            f"**Kanal:** {kanal.mention}\n\n"
            f"Kad član napusti server, bot će poslati embed sa:\n"
            f"<:icon_fire:1519358312188088466> **bye** ime člana\n"
            f"<:e_feather:1519363362322907218> broj članova\n"
            f"Thumbnail: avatar člana koji je otišao"
        ),
        color=COLORS["success"],
        timestamp=datetime.now(timezone.utc)
    )
    e_out.set_footer(text=f"{BOT_NAME} • Leave Setup")
    await i.response.send_message(embed=e_out, ephemeral=True)

@set_group.command(name="autorole", description="<:e_gear:1519362652516782194>️ Postavi automatsku ulogu pri ulasku [ADMIN]")
@discord.app_commands.describe(uloga="Uloga koja se daje svim novim članovima")
async def setup_autorole(i: discord.Interaction, uloga: discord.Role):
    if uloga >= i.guild.me.top_role:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Ta uloga je viša od moje! Ne mogu je davati.", color=COLORS["error"]), ephemeral=True)
    get_guild_config(i.guild.id)["auto_role"] = uloga.id
    save_data()
    await i.response.send_message(embed=em("<:icon_check:1519358376268533810> Auto-Uloga postavljena!", f"Svaki novi član dobije: {uloga.mention}", color=COLORS["success"]), ephemeral=True)

@set_group.command(name="log", description="<:e_gear:1519362652516782194>️ Postavi log kanal [ADMIN]")
@discord.app_commands.describe(kanal="Log kanal gdje bot šalje editovane/obrisane poruke, join/leave, banove")
async def setup_log(i: discord.Interaction, kanal: discord.TextChannel):
    get_guild_config(i.guild.id)["log_channel"] = kanal.id
    save_data()
    await i.response.send_message(embed=em("<:icon_check:1519358376268533810> Log kanal postavljen!", f"Kanal: {kanal.mention}\nBiće logovano: join/leave, edit, delete, ban.", color=COLORS["success"]), ephemeral=True)

@set_group.command(name="starboard", description="<:e_gear:1519362652516782194>️ Postavi starboard kanal [ADMIN]")
@discord.app_commands.describe(kanal="Starboard kanal", zvjezdice="Broj <:e_star2:1519363084253266031> za pin (default: 3)")
async def setup_starboard(i: discord.Interaction, kanal: discord.TextChannel, zvjezdice: int = 3):
    cfg = get_guild_config(i.guild.id)
    cfg["starboard_channel"]   = kanal.id
    cfg["starboard_threshold"] = max(1, zvjezdice)
    save_data()
    await i.response.send_message(embed=em("<:icon_check:1519358376268533810> Starboard postavljen!", f"Kanal: {kanal.mention}\nPotrebno <:e_star2:1519363084253266031>: `{zvjezdice}`", color=COLORS["success"]), ephemeral=True)

@set_group.command(name="levelrole", description="<:e_gear:1519362652516782194>️ Postavi ulogu za određeni level [ADMIN]")
@discord.app_commands.describe(level="Level za koji se daje uloga", uloga="Uloga koja se daje")
async def setup_levelrole(i: discord.Interaction, level: int, uloga: discord.Role):
    if level < 1 or level > 1000:
        return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Level mora biti između 1 i 1000.", color=COLORS["error"]), ephemeral=True)
    cfg = get_guild_config(i.guild.id)
    cfg.setdefault("level_roles", {})[str(level)] = uloga.id
    save_data()
    await i.response.send_message(embed=em("<:icon_check:1519358376268533810> Level uloga postavljena!", f"Level **{level}** → {uloga.mention}", color=COLORS["success"]), ephemeral=True)

@set_group.command(name="config", description="<:e_gear:1519362652516782194>️ Pregled konfiguracije servera [ADMIN]")
async def server_config_cmd(i: discord.Interaction):
    cfg = get_guild_config(i.guild.id)
    def ch(cid): return f"<#{cid}>" if cid else "*nije postavljeno*"
    def ro(rid): return f"<@&{rid}>" if rid else "*nije postavljeno*"
    lr = cfg.get("level_roles", {})
    lr_txt = "\n".join(f"Level **{k}** → <@&{v}>" for k, v in sorted(lr.items(), key=lambda x: int(x[0]))) or "*nema*"
    e = discord.Embed(title=f"<:e_gear:1519362652516782194>️ Konfiguracija — {i.guild.name}", color=COLORS["purple"], timestamp=datetime.now(timezone.utc))
    e.add_field(name="<:e_shake:1519362947766554737> Welcome kanal",    value=ch(cfg.get("welcome_channel")),   inline=True)
    e.add_field(name="<:e_shake:1519362947766554737> Leave kanal",      value=ch(cfg.get("leave_channel")),     inline=True)
    e.add_field(name="<:e_label:1519363326109417613>️ Auto-Uloga",      value=ro(cfg.get("auto_role")),         inline=True)
    e.add_field(name="<:e_clipboard:1519363052871614627> Log kanal",        value=ch(cfg.get("log_channel")),       inline=True)
    e.add_field(name="<:e_star2:1519363084253266031> Starboard",        value=f"{ch(cfg.get('starboard_channel'))} (min {cfg.get('starboard_threshold', 3)}<:e_star2:1519363084253266031>)", inline=True)
    e.add_field(name="<:e_party:1519363028334674070> Birthday kanal",   value=ch(cfg.get("birthday_channel")),  inline=True)
    e.add_field(name="<:e_confetti2:1519363348288901221> Level uloge",      value=lr_txt, inline=False)
    await i.response.send_message(embed=e, ephemeral=True)

@bot.tree.command(name="afk", description="<:e_sleep:1519362785291669644> Postavi AFK status")
@discord.app_commands.describe(razlog="Razlog zašto si AFK")
async def afk_cmd(i: discord.Interaction, razlog: str = "AFK"):
    uid = str(i.user.id)
    data["afk"][uid] = {"reason": razlog, "since": time.time()}
    save_data()
    await i.response.send_message(embed=em(f"<:e_sleep:1519362785291669644> {i.user.display_name} je sada AFK", f"Razlog: *{razlog}*\nBiće skinut AFK kada sljedeći put pišeš.", color=COLORS["warning"]))




# ═══════════════════════════════════════════
#    SELF ROLES
# ═══════════════════════════════════════════
def _selfrole_key(guild_id: int, channel_id: int) -> str:
    return f"{guild_id}:{channel_id}"

def _build_selfrole_view(key: str) -> discord.ui.View:
    panel = data["selfroles"].get(key, {})
    view  = discord.ui.View(timeout=None)
    for r in panel.get("roles", []):
        emoji = r.get("emoji") or None
        btn   = discord.ui.Button(
            label=r["label"],
            emoji=emoji,
            custom_id=f"sr_{key}_{r['role_id']}",
            style=discord.ButtonStyle.secondary,
        )
        async def _cb(interaction: discord.Interaction, role_id=r["role_id"], label=r["label"]):
            try:
                try:
                    await interaction.response.defer(ephemeral=True, thinking=False)
                except (discord.NotFound, discord.InteractionResponded):
                    pass
                role = interaction.guild.get_role(role_id)
                if not role:
                    try: await interaction.followup.send("<:icon_cross:1519358379917836508> Uloga ne postoji!", ephemeral=True)
                    except: pass
                    return
                me = interaction.guild.me
                if role >= me.top_role:
                    try: await interaction.followup.send(embed=em("<:icon_cross:1519358379917836508>", f"Uloga **{label}** je viša od moje! Admin: pomjeri moju ulogu iznad nje.", color=COLORS["error"]), ephemeral=True)
                    except: pass
                    return
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role, reason="Self-role panel")
                    try: await interaction.followup.send(embed=em("<:e_label:1519363326109417613>️", f"Uklonjena uloga **{label}**!", color=COLORS["error"]), ephemeral=True)
                    except: pass
                else:
                    await interaction.user.add_roles(role, reason="Self-role panel")
                    try: await interaction.followup.send(embed=em("<:icon_check:1519358376268533810>", f"Dobio/la si ulogu **{label}**!", color=COLORS["success"]), ephemeral=True)
                    except: pass
            except discord.Forbidden:
                try: await interaction.followup.send(embed=em("<:icon_cross:1519358379917836508>", "Nemam dozvolu za upravljanje tom ulogom!", color=COLORS["error"]), ephemeral=True)
                except: pass
            except Exception as ex:
                print(f"[selfrole _cb] {type(ex).__name__}: {ex}")
        btn.callback = _cb
        view.add_item(btn)
    return view

def _selfrole_embed(panel: dict) -> discord.Embed:
    e = discord.Embed(
        title=panel.get("title", "<:e_label:1519363326109417613>️ Self Roles"),
        description=panel.get("description", "Klikni dugme da dobiješ/skineš ulogu!"),
        color=_LP,
        timestamp=datetime.now(timezone.utc)
    )
    roles_txt = "\n".join(
        f"{r.get('emoji', '▸')} **{r['label']}**" for r in panel.get("roles", [])
    ) or "*Nema uloga. Admin treba dodati `/selfroles-add`.*"
    e.add_field(name="Dostupne uloge", value=roles_txt, inline=False)
    e.set_footer(text="Klikni dugme ispod ↓")
    return e

PANEL_PRESETS = [
    {
        "title": "<:e_globe2:1519362694887637004> Odaberi svoju državu",
        "description": "Klikni dugme da dobiješ/skineš ulogu!",
        "roles": [
            {"name": "〢 Bosnia and Herzegovina", "label": "Bosnia and Herzegovina", "emoji": "🇧🇦"},
            {"name": "〢 Croatia",                 "label": "Croatia",                 "emoji": "🇭🇷"},
            {"name": "〢 Serbia",                  "label": "Serbia",                  "emoji": "🇷🇸"},
            {"name": "〢 Macedonia",               "label": "Macedonia",               "emoji": "<:e_globe2:1519362694887637004>🇰"},
        ],
    },
    {
        "title": "Odaberi svoju malenokst",
        "description": "Klikni dugme da dobiješ/skineš ulogu!",
        "roles": [
            {"name": "〢 Musko",  "label": "Musko",  "emoji": "<:e_boy:1519362962530373742>"},
            {"name": "〢 Zensko", "label": "Zensko", "emoji": "<:e_woman:1519362926622806046>"},
        ],
    },
    {
        "title": "Klasične Permisije",
        "description": "Klikni dugme da dobiješ/skineš ulogu!",
        "roles": [
            {"name": "〢 Chatter",          "label": "Chatter",          "emoji": "<:e_bubble:1519363307998417148>"},
            {"name": "〢 Voice Permission", "label": "Voice Permission", "emoji": "<:e_speaker:1519363314524881048>"},
            {"name": "〢 Main Permission",  "label": "Main Permission",  "emoji": "<:icon_check:1519358376268533810>"},
        ],
    },
]


# ═══════════════════════════════════════════
#    SET-LEVEL  (Admin/Owner komanda)
# ═══════════════════════════════════════════
@set_group.command(name="level", description="<:e_crown2:1519363047163166922> [OWNER] Postavi level korisniku direktno")
@app_commands.describe(korisnik="Korisnik kojemu postavljaš level", level="Level (1–1000)", xp="XP (opciono, default je level×100)")
async def set_level_cmd(i: discord.Interaction, korisnik: discord.Member, level: int, xp: int = -1):
    if i.user.id not in OWNER_IDS:
        if not (i.user.guild_permissions.administrator):
            return await i.response.send_message(
                embed=em("<:icon_ban:1519358278356959284> Nemaš permisiju!", "Samo admini mogu koristiti ovu komandu.", color=COLORS["error"]),
                ephemeral=True
            )
    if level < 1 or level > 1000:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Neispravan level", "Level mora biti između **1** i **1000**.", color=COLORS["error"]),
            ephemeral=True
        )
    uid = str(korisnik.id)
    if uid not in data.get("xp", {}):
        data.setdefault("xp", {})[uid] = {"xp": 0, "level": 1}
    xp_val = xp if xp >= 0 else level * 100
    data["xp"][uid]["level"] = level
    data["xp"][uid]["xp"]    = xp_val
    save_data()
    e = discord.Embed(
        description=(
            f"## <:e_star2:1519363084253266031> Level Postavljen!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<:e_user:1519363093736718518> **Korisnik:** {korisnik.mention}\n"
            f"🎯 **Novi level:** `{level}`\n"
            f"<:e_bolt:1519362674717102160> **XP:** `{xp_val}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=COLORS["gold"],
        timestamp=datetime.now(timezone.utc)
    )
    e.set_thumbnail(url=korisnik.display_avatar.url)
    e.set_footer(text=f"Postavio/la: {i.user.display_name} • {BOT_NAME}")
    await i.response.send_message(embed=e)

# ═══════════════════════════════════════════
#    HELP
# ═══════════════════════════════════════════
@bot.tree.command(name="help", description="<:e_help2:1519362723148726534> Sve dostupne komande bota")
async def help_cmd(i: discord.Interaction):
    is_admin = False
    is_owner = i.user.id in OWNER_IDS
    try:
        is_admin = i.user.guild_permissions.administrator or any(r.name in ("〢 /GIAN", "〢 /GIANNI") for r in i.user.roles)
    except: pass

    # <:e_wrench:1519362745772802078> PREFIX DETEKCIJA — ako je pozvano kao .help → koristimo "." prefix u embedu (mobitel-mod)
    px = "/"
    is_mobile = False
    try:
        if isinstance(i, FakeInteraction):
            px = "."
            is_mobile = True
    except Exception: pass

    title = "<:e_diamond3:1519363370694738072> S Q U A D  —  K O M A N D E  <:e_diamond3:1519363370694738072>" if not is_mobile else "<:e_phone:1519362788462559323> S Q U A D  —  M O B I L E  <:e_diamond3:1519363370694738072>"
    prefix_txt = f"Prefiksi: `{px}` (slash) i `.` (mobitel)" if not is_mobile else f"Mobitel mod — koristi `.` prefix"

    e = discord.Embed(
        title=title,
        description=(
            f"<:e_sparkles:1519363032185176198> **Dobrodošli u komandni centar!**\n"
            f"<:e_pushpin:1519363357436543099> Verzija **{VERSION}**  ·  {prefix_txt}"
        ),
        color=COLORS["balkan"],
        timestamp=datetime.now(timezone.utc),
    )
    e.set_thumbnail(url=bot.user.display_avatar.url)

    e.add_field(
        name="ℹ️  INFO & UTILITI",
        value=(
            f"🎯 `{px}ping` `{px}serverinfo` `{px}userinfo` `{px}avatar`\n"
                       f"<:e_mail:1519362754732097546> `{px}invite` `{px}spotify` `{px}qr`\n"
"
            f"<:e_chart:1519362656568475880> `{px}topchatters` `{px}aktivnost`"
        ),
        inline=False,
    )
    e.add_field(
        name="<:e_sleep:1519362785291669644>  AFK & SOCIJALNO",
        value=(f"<:e_sleep:1519362785291669644> `{px}afk` — Postavi AFK status"),
        inline=False,
    )
    e.add_field(
        name="<:e_coins3:1519362621206298666>  EKONOMIJA",
        value=(
            f"<:e_coins3:1519362621206298666> `{px}baki` `{px}posao` `{px}daily` `{px}daj` `{px}kradi`\n"
            f"<:e_trophy2:1519362624742232146> `{px}rank` `{px}leaderboard` `{px}shop` `{px}kupi`\n"
            f"<:e_bank2:1519362662515871744> `{px}bank` `{px}lottery` `{px}heist`"
        ),
        inline=False,
    )
    e.add_field(
        name="<:e_ctrl:1519362682296209498>  IGRE & ZABAVA",
        value=(
            f"<:e_slotm:1519362699014967297> `{px}slots` <:e_dice2:1519362633763913931> `{px}rulet` <:e_keyboard:1519363499875242104>️ `{px}kpm`\n"
            f"📝 `{px}kaladont` `{px}kaladont-stop`\n"
            f"<:e_masks:1519363003424706671> `{px}vjasala` `{px}kviz` `{px}geografija`\n"
            f"<:e_cards2:1519362702835712010> `{px}blackjack` <:e_sun:1519362860218843399>️ `{px}toplo-hladno`\n"
            f"<:icon_game:1519358323667767346> `{px}amogus` `{px}amogus-stop`\n"
            f"<:e_sparkles:1519363032185176198> `{px}meme` <:e_chart:1519362656568475880> `{px}aktivnost`"
        ),
        inline=False,
    )
    # Mobitel mod = manje zatrpan, izostavi neke opširnije sekcije
    if not is_mobile:
        e.add_field(
            name="🎯  BINGO",
            value=(
                f"🎯 `{px}bingo` — Pokreni bingo rundu\n"
                f"<:e_refresh:1519362959187509461> Auto-bingo svakih **3 sata** automatski!\n"
                f"<:e_coins3:1519362621206298666> Nagrade: `2<:e_check2:1519362730057007268>=10k` · `3<:e_check2:1519362730057007268>=30k` · `4<:e_check2:1519362730057007268>=75k` · `5<:e_check2:1519362730057007268>=250k <:e_trophy2:1519362624742232146>`"
            ),
            inline=False,
        )
        e.add_field(
            name="<:e_wolf:1519363412625326161>  OWO — ŽIVOTINJE",
            value=(
                f"<:e_wolf:1519363412625326161> `{px}hunt` `{px}zoo` `{px}battle` `{px}sell`\n"
                f"<:e_pray:1519363406078021863> `{px}animals` `{px}pray` `{px}curse`"
            ),
            inline=False,
        )
        e.add_field(
            name="<:e_heart2:1519362668644012133>️  LJUBAV & AKCIJE",
            value=(
                f"<:e_shake:1519362947766554737> `{px}zagrljaj` `{px}poljubac` `{px}mazi` `{px}tapsi`\n"
                f"<:e_shake:1519362947766554737> `{px}high5` `{px}srce` `{px}brak` `{px}pocetkaj` `{px}cudan`\n"
                f"<:e_bubble:1519363307998417148> `{px}pozz` `{px}kompli` `{px}fora` `{px}muv` `{px}crush`"
            ),
            inline=False,
        )
        e.add_field(
            name="<:e_clipboard:1519363052871614627>  QUESTS, POLL & SOCIAL",
            value=(
                f"<:e_clipboard:1519363052871614627> `{px}quests` — Dnevni zadaci za XP i novac\n"
                f"<:e_chart:1519362656568475880> `{px}poll` — Napravi glasanje\n"
                f"<:e_skull:1519362992502997125> `{px}confess` — Anonimna ispovjed\n"
                f"<:e_report2:1519362714198347886> `{px}report` — Prijavi člana\n"
                f"<:e_ticket3:1519362637534597221> `{px}tiket` — Otvori tiket za podršku\n"
                f"📝 `{px}tiket-staff` — Prijavi se za Staff poziciju"
            ),
            inline=False,
        )
        e.add_field(
            name="<:e_chart:1519362656568475880>  BROJANJE",
            value=(f"<:e_chart:1519362656568475880> `/set brojanje` `/set brojanje-reset`"),
            inline=False,
        )
    else:
        # MOBITEL: kratka zbirna sekcija
        e.add_field(
            name="<:e_phone:1519362788462559323>  OSTALO (mobitel)",
            value=(
                f"🎯 `{px}bingo` <:e_wolf:1519363412625326161> `{px}hunt` `{px}zoo` `{px}battle`\n"
                f"<:e_clipboard:1519363052871614627> `{px}quests` `{px}poll` `{px}confess` `{px}tiket`\n"
                f"<:e_heart2:1519362668644012133>️ `{px}zagrljaj` `{px}poljubac` `{px}srce`\n"
                f"<:e_chart:1519362656568475880> `/set brojanje`"
            ),
            inline=False,
        )

    if (is_admin or is_owner) and not is_mobile:
        e.add_field(
            name="<:e_gear:1519362652516782194>️  SERVER SETUP  〔ADMIN〕",
            value=(
                f"<:e_gear:1519362652516782194>️ `/set all` — sve odjednom\n"
                f"<:e_label:1519363326109417613>️ `/set welcome` `/set leave` `/set log` `/set starboard`\n"
                f"<:e_shake:1519362947766554737> `/set autorole` `/set levelrole` `/set aktivnost`\n"
                f"<:e_clipboard:1519363052871614627> `/set config` `/set kanal` `/set level` `/set roles`"
            ),
            inline=False,
        )
        e.add_field(
            name="<:e_shield2:1519362627795554374>️  MODERACIJA  〔ADMIN〕",
            value=(
                f"<:e_hammer:1519362836671762494> `{px}ban` `{px}kick` `{px}timeout` `{px}warn`\n"
                f"<:e_clipboard:1519363052871614627> `{px}warnings` `{px}clearwarnings` `{px}clear`"
            ),
            inline=False,
        )
        e.add_field(
            name="<:e_gift:1519362618341462067>  GIVEAWAY  〔ADMIN〕",
            value=(f"<:e_gift:1519362618341462067> `{px}giveaway start` `{px}giveaway end` `{px}reset-gw`"),
            inline=False,
        )
        e.add_field(
            name="<:e_ticket3:1519362637534597221>  TICKET & BOT  〔ADMIN〕",
            value=(
                f"<:e_ticket3:1519362637534597221> `{px}tiket` `{px}ticket-setup` `{px}say`\n"
                f"<:e_wrench:1519362745772802078> `{px}sort-roles` `/set roles`"
            ),
            inline=False,
        )
        e.add_field(
            name="<:e_gear:1519362652516782194>️  /set KOMANDE  〔ADMIN〕",
            value=(
                f"<:e_gear:1519362652516782194>️ `/set all` `/set welcome` `/set leave` `/set log`\n"
                f"<:e_label:1519363326109417613>️ `/set autorole` `/set starboard` `/set levelrole`\n"
                f"<:e_chart:1519362656568475880> `/set aktivnost` `/set brojanje` `/set brojanje-reset`\n"
                f"<:e_clipboard:1519363052871614627> `/set config` `/set kanal` `/set level` `/set roles`"
            ),
            inline=False,
        )
        e.add_field(
            name="<:e_gear:1519362652516782194>  AUTO-MOD  〔AUTOMATSKI〕",
            value=(
                "<:icon_ban:1519358278356959284> Anti-Spam: 7 poruka/5s → 30s timeout\n"
                "<:e_shield2:1519362627795554374>️ Anti-Nuke: masovna zaštita kanala/uloga\n"
                "<:e_lock3:1519362717394403432> Anti-Raid: zaštita od botova pri joinu\n"
                "<:icon_check:1519358376268533810> Sve aktivno bez ikakve konfiguracije!"
            ),
            inline=False,
        )

    if is_owner and not is_mobile:
        e.add_field(
            name="<:e_crown2:1519363047163166922>  OWNER KOMANDE  〔VLASNIK〕",
            value=(
                f"<:e_moneywing:1519362955437805771> `{px}dodaj-novac` `{px}oduzmi-novac`\n"
                f"<:e_star2:1519363084253266031> `/set level` — Postavi level korisniku\n"
                f"<:e_mega2:1519362736566304818> `{px}event` — Objavi event (naslov + opis)"
            ),
            inline=False,
        )

    e.add_field(
        name="<:e_idea:1519363006599794799>  SAVJET",
        value=(
            f"<:e_ticket3:1519362637534597221> Bingo tiket košta **500 coina** <:e_coins3:1519362621206298666>\n"
            f"<:e_coins3:1519362621206298666> Koristi `{px}posao` i `{px}daily` za zaradu!\n"
            f"<:e_bubble:1519363307998417148> Za pomoć: kontaktiraj staff servera"
        ),
        inline=False,
    )

    role_tag = '<:e_crown2:1519363047163166922> Owner pristup' if is_owner else ('<:e_shield2:1519362627795554374>️ Admin pristup' if is_admin else '<:e_user:1519363093736718518> Member pristup')
    mob_tag = ' • <:e_phone:1519362788462559323> mobile' if is_mobile else ''
    e.set_footer(text=f"<:e_diamond3:1519363370694738072> {BOT_NAME} {VERSION} · {role_tag}{mob_tag} <:e_diamond3:1519363370694738072>")
    await i.response.send_message(embed=e, ephemeral=True)


# ═══════════════════════════════════════════
#    <:e_circus:1519363558809272371> EVENT — samo vlasnik
# ═══════════════════════════════════════════
@bot.tree.command(name="event", description="<:e_circus:1519363558809272371> Objavi event na serveru (samo vlasnik)")
@discord.app_commands.describe(
    naslov="Naslov eventa",
    opis="Opis eventa — šta, kada, gdje, nagrade itd."
)
async def event_cmd(i: discord.Interaction, naslov: str, opis: str):
    if i.user.id not in OWNER_IDS:
        return await i.response.send_message(
            embed=em("<:e_crown2:1519363047163166922> Nemaš pristup!", "Ova komanda je rezervisana samo za **Vlasnika** bota.", color=COLORS["error"]),
            ephemeral=True,
        )
    BAR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    e = discord.Embed(
        title=f"<:e_circus:1519363558809272371>  {naslov}",
        description=f"{BAR}\n\n{opis}\n\n{BAR}",
        color=_LP,
        timestamp=datetime.now(timezone.utc),
    )
    e.set_author(
        name=f"× GIAN — NOVI EVENT!",
        icon_url=bot.user.display_avatar.url,
    )
    e.set_footer(text=f"<:e_mega2:1519362736566304818> Event objavio: {i.user.display_name}  ·  {BOT_NAME}")
    e.set_thumbnail(url=bot.user.display_avatar.url)
    await i.response.send_message(embed=e)
    await i.followup.send(embed=em("<:icon_check:1519358376268533810> Event objavljen!", f"**{naslov}** je uspješno objavljen! <:e_circus:1519363558809272371>", color=COLORS["success"]), ephemeral=True)

# ═══════════════════════════════════════════
#    ERROR HANDLING
# ═══════════════════════════════════════════
@bot.tree.error
async def on_app_error(i: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        mins, secs = divmod(int(error.retry_after), 60)
        t = f"{mins}min {secs}s" if mins else f"{secs}s"
        e = em("<:e_time2:1519362726952964227> Cooldown!", f"Sačekaj još **{t}**.", color=COLORS["warning"])
    elif isinstance(error, app_commands.MissingPermissions):
        e = em("<:e_shield2:1519362627795554374>️ Nemaš dozvole!", "Nisi ovlašćen za ovu komandu.", color=COLORS["error"])
    elif isinstance(error, app_commands.BotMissingPermissions):
        e = em("<:e_gear:1519362652516782194> Bot nema dozvole!", "Daj mi potrebne dozvole.", color=COLORS["error"])
    else:
        e = em("<:icon_cross:1519358379917836508> Greška!", f"`{str(error)[:200]}`", color=COLORS["error"])
        print(f"[tree.error] {type(error).__name__}: {error}")
    try:
        if i.response.is_done(): await i.followup.send(embed=e, ephemeral=True)
        else: await i.response.send_message(embed=e, ephemeral=True)
    except: pass

# ═══════════════════════════════════════════
#    /igre — UKLONJENO
# ═══════════════════════════════════════════
_REMOVED_IGRE = """
GAMES_CATALOG = [
    {
        "emoji": "<:e_brain:1519362849548406975>", "name": "Balkan Trivia", "cmd": "/kviz",
        "img": "attached_assets/games/kviz.png", "color": COLORS["purple"],
        "desc": "Odgovaraj na Balkan pitanja i osvajaj pare!",
        "kako": "Uložiš okladu, biraš jedan od 4 odgovora u 20s.",
        "nagrada": "Tačno → +oklada × combo + 25 XP. Combo raste sa svakim tačnim!"
    },
    {
        "emoji": "<:e_globe2:1519362694887637004>", "name": "Geografija", "cmd": "/geografija",
        "img": "attached_assets/games/geografija.png", "color": COLORS["info"],
        "desc": "50+ pitanja o glavnim gradovima, rijekama i planinama.",
        "kako": "Uložiš okladu i biraš tačan odgovor.",
        "nagrada": "Tačno → +oklada × combo + 25 XP po nivou."
    },
    {
        "emoji": "<:e_dice2:1519362633763913931>", "name": "Kocka", "cmd": "/kocka",
        "img": "attached_assets/games/kocka.png", "color": COLORS["gold"],
        "desc": "Baci kocku protiv prijatelja — veći broj pobjeđuje!",
        "kako": "Pozoveš protivnika i uložite jednaku okladu.",
        "nagrada": "Pobjednik uzima sve. Gubitnik plaća."
    },
    {
        "emoji": "<:e_slotm:1519362699014967297>", "name": "Slot Mašina", "cmd": "/slots",
        "img": "attached_assets/games/slots.png", "color": COLORS["gold"],
        "desc": "Klasična slot mašina — uloži od 20 do 1.000.000.000 <:e_coins3:1519362621206298666> i okreni tri kotača!",
        "kako": "Postaviš ulog (npr. `.slots 50000`), vrtiš, čekaš kombinaciju.",
        "nagrada": "3x 7️⃣ = ×50 ulog! 3x <:e_diamond2:1519362640961474601> = ×15! Par vraća dio uloga."
    },
    {
        "emoji": "<:e_cards2:1519362702835712010>", "name": "Blackjack", "cmd": "/blackjack",
        "img": "attached_assets/games/blackjack.png", "color": COLORS["error"],
        "desc": "Pravi Blackjack protiv dilera. Cilj: 21 ili blizu!",
        "kako": "Hit za novu kartu, Stand da staneš. Diler igra po pravilu.",
        "nagrada": "Pobjeda = 2x uloga, Blackjack = 2.5x!"
    },
    {
        "emoji": "<:e_rocket2:1519363332266524813>", "name": "Among Us", "cmd": "/amogus",
        "img": "attached_assets/games/amogus.png", "color": COLORS["error"],
        "desc": "Kompletan Among Us u Discordu! Crewmates vs Impostor.",
        "kako": "Pokreni igru, čekaj igrače, zadaci/sastanci/glasanje.",
        "nagrada": "Pobjednička ekipa dobija nagradu i XP."
    },
    {
        "emoji": "📝", "name": "Kaladont", "cmd": "/kaladont",
        "img": "attached_assets/games/kaladont.png", "color": COLORS["info"],
        "desc": "Klasični Balkan word game — ulanči riječi!",
        "kako": "Svaka nova riječ mora počinjati zadnjim slovima prošle.",
        "nagrada": "Što duži lanac, to više XP-a za sve!"
    },
    {
        "emoji": "<:e_ctrl:1519362682296209498>", "name": "Vješala", "cmd": "/vjasala",
        "img": "attached_assets/games/vjasala.png", "color": COLORS["warning"],
        "desc": "Pogodi skrivenu riječ slovo po slovo!",
        "kako": "6 grešaka i visi! Predloži slovo dugmetom.",
        "nagrada": "Pogodak = pare + XP, neuspjeh = ništa."
    },
    {
        "emoji": "<:e_sun:1519362860218843399>️", "name": "Toplo-Hladno", "cmd": "/toplo-hladno",
        "img": "attached_assets/games/toplohladno.png", "color": COLORS["info"],
        "desc": "Pogodi skriveni broj — bot ti govori toplije/hladnije!",
        "kako": "Bot bira tajni broj, ti pogađaš.",
        "nagrada": "Manje pokušaja = veća nagrada!"
    },
    {
        "emoji": "<:e_muscle:1519362764244652122>", "name": "Kamen-Papir-Makaze", "cmd": "/kpm",
        "img": "attached_assets/games/kpm.png", "color": COLORS["purple"],
        "desc": "Klasika protiv bota ili igrača!",
        "kako": "Klikneš dugme i čekaš ishod.",
        "nagrada": "Pobjeda = +pare, neriješeno = nazad ulog."
    },
    {
        "emoji": "<:e_arrow:1519363399845154958>", "name": "Ruski Rulet", "cmd": "/rulet",
        "img": "attached_assets/games/rulet.png", "color": COLORS["error"],
        "desc": "Za hrabre — povuci obarač i pomoli se!",
        "kako": "1/6 šanse za 'metak'. Preživi i uzmi pare.",
        "nagrada": "Preživiš = veliki dobitak, padneš = timeout!"
    },
    {
        "emoji": "<:e_arrow:1519363399845154958>", "name": "Lov", "cmd": "/hunt",
        "img": "attached_assets/games/hunt.png", "color": COLORS["success"],
        "desc": "OWO-style lov! Uhvati životinje različitog rariteta.",
        "kako": "Komanda /hunt → bot izvuče nasumičnu životinju za tebe.",
        "nagrada": "Životinje idu u tvoj /zoo. Možeš ih /sell ili /battle."
    },
    {
        "emoji": "<:e_sword2:1519362631146930317>️", "name": "Battle", "cmd": "/battle",
        "img": "attached_assets/games/battle.png", "color": COLORS["error"],
        "desc": "Bori se sa drugim igračem životinjama iz zoo-a!",
        "kako": "Izabereš protivnika, jača životinja pobjeđuje.",
        "nagrada": "Pobjeda = pare + XP boost."
    },
    {
        "emoji": "<:e_chart:1519362656568475880>", "name": "Brojanje", "cmd": "/brojanje-postavi",
        "img": "attached_assets/games/brojanje.png", "color": COLORS["info"],
        "desc": "Klasični sistem brojanja u kanalu — ne smiješ pogriješiti!",
        "kako": "Admin postavi kanal, svi pišu brojeve redom 1, 2, 3…",
        "nagrada": "Svaki 50. broj = +100 <:e_coins3:1519362621206298666> +50 XP. Greška = reset!"
    },
]

class GamesView(discord.ui.View):
    def __init__(self, uid: int):
        super().__init__(timeout=180)
        self.uid = uid
        self.idx = 0
        self._update_buttons()

    def _update_buttons(self):
        self.prev_btn.disabled = self.idx == 0
        self.next_btn.disabled = self.idx == len(GAMES_CATALOG) - 1

    def _build_embed_and_file(self):
        g = GAMES_CATALOG[self.idx]
        e = discord.Embed(
            title=f"{g['emoji']}  {g['name']}",
            description=f"**`{g['cmd']}`**\n\n{g['desc']}",
            color=g["color"], timestamp=datetime.now(timezone.utc)
        )
        e.add_field(name="<:e_help2:1519362723148726534> Kako se igra", value=g["kako"], inline=False)
        e.add_field(name="<:e_coins3:1519362621206298666> Nagrada", value=g["nagrada"], inline=False)
        e.set_footer(text=f"Igra {self.idx+1}/{len(GAMES_CATALOG)} • {BOT_NAME} {VERSION}")
        try:
            file = discord.File(g["img"], filename=f"game_{self.idx}.png")
            e.set_image(url=f"attachment://game_{self.idx}.png")
            return e, file
        except Exception:
            return e, None

    @discord.ui.button(label="<:e_refresh:1519362959187509461> Nazad", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, i: discord.Interaction, _):
        if i.user.id != self.uid:
            return await i.response.send_message("Ovo nije tvoj meni!", ephemeral=True)
        self.idx = max(0, self.idx - 1)
        self._update_buttons()
        e, file = self._build_embed_and_file()
        kwargs = {"embed": e, "view": self}
        if file: kwargs["attachments"] = [file]
        await i.response.edit_message(**kwargs)

    @discord.ui.button(label="Naprijed <:e_right:1519363367712591922>", style=discord.ButtonStyle.primary)
    async def next_btn(self, i: discord.Interaction, _):
        if i.user.id != self.uid:
            return await i.response.send_message("Ovo nije tvoj meni!", ephemeral=True)
        self.idx = min(len(GAMES_CATALOG)-1, self.idx + 1)
        self._update_buttons()
        e, file = self._build_embed_and_file()
        kwargs = {"embed": e, "view": self}
        if file: kwargs["attachments"] = [file]
        await i.response.edit_message(**kwargs)

    @discord.ui.button(label="<:e_clipboard:1519363052871614627> Sve igre", style=discord.ButtonStyle.success)
    async def list_btn(self, i: discord.Interaction, _):
        if i.user.id != self.uid:
            return await i.response.send_message("Ovo nije tvoj meni!", ephemeral=True)
        lines = [f"{g['emoji']} `{g['cmd']:<22}` — {g['name']}" for g in GAMES_CATALOG]
        e = discord.Embed(
            title="<:e_ctrl:1519362682296209498> Sve GIAN igre",
            description="\n".join(lines) + f"\n\n*Ukupno: **{len(GAMES_CATALOG)} igara***",
            color=COLORS["gold"]
        )
        e.set_footer(text=f"{BOT_NAME} {VERSION}")
        await i.response.send_message(embed=e, ephemeral=True)

    @discord.ui.button(label="<:icon_cross:1519358379917836508>", style=discord.ButtonStyle.danger)
    async def close_btn(self, i: discord.Interaction, _):
        if i.user.id != self.uid:
            return await i.response.send_message("Ovo nije tvoj meni!", ephemeral=True)
        self.clear_items()
        await i.response.edit_message(content="Zatvoreno.", embed=None, view=self, attachments=[])

"""

# ═══════════════════════════════════════════
#    DODATNE KORISNE KOMANDE (v2.1)
# ═══════════════════════════════════════════
data.setdefault("bank", {})
data.setdefault("lottery", {"pot": 0, "tickets": {}, "last_draw": 0})
data.setdefault("reminders", [])
data.setdefault("heist_cooldown", {})
data.setdefault("confess_count", 0)
data.setdefault("cmd_uses", {})



# ─── <:e_trophy2:1519362624742232146> TOP CHATTERS ───
@bot.tree.command(name="topchatters", description="<:e_trophy2:1519362624742232146> Top 10 najaktivnijih chatera")
async def topchatters_cmd(i: discord.Interaction):
    gid = str(i.guild.id)
    rows = [(int(k.split(":")[1]), v) for k, v in data.get("msg_count", {}).items() if k.startswith(f"{gid}:")]
    rows.sort(key=lambda x: x[1], reverse=True)
    rows = rows[:10]
    if not rows:
        return await i.response.send_message(embed=em("<:e_trophy2:1519362624742232146> Top Chatters", "Još nema podataka.", color=COLORS["warning"]))
    medals = ["<:e_star2:1519363084253266031>", "<:icon_rank2:1519358512336212091>", "<:icon_rank3:1519358517633355919>"] + [f"`#{n}`" for n in range(4, 11)]
    desc = []
    for idx, (uid, cnt) in enumerate(rows):
        m = i.guild.get_member(uid)
        name = m.display_name if m else f"User {uid}"
        desc.append(f"{medals[idx]} **{name}** — `{cnt:,}` poruka")
    e = discord.Embed(title="<:e_trophy2:1519362624742232146> Top 10 Najaktivnijih", description="\n".join(desc), color=COLORS["success"], timestamp=datetime.now(timezone.utc))
    await i.response.send_message(embed=e)

# ─── <:e_bank2:1519362662515871744> BANKA ───
@bot.tree.command(name="bank", description="<:e_bank2:1519362662515871744> Banka — deposit/withdraw/balance (5% nedjeljna kamata)")
async def bank_cmd(i: discord.Interaction, akcija: str = "balance", iznos: int = 0):
    uid = str(i.user.id)
    bnk = data["bank"].setdefault(uid, {"saved": 0, "last_interest": int(time.time())})
    eco = get_economy(i.user.id)
    # kamata
    weeks = (int(time.time()) - bnk["last_interest"]) // (7*86400)
    if weeks > 0 and bnk["saved"] > 0:
        for _ in range(weeks): bnk["saved"] = int(bnk["saved"] * 1.05)
        bnk["last_interest"] = int(time.time())
    a = akcija.lower()
    if a in ("balance", "bal", "stanje"):
        return await i.response.send_message(embed=em("<:e_bank2:1519362662515871744> Banka", f"<:e_coins3:1519362621206298666> Wallet: `{eco['balance']:,}`\n<:e_bank2:1519362662515871744> Banka: `{bnk['saved']:,}`\n<:e_level2:1519362739749785610> Kamata: **5% / nedjeljno**", color=COLORS["info"]))
    if a in ("deposit", "dep", "ulozi"):
        if iznos <= 0 or iznos > eco["balance"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Nemaš toliko.", color=COLORS["error"]), ephemeral=True)
        eco["balance"] -= iznos; bnk["saved"] += iznos; save_data()
        return await i.response.send_message(embed=em("<:icon_check:1519358376268533810> Uloženo", f"Uloženo `{iznos:,}` u banku.", color=COLORS["success"]))
    if a in ("withdraw", "wd", "podigni"):
        if iznos <= 0 or iznos > bnk["saved"]:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Nemaš toliko u banci.", color=COLORS["error"]), ephemeral=True)
        eco["balance"] += iznos; bnk["saved"] -= iznos; save_data()
        return await i.response.send_message(embed=em("<:icon_check:1519358376268533810> Podignuto", f"Podigao `{iznos:,}` iz banke.", color=COLORS["success"]))
    await i.response.send_message(embed=em("<:e_bank2:1519362662515871744> Banka — pomoć", "`/bank balance` — stanje\n`/bank deposit 100` — uloži\n`/bank withdraw 50` — podigni", color=COLORS["info"]))

# ─── <:e_slotm:1519362699014967297> LOTO ───
@bot.tree.command(name="lottery", description="<:e_slotm:1519362699014967297> Sedmična loto — kupi tiket za 100 coina")
async def lottery_cmd(i: discord.Interaction, akcija: str = "info"):
    lot = data["lottery"]
    uid = str(i.user.id)
    a = akcija.lower()
    # auto-žrijeb svake nedjelje
    if int(time.time()) - lot.get("last_draw", 0) > 7*86400 and lot["tickets"]:
        winner_uid = random.choice(list(lot["tickets"].keys()))
        prize = lot["pot"]
        get_economy(int(winner_uid))["balance"] += prize
        lot["pot"] = 0; lot["tickets"] = {}; lot["last_draw"] = int(time.time())
        save_data()
        try:
            w = await bot.fetch_user(int(winner_uid))
            await w.send(embed=em("<:e_party:1519363028334674070> LOTO POBJEDA!", f"Osvojio si **{prize:,}** coina! <:e_coins3:1519362621206298666>", color=COLORS["success"]))
        except: pass
    if a == "buy":
        eco = get_economy(i.user.id)
        if eco["balance"] < 100:
            return await i.response.send_message(embed=em("<:icon_cross:1519358379917836508>", "Treba ti 100 coina.", color=COLORS["error"]), ephemeral=True)
        eco["balance"] -= 100; lot["pot"] += 100
        lot["tickets"][uid] = lot["tickets"].get(uid, 0) + 1
        save_data()
        return await i.response.send_message(embed=em("<:e_ticket3:1519362637534597221> Tiket kupljen", f"Imaš `{lot['tickets'][uid]}` tiket(a).\n<:e_coins3:1519362621206298666> Pot: `{lot['pot']:,}`", color=COLORS["success"]))
    total = sum(lot["tickets"].values())
    my = lot["tickets"].get(uid, 0)
    chance = (my/total*100) if total else 0
    next_draw = lot["last_draw"] + 7*86400
    e = discord.Embed(title="<:e_slotm:1519362699014967297> Sedmična Loto", color=COLORS["info"])
    e.add_field(name="<:e_coins3:1519362621206298666> Pot", value=f"`{lot['pot']:,}` coina", inline=True)
    e.add_field(name="<:e_ticket3:1519362637534597221> Tvoji tiketi", value=f"`{my}` / `{total}`", inline=True)
    e.add_field(name="🎯 Šansa", value=f"`{chance:.1f}%`", inline=True)
    e.add_field(name="<:e_time2:1519362726952964227> Sljedeći žrijeb", value=f"<t:{next_draw}:R>", inline=False)
    e.set_footer(text="/lottery buy — kupi tiket za 100 coina")
    await i.response.send_message(embed=e)

# ─── <:e_coins3:1519362621206298666> HEIST (timski razboj) ───
@bot.tree.command(name="heist", description="<:e_coins3:1519362621206298666> Timski razboj — okupi 3+ ljudi i dobijte 1000-5000")
async def heist_cmd(i: discord.Interaction):
    uid = str(i.user.id)
    cd = data["heist_cooldown"].get(uid, 0)
    if int(time.time()) < cd:
        return await i.response.send_message(embed=em("<:e_time2:1519362726952964227>", f"Pokušaj ponovo <t:{cd}:R>.", color=COLORS["warning"]), ephemeral=True)
    e = discord.Embed(title="<:e_coins3:1519362621206298666> RAZBOJ U PRIPREMI", description=f"{i.user.mention} organizuje razboj!\n**Klikni dugme da se pridružiš** (treba 3+ ljudi za uspjeh)\n<:e_time2:1519362726952964227> 30 sekundi do akcije!", color=COLORS["warning"])
    crew = {i.user.id}
    class HeistView(discord.ui.View):
        def __init__(self): super().__init__(timeout=30)
        @discord.ui.button(label="<:e_shake:1519362947766554737> Pridruži se", style=discord.ButtonStyle.success)
        async def join(self, ix: discord.Interaction, _):
            crew.add(ix.user.id)
            await ix.response.send_message(f"<:icon_check:1519358376268533810> {ix.user.mention} u ekipi! ({len(crew)} članova)", ephemeral=True, delete_after=5)
    v = HeistView()
    await i.response.send_message(embed=e, view=v)
    await asyncio.sleep(30)
    n = len(crew)
    data["heist_cooldown"][uid] = int(time.time()) + 3600
    if n < 3:
        save_data()
        return await i.followup.send(embed=em("<:e_bomb:1519363456334168255> PROPAO RAZBOJ", f"Samo {n} članova — premalo. Policija je došla! <:e_taxi:1519363380513603615>", color=COLORS["error"]))
    success = random.random() < (0.4 + n*0.05)
    if success:
        per = random.randint(1000, 5000) // n
        for cid in crew: get_economy(cid)["balance"] += per
        save_data()
        await i.followup.send(embed=em("<:e_party:1519363028334674070> USPJEŠAN RAZBOJ!", f"Ekipa od **{n}** članova podijelila plijen!\n<:e_coins3:1519362621206298666> Svako je dobio: `{per:,}` coina", color=COLORS["success"]))
    else:
        for cid in crew:
            eco = get_economy(cid); eco["balance"] = max(0, eco["balance"] - 200)
        save_data()
        await i.followup.send(embed=em("<:e_taxi:1519363380513603615> UHVAĆENI!", f"Policija je sve pohvatala! Svako je izgubio 200 coina.", color=COLORS["error"]))

# ─── <:e_phone:1519362788462559323> QR KOD ───
@bot.tree.command(name="qr", description="<:e_phone:1519362788462559323> Generiši QR kod iz teksta ili URL-a")
async def qr_cmd(i: discord.Interaction, tekst: str):
    url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={discord.utils.escape_markdown(tekst).replace(' ', '%20')}"
    e = discord.Embed(title="<:e_phone:1519362788462559323> QR Kod", description=f"```{tekst[:200]}```", color=COLORS["info"])
    e.set_image(url=url)
    e.set_footer(text=f"{BOT_NAME} • QR Generator")
    await i.response.send_message(embed=e)

# ─── <:e_lock3:1519362717394403432> CONFESS (anonimno) ───
# /confess uklonjeno (v2.1) — anonimnost se može zloupotrijebiti za uznemiravanje.

@set_group.command(name="kanal", description="<:e_gear:1519362652516782194>️ [ADMIN] Postavi confess/report/birthday/staff-apps kanal")
@app_commands.describe(tip="Tip kanala", kanal="Kanal za taj tip")
@app_commands.choices(tip=[
    app_commands.Choice(name="confess",    value="confess_channel"),
    app_commands.Choice(name="report",     value="report_channel"),
    app_commands.Choice(name="birthday",   value="birthday_channel"),
    app_commands.Choice(name="staff-apps", value="staff_apps_channel"),
])
async def setchannel_cmd(i: discord.Interaction, tip: app_commands.Choice[str], kanal: discord.TextChannel):
    if not i.user.guild_permissions.administrator:
        return await i.response.send_message("<:icon_cross:1519358379917836508> Samo admin.", ephemeral=True)
    get_guild_config(i.guild.id)[tip.value] = kanal.id; save_data()
    await i.response.send_message(embed=em("<:icon_check:1519358376268533810>", f"{tip.name.capitalize()} kanal: {kanal.mention}", color=COLORS["success"]), ephemeral=True)

bot.tree.add_command(set_group)

# ═══════════════════════════════════════════
#    🎯 AUTO BINGO — svakih 3h u chatu
# ═══════════════════════════════════════════
@tasks.loop(hours=3)
async def auto_game_loop():
    for guild in bot.guilds:
        chan = discord.utils.get(guild.text_channels, name="chat")
        if not chan: continue

        pool = list(range(1, 76))
        random.shuffle(pool)
        izvuceni = pool[:20]
        session = {"drawn": izvuceni, "players": {}}

        now_str = datetime.now(timezone.utc).strftime("%H:%M")
        e = discord.Embed(
            title="🎯  <:e_diamond3:1519363370694738072>  B  I  N  G  O  <:e_diamond3:1519363370694738072>  🎯",
            description=(
                "🎯 **Klikni dugme ispod i unesi 5 brojeva (1–75)!**\n"
                "<:e_ticket3:1519362637534597221> Tiket košta samo **500 coina** <:e_coins3:1519362621206298666>\n\n"
                "<:e_time2:1519362726952964227>️ Imaš **2 minute** za tiket — brzo! <:e_fire2:1519362671491678280>\n"
                "<:e_mega2:1519362736566304818> Rezultati se objavljuju **javno** za sve <:e_globe2:1519362694887637004>"
            ),
            color=_LP,
            timestamp=datetime.now(timezone.utc),
        )
        e.add_field(
            name="<:e_trophy2:1519362624742232146>  Nagradna lista",
            value=(
                "<:icon_rank3:1519358517633355919> `2 pogotka`  ──  **10.000** coina\n"
                "<:icon_rank2:1519358512336212091> `3 pogotka`  ──  **30.000** coina\n"
                "<:e_star2:1519363084253266031> `4 pogotka`  ──  **75.000** coina\n"
                "<:e_crown2:1519363047163166922> `5 pogodaka` ── **250.000** coina  <:e_trophy2:1519362624742232146> **JACKPOT!**"
            ),
            inline=False,
        )
        e.set_footer(text=f"🎯 × GIAN Auto-Bingo • svakih 3h • danas u {now_str} UTC")

        view = AutoBingoPupView(session)
        try:
            bingo_msg = await chan.send(embed=e, view=view)
            view.message = bingo_msg
        except: continue

        await asyncio.sleep(120)

        if not view.is_finished():
            view.stop()
        # Zaključaj dugme na originalnoj poruci
        try:
            await bingo_msg.edit(view=None)
        except: pass
        # Objavi javne rezultate
        await _bingo_reveal(session, chan)

@auto_game_loop.before_loop
async def _auto_game_wait(): await bot.wait_until_ready()

# ═══════════════════════════════════════════
#    <:e_trophy2:1519362624742232146> ACTIVE MEMBER OF THE WEEK
# ═══════════════════════════════════════════
@tasks.loop(hours=24)
async def active_member_week():
    """Svaki ponedjeljak u 12:00 UTC objavi najaktivnijeg člana sedmice."""
    now = datetime.now(timezone.utc)
    if now.weekday() != 0 or now.hour != 12:
        return
    last = data.get("aotw_last")
    today_str = now.strftime("%Y-%m-%d")
    if last == today_str:
        return
    for guild in bot.guilds:
        cfg = get_guild_config(guild.id)
        weekly = data.get("msg_count_week", {})
        gprefix = f"{guild.id}:"
        gusers = [(k.split(":")[1], v) for k, v in weekly.items() if k.startswith(gprefix)]
        if not gusers:
            continue
        gusers.sort(key=lambda x: x[1], reverse=True)
        top_uid, top_count = gusers[0]
        try:
            top_member = guild.get_member(int(top_uid)) or await guild.fetch_member(int(top_uid))
        except: continue
        if not top_member: continue
        ch = guild.get_channel(cfg.get("welcome_channel") or 1494687347558715543) or guild.system_channel
        if not ch: continue
        # Bonus: 500 coina + 100 XP
        mkey = f"{guild.id}:{top_member.id}"
        data["money"][mkey] = data["money"].get(mkey, 0) + 500
        add_xp(top_member.id, 100)
        e = discord.Embed(
            title="<:e_trophy2:1519362624742232146> ᴀᴄᴛɪᴠᴇ ᴍᴇᴍʙᴇʀ ᴏꜰ ᴛʜᴇ ᴡᴇᴇᴋ <:e_trophy2:1519362624742232146>",
            description=(
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<:e_crown2:1519363047163166922> Najaktivniji član ove sedmice je:\n\n"
                f"## {top_member.mention}\n\n"
                f"<:e_bubble:1519363307998417148> Napisao/la **{top_count:,}** poruka u zadnjih 7 dana!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"<:e_gift:1519362618341462067> **Nagrada:** `+500 coina` <:e_coins3:1519362621206298666> + `+100 XP` <:e_bolt:1519362674717102160>\n"
                f"<:e_flower:1519362984818901173> Hvala što si dio × GIAN porodice!"
            ),
            color=_LP, timestamp=now
        )
        e.set_thumbnail(url=top_member.display_avatar.url)
        # Top 3
        top3 = gusers[:3]
        leaderboard = ""
        medals = ["<:e_star2:1519363084253266031>", "<:icon_rank2:1519358512336212091>", "<:icon_rank3:1519358517633355919>"]
        for i, (uid, cnt) in enumerate(top3):
            mem = guild.get_member(int(uid))
            if mem:
                leaderboard += f"{medals[i]} {mem.mention} — `{cnt:,}` poruka\n"
        if leaderboard:
            e.add_field(name="<:e_chart:1519362656568475880> Top 3 sedmice", value=leaderboard, inline=False)
        e.set_footer(text=f"{BOT_NAME} • Sljedeći AOTW za 7 dana <:e_cal:1519362659676455046>")
        try:
            await ch.send(embed=e)
        except Exception as _e: print(f"[AOTW] {_e}")
    # Resetuj weekly counter
    data["msg_count_week"] = {}
    data["aotw_last"] = today_str
    save_data()

@active_member_week.before_loop
async def _aotw_wait(): await bot.wait_until_ready()

# ─── 🎯 RUČNI BINGO ───
@bot.tree.command(name="bingo", description="Pokreni Bingo — klikni dugme, unesi 5 brojeva i osvoji nagradu!")
async def bingo_cmd(i: discord.Interaction):
    if i.user.id not in OWNER_IDS:
        return await i.response.send_message(
            embed=em("<:e_crown2:1519363047163166922> Nemaš pristup!", "Komandu `/bingo` može pokrenuti samo **Vlasnik** bota.", color=COLORS["error"]),
            ephemeral=True,
        )
    pool = list(range(1, 76))
    random.shuffle(pool)
    izvuceni = pool[:20]
    session = {"drawn": izvuceni, "players": {}}

    now_str = datetime.now(timezone.utc).strftime("%H:%M")
    e = discord.Embed(
        title="🎯  <:e_diamond3:1519363370694738072>  B  I  N  G  O  <:e_diamond3:1519363370694738072>  🎯",
        description=(
            "🎯 **Klikni dugme ispod i unesi 5 brojeva (1–75)!**\n"
            "<:e_ticket3:1519362637534597221> Tiket košta samo **500 coina** <:e_coins3:1519362621206298666>\n\n"
            "<:e_time2:1519362726952964227>️ Imaš **2 minute** za tiket — brzo! <:e_fire2:1519362671491678280>\n"
            "<:e_mega2:1519362736566304818> Rezultati se objavljuju **javno** za sve <:e_globe2:1519362694887637004>"
        ),
        color=_LP,
        timestamp=datetime.now(timezone.utc),
    )
    e.set_author(name=f"🎯 Pokrenuo/la: {i.user.display_name}", icon_url=i.user.display_avatar.url)
    e.add_field(
        name="<:e_trophy2:1519362624742232146>  Nagradna lista",
        value=(
            "<:icon_rank3:1519358517633355919> `2 pogotka`  ──  **10.000** coina\n"
            "<:icon_rank2:1519358512336212091> `3 pogotka`  ──  **30.000** coina\n"
            "<:e_star2:1519363084253266031> `4 pogotka`  ──  **75.000** coina\n"
            "<:e_crown2:1519363047163166922> `5 pogodaka` ── **250.000** coina  <:e_trophy2:1519362624742232146> **JACKPOT!**"
        ),
        inline=False,
    )
    e.set_footer(text=f"🎯 × GIAN Bingo • danas u {now_str} UTC • Cijena tiketa: 500 coina <:e_coins3:1519362621206298666>")

    view = AutoBingoPupView(session)
    await i.response.send_message(embed=e, view=view)
    view.message = await i.original_response()

    await asyncio.sleep(120)

    if not view.is_finished():
        view.stop()
    # Zaključaj dugme na originalnoj poruci
    try:
        await view.message.edit(view=None)
    except: pass
    # Objavi javne rezultate u istom kanalu
    await _bingo_reveal(session, i.channel)


# ═══════════════════════════════════════════
#    <:e_ticket3:1519362637534597221>️ PUP — BINGO LISTIĆ (dugme + modal)
# ═══════════════════════════════════════════
# Nagrade: 2=10k | 3=30k | 4=75k | 5=250k (JACKPOT)
# Cijena listića: 500 coina | Brojevi: 1-75 | Izvlači se 20
# ═══════════════════════════════════════════

PUP_CIJENA = 500
PUP_NAGRADE = {2: 10_000, 3: 30_000, 4: 75_000, 5: 250_000}
PUP_XP      = {2: 50,     3: 100,    4: 200,     5: 500}

class PupModal(discord.ui.Modal, title="<:e_ticket3:1519362637534597221>️ Unesi 5 brojeva (1–75)"):
    brojevi_input = discord.ui.TextInput(
        label="Unesi 5 različitih brojeva odvojenih razmakom",
        placeholder="Primjer:  7  15  33  55  72",
        min_length=5,
        max_length=30,
        style=discord.TextStyle.short,
    )

    def __init__(self, session: dict):
        super().__init__()
        self.session = session

    async def on_submit(self, i: discord.Interaction):
        uid = i.user.id

        # ── Provjera duplikata ──
        if uid in self.session["players"]:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Već si uzeo/la tiket", "Možeš uzeti samo jedan tiket po bingu!", color=COLORS["error"]),
                ephemeral=True,
            )

        # ── Parsiranje ──
        parts = self.brojevi_input.value.strip().split()
        if len(parts) != 5:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Pogrešan unos", "Moraš unijeti **tačno 5 brojeva**!\n<:e_idea:1519363006599794799> Primjer: `7 15 33 55 72`", color=COLORS["error"]),
                ephemeral=True,
            )
        try:
            odabrani = [int(x) for x in parts]
        except ValueError:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Pogrešan unos", "Svi unosi moraju biti **cijeli brojevi**!", color=COLORS["error"]),
                ephemeral=True,
            )
        if any(n < 1 or n > 75 for n in odabrani):
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Broj izvan raspona", "Svi brojevi moraju biti između **1** i **75**!", color=COLORS["error"]),
                ephemeral=True,
            )
        if len(set(odabrani)) != 5:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Duplikati", "Svih 5 brojeva mora biti **različito**!", color=COLORS["error"]),
                ephemeral=True,
            )

        # ── Balans ──
        eco = get_economy(uid)
        if eco.get("balance", 0) < PUP_CIJENA:
            return await i.response.send_message(
                embed=em(
                    "<:icon_cross:1519358379917836508> Nema dovoljno coina",
                    f"Cijena listića je **{PUP_CIJENA:,} coina**.\n"
                    f"Tvoj balans: **{eco.get('balance', 0):,}** coina <:e_moneywing:1519362955437805771>\n\n"
                    f"Zaradi više sa `/posao` ili `/daily`!",
                    color=COLORS["error"],
                ),
                ephemeral=True,
            )

        # ── Oduzmi cijenu i sačuvaj tiket (bez otkrivanja rezultata!) ──
        eco["balance"] = eco.get("balance", 0) - PUP_CIJENA
        self.session["players"][uid] = {"brojevi": odabrani, "user": i.user.display_name, "avatar": str(i.user.display_avatar.url)}
        save_data()

        # ── Potvrda — rezultati se otkrivaju tek nakon 2 minute ──
        potvrda = discord.Embed(
            title="<:e_ticket3:1519362637534597221>️  Tiket primljen!  <:icon_check:1519358376268533810>",
            description=(
                f"<:e_check2:1519362730057007268>️ Tvoji brojevi su **tajno zabilježeni** i čekaju kraj runde!\n"
                f"<:e_pray:1519363406078021863> Drži fige i čekaj objavu!"
            ),
            color=_LP,
            timestamp=datetime.now(timezone.utc),
        )
        potvrda.add_field(
            name="<:e_chart:1519362656568475880>  Tvoji odabrani brojevi",
            value=" ".join(f"`{n:02d}`" for n in sorted(odabrani)),
            inline=False,
        )
        potvrda.add_field(name="<:e_coins3:1519362621206298666>  Plaćeno", value=f"**{PUP_CIJENA:,} coina** <:e_coins3:1519362621206298666>", inline=True)
        potvrda.add_field(name="<:e_time2:1519362726952964227>  Rezultati", value="**za ~2 minute** — javno! <:e_mega2:1519362736566304818>", inline=True)
        potvrda.set_footer(text="🎯 × GIAN Bingo • Sreće ti! <:e_clover:1519363694549667881>")
        await i.response.send_message(embed=potvrda, ephemeral=True)


async def _bingo_reveal(session: dict, channel: discord.TextChannel):
    """Nakon 2 minute — javno objavi rezultate za sve igrače."""
    drawn     = sorted(session["drawn"])
    drawn_set = set(drawn)
    players   = session.get("players", {})

    # ── Red izvučenih 20 brojeva (vizualni prikaz) ──
    drawn_display = " ".join(f"`{n:02d}`" for n in drawn)

    if not players:
        e = discord.Embed(
            title="🎯  Bingo — Runda završena",
            description="<:e_cry:1519362944717160530> **Niko nije uzeo tiket ovaj put.**\n<:e_idea:1519363006599794799> Sljedeći auto-bingo za **~3 sata**! <:e_time2:1519362726952964227>",
            color=_LP,
            timestamp=datetime.now(timezone.utc),
        )
        e.add_field(
            name="<:e_dice2:1519362633763913931>  Izvučenih 20 brojeva",
            value=drawn_display,
            inline=False,
        )
        e.set_footer(text="🎯 × GIAN Bingo • Budi brži/a idući put! <:e_clover:1519363694549667881>")
        try:
            await channel.send(embed=e)
        except Exception:
            pass
        return

    # ── Izračunaj rezultate za svakog igrača ──
    results      = []
    total_prizes = 0
    jackpot_uid  = None

    for uid_str, info in players.items():
        uid     = int(uid_str)
        odabrani = info["brojevi"] if isinstance(info, dict) else info
        ime      = info["user"]    if isinstance(info, dict) else f"Igrač#{uid}"
        pogoci   = sorted(set(odabrani) & drawn_set)
        br       = len(pogoci)
        nagrada  = PUP_NAGRADE.get(br, 0)
        xp_n     = PUP_XP.get(br, 0)

        if nagrada > 0:
            eco = get_economy(uid)
            eco["balance"] = eco.get("balance", 0) + nagrada
            add_xp(uid, xp_n)
            total_prizes += nagrada
            if br == 5:
                jackpot_uid = uid

        results.append({
            "uid": uid, "ime": ime,
            "odabrani": sorted(odabrani), "pogoci": pogoci,
            "br": br, "nagrada": nagrada,
        })

    save_data()

    # ── Sortiraj po broju pogodaka (desc) ──
    results.sort(key=lambda x: x["br"], reverse=True)

    # ── Napravi listu rezultata ──
    icon = {0: "<:e_wind:1519362878300229883>", 1: "<:e_wind:1519362878300229883>", 2: "<:e_coins3:1519362621206298666>", 3: "<:e_coins3:1519362621206298666><:e_coins3:1519362621206298666>", 4: "<:e_coins3:1519362621206298666><:e_coins3:1519362621206298666><:e_coins3:1519362621206298666>", 5: "<:e_trophy2:1519362624742232146>"}
    medal = {0: "▫️", 1: "▫️", 2: "<:icon_rank3:1519358517633355919>", 3: "<:icon_rank2:1519358512336212091>", 4: "<:e_star2:1519363084253266031>", 5: "<:e_crown2:1519363047163166922>"}
    rows = []
    for r in results:
        br_icon   = icon.get(r["br"], "")
        med       = medal.get(r["br"], "▫️")
        odab_str  = " ".join(f"`{n:02d}`" for n in r["odabrani"])
        pogoc_str = " ".join(f"**`{n:02d}`**" for n in r["pogoci"]) if r["pogoci"] else "`—`"
        nagrada_str = f"**+{r['nagrada']:,} coina** <:e_coins3:1519362621206298666>" if r["nagrada"] > 0 else "_bez nagrade_"
        rows.append(
            f"{med} {br_icon} **{r['ime']}**  •  {r['br']}/5 <:e_check2:1519362730057007268>  •  {nagrada_str}\n"
            f"> <:e_chart:1519362656568475880> {odab_str}\n"
            f"> 🎯 Pogoci: {pogoc_str}"
        )

    results_txt = "\n\n".join(rows) if rows else "*Niko nije igrao.*"

    title = "<:e_trophy2:1519362624742232146>  <:e_diamond3:1519363370694738072>  J A C K P O T  <:e_diamond3:1519363370694738072>  <:e_trophy2:1519362624742232146>" if jackpot_uid else "🎯  <:e_diamond3:1519363370694738072>  B I N G O  —  Rezultati  <:e_diamond3:1519363370694738072>"
    color=_LP if jackpot_uid else 0xF1C40F

    e = discord.Embed(
        title=title,
        description="<:e_party:1519363028334674070> Runda je gotova! Pogledaj ko je pobijedio!" if total_prizes > 0 else "Ovaj put nema pobjednika. Sreće idući put!",
        color=color,
        timestamp=datetime.now(timezone.utc),
    )
    e.add_field(
        name="<:e_dice2:1519362633763913931>  Izvučenih 20 brojeva",
        value=drawn_display,
        inline=False,
    )
    e.add_field(name=f"<:e_clipboard:1519363052871614627>  Rezultati  ({len(results)} igrača)", value=results_txt[:1020], inline=False)
    if total_prizes > 0:
        e.add_field(name="<:e_coins3:1519362621206298666>  Ukupno podijeljeno", value=f"**{total_prizes:,} coina** <:e_coins3:1519362621206298666>", inline=True)
        e.add_field(name="<:e_medal3:1519363547514015764>  Pobjednici", value=f"**{sum(1 for r in results if r['nagrada'] > 0)}** igrača", inline=True)
    e.set_footer(text="🎯 × GIAN Bingo • Čestitamo pobjednicima! <:e_party:1519363028334674070>")
    try:
        await channel.send(embed=e)
    except Exception:
        pass


class AutoBingoPupView(discord.ui.View):
    """View za auto bingo loop — dugme Uzmi tiket otvara modal."""
    def __init__(self, session: dict):
        super().__init__(timeout=120)
        self.session = session
        self.message: discord.Message | None = None

    @discord.ui.button(label="Uzmi tiket", emoji="🎯", style=discord.ButtonStyle.primary)
    async def uzmi_tiket(self, i: discord.Interaction, _btn: discord.ui.Button):
        await i.response.send_modal(PupModal(self.session))

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

# ═══════════════════════════════════════════
#    <:e_chart:1519362656568475880> USAGE TRACKING — broji koliko se koja komanda koristi
# ═══════════════════════════════════════════

# ═══════════════════════════════════════════
#    <:e_speaker:1519363314524881048> PRIVATE VOICE — Join To Create
# ═══════════════════════════════════════════
JTC_VOICE_ID = 1494043959213953114  # Glavni "Kreiraj svoj kanal" voice
PVC_INFO_CHANNEL_ID = 1494043958681145570  # Kanal gdje se postavlja uputstvo
data.setdefault("private_voices", {})  # {channel_id: owner_id}
data.setdefault("pvc_info_posted", False)

async def post_pvc_info():
    """Jednom postavi lijep uputstvo embed u info kanal."""
    if data.get("pvc_info_posted"): return
    for guild in bot.guilds:
        ch = guild.get_channel(PVC_INFO_CHANNEL_ID)
        if not ch: continue
        try:
            sep = "━━━━━━━━━━━━━━━━━━━━━━"
            e = discord.Embed(
                title="<:e_speaker:1519363314524881048> ᴋᴀᴋᴏ ᴋᴏʀɪꜱᴛɪᴛɪ ᴘʀɪᴠᴀᴛɴɪ ᴠᴏɪᴄᴇ?",
                description=(
                    f"{sep}\n"
                    f"<:e_idea:1519363006599794799> Napravi **svoj vlastiti voice kanal** koji možeš zaključati, sakriti, "
                    f"renamati, postaviti limit i još mnogo toga!\n"
                    f"{sep}"
                ),
                color=_LP
            )
            e.add_field(
                name="1️⃣ Kako napraviti svoj kanal",
                value=(
                    f"<:e_right:1519363367712591922> Uđi u voice kanal **<:e_speaker:1519363314524881048> Kreiraj svoj kanal** <#{JTC_VOICE_ID}>\n"
                    f"<:e_right:1519363367712591922> Bot će ti **automatski** napraviti privatni voice\n"
                    f"<:e_right:1519363367712591922> I **odmah** te prebaciti u njega\n"
                    f"<:e_right:1519363367712591922> Postaješ **vlasnik** <:e_crown2:1519363047163166922> i dobijaš kontrolni panel!\n{sep}"
                ),
                inline=False
            )
            e.add_field(
                name="2️⃣ Kontrolni panel (dugmad u tvom VC-u)",
                value=(
                    "<:e_lock3:1519362717394403432> **Lock** — niko ne može ući u tvoj kanal\n"
                    "<:e_unlock2:1519362720506449960> **Unlock** — svi mogu ući\n"
                    "<:e_eye:1519362936777478326>️ **Hide** — sakrij kanal od svih\n"
                    "<:e_eyes:1519362845970530577> **Show** — vrati kanal vidljiv\n"
                    "<:e_pencil:1519363059909398610>️ **Rename** — promijeni ime kanala\n"
                    "<:e_users:1519363096601301120> **Limit** — postavi max broj članova (1-99)\n"
                    "<:icon_ban:1519358278356959284> **Kick** — izbaci nekog iz tvog kanala\n"
                    "<:e_crown2:1519363047163166922> **Owner** — prebaci vlasništvo na drugog\n"
                    "<:icon_cross:1519358379917836508> **Delete** — odmah obriši kanal\n"
                    f"{sep}"
                ),
                inline=False
            )
            e.add_field(
                name="3️⃣ Automatsko brisanje",
                value=(
                    "<:e_trash:1519362951247691898>️ Kad **svi izađu**, kanal se **automatski briše**\n"
                    "<:e_floppy:1519363015147913396> Ne brini o čišćenju — bot to radi za tebe!\n"
                    f"{sep}"
                ),
                inline=False
            )
            e.add_field(
                name="<:e_idea:1519363006599794799> Korisni Tip",
                value=(
                    "<:e_sparkles:1519363032185176198> Lock + Hide = potpuno privatan VC samo za tebe i prijatelje\n"
                    "<:e_ctrl:1519362682296209498> Pozovi prijatelje preko **Invite to channel** desnim klikom\n"
                    "<:e_crown2:1519363047163166922> Prebaci vlasništvo prije izlaska ako želiš da kanal ostane"
                ),
                inline=False
            )
            e.set_footer(text=f"{BOT_NAME} • Privatni Voice Sistem <:e_speaker:1519363314524881048>")
            e.set_thumbnail(url="https://cdn.discordapp.com/emojis/963322998568083477.gif")
            await ch.send(embed=e)
            data["pvc_info_posted"] = True
            save_data()
        except Exception as _e:
            print(f"[pvc-info] {_e}")

class PrivateVCPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def _check_owner(self, interaction):
        ch = interaction.user.voice.channel if interaction.user.voice else None
        if not ch or str(ch.id) not in data.get("private_voices", {}):
            await interaction.response.send_message("<:icon_cross:1519358379917836508> Nisi u privatnom voice kanalu!", ephemeral=True)
            return None
        if data["private_voices"][str(ch.id)] != interaction.user.id:
            await interaction.response.send_message("<:icon_cross:1519358379917836508> Nisi vlasnik ovog kanala!", ephemeral=True)
            return None
        return ch

    @discord.ui.button(label="<:e_lock3:1519362717394403432> Lock", style=discord.ButtonStyle.danger, custom_id="pvc_lock")
    async def lock(self, i: discord.Interaction, b):
        ch = await self._check_owner(i)
        if not ch: return
        await ch.set_permissions(i.guild.default_role, connect=False)
        await i.response.send_message("<:e_lock3:1519362717394403432> Kanal **zaključan** — niko ne može ući!", ephemeral=True)

    @discord.ui.button(label="<:e_unlock2:1519362720506449960> Unlock", style=discord.ButtonStyle.success, custom_id="pvc_unlock")
    async def unlock(self, i: discord.Interaction, b):
        ch = await self._check_owner(i)
        if not ch: return
        await ch.set_permissions(i.guild.default_role, connect=None)
        await i.response.send_message("<:e_unlock2:1519362720506449960> Kanal **otključan** — svi mogu ući!", ephemeral=True)

    @discord.ui.button(label="<:e_eye:1519362936777478326>️ Hide", style=discord.ButtonStyle.secondary, custom_id="pvc_hide")
    async def hide(self, i: discord.Interaction, b):
        ch = await self._check_owner(i)
        if not ch: return
        await ch.set_permissions(i.guild.default_role, view_channel=False)
        await i.response.send_message("<:e_eye:1519362936777478326>️ Kanal **sakriven** — niko ga ne vidi!", ephemeral=True)

    @discord.ui.button(label="<:e_eyes:1519362845970530577> Show", style=discord.ButtonStyle.secondary, custom_id="pvc_show")
    async def show(self, i: discord.Interaction, b):
        ch = await self._check_owner(i)
        if not ch: return
        await ch.set_permissions(i.guild.default_role, view_channel=None)
        await i.response.send_message("<:e_eyes:1519362845970530577> Kanal **vidljiv** svima!", ephemeral=True)

    @discord.ui.button(label="<:e_pencil:1519363059909398610>️ Rename", style=discord.ButtonStyle.primary, custom_id="pvc_rename")
    async def rename(self, i: discord.Interaction, b):
        ch = await self._check_owner(i)
        if not ch: return
        modal = discord.ui.Modal(title="<:e_pencil:1519363059909398610>️ Promijeni ime kanala")
        name_in = discord.ui.TextInput(label="Novo ime", placeholder="<:e_speaker:1519363314524881048> Moj kanal", max_length=50)
        modal.add_item(name_in)
        async def cb(m_int):
            await ch.edit(name=name_in.value)
            await m_int.response.send_message(f"<:icon_check:1519358376268533810> Ime promijenjeno u: **{name_in.value}**", ephemeral=True)
        modal.on_submit = cb
        await i.response.send_modal(modal)

    @discord.ui.button(label="<:e_users:1519363096601301120> Limit", style=discord.ButtonStyle.primary, custom_id="pvc_limit")
    async def limit(self, i: discord.Interaction, b):
        ch = await self._check_owner(i)
        if not ch: return
        modal = discord.ui.Modal(title="<:e_users:1519363096601301120> Postavi limit članova")
        lim_in = discord.ui.TextInput(label="Broj (0 = bez limita, max 99)", placeholder="5")
        modal.add_item(lim_in)
        async def cb(m_int):
            try: n = max(0, min(99, int(lim_in.value)))
            except: return await m_int.response.send_message("<:icon_cross:1519358379917836508> Mora biti broj!", ephemeral=True)
            await ch.edit(user_limit=n)
            await m_int.response.send_message(f"<:icon_check:1519358376268533810> Limit postavljen na **{n}** {'(bez limita)' if n==0 else 'članova'}", ephemeral=True)
        modal.on_submit = cb
        await i.response.send_modal(modal)

    @discord.ui.button(label="<:icon_ban:1519358278356959284> Kick", style=discord.ButtonStyle.danger, custom_id="pvc_kick", row=1)
    async def kick(self, i: discord.Interaction, b):
        ch = await self._check_owner(i)
        if not ch: return
        if not ch.members or len([m for m in ch.members if m.id != i.user.id]) == 0:
            return await i.response.send_message("<:icon_cross:1519358379917836508> Nema nikog za izbacit!", ephemeral=True)
        opts = [discord.SelectOption(label=m.display_name, value=str(m.id))
                for m in ch.members if m.id != i.user.id][:25]
        sel = discord.ui.Select(placeholder="Izaberi koga da izbaciš", options=opts)
        async def sel_cb(s_int):
            mid = int(sel.values[0])
            mem = ch.guild.get_member(mid)
            if mem and mem.voice and mem.voice.channel == ch:
                await mem.move_to(None)
                await s_int.response.send_message(f"<:icon_ban:1519358278356959284> {mem.mention} izbačen iz kanala!", ephemeral=True)
            else:
                await s_int.response.send_message("<:icon_cross:1519358379917836508> Već nije u kanalu.", ephemeral=True)
        sel.callback = sel_cb
        view = discord.ui.View(timeout=60)
        view.add_item(sel)
        await i.response.send_message("Izaberi člana:", view=view, ephemeral=True)

    @discord.ui.button(label="<:e_crown2:1519363047163166922> Owner", style=discord.ButtonStyle.secondary, custom_id="pvc_transfer", row=1)
    async def transfer(self, i: discord.Interaction, b):
        ch = await self._check_owner(i)
        if not ch: return
        opts = [discord.SelectOption(label=m.display_name, value=str(m.id))
                for m in ch.members if m.id != i.user.id and not m.bot][:25]
        if not opts:
            return await i.response.send_message("<:icon_cross:1519358379917836508> Nema nikog kome bi prebacio vlasništvo!", ephemeral=True)
        sel = discord.ui.Select(placeholder="Novi vlasnik", options=opts)
        async def sel_cb(s_int):
            new_id = int(sel.values[0])
            new_owner = ch.guild.get_member(new_id)
            data["private_voices"][str(ch.id)] = new_id
            save_data()
            await ch.set_permissions(i.user, overwrite=None)
            await ch.set_permissions(new_owner, manage_channels=True, move_members=True, mute_members=True, deafen_members=True)
            await s_int.response.send_message(f"<:e_crown2:1519363047163166922> Vlasništvo prebačeno na {new_owner.mention}!", ephemeral=True)
        sel.callback = sel_cb
        view = discord.ui.View(timeout=60)
        view.add_item(sel)
        await i.response.send_message("Izaberi novog vlasnika:", view=view, ephemeral=True)

    @discord.ui.button(label="<:icon_cross:1519358379917836508> Delete", style=discord.ButtonStyle.danger, custom_id="pvc_delete", row=1)
    async def delete(self, i: discord.Interaction, b):
        ch = await self._check_owner(i)
        if not ch: return
        await i.response.send_message("<:icon_cross:1519358379917836508> Brišem kanal za 3s...", ephemeral=True)
        await asyncio.sleep(3)
        try:
            data["private_voices"].pop(str(ch.id), None)
            save_data()
            await ch.delete(reason="Vlasnik obrisao privatni VC")
        except: pass

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot: return
    # ── KREIRAJ NOVI PRIVATNI VC ──
    if after.channel and after.channel.id == JTC_VOICE_ID:
        new_ch = None
        try:
            cat = after.channel.category
            me = member.guild.me
            # ── Provjera permisija ──
            missing = []
            if not me.guild_permissions.manage_channels: missing.append("Manage Channels")
            if not me.guild_permissions.move_members:    missing.append("Move Members")
            if cat is not None:
                cat_perms = cat.permissions_for(me)
                if not cat_perms.manage_channels: missing.append("Manage Channels (kategorija)")
                if not cat_perms.connect:         missing.append("Connect (kategorija)")
            if missing:
                msg = f"Botu nedostaju permisije: **{', '.join(missing)}**"
                print(f"[pvc create] <:e_cross2:1519362733613776967> {msg}")
                try: await member.send(f"<:icon_cross:1519358379917836508> Ne mogu napraviti tvoj voice kanal.\n{msg}")
                except: pass
                return
            # ── Kreiraj kanal (fallback bez kategorije ako je puna) ──
            try:
                new_ch = await member.guild.create_voice_channel(
                    name=f"<:e_speaker:1519363314524881048> {member.display_name}",
                    category=cat,
                    reason=f"Privatni VC za {member}"
                )
            except discord.HTTPException as he:
                if (he.code == 30013) or ("Maximum number" in str(he)):
                    print(f"[pvc create] kategorija puna → pravim bez kategorije")
                    new_ch = await member.guild.create_voice_channel(
                        name=f"<:e_speaker:1519363314524881048> {member.display_name}",
                        reason=f"Privatni VC za {member} (bez kategorije)"
                    )
                else:
                    raise
            await new_ch.set_permissions(member, manage_channels=True, move_members=True,
                mute_members=True, deafen_members=True, connect=True, view_channel=True)
            data["private_voices"][str(new_ch.id)] = member.id
            save_data()
            await member.move_to(new_ch)
            print(f"[pvc create] <:e_check2:1519362730057007268> {member} → {new_ch.name} ({new_ch.id})")
            # Pošalji panel u kanal (text chat unutar VC-a, Discord 2024+ feature)
            try:
                e = discord.Embed(
                    title=f"<:e_speaker:1519363314524881048> Dobrodošao u svoj kanal, {member.display_name}!",
                    description=(
                        "**Ti si vlasnik!** <:e_crown2:1519363047163166922> Koristi dugmad ispod:\n\n"
                        "<:e_lock3:1519362717394403432> **Lock** — niko ne može ući\n"
                        "<:e_unlock2:1519362720506449960> **Unlock** — svi mogu ući\n"
                        "<:e_eye:1519362936777478326>️ **Hide / Show** — sakrij/pokaži kanal\n"
                        "<:e_pencil:1519363059909398610>️ **Rename** — promijeni ime\n"
                        "<:e_users:1519363096601301120> **Limit** — postavi max članova\n"
                        "<:icon_ban:1519358278356959284> **Kick** — izbaci nekog iz kanala\n"
                        "<:e_crown2:1519363047163166922> **Owner** — prebaci vlasništvo\n"
                        "<:icon_cross:1519358379917836508> **Delete** — obriši kanal\n\n"
                        "*Kanal se automatski briše kad ostane prazan.*"
                    ),
                    color=COLORS.get("balkan", 0x9B59B6)
                )
                e.set_footer(text=f"{BOT_NAME} • Privatni Voice Sistem")
                await new_ch.send(content=member.mention, embed=e, view=PrivateVCPanel())
            except Exception as _e: print(f"[pvc panel] {_e}")
        except Exception as _e:
            import traceback
            print(f"[pvc create] <:e_cross2:1519362733613776967> {type(_e).__name__}: {_e}")
            traceback.print_exc()
            try: await member.send(f"<:icon_cross:1519358379917836508> Greška pri kreiranju voice kanala:\n```{type(_e).__name__}: {_e}```")
            except: pass

    # ── OBRIŠI PRAZAN PRIVATNI VC ──
    if before.channel and str(before.channel.id) in data.get("private_voices", {}):
        if len([m for m in before.channel.members if not m.bot]) == 0:
            try:
                data["private_voices"].pop(str(before.channel.id), None)
                save_data()
                await before.channel.delete(reason="Privatni VC prazan")
            except Exception as _e: print(f"[pvc delete] {_e}")

    # napomena: tree.error handler je gore (on_app_error)

@bot.event
async def on_app_command_completion(interaction, command):
    try:
        n = command.qualified_name if hasattr(command, "qualified_name") else command.name
        data["cmd_uses"][n] = data["cmd_uses"].get(n, 0) + 1
    except Exception: pass

# ─── <:e_report2:1519362714198347886> REPORT — 1 minuta cooldown po članu ───
@bot.tree.command(name="report", description="<:e_report2:1519362714198347886> Prijavi člana staffu (1x u minuti)")
@app_commands.describe(korisnik="Koga prijavljuješ", razlog="Razlog prijave (kratko i jasno)")
@app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
async def report_cmd(i: discord.Interaction, korisnik: discord.Member, razlog: str):
    if korisnik.id == i.user.id:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Greška", "Ne možeš prijaviti samog sebe.", color=COLORS["error"]),
            ephemeral=True
        )
    if korisnik.bot:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Greška", "Botove ne možeš prijaviti.", color=COLORS["error"]),
            ephemeral=True
        )

    # ── Sigurnost: ukloni eventualne invite linkove iz razloga ──
    safe_razlog = INVITE_REGEX.sub("[link uklonjen]", razlog[:1000])
    # ── Sigurnost: očisti ime servera od potencijalnih linkova ──
    safe_guild_name = INVITE_REGEX.sub("[link]", i.guild.name) if i.guild else "—"

    cfg = get_guild_config(i.guild.id)
    ch_id = cfg.get("report_channel")
    target_ch = i.guild.get_channel(ch_id) if ch_id else None

    e = discord.Embed(
        title="<:e_report2:1519362714198347886> NOVA PRIJAVA",
        color=COLORS["error"],
        timestamp=discord.utils.utcnow(),
    )
    e.add_field(name="<:e_user:1519363093736718518> Prijavio",   value=f"{i.user.mention}\n`{i.user}`\nID: `{i.user.id}`",     inline=True)
    e.add_field(name="🎯 Prijavljen", value=f"{korisnik.mention}\n`{korisnik}`\nID: `{korisnik.id}`", inline=True)
    e.add_field(name="<:e_pin:1519363329259208836> Kanal",      value=i.channel.mention if i.channel else "—",                  inline=True)
    e.add_field(name="📝 Razlog",     value=safe_razlog,                                               inline=False)
    try:
        e.set_thumbnail(url=korisnik.display_avatar.url)
    except Exception: pass
    e.set_footer(text=f"Server: {safe_guild_name}")

    sent = False
    if target_ch:
        try:
            await target_ch.send(embed=e)
            sent = True
        except Exception: pass

    if not sent:
        for oid in OWNER_IDS:
            try:
                u = await bot.fetch_user(oid)
                await u.send(embed=e)
                sent = True
            except Exception: pass

    if sent:
        await i.response.send_message(
            embed=em("<:icon_check:1519358376268533810> Prijava poslata", "Staff je obaviješten. Hvala!\n\n*Možeš ponovo prijaviti za 1 minutu.*", color=COLORS["success"]),
            ephemeral=True
        )
    else:
        await i.response.send_message(
            embed=em("<:icon_warning:1519358274284032030>️ Nije poslato", "Ne mogu poslati prijavu.\nReci adminu: `/set kanal tip:report kanal:#kanal`", color=COLORS["warning"]),
            ephemeral=True
        )

@report_cmd.error
async def report_cmd_error(i: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        secs = int(error.retry_after)
        try:
            await i.response.send_message(
                embed=em("<:e_time2:1519362726952964227> Sačekaj", f"Možeš opet prijaviti za **{secs}s**.\n*Limit: 1 prijava u minuti po članu.*", color=COLORS["warning"]),
                ephemeral=True
            )
        except Exception: pass
    else:
        try:
            await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Greška", f"`{error}`", color=COLORS["error"]),
                ephemeral=True
            )
        except Exception: pass

# ═══════════════════════════════════════════
#    <:e_clipboard:1519363052871614627> STAFF PRIJAVA — /tiket-staff
# ═══════════════════════════════════════════

class StaffApplicationModal(discord.ui.Modal, title="<:e_clipboard:1519363052871614627> Prijava za Staff"):
    god = discord.ui.TextInput(
        label="Koliko imaš godina?",
        placeholder="Npr: 18",
        min_length=1, max_length=3,
        style=discord.TextStyle.short,
    )
    iskustvo = discord.ui.TextInput(
        label="Imaš li iskustva kao mod/staff?",
        placeholder="Opiši prethodno iskustvo na Discordu...",
        min_length=10, max_length=500,
        style=discord.TextStyle.paragraph,
    )
    zasto = discord.ui.TextInput(
        label="Zašto želiš biti staff?",
        placeholder="Reci nam šta te motiviše...",
        min_length=20, max_length=600,
        style=discord.TextStyle.paragraph,
    )
    igraci = discord.ui.TextInput(
        label="Koliko igrača možeš dovesti na server?",
        placeholder="Npr: 5-10, imam Discord/Instagram zajednicu...",
        min_length=5, max_length=300,
        style=discord.TextStyle.paragraph,
    )
    aktivnost = discord.ui.TextInput(
        label="Koliko sati dnevno + timezone zona?",
        placeholder="Npr: 3-5 sati, CET zona...",
        min_length=3, max_length=200,
        style=discord.TextStyle.short,
    )

    async def on_submit(self, i: discord.Interaction):
        guild     = i.guild
        safe_name = "".join(c for c in i.user.name.lower() if c.isalnum() or c in "-_")[:20] or str(i.user.id)

        # Provjeri već postojeću prijavu
        existing = discord.utils.get(guild.text_channels, name=f"prijava-{safe_name}")
        if existing:
            return await i.response.send_message(
                embed=em("<:icon_warning:1519358274284032030>️ Već prijavljen/a", f"Imaš već aktivnu prijavu: {existing.mention}", color=COLORS["warning"]),
                ephemeral=True,
            )

        if not guild.me.guild_permissions.manage_channels:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Permisija", "Bot nema **Manage Channels** permisiju! Javi adminu.", color=COLORS["error"]),
                ephemeral=True,
            )

        # <:e_lock3:1519362717394403432> PRIVATNO — vidi SAMO vlasnik bota + aplikant (po želji korisnika)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False, send_messages=False, add_reactions=False
            ),
            i.user: discord.PermissionOverwrite(
                read_messages=True, send_messages=False, add_reactions=False
            ),
            guild.me: discord.PermissionOverwrite(
                read_messages=True, send_messages=True, manage_channels=True
            ),
        }
        # Dodaj sve OWNER-e iz OWNER_IDS whiteliste
        for owner_id in OWNER_IDS:
            owner_member = guild.get_member(owner_id)
            if owner_member:
                overwrites[owner_member] = discord.PermissionOverwrite(
                    read_messages=True, send_messages=True, add_reactions=True, manage_channels=True
                )
        # Dodaj i vlasnika servera (guild.owner) da uvijek vidi
        if guild.owner and guild.owner.id not in OWNER_IDS:
            overwrites[guild.owner] = discord.PermissionOverwrite(
                read_messages=True, send_messages=True, add_reactions=True
            )

        # Kategorija: "Staff Prijave" → "Prijave" → "Tickets" → bez kategorije
        category = (
            discord.utils.find(lambda c: any(w in c.name.lower() for w in ("staff prijav", "prijav")), guild.categories) or
            discord.utils.find(lambda c: "ticket" in c.name.lower(), guild.categories)
        )

        try:
            chan = await guild.create_text_channel(
                f"prijava-{safe_name}",
                overwrites=overwrites,
                category=category,
                reason=f"Staff prijava od {i.user}",
                topic=f"<:e_clipboard:1519363052871614627> Staff prijava — {i.user.display_name} ({i.user.id})",
            )
        except discord.Forbidden:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Permisija", "Bot nema dozvolu da kreira kanale!", color=COLORS["error"]),
                ephemeral=True,
            )
        except Exception as ex:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Greška", f"`{ex}`", color=COLORS["error"]),
                ephemeral=True,
            )

        BAR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        e = discord.Embed(
            title="<:e_clipboard:1519363052871614627>  Nova Staff Prijava",
            description=(
                f"{BAR}\n"
                f"<:e_user:1519363093736718518> **{i.user.display_name}** ({i.user.mention})\n"
                f"🆔 ID: `{i.user.id}`\n"
                f"<:e_cal:1519362659676455046> Nalog: <t:{int(i.user.created_at.timestamp())}:R>\n"
                f"<:e_internet:1519363106395000994> Server: **{guild.name}**\n"
                f"{BAR}"
            ),
            color=_LP,
            timestamp=datetime.now(timezone.utc),
        )
        e.set_thumbnail(url=i.user.display_avatar.url)
        e.set_author(
            name=f"× GIAN — STAFF PRIJAVA",
            icon_url=guild.me.display_avatar.url,
        )
        e.add_field(name="<:e_party:1519363028334674070>  Godine",               value=self.god.value,       inline=True)
        e.add_field(name="<:e_time2:1519362726952964227>  Aktivnost / Zona",     value=self.aktivnost.value,  inline=True)
        e.add_field(name="<:e_books:1519363612978839642>  Iskustvo kao Staff",   value=self.iskustvo.value,   inline=False)
        e.add_field(name="<:e_bubble:1519363307998417148>  Zašto želi biti Staff", value=self.zasto.value,     inline=False)
        e.add_field(name="<:e_users:1519363096601301120>  Koliko igrača dovodi",  value=self.igraci.value,    inline=False)
        e.add_field(
            name="<:e_pushpin:1519363357436543099>  Obaveze Staffa",
            value=(
                "<:icon_check:1519358376268533810> Dovodiš nove igrače na server\n"
                "<:icon_check:1519358376268533810> Redovito si aktivan/na u chatovima\n"
                "<:icon_check:1519358376268533810> Pomažeš moderirati i primjenjuješ pravila\n"
                "<:icon_check:1519358376268533810> Štitis server od raida, napada i spama\n"
                "<:icon_check:1519358376268533810> Komuniciraš s timom i prijaviš probleme"
            ),
            inline=False,
        )
        e.add_field(
            name="<:icon_stats:1519358289173807246>️  Glasanje Admina",
            value=(
                "<:icon_check:1519358376268533810> **Prihvati** — dodjeljuje StaffTeam ulogu\n"
                "<:icon_cross:1519358379917836508> **Odbij** — zatvara kanal\n"
                "<:e_time2:1519362726952964227> **Na čekanju** — čeka više informacija"
            ),
            inline=False,
        )
        e.set_footer(text=f"<:e_lock3:1519362717394403432> GIAN Staff Prijava  •  {guild.name}  •  PRIVATNO — vidi samo vlasnik")

        await chan.send(
            content=f"<:e_lock3:1519362717394403432> **Nova staff prijava od {i.user.mention}** — vidljivo samo vlasniku <:e_down:1519363345252090081>",
            embed=e,
            view=StaffVoteView(),
        )

        # Ako postoji konfigurisani staff_apps kanal — pošalji i tamo (ping za admina)
        cfg = get_guild_config(guild.id)
        notify_id = cfg.get("staff_apps_channel") or cfg.get("log_channel")
        notify_ch = guild.get_channel(notify_id) if notify_id else None
        if notify_ch and notify_ch != chan:
            try:
                notif = discord.Embed(
                    title="<:e_bell:1519363063738925187> Nova Staff Prijava",
                    description=f"**{i.user.display_name}** je podnio/la prijavu!\n<:e_folder:1519363642808729690> Pogledaj: {chan.mention}",
                    color=_LP,
                )
                await notify_ch.send(embed=notif)
            except Exception:
                pass

        potvrda = discord.Embed(
            title="<:icon_check:1519358376268533810>  Prijava primljena!",
            description=(
                f"## <:e_party:1519363028334674070> Uspješno si se prijavio/la za Staff!\n"
                f"<:e_folder:1519363642808729690> Tvoja prijava je objavljena: {chan.mention}\n\n"
                f"<:e_lock3:1519362717394403432> Tvoja prijava je **privatna** — vidi je samo vlasnik bota.\n"
                f"<:e_time2:1519362726952964227> Pregled traje **1–3 dana**. Budemo te obavijestili! <:e_invite2:1519362710469476405>"
            ),
            color=_LP,
            timestamp=datetime.now(timezone.utc),
        )
        potvrda.add_field(
            name="<:e_clipboard:1519363052871614627>  Šta se čeka od Staffa",
            value=(
                "<:e_users:1519363096601301120> Dovodiš nove igrače i rasteš zajednicu\n"
                "<:e_shield2:1519362627795554374>️ Štitis server od raida, napada i spama\n"
                "<:e_bubble:1519363307998417148> Modiraš chatove i primjenjuješ pravila\n"
                "<:e_time2:1519362726952964227> Admin ručno pregleda prijavu i dodjeljuje ulogu\n"
                "<:e_shake:1519362947766554737> Nema automatskih permisija — sve odobrava Admin!"
            ),
            inline=False,
        )
        potvrda.set_footer(text="<:e_clipboard:1519363052871614627> GIAN  •  Hvala na prijavi! <:e_pray:1519363406078021863>")
        await i.response.send_message(embed=potvrda, ephemeral=True)


class StaffVoteView(discord.ui.View):
    """Admin glasanje za staff prijavu — Prihvati / Odbij / Na čekanju.
    custom_id-ovi su statični → view preživljava bot restart.
    applicant_id se čita direktno iz embed opisa poruke."""
    def __init__(self):
        super().__init__(timeout=None)

    @staticmethod
    def _extract_aid(message) -> int:
        """Izvuci ID prijavljenog iz embeda poruke."""
        if message and message.embeds:
            import re as _re
            m = _re.search(r'ID: `(\d+)`', message.embeds[0].description or "")
            if m:
                return int(m.group(1))
        return 0

    @staticmethod
    async def _auto_close_channel(channel, delay: int = 10):
        """Briše 'prijava-*' kanal nakon zadatog delayas."""
        if channel and channel.name.startswith("prijava-"):
            await asyncio.sleep(delay)
            try:
                await channel.delete(reason="Staff prijava završena — auto-close")
            except Exception:
                pass

    @discord.ui.button(label="Prihvati", emoji="<:icon_check:1519358376268533810>", style=discord.ButtonStyle.success, custom_id="sv_prihvati")
    async def prihvati(self, i: discord.Interaction, b: discord.ui.Button):
        if not i.user.guild_permissions.manage_roles:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Nemaš permisiju!", "Samo Staff/Admini mogu glasati.", color=COLORS["error"]),
                ephemeral=True,
            )
        aid = self._extract_aid(i.message)
        for child in self.children: child.disabled = True
        await i.message.edit(view=self)
        if aid:
            try:
                member = i.guild.get_member(aid) or await i.guild.fetch_member(aid)
                dm_e = discord.Embed(
                    title="<:e_party:1519363028334674070>  Čestitamo — Primljeni si u Staff!",
                    description=(
                        f"## <:icon_check:1519358376268533810> Tvoja prijava na **{i.guild.name}** je **PRIHVAĆENA**!\n\n"
                        f"Kontaktiraj administratora da dobiješ Staff ulogu.\n"
                        f"Dobrodošao/la u tim! <:e_shake:1519362947766554737><:e_shield2:1519362627795554374>️"
                    ),
                    color=_LP,
                    timestamp=datetime.now(timezone.utc),
                )
                dm_e.set_footer(text=f"<:e_clipboard:1519363052871614627> {i.guild.name}  •  GIAN Bot")
                await member.send(embed=dm_e)
            except Exception:
                pass
        await i.response.send_message(
            embed=em("<:icon_check:1519358376268533810> Prijava prihvaćena!",
                     "Kandidat je obaviješten putem DM-a.\n"
                     "<:icon_warning:1519358274284032030>️ **Ulogu dodijeli ručno** — bot ne daje nikakve permisije automatski!\n"
                     "<:e_trash:1519362951247691898>️ Kanal se briše za **10 sekundi**.",
                     color=COLORS["success"]),
            ephemeral=True,
        )
        asyncio.create_task(self._auto_close_channel(i.channel, delay=10))

    @discord.ui.button(label="Odbij", emoji="<:icon_cross:1519358379917836508>", style=discord.ButtonStyle.danger, custom_id="sv_odbij")
    async def odbij(self, i: discord.Interaction, b: discord.ui.Button):
        if not i.user.guild_permissions.manage_roles:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Nemaš permisiju!", "Samo Staff/Admini mogu glasati.", color=COLORS["error"]),
                ephemeral=True,
            )
        aid = self._extract_aid(i.message)
        for child in self.children: child.disabled = True
        await i.message.edit(view=self)
        if aid:
            try:
                member = i.guild.get_member(aid) or await i.guild.fetch_member(aid)
                dm_e = discord.Embed(
                    title="<:e_clipboard:1519363052871614627>  Staff Prijava — Odgovor",
                    description=(
                        f"## <:icon_cross:1519358379917836508> Nažalost, tvoja prijava na **{i.guild.name}** je **ODBIJENA**.\n\n"
                        f"Možeš pokušati ponovo za **30 dana**.\n"
                        f"Ne odustaji — nastavite biti aktivni! <:e_muscle:1519362764244652122>"
                    ),
                    color=_LP,
                    timestamp=datetime.now(timezone.utc),
                )
                dm_e.set_footer(text=f"<:e_clipboard:1519363052871614627> {i.guild.name}  •  GIAN Bot")
                await member.send(embed=dm_e)
            except Exception:
                pass
        await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Prijava odbijena.",
                     "Kandidat je obaviješten putem DM-a.\n"
                     "<:e_trash:1519362951247691898>️ Kanal se briše za **10 sekundi**.",
                     color=COLORS["error"]),
            ephemeral=True,
        )
        asyncio.create_task(self._auto_close_channel(i.channel, delay=10))

    @discord.ui.button(label="Na čekanju", emoji="<:e_time2:1519362726952964227>", style=discord.ButtonStyle.secondary, custom_id="sv_cekanje")
    async def na_cekanju(self, i: discord.Interaction, b: discord.ui.Button):
        if not i.user.guild_permissions.manage_roles:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Nemaš permisiju!", "Samo Staff/Admini mogu glasati.", color=COLORS["error"]),
                ephemeral=True,
            )
        await i.response.send_message(
            embed=em("<:e_time2:1519362726952964227> Na čekanju!",
                     "Prijava je stavljena na čekanje za daljnju diskusiju.\n"
                     "<:e_bubble:1519363307998417148> Razgovarajte u ovom kanalu i onda glasajte!",
                     color=COLORS["warning"]),
            ephemeral=True,
        )


# ═══════════════════════════════════════════
#    <:e_clipboard:1519363052871614627> STAFF PRIJAVA PANEL — /tiketstaff
#    Postavlja PUBLIČNU panel poruku u kanal (vidi je svako).
#    Ispod je 5 dugmadi (rubrika) — klikom član popunjava polje za polje,
#    ili klikom na "<:e_clipboard:1519363052871614627> Prijavi se" odmah otvara modal sa svih 5 polja.
# ═══════════════════════════════════════════
def _staff_draft_store():
    if "staff_draft" not in data: data["staff_draft"] = {}
    return data["staff_draft"]

def _staff_draft(guild_id: int, user_id: int) -> dict:
    s = _staff_draft_store()
    k = f"{guild_id}:{user_id}"
    if k not in s: s[k] = {}
    return s[k]

class _OnePoljeModal(discord.ui.Modal):
    def __init__(self, polje_kljuc: str, polje_label: str, placeholder: str, paragraph: bool = False):
        super().__init__(title=f"<:e_clipboard:1519363052871614627> {polje_label}"[:45])
        self.polje_kljuc = polje_kljuc
        self.tekst = discord.ui.TextInput(
            label=polje_label[:45],
            placeholder=placeholder[:100],
            style=discord.TextStyle.paragraph if paragraph else discord.TextStyle.short,
            min_length=1, max_length=600 if paragraph else 200,
        )
        self.add_item(self.tekst)

    async def on_submit(self, i: discord.Interaction):
        d = _staff_draft(i.guild.id, i.user.id)
        d[self.polje_kljuc] = str(self.tekst.value)
        save_data()
        popunjeno = sum(1 for k in ("god","iskustvo","zasto","igraci","aktivnost") if d.get(k))
        await i.response.send_message(
            embed=em("<:icon_check:1519358376268533810> Sačuvano",
                     f"Polje **{self.polje_kljuc}** sačuvano.\n"
                     f"Popunjeno: **{popunjeno}/5**\n\n"
                     f"Kad popuniš sve, klikni dugme **<:e_box:1519363099478458498> Pošalji prijavu**.",
                     color=COLORS["success"]),
            ephemeral=True,
        )

class TiketStaffPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="<:e_chart:1519362656568475880> Godine", style=discord.ButtonStyle.secondary, custom_id="ts_god", row=0)
    async def b_god(self, i, b):
        await i.response.send_modal(_OnePoljeModal("god", "Koliko imaš godina?", "Npr: 18"))

    @discord.ui.button(label="<:e_shield2:1519362627795554374>️ Iskustvo", style=discord.ButtonStyle.secondary, custom_id="ts_isk", row=0)
    async def b_isk(self, i, b):
        await i.response.send_modal(_OnePoljeModal("iskustvo", "Imaš li iskustva kao mod/staff?",
                                                  "Opiši prethodno iskustvo na Discordu...", paragraph=True))

    @discord.ui.button(label="<:e_bubble:1519363307998417148> Motivacija", style=discord.ButtonStyle.secondary, custom_id="ts_mot", row=0)
    async def b_mot(self, i, b):
        await i.response.send_modal(_OnePoljeModal("zasto", "Zašto želiš biti staff?",
                                                  "Reci nam šta te motiviše...", paragraph=True))

    @discord.ui.button(label="<:e_users:1519363096601301120> Igrači", style=discord.ButtonStyle.secondary, custom_id="ts_igr", row=1)
    async def b_igr(self, i, b):
        await i.response.send_modal(_OnePoljeModal("igraci", "Koliko igrača možeš dovesti?",
                                                  "Npr: 5-10, imam zajednicu...", paragraph=True))

    @discord.ui.button(label="<:e_time2:1519362726952964227> Aktivnost", style=discord.ButtonStyle.secondary, custom_id="ts_akt", row=1)
    async def b_akt(self, i, b):
        await i.response.send_modal(_OnePoljeModal("aktivnost", "Sati dnevno + timezone",
                                                  "Npr: 3-5 sati, CET..."))

    @discord.ui.button(label="<:e_box:1519363099478458498> Pošalji prijavu", style=discord.ButtonStyle.success, custom_id="ts_send", row=2)
    async def b_send(self, i: discord.Interaction, b):
        d = _staff_draft(i.guild.id, i.user.id)
        nedostaje = [k for k in ("god","iskustvo","zasto","igraci","aktivnost") if not d.get(k)]
        if nedostaje:
            return await i.response.send_message(
                embed=em("<:icon_warning:1519358274284032030>️ Nedostaju polja",
                         "Popuni sva polja prije slanja:\n• " + ", ".join(nedostaje),
                         color=COLORS["warning"]),
                ephemeral=True,
            )
        # Provjeri reklamu u poljima
        spojeno = " ".join(d.values())
        if INVITE_REGEX.search(spojeno):
            return await i.response.send_message(
                embed=em("<:icon_ban:1519358278356959284> Reklama zabranjena",
                         "Discord invite linkovi (`discord.gg/...`, `.gg/...`) nisu dozvoljeni u prijavi!",
                         color=COLORS["error"]),
                ephemeral=True,
            )
        # Pošalji kroz isti tok kao stari modal
        fake_modal = StaffApplicationModal()
        # Override vrijednosti
        fake_modal.god._value      = d.get("god", "")
        fake_modal.iskustvo._value = d.get("iskustvo", "")
        fake_modal.zasto._value    = d.get("zasto", "")
        fake_modal.igraci._value   = d.get("igraci", "")
        fake_modal.aktivnost._value = d.get("aktivnost", "")
        await fake_modal.on_submit(i)
        # Obriši draft nakon uspješnog slanja
        try:
            _staff_draft_store().pop(f"{i.guild.id}:{i.user.id}", None)
            save_data()
        except: pass

    @discord.ui.button(label="<:e_trash:1519362951247691898>️ Resetuj polja", style=discord.ButtonStyle.danger, custom_id="ts_reset", row=2)
    async def b_reset(self, i, b):
        try:
            _staff_draft_store().pop(f"{i.guild.id}:{i.user.id}", None)
            save_data()
        except: pass
        await i.response.send_message(
            embed=em("<:e_trash:1519362951247691898>️ Resetovano", "Tvoja polja su obrisana.", color=COLORS["info"]),
            ephemeral=True,
        )


@bot.command(name="tiketstaff")
async def tiketstaff_cmd(ctx: commands.Context):
    if not ctx.author.guild_permissions.administrator and ctx.author.id not in OWNER_IDS:
        return await ctx.send(embed=em("<:icon_cross:1519358379917836508> Nemaš pristup", "Samo admin može postaviti panel.", color=COLORS["error"]))
    BAR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    e = discord.Embed(
        title="<:e_clipboard:1519363052871614627>  STAFF PRIJAVA",
        description=(
            f"{BAR}\n"
            f"Otvorene su prijave za **Staff tim** servera **{ctx.guild.name}**!\n\n"
            f"📝 **Kako se prijaviti:**\n"
            f"1️⃣  Klikni redom na **5 dugmadi** ispod i upiši svoje podatke\n"
            f"2️⃣  Kad popuniš **sva polja**, klikni **<:e_box:1519363099478458498> Pošalji prijavu**\n"
            f"3️⃣  Bot će ti otvoriti **privatni kanal** sa staff timom\n\n"
            f"<:e_lock3:1519362717394403432> Tvoji odgovori se vide samo tebi dok ne pošalješ prijavu.\n"
            f"<:icon_ban:1519358278356959284> **Discord invite linkovi nisu dozvoljeni** u poljima!\n"
            f"{BAR}"
        ),
        color=_LP, timestamp=datetime.now(timezone.utc),
    )
    e.add_field(name="<:e_pushpin:1519363357436543099> Rubrike", value=(
        "<:e_chart:1519362656568475880> **Godine** — koliko imaš godina\n"
        "<:e_shield2:1519362627795554374>️ **Iskustvo** — prethodno iskustvo\n"
        "<:e_bubble:1519363307998417148> **Motivacija** — zašto želiš staff\n"
        "<:e_users:1519363096601301120> **Igrači** — koliko ljudi možeš dovesti\n"
        "<:e_time2:1519362726952964227> **Aktivnost** — sati dnevno + timezone"
    ), inline=False)
    if ctx.guild.icon:
        e.set_thumbnail(url=ctx.guild.icon.url)
    e.set_footer(text=f"<:e_clipboard:1519363052871614627> {BOT_NAME} • Staff Prijava")
    try:
        await ctx.send(embed=e, view=TiketStaffPanelView())
    except discord.Forbidden:
        await ctx.send(embed=em("<:icon_cross:1519358379917836508> Permisija", "Bot nema dozvolu da piše u ovaj kanal!", color=COLORS["error"]))

# ═══════════════════════════════════════════
#    /INFO — Server info embed (owner only)
# ═══════════════════════════════════════════
@bot.command(name="info")
async def info_cmd(ctx: commands.Context):
    if ctx.author.id not in OWNER_IDS:
        return await ctx.send(embed=em("<:icon_cross:1519358379917836508> Nemaš pristup", "Ova komanda je dostupna samo vlasniku bota.", color=COLORS["error"]))

    BAR  = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
    LINE = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    e = discord.Embed(
        title="<:e_ctrl:1519362682296209498> <:e_diamond3:1519363370694738072> GIAN (Custom) — Komande <:e_diamond3:1519363370694738072> <:e_ctrl:1519362682296209498>",
        description=(
            f"```fix\n<:e_laptop:1519363516002467871> Kompjuter: /komanda   <:e_phone:1519362788462559323> Mobitel: .komanda```\n"
            f"{LINE}"
        ),
        color=COLORS["default"],
        timestamp=datetime.now(timezone.utc),
    )

    e.add_field(name="<:e_globe2:1519362694887637004> ═╡ B A L K A N  D U H ╞═ <:e_globe2:1519362694887637004>", value=(
        "> *Ovde nije važno odakle si, već kakav si.*\n"
        "> *Donesi smijeh, donesi kafu, donesi sebe.*\n"
        "> <:e_house:1519362841369378961> *Dobrodošao u GIAN — gdje svaka noć ima priču.*"
    ), inline=False)

    e.add_field(name=f"{BAR}\n<:e_ctrl:1519362682296209498>️ ═╡ K L A S I Č N E  I G R E ╞═ <:e_ctrl:1519362682296209498>️", value=(
        "<:e_hammer:1519362836671762494> `/kpm` `.kpm` — Kamen, Papir, Makaze\n"
        "<:e_slotm:1519362699014967297> `/slots [ulog]` `.slots [ulog]` — Slot mašina (20–1.000.000.000 <:e_coins3:1519362621206298666>)\n"
        "<:e_arrow:1519363399845154958> `/rulet` `.rulet` — Ruski rulet, za hrabre!\n"
        "<:e_cards2:1519362702835712010> `/blackjack` `.blackjack` — Blackjack protiv dilera\n"
        "<:e_dice2:1519362633763913931> `/kocka` `.kocka` — Baci kocku protiv nekog igrača"
    ), inline=False)

    e.add_field(name=f"{BAR}\n<:e_brain:1519362849548406975> ═╡ T R I V I A  &  Z N A N J E ╞═ <:e_brain:1519362849548406975>", value=(
        "<:e_question:1519362691813085386> `/kviz` `.kviz` — Balkan kviz, sa combo multiplierom!\n"
        "<:e_internet:1519363106395000994> `/geografija` `.geografija` — Geografski kviz sa combo sistemom"
    ), inline=False)

    e.add_field(name=f"{BAR}\n📝 ═╡ R I J E Č I  &  L O G I K A ╞═ 📝", value=(
        "<:e_link:1519363321458065408> `/vjasala` `.vjasala` — Vješala, pogodi skrivenu riječ\n"
        "<:e_link:1519363321458065408> `/kaladont` `.kaladont` — Ulančavanje riječi (kao Activity)\n"
        "<:e_stop:1519363022399995914> `/kaladont-stop` `.kaladont-stop` — Zaustavi Kaladont igru\n"
        "<:e_sun:1519362860218843399>️ `/toplo-hladno` `.toplo-hladno` — Pogodi tajni broj"
    ), inline=False)

    e.add_field(name=f"{BAR}\n<:e_users:1519363096601301120> ═╡ M U L T I P L A Y E R ╞═ <:e_users:1519363096601301120>", value=(
        "<:e_mega2:1519362736566304818> `/amogus` `.amogus` — Pokreni Among Us igru u kanalu\n"
        "<:icon_ban:1519358278356959284> `/amogus-stop` `.amogus-stop` — Zaustavi Among Us igru"
    ), inline=False)

    e.add_field(name=f"{BAR}\n<:e_chart:1519362656568475880> ═╡ B R O J A N J E ╞═ <:e_chart:1519362656568475880>", value=(
        "<:e_gear:1519362652516782194>️ `/set brojanje` — Postavi kanal *(ADMIN)*\n"
        "<:e_chart:1519362656568475880> `/brojanje-info` — Pokaži trenutno stanje\n"
        "<:e_refresh:1519362959187509461> `/set brojanje-reset` — Resetuj brojanje *(ADMIN)*"
    ), inline=False)

    e.add_field(name=f"{BAR}\n<:e_heart2:1519362668644012133> ═╡ S O C I J A L N E  &  L J U B A V N E ╞═ <:e_heart2:1519362668644012133>", value=(
        "<:e_shake:1519362947766554737> `/zagrljaj` `.zagrljaj` — Zagrli nekog\n"
        "<:e_heart2:1519362668644012133> `/poljubac` `.poljubac` — Pošalji poljubac\n"
        "<:e_heart2:1519362668644012133> `/mazi` `.mazi` — Pomazi nekog nježno\n"
        "<:e_shake:1519362947766554737> `/tapsi` `.tapsi` — Tapši nekog prijateljski\n"
        "<:e_pray:1519363406078021863> `/high5` `.high5` — Daj peticu\n"
        "<:e_heart2:1519362668644012133>️ `/srce` `.srce` — Pošalji srce nekome\n"
        "<:e_ring:1519362941617438750> `/brak` `.brak` — Zaprosi nekog *(za fun)*\n"
        "<:e_cherry:1519363439385116812> `/kompli` `.kompli` — Slatki kompliment\n"
        "<:e_dizzy:1519362812554510509> `/crush` `.crush` — Otkrij ko je tvoj tajni crush\n"
        "<:e_dizzy:1519362812554510509> `/cudan` `.cudan` — Razne reakcije"
    ), inline=False)

    e.add_field(name=f"{BAR}\n🇧🇦 ═╡ B A L K A N  S T I L ╞═ 🇧🇦", value=(
        "<:e_shake:1519362947766554737> `/pozz` `.pozz` — Pozdrav sa humorom\n"
        "<:e_sparkles:1519363032185176198> `/fora` `.fora` — Ubaci foru na nečiji račun\n"
        "<:e_crystal:1519362965558657146> `/muv` `.muv` — Muvaj nekog Balkan stilom"
    ), inline=False)

    e.add_field(name=f"{BAR}\n<:e_lion:1519363402890346658> ═╡ O W O  H U N T I N G ╞═ <:e_lion:1519363402890346658>", value=(
        "<:e_arrow:1519363399845154958> `/hunt` `.hunt` — Lovi divlje životinje\n"
        "<:e_deer2:1519362689212874883> `/zoo` `.zoo` — Pogledaj svoju zbirku\n"
        "<:e_sword2:1519362631146930317>️ `/battle` `.battle` — Bori se sa drugim igračem\n"
        "<:e_coins3:1519362621206298666> `/sell` `.sell` — Prodaj životinje za pare\n"
        "<:e_clipboard:1519363052871614627> `/animals` `.animals` — Lista svih životinja i raritet\n"
        "<:e_pray:1519363406078021863> `/pray` `.pray` — Pomoli se za nekog *(boost sreće)*"
    ), inline=False)

    e.add_field(name=f"{BAR}\n<:e_coins3:1519362621206298666> ═╡ E K O N O M I J A  &  X P ╞═ <:e_coins3:1519362621206298666>", value=(
        "<:e_coins3:1519362621206298666> `/baki` `.baki` — Provjeri stanje novca\n"
        "<:e_hammer:1519362836671762494> `/posao` `.posao` — Radi i zaradi *(svaki sat)*\n"
        "<:e_gift:1519362618341462067> `/daily` `.daily` — Dnevna nagrada\n"
        "<:e_box:1519363099478458498> `/daj` `.daj` — Pošalji pare drugaru\n"
        "<:e_skull2:1519362997443629186> `/kradi` `.kradi` — Pokušaj ukrasti pare *(rizično!)*\n"
        "<:e_level2:1519362739749785610> `/rank` `.rank` — Tvoj level i XP profil\n"
        "<:e_trophy2:1519362624742232146> `/leaderboard` `.leaderboard` — Top lista servera\n"
        "<:e_cart:1519362665347153930> `/shop` `.shop` — Pogledaj šta možeš kupiti\n"
        "<:e_bank2:1519362662515871744> `/kupi` `.kupi` — Kupi predmet iz shopa\n"
        "📝 `/quests` `.quests` — Tvoji dnevni zadaci"
    ), inline=False)

    e.add_field(name=LINE, value="<:e_sparkles:1519363032185176198> *Uživaj i budi dio ekipe!* <:e_sparkles:1519363032185176198>", inline=False)

    if ctx.guild and ctx.guild.icon:
        e.set_thumbnail(url=ctx.guild.icon.url)
    e.set_footer(text="<:e_ctrl:1519362682296209498> GIAN (Custom) • Komande", icon_url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None)

    try:
        await ctx.send(embed=e)
    except discord.Forbidden:
        await ctx.send(embed=em("<:icon_cross:1519358379917836508> Permisija", "Bot nema dozvolu da piše u ovaj kanal!", color=COLORS["error"]))


# ═══════════════════════════════════════════
#    .pravila — Pravilnik servera (owner only)
# ═══════════════════════════════════════════
@bot.command(name="pravila")
async def pravila_cmd(ctx: commands.Context):
    if ctx.author.id not in OWNER_IDS:
        return await ctx.send(embed=em("<:icon_cross:1519358379917836508> Nemaš pristup", "Ova komanda je dostupna samo vlasniku bota.", color=COLORS["error"]))

    e = discord.Embed(
        title="📝  P R A V I L N I K  S E R V E R A",
        description=(
            "Dobrodošli na **GIAN** zajednicu!\n"
            "Molimo pročitajte i poštujte sljedeća pravila."
        ),
        color=COLORS["default"],
        timestamp=datetime.now(timezone.utc),
    )

    e.add_field(name="<:e_shake:1519362947766554737>  Poštovanje članova", value=(
        "<:icon_ban:1519358278356959284> Zabranjeno vrijeđanje, maltretiranje i provociranje\n"
        "<:icon_cross:1519358379917836508> Nema rasizma, diskriminacije ni govora mržnje\n"
        "<:e_bubble:1519363307998417148> Poštuj tuđe mišljenje čak i kad se ne slažeš"
    ), inline=False)

    e.add_field(name="<:e_mute2:1519362648972595289>  Bez spama", value=(
        "<:e_repeat:1519363009883934740> Ne šalji iste poruke više puta\n"
        "<:e_user:1519363093736718518> Ne spamuj emojima, gifovima ni tagovanjem\n"
        "<:e_dolphin:1519363432615510078> Flood poruke nisu dozvoljene"
    ), inline=False)

    e.add_field(name="<:e_mega2:1519362736566304818>  Reklamiranje", value=(
        "<:e_link:1519363321458065408> Zabranjena reklama servera i mreža bez odobrenja admina\n"
        "<:e_invite2:1519362710469476405> Zabranjeno slanje reklama u DM porukama"
    ), inline=False)

    e.add_field(name="<:icon_ban:1519358278356959284>  Neprikladan sadržaj", value=(
        "<:e_stop:1519363022399995914> Nema nasilnih, šokantnih ni uznemirujućih slika\n"
        "<:icon_ban:1519358278356959284> NSFW sadržaj je zabranjen na cijelom serveru\n"
        "<:e_clipboard:1519363052871614627> Poštuj pravila Discord platforme i TOS"
    ), inline=False)

    e.add_field(name="<:e_folder:1519363642808729690>  Kanali", value=(
        "🎯 Koristi kanale za njihovu predviđenu svrhu\n"
        "<:e_gear:1519362652516782194> Komande za bota koristi u za to određenim kanalima"
    ), inline=False)

    e.add_field(name="<:e_shield2:1519362627795554374>️  Staff & Drama", value=(
        "<:icon_report:1519358353208508566> Odluke admina i moderatora su konačne\n"
        "<:e_ticket3:1519362637534597221> Za probleme koristi ticket sistem\n"
        "<:e_feather:1519363362322907218>️ Sporove rješavaj mirno — bez javnih svađa"
    ), inline=False)

    e.add_field(name="<:icon_warning:1519358274284032030>️  Kazne", value=(
        "`1.` <:icon_warning:1519358274284032030>️ Upozorenje  `2.` <:e_mute2:1519362648972595289> Mute  `3.` <:e_run:1519362884868636883> Kick  `4.` <:e_hammer:1519362836671762494> Ban"
    ), inline=False)

    e.add_field(name="<:e_sparkles:1519363032185176198>  Uživaj i budi dio ekipe!", value=(
        "Pravila postoje da bi se **svi** osjećali dobrodošlo.\n"
        "Poštuj druge, čuvaj atmosferu — **dobrodošao kući** <:e_house:1519362841369378961>"
    ), inline=False)

    if ctx.guild and ctx.guild.icon:
        e.set_thumbnail(url=ctx.guild.icon.url)
    e.set_footer(text="📝 GIAN • Pravilnik", icon_url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None)

    try:
        await ctx.send(embed=e)
    except discord.Forbidden:
        await ctx.send(embed=em("<:icon_cross:1519358379917836508> Permisija", "Bot nema dozvolu da piše u ovaj kanal!", color=COLORS["error"]))


# ─── <:e_speaker:1519363314524881048> PRAVILA VOICE (privatni voice kanali) ───
# ─── Panel Role Button — daje/uzima ulogu na klik ───────────────────────────
@bot.event
async def on_interaction(interaction: discord.Interaction):
    """Hvataj panel_role_{roleId} dugmad poslana iz GIAN panela."""
    if interaction.type != discord.InteractionType.component:
        return
    custom_id = (interaction.data or {}).get("custom_id", "")
    if not custom_id.startswith("panel_role_"):
        return
    parts = custom_id.split("_")
    if len(parts) < 3:
        return await interaction.response.send_message("<:icon_cross:1519358379917836508> Nevalidan ID dugmeta.", ephemeral=True)
    try:
        role_id = int(parts[2])
    except ValueError:
        return await interaction.response.send_message("<:icon_cross:1519358379917836508> Nevalidan ID uloge.", ephemeral=True)

    guild  = interaction.guild
    member = interaction.user
    if not guild or not isinstance(member, discord.Member):
        return await interaction.response.send_message("<:icon_cross:1519358379917836508> Greška — pokušaj na serveru.", ephemeral=True)

    role = guild.get_role(role_id)
    if not role:
        return await interaction.response.send_message("<:icon_cross:1519358379917836508> Uloga ne postoji!", ephemeral=True)
    if role >= guild.me.top_role:
        return await interaction.response.send_message(
            f"<:icon_cross:1519358379917836508> Ne mogu dodijeliti **{role.name}** — uloga je viša od moje. Admin: pomjeri me iznad nje.",
            ephemeral=True,
        )

    try:
        if role in member.roles:
            await member.remove_roles(role, reason="Panel role button — uklanjanje")
            await interaction.response.send_message(
                f"<:icon_check:1519358376268533810> Uloga **{role.name}** je uklonjena.", ephemeral=True
            )
        else:
            await member.add_roles(role, reason="Panel role button — dodavanje")
            await interaction.response.send_message(
                f"<:icon_check:1519358376268533810> Dobio si ulogu **{role.name}**!", ephemeral=True
            )
    except discord.Forbidden:
        await interaction.response.send_message("<:icon_cross:1519358379917836508> Bot nema permisiju za upravljanje ulogama.", ephemeral=True)
    except Exception as ex:
        await interaction.response.send_message(f"<:icon_cross:1519358379917836508> Greška: `{ex}`", ephemeral=True)


class VoiceCreateButton(discord.ui.View):
    """Dugme ispod /pravila-voice — kreira privatni VC na klik."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="<:e_speaker:1519363314524881048> Kreiraj svoj voice", style=discord.ButtonStyle.success, custom_id="vc_create_btn")
    async def create(self, i: discord.Interaction, b):
        guild = i.guild
        member = i.user
        # Ako već ima privatni VC, javi
        for ch_id_str, owner_id in data.get("private_voices", {}).items():
            if owner_id == member.id:
                ch = guild.get_channel(int(ch_id_str)) if guild else None
                if ch:
                    return await i.response.send_message(
                        embed=em("<:icon_warning:1519358274284032030>️ Već imaš kanal", f"Tvoj voice: {ch.mention}\nUđi i koristi panel za upravljanje.", color=COLORS["warning"]),
                        ephemeral=True,
                    )
        await i.response.defer(ephemeral=True, thinking=True)
        # Kategorija = ista kao JTC voice ili kao text kanal
        jtc = guild.get_channel(JTC_VOICE_ID) if guild else None
        cat = (jtc.category if jtc else None) or i.channel.category
        me = guild.me
        missing = []
        if not me.guild_permissions.manage_channels: missing.append("Manage Channels")
        if not me.guild_permissions.move_members:    missing.append("Move Members")
        if missing:
            return await i.followup.send(
                embed=em("<:icon_cross:1519358379917836508> Nedostaju permisije", f"Botu treba: **{', '.join(missing)}**", color=COLORS["error"]),
                ephemeral=True,
            )
        try:
            new_ch = None
            try:
                new_ch = await guild.create_voice_channel(
                    name=f"<:e_speaker:1519363314524881048> {member.display_name}",
                    category=cat,
                    reason=f"Privatni VC (dugme) za {member}"
                )
            except discord.HTTPException as he:
                if he.code == 30013 or "Maximum number" in str(he):
                    new_ch = await guild.create_voice_channel(
                        name=f"<:e_speaker:1519363314524881048> {member.display_name}",
                        reason=f"Privatni VC (dugme, bez kategorije) za {member}"
                    )
                else:
                    raise
            await new_ch.set_permissions(member, manage_channels=True, move_members=True,
                mute_members=True, deafen_members=True, connect=True, view_channel=True)
            data.setdefault("private_voices", {})[str(new_ch.id)] = member.id
            save_data()
            # Ako je već u nekom voice-u, prebaci ga
            try:
                if member.voice and member.voice.channel:
                    await member.move_to(new_ch)
            except: pass
            # Pošalji panel u sam voice kanal
            try:
                ev = discord.Embed(
                    title=f"<:e_speaker:1519363314524881048> Dobrodošao u svoj kanal, {member.display_name}!",
                    description=(
                        "**Ti si vlasnik!** <:e_crown2:1519363047163166922> Koristi dugmad ispod:\n\n"
                        "<:e_lock3:1519362717394403432> **Lock / Unlock** — kontrola ulaza\n"
                        "<:e_eye:1519362936777478326>️ **Hide / Show** — sakrij/pokaži\n"
                        "<:e_pencil:1519363059909398610>️ **Rename** • <:e_users:1519363096601301120> **Limit** • <:icon_ban:1519358278356959284> **Kick**\n"
                        "<:e_crown2:1519363047163166922> **Owner transfer** • <:icon_cross:1519358379917836508> **Delete**\n\n"
                        "*Kanal se automatski briše kad ostane prazan.*"
                    ),
                    color=COLORS.get("balkan", 0x9B59B6)
                )
                ev.set_footer(text=f"{BOT_NAME} • Privatni Voice Sistem")
                await new_ch.send(content=member.mention, embed=ev, view=PrivateVCPanel())
            except Exception as _e: print(f"[vc-btn panel] {_e}")
            await i.followup.send(
                embed=em("<:icon_check:1519358376268533810> Voice kreiran!", f"Tvoj kanal: {new_ch.mention}\n<:e_right:1519363367712591922> Klikni i pridruži se!", color=COLORS["success"]),
                ephemeral=True,
            )
            print(f"[vc-btn] <:e_check2:1519362730057007268> {member} → {new_ch.name}")
        except Exception as ex:
            import traceback; traceback.print_exc()
            await i.followup.send(
                embed=em("<:icon_cross:1519358379917836508> Greška", f"`{type(ex).__name__}: {ex}`", color=COLORS["error"]),
                ephemeral=True,
            )


@bot.command(name="pravila-voice")
async def pravila_voice_cmd(ctx: commands.Context):
    if ctx.author.id not in OWNER_IDS:
        return await ctx.send(embed=em("<:icon_cross:1519358379917836508> Nemaš pristup", "Ova komanda je dostupna samo vlasniku bota.", color=COLORS["error"]))

    # ── Fetch embed config from panel (fallback to hardcoded) ──
    _pv = await get_panel_embed("voice-pravila")

    if _pv:
        _vc = int((_pv.get("color") or "#2B2D3A").lstrip("#") or "2B2D3A", 16)
        e = discord.Embed(
            title=_pv.get("title") or "<:e_speaker:1519363314524881048>  P R I V A T N I  V O I C E  K A N A L I",
            description=_pv.get("description") or "",
            color=_vc,
            timestamp=datetime.now(timezone.utc),
        )
        for f in (_pv.get("fields") or []):
            e.add_field(name=f.get("name", ""), value=f.get("value", ""), inline=bool(f.get("inline", True)))
        if _pv.get("footer"):
            e.set_footer(text=_pv["footer"], icon_url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None)
        else:
            e.set_footer(text="<:e_speaker:1519363314524881048> GIAN • Voice Pravila", icon_url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None)
    else:
        e = discord.Embed(
            title="<:e_speaker:1519363314524881048>  P R I V A T N I  V O I C E  K A N A L I",
            description=(
                f"Uđi u <#{JTC_VOICE_ID}> i bot ti **automatski** kreira vlastiti voice kanal.\n"
                "Postaješ **vlasnik** <:e_crown2:1519363047163166922> i dobijaš puni kontrolni panel."
            ),
            color=COLORS["default"],
            timestamp=datetime.now(timezone.utc),
        )
        e.add_field(name="<:e_shake:1519362947766554737>  Ponašanje", value=(
            "<:icon_ban:1519358278356959284> Bez vrijeđanja, maltretiranja i rasizma\n"
            "<:e_speaker:1519363314524881048>️ Ne prekidaj druge dok pričaju\n"
            "<:e_mute2:1519362648972595289> Ne lupaj mikrofonom bez razloga"
        ), inline=True)
        e.add_field(name="<:e_crown2:1519363047163166922>  Vlasništvo", value=(
            "<:e_gear:1519362652516782194>️ Samo vlasnik koristi Lock / Hide / Kick panel\n"
            "<:e_repeat:1519363009883934740> Prebaci vlasništvo prije izlaska\n"
            "<:e_scales:1519362852853649439>️ Ne koristi panel za maltretiranje"
        ), inline=True)
        e.add_field(name="<:icon_ban:1519358278356959284>  Sadržaj & Imena", value=(
            "<:icon_ban:1519358278356959284> Bez NSFW sadržaja i streaminga\n"
            "<:e_pencil:1519363059909398610>️ Ime kanala mora biti pristojno\n"
            "<:e_clipboard:1519363052871614627> Vrijede sva opšta pravila servera"
        ), inline=True)
        e.add_field(name="<:e_trash:1519362951247691898>️  Automatsko brisanje", value=(
            "Kad svi izađu, bot **automatski briše** kanal.\n"
            "<:icon_report:1519358353208508566> Staff ima pristup svim kanalima zbog moderacije."
        ), inline=False)
        e.add_field(name="<:icon_warning:1519358274284032030>️  Kazne", value=(
            "`1.` <:icon_warning:1519358274284032030>️ Upozorenje  `2.` <:e_mute2:1519362648972595289> Voice mute  `3.` <:icon_ban:1519358278356959284> Zabrana voice-a  `4.` <:e_run:1519362884868636883> Kick / <:e_hammer:1519362836671762494> Ban"
        ), inline=False)
        e.set_footer(text="<:e_speaker:1519363314524881048> GIAN • Voice Pravila", icon_url=ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None)

    if ctx.guild and ctx.guild.icon:
        e.set_thumbnail(url=ctx.guild.icon.url)

    # ── Build view — optionally use panel button label ──
    view = VoiceCreateButton()
    if _pv:
        _btns = _pv.get("buttons") or []
        if _btns and view.children:
            _bc = _btns[0]
            view.children[0].label = _bc.get("label", "<:e_speaker:1519363314524881048> Kreiraj svoj voice")

    try:
        await ctx.send(embed=e, view=view)
    except discord.Forbidden:
        await ctx.send(embed=em("<:icon_cross:1519358379917836508> Permisija", "Bot nema dozvolu da piše u ovaj kanal!", color=COLORS["error"]))


# ─── <:e_refresh:1519362959187509461> SYNC — manualno ponovno učitavanje slash komandi ───
@bot.tree.command(name="sync", description="<:e_refresh:1519362959187509461> Force-sync svih slash komandi (samo vlasnik)")
@app_commands.describe(scope="global = svi serveri (~1h cache), guild = ovaj server (odmah)")
@app_commands.choices(scope=[
    app_commands.Choice(name="guild (samo ovaj server, odmah)", value="guild"),
    app_commands.Choice(name="global (svi serveri, do 1h cache)", value="global"),
    app_commands.Choice(name="both (oba)", value="both"),
])
async def sync_cmd(i: discord.Interaction, scope: app_commands.Choice[str] = None):
    if i.user.id not in OWNER_IDS:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Nemaš pristup", "Ova komanda je dostupna samo vlasniku bota.", color=COLORS["error"]),
            ephemeral=True,
        )
    await i.response.defer(ephemeral=True)
    sc = scope.value if scope else "both"
    results = []
    # GUILD sync (instant)
    if sc in ("guild", "both") and i.guild:
        try:
            bot.tree.copy_global_to(guild=i.guild)
            synced = await bot.tree.sync(guild=i.guild)
            results.append(f"<:icon_check:1519358376268533810> **Guild sync ({i.guild.name}):** {len(synced)} komandi (odmah dostupne)")
        except Exception as e:
            results.append(f"<:icon_cross:1519358379917836508> **Guild sync error:** `{e}`")
    # GLOBAL sync (cached)
    if sc in ("global", "both"):
        try:
            synced = await bot.tree.sync()
            data["_last_synced_count"] = len(synced)
            save_data()
            results.append(f"<:icon_check:1519358376268533810> **Global sync:** {len(synced)} komandi (cache do 1h)")
        except Exception as e:
            results.append(f"<:icon_cross:1519358379917836508> **Global sync error:** `{e}`")
    e = discord.Embed(
        title="<:e_refresh:1519362959187509461> Sync rezultati",
        description="\n".join(results) if results else "Ništa nije sinhronizovano.",
        color=COLORS["success"],
        timestamp=datetime.now(timezone.utc),
    )
    e.set_footer(text=f"{BOT_NAME} • Force Sync")
    await i.followup.send(embed=e, ephemeral=True)


# ═══════════════════════════════════════════
#    <:e_masks:1519363003424706671> MAFIA IGRA — sve sa embedima i klikabilnim dugmadima
#    /mafia       — pokreni novu igru u kanalu (lobby)
#    Igra ima 4–12 igrača, uloge: Civil / Mafia / Doktor / Detektiv
#    Faze: <:e_moon:1519363445466595522> Noć (DM komande) → <:e_sun:1519362860218843399>️ Dan (rasprava) → <:icon_stats:1519358289173807246>️ Glasanje
# ═══════════════════════════════════════════
MAFIA_GAMES: dict[int, "MafiaGame"] = {}   # channel_id -> game

class MafiaGame:
    def __init__(self, channel: discord.TextChannel, host: discord.Member):
        self.channel  = channel
        self.host     = host
        self.players: list[discord.Member] = [host]
        self.alive:   set[int]             = set()
        self.roles:   dict[int, str]       = {}   # uid -> role
        self.actions: dict[str, int]       = {}   # "mafia_kill"/"doc_heal"/"det_check" -> uid
        self.vote_msgs: dict[int, int]     = {}   # voter -> target
        self.day      = 0
        self.phase    = "lobby"   # lobby/night/day/vote/over
        self.lock     = asyncio.Lock()
        self.task: asyncio.Task | None = None

    def alive_players(self) -> list[discord.Member]:
        return [p for p in self.players if p.id in self.alive]

    def role_of(self, uid: int) -> str:
        return self.roles.get(uid, "civil")

    def alive_with_role(self, role: str) -> list[discord.Member]:
        return [p for p in self.alive_players() if self.role_of(p.id) == role]

    def winner(self) -> str | None:
        mafia = len(self.alive_with_role("mafia"))
        rest  = len(self.alive_players()) - mafia
        if mafia == 0:                return "civili"
        if mafia >= rest:             return "mafia"
        return None

    def assign_roles(self):
        n = len(self.players)
        ids = [p.id for p in self.players]
        random.shuffle(ids)
        n_mafia = 1 if n <= 6 else 2 if n <= 10 else 3
        # Specijalne uloge se dodaju kako raste broj igrača
        specials = ["doktor", "detektiv"]
        if n >= 6: specials.append("serif")        # <:icon_report:1519358353208508566> Šerif (1 hitac noću)
        if n >= 8: specials.append("saljivdzija")  # <:e_cards2:1519362702835712010> Šaljivdžija (pobjeđuje ako ga linčuju)
        n_civil = max(0, n - n_mafia - len(specials))
        roles = (["mafia"] * n_mafia + specials + ["civil"] * n_civil)[:n]
        random.shuffle(roles)
        self.roles = dict(zip(ids, roles))
        self.alive = set(ids)
        # Šerif ima samo 1 hitac u igri
        self.serif_shots: dict[int, int] = {uid: 1 for uid, r in self.roles.items() if r == "serif"}
        self.jester_lynched: int | None  = None

ROLE_INFO = {
    "civil":        ("<:e_user:1519363093736718518>‍<:e_herb:1519363706243387573> Civil",       "Tvoj cilj: otkrij i izglasaj mafiju!", COLORS["info"]),
    "mafia":        ("<:e_sword2:1519362631146930317> Mafia",         "Noću ubijaš jednog igrača. Cilj: pobij sve civile.", COLORS["error"]),
    "doktor":       ("<:e_shield2:1519362627795554374>️ Doktor",       "Noću spašavaš jednog igrača (možeš i sebe — jednom).", COLORS["success"]),
    "detektiv":     ("<:e_search:1519363103064723547>️ Detektiv",     "Noću provjeravaš identitet jednog igrača.", COLORS["purple"]),
    "serif":        ("<:icon_report:1519358353208508566> Šerif",         "Imaš **1 hitac** za cijelu igru. Pažljivo gađaj — pogodiš li civila, gubiš.", COLORS["gold"]),
    "saljivdzija":  ("<:e_cards2:1519362702835712010> Šaljivdžija",   "Tvoj cilj: budi izglasan na danu! Ako te linčuju — POBJEĐUJEŠ!", COLORS["pink"] if "pink" in COLORS else COLORS["purple"]),
}

# ── LOBBY VIEW ──
class MafiaLobbyView(discord.ui.View):
    def __init__(self, game: MafiaGame):
        super().__init__(timeout=600)
        self.game = game

    @discord.ui.button(label="Pridruži se", style=discord.ButtonStyle.success, emoji="<:e_shake:1519362947766554737>")
    async def join(self, i: discord.Interaction, b: discord.ui.Button):
        g = self.game
        if g.phase != "lobby":
            return await i.response.send_message(
                embed=em("<:icon_warning:1519358274284032030>️ Lobby zatvoren", "Igra je već počela.", color=COLORS["warning"]), ephemeral=True)
        if any(p.id == i.user.id for p in g.players):
            return await i.response.send_message(
                embed=em("<:icon_warning:1519358274284032030>️", "Već si u lobby-ju.", color=COLORS["warning"]), ephemeral=True)
        if len(g.players) >= 12:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Puna igra", "Maksimalno 12 igrača.", color=COLORS["error"]), ephemeral=True)
        g.players.append(i.user)
        await i.response.send_message(
            embed=em("<:icon_check:1519358376268533810> Ušao u igru", f"{i.user.mention} se pridružio Mafia igri!", color=COLORS["mafia"]),
            ephemeral=True,
        )
        await self.refresh_lobby_msg(i)

    @discord.ui.button(label="Napusti", style=discord.ButtonStyle.secondary, emoji="<:e_door:1519363657404776661>")
    async def leave(self, i: discord.Interaction, b: discord.ui.Button):
        g = self.game
        if g.phase != "lobby":
            return await i.response.send_message(
                embed=em("<:icon_warning:1519358274284032030>️", "Igra je već počela — ne možeš izaći.", color=COLORS["warning"]), ephemeral=True)
        if i.user.id == g.host.id:
            return await i.response.send_message(
                embed=em("<:icon_warning:1519358274284032030>️", "Domaćin ne može izaći. Otkaži igru dugmetom **Otkaži**.", color=COLORS["warning"]), ephemeral=True)
        g.players = [p for p in g.players if p.id != i.user.id]
        await i.response.send_message(
            embed=em("<:e_shake:1519362947766554737>", f"{i.user.mention} je napustio igru.", color=COLORS["mafia"]), ephemeral=True)
        await self.refresh_lobby_msg(i)

    @discord.ui.button(label="POKRENI", style=discord.ButtonStyle.primary, emoji="<:e_right:1519363367712591922>️", row=1)
    async def start(self, i: discord.Interaction, b: discord.ui.Button):
        g = self.game
        if i.user.id != g.host.id:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>", "Samo domaćin može pokrenuti.", color=COLORS["error"]), ephemeral=True)
        if len(g.players) < 4:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508> Premalo igrača", "Trebaju **minimalno 4 igrača**.", color=COLORS["error"]), ephemeral=True)
        if g.phase != "lobby":
            return await i.response.send_message("<:icon_warning:1519358274284032030>️ Već pokrenuto.", ephemeral=True)
        g.phase = "starting"
        for c in self.children: c.disabled = True
        await i.response.edit_message(view=self)
        await mafia_start_game(g, i)

    @discord.ui.button(label="Otkaži igru", style=discord.ButtonStyle.danger, emoji="<:e_stop:1519363022399995914>", row=1)
    async def cancel(self, i: discord.Interaction, b: discord.ui.Button):
        g = self.game
        if i.user.id != g.host.id:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>", "Samo domaćin može otkazati.", color=COLORS["error"]), ephemeral=True)
        g.phase = "over"
        MAFIA_GAMES.pop(g.channel.id, None)
        for c in self.children: c.disabled = True
        await i.response.edit_message(
            embed=em("<:e_stop:1519363022399995914> Igra otkazana", "Domaćin je otkazao Mafia igru.", color=COLORS["error"]),
            view=self,
        )

    async def refresh_lobby_msg(self, i: discord.Interaction):
        g = self.game
        try:
            await i.message.edit(embed=mafia_lobby_embed(g), view=self)
        except Exception: pass

def mafia_lobby_embed(g: MafiaGame) -> discord.Embed:
    lst = "\n".join(f"`{n+1}.` {p.mention}" for n, p in enumerate(g.players)) or "_prazno_"
    e = em(
        "<:e_masks:1519363003424706671> MAFIA — Lobby",
        f"Domaćin: {g.host.mention}\nKlikni **Pridruži se** da uđeš u igru.\nKad bude **min. 4 igrača**, domaćin klikne **POKRENI**.",
        color=COLORS["mafia"],
        fields=[
            (f"<:e_users:1519363096601301120> Igrači ({len(g.players)}/12)", lst, False),
            ("<:e_time2:1519362726952964227>️ Trajanje faze", "Noć **45s** • Dan **60s** • Glasanje **45s**", True),
            ("<:e_dice2:1519362633763913931> Uloge", "Civil • <:e_sword2:1519362631146930317> Mafia • <:e_shield2:1519362627795554374>️ Doktor • <:e_search:1519363103064723547>️ Detektiv\n<:icon_report:1519358353208508566> Šerif (6+) • <:e_cards2:1519362702835712010> Šaljivdžija (8+)", True),
        ],
    )
    e.set_footer(text=f"{BOT_NAME} • Mafia Online")
    return e

# ── ACTION VIEWS (target select za noćne uloge) ──
class MafiaTargetView(discord.ui.View):
    def __init__(self, game: MafiaGame, actor: discord.Member, action_key: str, label: str, allow_self: bool = False):
        super().__init__(timeout=40)
        self.game = game
        self.actor = actor
        self.action_key = action_key
        opts = []
        for p in game.alive_players():
            if not allow_self and p.id == actor.id: continue
            opts.append(discord.SelectOption(label=p.display_name[:80], value=str(p.id)))
        self.sel = discord.ui.Select(placeholder=label, options=opts[:25], min_values=1, max_values=1)
        self.sel.callback = self._cb
        self.add_item(self.sel)

    async def _cb(self, i: discord.Interaction):
        if i.user.id != self.actor.id:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>", "Ovo nije tvoj odabir.", color=COLORS["error"]), ephemeral=True)
        tid = int(self.sel.values[0])
        self.game.actions[self.action_key] = tid
        target = self.game.channel.guild.get_member(tid)
        await i.response.edit_message(
            embed=em("<:icon_check:1519358376268533810> Akcija primljena",
                     f"Tvoj cilj: **{target.display_name if target else tid}**.\nSačekaj jutro.",
                     color=COLORS["mafia"]),
            view=None,
        )

# ── VOTE VIEW (u glavnom kanalu) ──
class MafiaVoteView(discord.ui.View):
    def __init__(self, game: MafiaGame):
        super().__init__(timeout=50)
        self.game = game
        opts = [discord.SelectOption(label=p.display_name[:80], value=str(p.id))
                for p in game.alive_players()]
        opts.append(discord.SelectOption(label="<:icon_cross:1519358379917836508> Preskoči (nikoga)", value="skip"))
        self.sel = discord.ui.Select(placeholder="Glasaj koga linčovati…", options=opts[:25])
        self.sel.callback = self._cb
        self.add_item(self.sel)

    async def _cb(self, i: discord.Interaction):
        g = self.game
        if i.user.id not in g.alive:
            return await i.response.send_message(
                embed=em("<:icon_cross:1519358379917836508>", "Mrtvi i nedužni-spektatori ne glasaju.", color=COLORS["error"]), ephemeral=True)
        v = self.sel.values[0]
        g.vote_msgs[i.user.id] = 0 if v == "skip" else int(v)
        await i.response.send_message(
            embed=em("<:icon_stats:1519358289173807246>️ Glas zabilježen", "Možeš promijeniti glas dok glasanje traje.", color=COLORS["mafia"]),
            ephemeral=True,
        )

# ── ENGINE ──
async def _safe_dm(member: discord.Member, **kw):
    try: return await member.send(**kw)
    except Exception: return None

async def mafia_start_game(g: MafiaGame, i: discord.Interaction):
    g.assign_roles()
    g.phase = "starting"
    # DM uloge
    for p in g.players:
        role = g.role_of(p.id)
        title, desc, color = ROLE_INFO[role]
        e = em(f"<:e_masks:1519363003424706671> Tvoja uloga: {title}", desc, color=color, fields=[
            ("<:e_pin:1519363329259208836> Server", g.channel.guild.name, True),
            ("<:e_tv:1519362825670230097> Kanal igre", g.channel.mention, True),
        ])
        e.set_footer(text="<:e_lock3:1519362717394403432> NIKOM ne otkrivaj svoju ulogu!")
        await _safe_dm(p, embed=e)
    # Najava
    n = len(g.players)
    n_mafia = sum(1 for r in g.roles.values() if r == "mafia")
    await g.channel.send(embed=em(
        "<:e_masks:1519363003424706671> MAFIA — POČETAK",
        f"**{n} igrača** ulazi u igru.\n<:e_sword2:1519362631146930317> Mafia: **{n_mafia}** • <:e_shield2:1519362627795554374>️ Doktor: **1** • <:e_search:1519363103064723547>️ Detektiv: **1**\n\n"
        "Provjerite **DM** — tamo je vaša uloga.",
        color=COLORS["mafia"],
    ))
    await asyncio.sleep(4)
    g.task = asyncio.create_task(mafia_loop(g))

async def mafia_loop(g: MafiaGame):
    try:
        while True:
            g.day += 1
            # ── NOĆ ──
            g.phase = "night"
            g.actions.clear()
            await g.channel.send(embed=em(
                f"<:e_moon:1519363445466595522> NOĆ #{g.day}",
                "Selo spava… Mafia, Doktor i Detektiv djeluju u DM-u.\nImate **45 sekundi**.",
                color=COLORS["mafia"],
            ))
            # Pošalji noćne akcije svim relevantnim igračima u DM
            mafias     = g.alive_with_role("mafia")
            doctors    = g.alive_with_role("doktor")
            detectives = g.alive_with_role("detektiv")
            sherifs    = g.alive_with_role("serif")
            for m in mafias:
                await _safe_dm(m,
                    embed=em("<:e_sword2:1519362631146930317> Mafia akcija", "Odaberi koga noćas ubijate:", color=COLORS["error"]),
                    view=MafiaTargetView(g, m, "mafia_kill", "Žrtva noći…", allow_self=False))
            for d in doctors:
                await _safe_dm(d,
                    embed=em("<:e_shield2:1519362627795554374>️ Doktor akcija", "Koga noćas spašavaš?", color=COLORS["mafia"]),
                    view=MafiaTargetView(g, d, "doc_heal", "Spasi…", allow_self=True))
            for det in detectives:
                await _safe_dm(det,
                    embed=em("<:e_search:1519363103064723547>️ Detektiv akcija", "Koga noćas provjeravaš?", color=COLORS["mafia"]),
                    view=MafiaTargetView(g, det, "det_check", "Provjeri…", allow_self=False))
            for sh in sherifs:
                shots_left = getattr(g, "serif_shots", {}).get(sh.id, 0)
                if shots_left > 0:
                    await _safe_dm(sh,
                        embed=em("<:icon_report:1519358353208508566> Šerif akcija", f"Imaš **{shots_left} hitac**. Možeš pucati ili preskočiti (ne odabirati).\n<:icon_warning:1519358274284032030>️ Ako pogodiš civila — **gubiš igru!**", color=COLORS["mafia"]),
                        view=MafiaTargetView(g, sh, "serif_shot", "Pucaj na…", allow_self=False))
                else:
                    await _safe_dm(sh,
                        embed=em("<:icon_report:1519358353208508566> Šerif", "Već si potrošio svoj hitac — noćas miruješ.", color=COLORS["mafia"]))
            await asyncio.sleep(45)
            # Razrešenje noći
            killed_id  = g.actions.get("mafia_kill")
            healed_id  = g.actions.get("doc_heal")
            checked_id = g.actions.get("det_check")
            shot_id    = g.actions.get("serif_shot")
            if checked_id and detectives:
                target = g.channel.guild.get_member(checked_id)
                role   = g.role_of(checked_id)
                t_title, _, t_col = ROLE_INFO.get(role, ROLE_INFO["civil"])
                for det in detectives:
                    await _safe_dm(det, embed=em(
                        "<:e_search:1519363103064723547>️ Rezultat istrage",
                        f"**{target.display_name if target else checked_id}** je: **{t_title}**",
                        color=t_col,
                    ))
            died = None
            if killed_id and killed_id != healed_id and killed_id in g.alive:
                g.alive.discard(killed_id)
                died = g.channel.guild.get_member(killed_id)
            # Šerif puca (ne može biti spašen od doktora)
            sherif_died = None
            sherif_kill_target = None
            if shot_id and sherifs and shot_id in g.alive:
                shooter = sherifs[0]
                if g.serif_shots.get(shooter.id, 0) > 0:
                    g.serif_shots[shooter.id] -= 1
                    target_role = g.role_of(shot_id)
                    if target_role == "civil":
                        # Šerif je pogodio civila — sam umire kao kazna
                        g.alive.discard(shooter.id)
                        sherif_died = shooter
                        sherif_kill_target = g.channel.guild.get_member(shot_id)
                        await _safe_dm(shooter, embed=em(
                            "<:e_skull:1519362992502997125> Šerif je promašio!",
                            f"Pucao si u **civila** — kazna je smrt!", color=COLORS["error"]))
                    else:
                        g.alive.discard(shot_id)
                        sherif_kill_target = g.channel.guild.get_member(shot_id)
                        await _safe_dm(shooter, embed=em(
                            "🎯 Pogodak!",
                            f"Eliminisao/la si **{sherif_kill_target.display_name if sherif_kill_target else shot_id}**!", color=COLORS["mafia"]))
            # Najava jutra
            morning_lines = []
            if died:
                morning_lines.append(f"<:e_skull:1519362992502997125> **{died.display_name}** je pronađen mrtav (mafija)!\nUloga: **{ROLE_INFO[g.role_of(died.id)][0]}**")
            elif killed_id and killed_id == healed_id:
                morning_lines.append("<:e_shield2:1519362627795554374>️ Doktor je **spasio žrtvu** noćas!")
            if sherif_kill_target and not sherif_died:
                morning_lines.append(f"🎯 **{sherif_kill_target.display_name}** je upucan/a — Šerif je djelovao!\nUloga: **{ROLE_INFO[g.role_of(sherif_kill_target.id)][0]}**")
            if sherif_died:
                morning_lines.append(f"<:e_scales:1519362852853649439>️ **{sherif_died.display_name}** (Šerif) je pucao u civila i umro od kazne!")
            if not morning_lines:
                morning_lines.append("<:e_sunrise:1519362915801501767> Selo je spavalo mirno — nema žrtava.")
            de = em(f"<:e_sun:1519362860218843399>️ JUTRO #{g.day}", "\n\n".join(morning_lines),
                    color=COLORS["error"] if (died or sherif_kill_target or sherif_died) else COLORS["info"])
            de.add_field(name="<:e_chart:1519362656568475880> Stanje", value=f"<:e_users:1519363096601301120> Živih: **{len(g.alive_players())}** / {len(g.players)}", inline=False)
            await g.channel.send(embed=de)
            # Pobjeda?
            w = g.winner()
            if w: return await mafia_end(g, w)
            # ── DAN — diskusija ──
            g.phase = "day"
            await g.channel.send(embed=em(
                "<:e_bubble:1519363307998417148> DISKUSIJA",
                f"Imate **60 sekundi** da razgovarate prije glasanja.\nŽivi: {', '.join(p.mention for p in g.alive_players())}",
                color=COLORS["mafia"],
            ))
            await asyncio.sleep(60)
            # ── GLASANJE ──
            g.phase = "vote"
            g.vote_msgs.clear()
            view = MafiaVoteView(g)
            await g.channel.send(
                embed=em("<:icon_stats:1519358289173807246>️ GLASANJE", "Svaki živi igrač bira metu (ili **Preskoči**). Imate **45s**.",
                         color=COLORS["warning"]),
                view=view,
            )
            await asyncio.sleep(45)
            for c in view.children: c.disabled = True
            # Prebroji
            tally: dict[int, int] = {}
            for v, t in g.vote_msgs.items():
                if v in g.alive:
                    tally[t] = tally.get(t, 0) + 1
            target_id, top = (None, 0)
            for tid, cnt in tally.items():
                if cnt > top:
                    target_id, top = tid, cnt
            if target_id and target_id != 0 and top > 0:
                victim = g.channel.guild.get_member(target_id)
                g.alive.discard(target_id)
                victim_role = g.role_of(target_id)
                await g.channel.send(embed=em(
                    "<:e_scales:1519362852853649439>️ PRESUDA",
                    f"<:e_skull:1519362992502997125> **{victim.display_name}** je linčovan glasanjem ({top} glasova).\nUloga: **{ROLE_INFO[victim_role][0]}**",
                    color=COLORS["error"],
                ))
                # Šaljivdžija pobjeđuje ako bude izglasan!
                if victim_role == "saljivdzija":
                    g.jester_lynched = target_id
                    return await mafia_end(g, "saljivdzija")
            else:
                await g.channel.send(embed=em(
                    "<:e_scales:1519362852853649439>️ PRESUDA", "Nema dovoljno glasova — niko nije linčovan.", color=COLORS["mafia"]))
            w = g.winner()
            if w: return await mafia_end(g, w)
            await asyncio.sleep(3)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        await g.channel.send(embed=em("<:icon_cross:1519358379917836508> Mafia greška", f"`{e}`", color=COLORS["error"]))
        MAFIA_GAMES.pop(g.channel.id, None)

async def mafia_end(g: MafiaGame, winner: str):
    g.phase = "over"
    if winner == "mafia":
        title, color = "<:e_sword2:1519362631146930317> MAFIA POBJEDJUJE!", COLORS["error"]
    elif winner == "civili":
        title, color = "<:e_user:1519363093736718518>‍<:e_herb:1519363706243387573> CIVILI POBJEDJUJU!", COLORS["success"]
    elif winner == "saljivdzija":
        title, color = "<:e_cards2:1519362702835712010> ŠALJIVDŽIJA POBJEDJUJE!", COLORS["gold"]
    else:
        title, color = f"🎯 KRAJ — {winner}", COLORS["info"]
    revealed = "\n".join(f"{ROLE_INFO[g.role_of(p.id)][0]} — {p.mention}" for p in g.players)
    await g.channel.send(embed=em(
        title,
        f"**Igra završena u danu {g.day}.**\n\n__Otkrivene uloge:__\n{revealed}",
        color=color,
    ))
    MAFIA_GAMES.pop(g.channel.id, None)

@bot.tree.command(name="mafia", description="<:e_masks:1519363003424706671> Pokreni Mafia igru u ovom kanalu")
async def mafia_cmd(i: discord.Interaction):
    if not isinstance(i.channel, discord.TextChannel):
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508>", "Mafia se igra samo u tekstualnom kanalu.", color=COLORS["error"]),
            ephemeral=True,
        )
    ok, left = _check_game_cooldown(i.user, i.guild_id, "mafia")
    if not ok:
        return await _send_cooldown_msg(i, "mafia", left)
    if i.channel.id in MAFIA_GAMES and MAFIA_GAMES[i.channel.id].phase != "over":
        return await i.response.send_message(
            embed=em("<:icon_warning:1519358274284032030>️ Već postoji igra",
                     "U ovom kanalu već traje Mafia igra. Sačekaj kraj ili neka domaćin otkaže.",
                     color=COLORS["warning"]),
            ephemeral=True,
        )
    _set_game_cooldown(i.user, i.guild_id, "mafia")
    g = MafiaGame(i.channel, i.user)
    MAFIA_GAMES[i.channel.id] = g
    view = MafiaLobbyView(g)
    await i.response.send_message(embed=mafia_lobby_embed(g), view=view)

@bot.tree.command(name="mafia-stop", description="<:e_stop:1519363022399995914> [DOMAĆIN] Prekini Mafia igru u ovom kanalu")
async def mafia_stop_cmd(i: discord.Interaction):
    g = MAFIA_GAMES.get(i.channel.id)
    if not g:
        return await i.response.send_message(
            embed=em("ℹ️", "Nema aktivne Mafia igre ovdje.", color=COLORS["mafia"]), ephemeral=True)
    if i.user.id != g.host.id and i.user.id not in OWNER_IDS:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508>", "Samo domaćin igre ili vlasnik bota.", color=COLORS["error"]), ephemeral=True)
    g.phase = "over"
    if g.task: g.task.cancel()
    MAFIA_GAMES.pop(i.channel.id, None)
    await i.response.send_message(embed=em("<:e_stop:1519363022399995914> Mafia prekinuta", "Igra je nasilno zaustavljena.", color=COLORS["error"]))

# ═══════════════════════════════════════════
#    <:e_floppy:1519363015147913396> CLOUD BACKUP — /backup grupa (now/restore/status)
#    Spojeno u JEDNU grupu da ne probijemo 100-cmd Discord limit.
# ═══════════════════════════════════════════
backup_group = app_commands.Group(name="backup", description="<:e_floppy:1519363015147913396> [VLASNIK] Cloud backup sistem")

@backup_group.command(name="now", description="<:e_floppy:1519363015147913396> [VLASNIK] Forsiraj odmah upload backupa na Discord")
async def backup_now_cmd(i: discord.Interaction):
    if i.user.id not in OWNER_IDS:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Samo vlasnik", "Samo vlasnik bota može pokrenuti backup.", color=COLORS["error"]),
            ephemeral=True,
        )
    if not BACKUP_CHANNEL_ID:
        return await i.response.send_message(
            embed=em("<:icon_warning:1519358274284032030>️ BACKUP_CHANNEL_ID nije postavljen",
                     "Postavi env varijablu **BACKUP_CHANNEL_ID** (ID privatnog kanala) i restartuj bota.",
                     color=COLORS["warning"]),
            ephemeral=True,
        )
    await i.response.defer(ephemeral=True)
    save_data()
    await _discord_backup_upload()
    await i.followup.send(
        embed=em("<:icon_check:1519358376268533810> Backup gurnut", f"Fajl `oleun_data.json` poslan u <#{BACKUP_CHANNEL_ID}>.",
                 color=COLORS["success"]),
        ephemeral=True,
    )

@backup_group.command(name="restore", description="<:e_floppy:1519363015147913396> [VLASNIK] Vrati podatke iz zadnjeg backupa sa Discorda")
async def backup_restore_cmd(i: discord.Interaction):
    if i.user.id not in OWNER_IDS:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Samo vlasnik", "Samo vlasnik bota može pokrenuti restore.", color=COLORS["error"]),
            ephemeral=True,
        )
    if not BACKUP_CHANNEL_ID:
        return await i.response.send_message(
            embed=em("<:icon_warning:1519358274284032030>️ BACKUP_CHANNEL_ID nije postavljen",
                     "Postavi env varijablu **BACKUP_CHANNEL_ID** i restartuj bota.",
                     color=COLORS["warning"]),
            ephemeral=True,
        )
    await i.response.defer(ephemeral=True)
    # privremeno izbriši lokalni fajl da restore prođe
    try:
        if os.path.exists(DATA_FILE):
            os.replace(DATA_FILE, DATA_FILE + ".manual_restore.bak")
    except Exception: pass
    ok = await _discord_backup_restore()
    if ok:
        await i.followup.send(
            embed=em("<:icon_check:1519358376268533810> Restore uspio", "Podaci su vraćeni iz zadnjeg backupa.", color=COLORS["success"]),
            ephemeral=True,
        )
    else:
        # vrati lokalni fajl ako restore nije uspio
        try:
            if os.path.exists(DATA_FILE + ".manual_restore.bak"):
                os.replace(DATA_FILE + ".manual_restore.bak", DATA_FILE)
                load_data()
        except Exception: pass
        await i.followup.send(
            embed=em("<:icon_cross:1519358379917836508> Restore neuspješan",
                     "Nema validnog backupa u zadnjih 50 poruka kanala. Lokalni fajl vraćen.",
                     color=COLORS["error"]),
            ephemeral=True,
        )

@backup_group.command(name="status", description="<:e_floppy:1519363015147913396> [VLASNIK] Status cloud backup sistema")
async def backup_status_cmd(i: discord.Interaction):
    if i.user.id not in OWNER_IDS:
        return await i.response.send_message(
            embed=em("<:icon_cross:1519358379917836508> Samo vlasnik", "Samo vlasnik može vidjeti status.", color=COLORS["error"]),
            ephemeral=True,
        )
    last = _DBACKUP_STATE.get("last", 0)
    last_str = datetime.fromtimestamp(last, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if last else "_nikad_"
    ch_str = f"<#{BACKUP_CHANNEL_ID}>" if BACKUP_CHANNEL_ID else "<:icon_cross:1519358379917836508> **NIJE POSTAVLJENO** (env var BACKUP_CHANNEL_ID)"
    restored_str = "<:icon_check:1519358376268533810> DA" if _DBACKUP_STATE.get("restored") else "—"
    pending_str = "<:e_time2:1519362726952964227> DA" if _DBACKUP_STATE.get("pending") else "—"
    fsize = os.path.getsize(DATA_FILE) if os.path.exists(DATA_FILE) else 0
    desc = (
        f"<:e_satellite:1519363311207186482> **Backup kanal:** {ch_str}\n"
        f"<:e_floppy:1519363015147913396> **Lokalni fajl:** `{DATA_FILE}` ({fsize:,} B)\n"
        f"<:e_time2:1519362726952964227> **Zadnji upload:** {last_str}\n"
        f"<:e_recycle:1519362875129335849>️ **Restore na ovom startu:** {restored_str}\n"
        f"<:e_box:1519363099478458498> **Pending upload:** {pending_str}\n"
        f"<:e_time2:1519362726952964227>️ **Min interval:** {DBACKUP_INTERVAL}s"
    )
    await i.response.send_message(
        embed=em("<:e_floppy:1519363015147913396> Cloud Backup status", desc, color=COLORS["info"]),
        ephemeral=True,
    )

bot.tree.add_command(backup_group)


# ═══════════════════════════════════════════
#    BALKANSKI MEMOVI lista
# ═══════════════════════════════════════════
BALKANSKI_MEMOVI = [
    "Kad kazes 'idem samo na 5 minuta' a vratis se za 2 sata",
    "Balkanska dijeta: jednom jedes, drugi put gledat kako drugi jedu",
    "Balkanski 'odmah' = negdje izmedju 30 minuta i nikad",
    "Nana: 'nisi jeo?' Ti: 'jesam' Nana: 'ajde pojedi ovo'",
    "Kad bolja polovina kaze 'kako hoces' — PAZI SE!",
    "Mi ne kazemo 'te volim', mi kazemo 'jesi jeo?'",
    "Balkanski WiFi password: pitaj komšiju",
    "Balkanski 'nije daleko': 45 minuta i tri kontrole",
    "Nema problema koji se ne moze riješiti uz kafu",
    "Kad kaze 'ne ljutim se' — najgore pocinje",
    "Mi smo jedini narod gdje se svi svadjaju a svi u pravu",
    "Nana vs. frizider: nana uvijek pobijedi",
    "Balkanska fizika: rakija lijeci sve, ili boli manje posle",
    "Balkanci ne kazu zbogom, kazu 'e, ajmo' i stoje jos sat",
    "Kad si gladan a mama kaze 'ima u frizideru' — traganje pocinje",
    "Svaka balkanska prica pocinje 'ti ne znas kako je bilo'",
    "Balkanski domacin: gost ne smije gladovati, cak ni slucajno",
    "Piknik plan: idemo u prirodu, jedemo 6 sati, ne vidimo prirodu",
    "Balkanski grad: 10 hiljada ljudi, svi znaju sve o svima",
    "Kad kazes 'gledam samo minutu' a sat prosao",
    "Balkanska logika: sunce zari, ali nosimo jaknu za svaki slucaj",
    "Viber poruka od mame u 6 ujutro: 'jesi ziv?'",
    "Ko nije kasnio 45 minuta na vlak koji je kasnio sat — nije Balkanac",
    "Balkanska tajna: svi znaju, niko ne govori — osim uz rakiju",
    "Komšijska posjeta: dodju na kavu, ostanu na veceri",
    "Balkanski ljekar: 'ajde, nije nista, uzmi caj'",
    "Svaki put kad izlaziš: 'di si bio?' 'di ideš?' 'kad se vracas?'",
    "Balkanski put do prodavnice: sretnješ 3 komšije, sat vremena",
    "Proslava u 14:00 = pocni dolaziti u 16:00",
    "Tata u kuci: tiho. Tata na auto: komentator",
    "Kad mama kaze 'vidi sto si uradio' otac gleda u pod",
    "Balkanski sat: 10:00 = izmedju 10:30 i 11:15",
    "Svadbeni stres: tko sjedi pored koga? Veci problem od rata",
    "Balkanski turist: svi frizideri otvoreni, restorani zaobidjeni",
    "Balkanci na moru: sjena, rostilj, muzika, mora nema",
    "Balkanski muzicki ukus: turbofolk ili metal, ne postoji sredina",
    "Nana ne mari za dijetu — ali mari za tvoje lijepo lice",
    "Djed kaze 'u moje vrjeme': pocni planirati 45 min slusanja",
    "Kad si bolestan: mama donese supu, baka donese rakiju, tata donese savjet",
    "Balkanski frizider: uvijek pun, nikad ne znas cega",
    "Ko ne dodje na slavlje nije nas — ko dodje ne ode kuci sit",
    "Balkanska autopilotnija: put do hamburgera poznaješ bolje od kuce",
    "Rodbina koja te ne vidi: 'narasao si!' (uvijek, bez obzira)",
    "Balkanski dorucak: caj, jaja, med, kajmak, burek — 'nista posebno'",
    "Nana gura hranu, mama gura kapu, tata gura savjete",
    "Balkanski 'jesmo li stigli?' = svakih 5 minuta od polaska",
    "Praznik plan: ne radimo nista CIJELI DAN zajedno",
    "Mama: 'ne brini, niko nista ne prica o tebi' Mama malo posle: '...'",
    "Balkanska ptica rane: mama u 7, svi u kuci u 10",
    "Svaka balkanska prica: pocne s kafom, zavrsi s politikom",
    "Kad sav grad zna tvoj problem, a ti si ga samo rekao prijatelju",
    "Djed u prici: 'a onda...' — pocinje sat vremena epske istorije",
    "Balkanski 'miran covjek': tih dok ne pocne fudbal",
    "Mama cita horoskop, baba cita solje, otac cita novine — svi u pravu",
    "Balkanski domacin misli 'mozda je gladan' = donese cijeli bife",
    "Kad neko kaze 'bit cu za 10 minuta' — naruci pice, moze cekati",
    "Balkanski 'nikad nije kasno' = vec kasno, ali idemo",
    "Kad pise 'br' u chatu — ne znas je l' brate ili nema teksta",
    "Balkanska strpljost: cekaj red 5 minuta, onda gurni se naprijed",
    "Balkanski film: svadba ili sprovod, uvijek ista muzika",
    "Kad ti kazu 'imas vremena' — to znaci hitno",
    "Komšija na vjencanju: 'tko je ova?' Svi gledaju. Komšija zna sve.",
    "Balkanci smo: gledamo lose vrijeme na Balkanu, kunemo vladu",
    "Balkanski 'nije skupo': vise nego sto imam",
    "Kad kazes 'ne trebam nista': trebas svaki dio, ali ne priznaješ",
    "Balkanski poklon: uvijek previse hrane, nikad dovoljno kesa",
    "Tata: 'je l' ugaseno?' Gasi sam, ali pita 3 puta",
    "Balkanski vijest: 10% info, 90% komentar",
    "Kad si kuci kasno — mama je budna, otac spava, ali cuje sve",
    "Balkan matematika: jedna kafa = 3 sata pricanja",
    "Rodit ces se opet ako izjedeš sve s tanjira — balkanska legenda",
    "Balkanski 'odmah se vracam' = video na ulici Ziku i tri sata nestao",
    "Balkanska izjava 'idem lezati malo' = cijela noc",
    "Balkanski alarm: mama vikne jednom, to je upozorenje",
    "Planiram odmor: torba spakirana, novac nema. Klasika.",
    "Cijela familija na telefonu za Bajram — nijedan ne moze da cuje",
    "Balkanska kuhinja: 'tjestenina za troje' = dovoljno za deset",
    "Nije pijanka ako si otisao pjeske i vratio taksijem",
    "Balkanac u restoranu: 'sta je najjeftinije?' (uzme najskuplje)",
    "Svaka balkan porodica ima jednog strucnjaka za sve",
    "Kad kazes 'sad cu' a ni za sat nisi pobjegao iz kreveta",
    "Balkanski 'bit ce gotovo za 5 minuta' a radio 3 sata",
    "Balkanski plan: 'odma idemo' = polazak za pola sata",
    "Godisnija — on zaboravi, ona pamti ZAUVIJEK",
    "Kad kazes 'idem spavati' a sedeš YouTube gledati do 3 ujutro",
    "Ko nije kasnio na vlastitu proslavu — nije nas",
    "Balkanci na dijeti: 'jedan komad torte ne steti' (uzme tri)",
    "Svaka balkanska familija: jedan koji jede sve, jedan koji ne jede nista",
    "Nana u bolnici: svi posjete tamo, nana kuha, doktori jedu",
    "Kad kazes 'nema nista u frizideru' — u njemu je hrana za tjedan",
    "Balkanski 'je l' sve ok?' = pricaj mi o svemu godinu dana",
    "Balkanska prazna torba: uvijek 12 kilograma hrane kad se vrati",
    "Svadbeni ples: stariji par — ne krecu se. Djeca — ne stanu.",
    "Balkanska filozofija: ko ne ceka, ne doceka",
    "Kad imas 'samo jedno pitanje' a imas sto",
    "Balkanci smo: ako nisi zakasnio, stigao si prerano",
    "Kad nana kaze 'pojedi jos malo' a si vec pun 40 minuta",
]

def get_next_meme(guild_id: int) -> str:
    return random.choice(BALKANSKI_MEMOVI)

# ═══════════════════════════════════════════
#    /meme — balkanski mem
# ═══════════════════════════════════════════
@bot.tree.command(name="meme", description="<:e_sparkles:1519363032185176198> Pošalji balkanski mem u kanal")
async def meme_cmd(i: discord.Interaction):
    meme_text = get_next_meme(i.guild.id if i.guild else 0)
    e = discord.Embed(
        description=f"<:e_sparkles:1519363032185176198>  {meme_text}",
        color=COLORS["fun"],
        timestamp=datetime.now(timezone.utc)
    )
    e.set_author(name=f"{i.user.display_name} šalje mem", icon_url=i.user.display_avatar.url)
    e.set_footer(text=f"{BOT_NAME} • Balkanski memovi")
    await i.response.send_message(embed=e)
    _poo_task_progress(i.guild.id if i.guild else 0, i.user.id, "use_meme")


# ═══════════════════════════════════════════
#    <:e_skull:1519362992502997125> POO GAME — 24/7 virtuelna kreatura
# ═══════════════════════════════════════════
POO_STAGES = [
    (0,    '<:e_skull:1519362992502997125>',    'Jaje Poo-a',      'Tek se izleglo. Jedva se pomjera.'),
    (50,   '<:e_skull:1519362992502997125>',    'Beba Poo',         'Probudio se! Traži pažnju i hranu.'),
    (150,  '<:e_skull:1519362992502997125><:e_sparkles:1519363032185176198>',  'Rastući Poo',      'Raste svakim danom! Počinje sjajiti.'),
    (350,  '<:e_skull:1519362992502997125><:e_bolt:1519362674717102160>',  'Energični Poo',    'Pun energije! Skace unaokolo.'),
    (700,  '<:e_skull:1519362992502997125><:e_fire2:1519362671491678280>',  'Vatreni Poo',      'Plamen izlazi iz njega! Vruc i mocan.'),
    (1200, '<:e_skull:1519362992502997125><:e_diamond2:1519362640961474601>',  'Kristalni Poo',    'Pretvorio se u nešto nevjerojatno.'),
    (2000, '<:e_skull:1519362992502997125><:e_crown2:1519363047163166922>',  'Kraljevski Poo',   'Vladar svih Poo-ova. Legenda servera.'),
    (3500, '<:e_skull:1519362992502997125><:e_moon:1519363445466595522>',  'Kosmički Poo',     'Transcendirao granice prostora i vremena.'),
]

POO_ZADACI = [
    ('chat1','Početnički Chatter','Pošalji 10 poruka u chatu','chat',10,50,1),
    ('chat2','Aktivni Chatter','Pošalji 50 poruka ukupno','chat',50,120,2),
    ('chat3','Neumorni Pisac','Pošalji 200 poruka ukupno','chat',200,300,3),
    ('chat4','Chat Manijak','Pošalji 1000 poruka ukupno','chat',1000,1500,12),
    ('chat5','Legenda Chata','Pošalji 5000 poruka ukupno','chat',5000,5000,25),
    ('meme1','Memer Početnik','Koristi /meme 3 puta','use_meme',3,50,1),
    ('meme2','Balkanski Memer','Koristi /meme 20 puta','use_meme',20,150,2),
    ('meme3','Meme Legenda','Koristi /meme 100 puta','use_meme',100,500,5),
    ('meme4','Meme Bog','Koristi /meme 500 puta','use_meme',500,2000,15),
    ('meme5','Meme Vjecnost','Koristi /meme 2000 puta','use_meme',2000,8000,50),
    ('broj1','Broji Pocetniku','Unesi tacan broj u brojanje 5 puta','count',5,75,1),
    ('broj2','Majstor Brojeva','Unesi tacan broj 25 puta','count',25,200,3),
    ('broj3','Numericki Bog','Unesi tacan broj 100 puta','count',100,600,6),
    ('broj4','Matematicki Genij','Unesi tacan broj 500 puta','count',500,2500,18),
    ('broj5','Numericki Demon','Unesi tacan broj 2000 puta','count',2000,10000,60),
    ('posao1','Mali Radnik','Odradi /posao 5 puta','work',5,80,1),
    ('posao2','Marljivi Radnik','Odradi /posao 25 puta','work',25,220,3),
    ('posao3','Trudenik Dana','Odradi /posao 100 puta','work',100,700,7),
    ('posao4','Radoholic','Odradi /posao 500 puta','work',500,3000,20),
    ('posao5','Radni Bog','Odradi /posao 2000 puta','work',2000,10000,50),
    ('daily1','Dnevna Rutina','Uzmi /daily nagradu 5 puta','daily',5,80,1),
    ('daily2','Konzistentnost','Uzmi /daily nagradu 30 puta','daily',30,300,4),
    ('daily3','Disciplina','Uzmi /daily nagradu 100 puta','daily',100,800,8),
    ('daily4','Daily Master','Uzmi /daily nagradu 500 puta','daily',500,4000,22),
    ('daily5','Vjecni Daily','Uzmi /daily nagradu 2000 puta','daily',2000,15000,80),
    ('daj1','Poklon Darivac','Pošalji pare nekome /daj 10 puta','daj',10,150,2),
    ('daj2','Veliki Darivac','Pošalji pare nekome /daj 50 puta','daj',50,600,6),
    ('mile1','Bogatash','Dostigne 10 000 coina','balance',10000,200,3),
    ('mile2','Milioner','Dostigne 100 000 coina','balance',100000,1000,10),
    ('mile3','Milijarder','Dostigne 1 000 000 coina','balance',1000000,5000,30),
    ('hunt1','Lovac Pocetnik','Idi u lov /hunt 10 puta','hunt',10,100,2),
    ('hunt2','Iskusni Lovac','Idi u lov /hunt 50 puta','hunt',50,350,4),
    ('hunt3','Legendarni Lovac','Idi u lov /hunt 200 puta','hunt',200,1500,12),
    ('hunt4','Bog Lova','Idi u lov /hunt 1000 puta','hunt',1000,6000,35),
    ('kviz1','Kviz Igrac','Odgovori na /kviz 5 puta','kviz',5,80,1),
    ('kviz2','Znalac','Odgovori na /kviz 25 puta','kviz',25,250,3),
    ('kviz3','Enciklopedija','Odgovori na /kviz 100 puta','kviz',100,900,10),
    ('kviz4','Omniznalac','Odgovori na /kviz 500 puta','kviz',500,4000,25),
    ('slots1','Kockar Pocetnik','Odigraj /slots 5 puta','slots',5,70,1),
    ('slots2','Kockar','Odigraj /slots 30 puta','slots',30,280,4),
    ('slots3','Kockar Veteran','Odigraj /slots 100 puta','slots',100,750,8),
    ('slots4','Kockar Boga','Odigraj /slots 500 puta','slots',500,3500,22),
    ('bj1','Blackjack Debi','Odigraj /blackjack 10 puta','blackjack',10,120,2),
    ('bj2','BJ Profesionalac','Odigraj /blackjack 50 puta','blackjack',50,400,5),
    ('bj3','Blackjack Legenda','Odigraj /blackjack 200 puta','blackjack',200,2000,15),
    ('battle1','Borac','Učestvuj u /battle 5 puta','battle',5,80,1),
    ('battle2','Ratnik','Učestvuj u /battle 25 puta','battle',25,280,4),
    ('battle3','Sampion','Učestvuj u /battle 100 puta','battle',100,800,8),
    ('battle4','Ratni Bog','Učestvuj u /battle 500 puta','battle',500,4500,28),
    ('vjasala1','Rjesavac Vjasala','Odigraj /vjasala 5 puta','vjasala',5,70,1),
    ('vjasala2','Majstor Vjasala','Odigraj /vjasala 20 puta','vjasala',20,220,3),
    ('vjasala3','Vjasala Majstor','Odigraj /vjasala 100 puta','vjasala',100,900,10),
    ('kaladont1','Kaladont Pocetniku','Pokreni /kaladont 5 puta','kaladont',5,100,2),
    ('kaladont2','Kaladont Majstor','Pokreni /kaladont 25 puta','kaladont',25,500,6),
    ('bingo1','Bingo Igrac','Uzmi bingo tiket 5 puta','bingo',5,80,1),
    ('bingo2','Bingo Veteran','Uzmi bingo tiket 25 puta','bingo',25,300,4),
    ('zagrljaj1','Zagrljaj Podijelac','Zagrli nekoga 10 puta','zagrljaj',10,80,1),
    ('srce1','Ljubavni Heroj','Pošalji srce 20 puta','srce',20,120,2),
    ('vers1','Zadnji Stih','Pošalji vers /vers 5 puta','vers',5,100,2),
    ('vers2','Reper Servera','Pošalji vers /vers 25 puta','vers',25,400,5),
    ('poll1','Glasac','Napravi /poll glasanje 5 puta','poll',5,80,1),
    ('tiket1','Tiket Heroj','Otvori /tiket 3 puta','tiket',3,100,2),
    ('report1','Reportaz','Prijavi nekoga /report 5 puta','report',5,60,1),
    ('afk1','AFK Nomad','Postavi /afk status 10 puta','afk',10,80,1),
    ('geo1','Geograf','Odigraj /geografija 5 puta','geo',5,70,1),
    ('geo2','Geograf Znalac','Odigraj /geografija 25 puta','geo',25,250,3),
    ('kpm1','KPM Igrac','Odigraj /kpm 10 puta','kpm',10,70,1),
    ('kpm2','KPM Majstor','Odigraj /kpm 50 puta','kpm',50,250,3),
    ('zoo1','Zoo Ljubitelj','Pogledaj /zoo 10 puta','zoo',10,60,1),
    ('lottery1','Loto Igrac','Kupi loto tiket /lottery 5 puta','lottery',5,80,1),
    ('heist1','Razbojnik','Učestvuj u /heist 3 puta','heist',3,150,3),
    ('allpoo1','Poo Sluga','Pomozi Poo-u 50 puta ukupno','poo_total',50,500,5),
    ('allpoo2','Poo Prijatelj','Pomozi Poo-u 200 puta ukupno','poo_total',200,2000,15),
    ('allpoo3','Poo Cuvar','Pomozi Poo-u 1000 puta ukupno','poo_total',1000,10000,60),
    ('allpoo4','Poo Bog','Pomozi Poo-u 5000 puta ukupno','poo_total',5000,50000,250),
    ('mile4','Level 10','Dostigne Level 10','level',10,200,3),
    ('mile5','Level 25','Dostigne Level 25','level',25,500,6),
    ('mile6','Level 50','Dostigne Level 50','level',50,1000,10),
    ('mile7','Level 100','Dostigne Level 100','level',100,5000,30),
    ('mile8','Level 250','Dostigne Level 250','level',250,15000,75),
    ('xp1','XP Sakupljac','Sakupi 1 000 XP ukupno','xp',1000,100,2),
    ('xp2','XP Veteran','Sakupi 10 000 XP ukupno','xp',10000,500,6),
    ('xp3','XP Bog','Sakupi 100 000 XP ukupno','xp',100000,5000,40),
    ('stage1','Poo Budjenje','Pomozi Poo-u da dostigne Stage 2','stage',2,200,0),
    ('stage2','Poo Rast','Pomozi Poo-u da dostigne Stage 3','stage',3,300,0),
    ('stage3','Poo Energija','Pomozi Poo-u da dostigne Stage 4','stage',4,500,0),
    ('stage4','Vatreni Poo','Pomozi Poo-u da dostigne Stage 5','stage',5,1000,0),
    ('stage5','Kristalni Poo','Pomozi Poo-u da dostigne Stage 6','stage',6,2000,0),
    ('stage6','Kraljevski Poo','Pomozi Poo-u da dostigne Stage 7','stage',7,5000,0),
    ('stage7','Kosmicki Poo','Pomozi Poo-u da dostigne Stage 8','stage',8,15000,0),
    ('epic1','Vjecni Pisac','Pošalji 20 000 poruka ukupno','chat',20000,20000,100),
    ('epic2','Workaholic God','Odradi /posao 10 000 puta','work',10000,50000,200),
    ('epic3','Neumorni Lovac','Idi u lov 5 000 puta','hunt',5000,25000,120),
]

def _get_poo_data(guild_id: int) -> dict:
    key = str(guild_id)
    if key not in data['poo']:
        data['poo'][key] = {'xp': 0, 'stage': 0, 'total_helps': 0, 'contributors': {}}
    d = data['poo'][key]
    d.setdefault('xp', 0); d.setdefault('stage', 0)
    d.setdefault('total_helps', 0); d.setdefault('contributors', {})
    return d

def _get_poo_tasks(guild_id: int, uid: int) -> dict:
    key = f"{guild_id}:{uid}"
    if key not in data['poo_tasks']:
        data['poo_tasks'][key] = {}
    return data['poo_tasks'][key]

def _poo_stage_for(xp: int) -> int:
    stage_idx = 0
    for idx, (req, emoji, name, desc) in enumerate(POO_STAGES):
        if xp >= req: stage_idx = idx
        else: break
    return stage_idx

def _poo_task_progress(guild_id: int, uid: int, task_type: str, amount: int = 1):
    if not guild_id: return
    tasks = _get_poo_tasks(guild_id, uid)
    poo = _get_poo_data(guild_id)
    uid_str = str(uid)
    contributed = False
    for row in POO_ZADACI:
        tid, tname, tdesc, ttype, goal, coin_r, poo_contrib = row
        if ttype != task_type: continue
        if tasks.get(tid, 0) >= goal: continue
        tasks[tid] = tasks.get(tid, 0) + amount
        if tasks[tid] >= goal:
            tasks[tid] = goal
            poo['xp'] = poo.get('xp', 0) + poo_contrib
            poo['total_helps'] = poo.get('total_helps', 0) + 1
            poo['contributors'][uid_str] = poo['contributors'].get(uid_str, 0) + poo_contrib
            eco = get_economy(uid)
            eco['balance'] = eco.get('balance', 0) + coin_r
            contributed = True
    new_stage = _poo_stage_for(poo.get('xp', 0))
    if new_stage != poo.get('stage', 0): poo['stage'] = new_stage
    if contributed: save_data()

async def poo_cmd(i: discord.Interaction):
    gid = i.guild.id if i.guild else 0
    poo = _get_poo_data(gid)
    xp = poo.get('xp', 0)
    stage_idx = _poo_stage_for(xp)
    stage_xp, emoji, stage_name, stage_desc = POO_STAGES[stage_idx]
    next_stage = POO_STAGES[stage_idx + 1] if stage_idx + 1 < len(POO_STAGES) else None
    helps = poo.get('total_helps', 0)
    if next_stage:
        next_xp = next_stage[0]
        prog = xp - stage_xp
        needed = next_xp - stage_xp
        bar_filled = min(int(prog / needed * 15), 15) if needed > 0 else 15
        bar = '█' * bar_filled + '░' * (15 - bar_filled)
        progress_text = f'\'`{bar}`\' \'`{prog}/{needed} XP`\''
        next_txt = f"{next_stage[1]} {next_stage[2]}"
    else:
        progress_text = '**<:e_skull:1519362992502997125> MAX STAGE DOSTIGNUTO!** <:e_crown2:1519363047163166922>'
        next_txt = 'MAX'
    contribs = poo.get('contributors', {})
    top3 = sorted(contribs.items(), key=lambda x: x[1], reverse=True)[:3]
    top_text = ''
    medals = ['<:e_star2:1519363084253266031>', '<:icon_rank2:1519358512336212091>', '<:icon_rank3:1519358517633355919>']
    for idx, (uid_str, pts) in enumerate(top3):
        m = i.guild.get_member(int(uid_str)) if i.guild else None
        uname = m.display_name if m else f'User #{uid_str[:4]}'
        top_text += f"{medals[idx]} **{uname}** — `+{pts} Poo XP`\n"
    e = discord.Embed(
        title=f'<:e_skull:1519362992502997125> Serverski POO — Stage {stage_idx + 1}/{len(POO_STAGES)}',
        description=(
            f'{emoji}  **{stage_name}**\n'
            f'*{stage_desc}*\n\n'
            f'**Progres do sljedeceg stage-a:**\n'
            f'{progress_text}\n'
            f'Sljedeci: {next_txt}\n\n'
            f'<:e_chart:1519362656568475880> Ukupni Poo XP: **{xp:,}**\n'
            f'<:e_shake:1519362947766554737> Ukupno doprinosa: **{helps:,}**'
        ),
        color=_LP,
        timestamp=datetime.now(timezone.utc)
    )
    if top_text:
        e.add_field(name='<:e_trophy2:1519362624742232146> Top 3 Cuvara Poo-a', value=top_text, inline=False)
    e.add_field(name='<:e_idea:1519363006599794799> Kako hraniti Poo?', value=(
        '• Pisi u chat aktivno\n'
        '• Koristi `/meme` komandu\n'
        '• Broji u kanalu za brojanje\n'
        '• Igraj igre: `/hunt` `/slots` `/kviz` `/blackjack`\n'
        '• Zaradjuj novac: `/posao` `/daily`\n'
        '• Ili plati direktno: `/poo-hrani` (200 <:e_coins3:1519362621206298666>)'
    ), inline=False)
    e.set_footer(text=f'<:e_skull:1519362992502997125> POO igra • {BOT_NAME} • 24/7 aktivan • /poo-zadaci za zadatke')
    await i.response.send_message(embed=e)

async def poo_zadaci_cmd(i: discord.Interaction, stranica: int = 1):
    gid = i.guild.id if i.guild else 0
    user_tasks = _get_poo_tasks(gid, i.user.id)
    stranica = max(1, min(stranica, 10))
    start = (stranica - 1) * 10
    zadaci_slice = POO_ZADACI[start:start + 10]
    desc = ''
    for tid, tname, tdesc, ttype, goal, coin_r, poo_contrib in zadaci_slice:
        prog = user_tasks.get(tid, 0)
        done = prog >= goal
        icon = '<:icon_check:1519358376268533810>' if done else '<:e_check2:1519362730057007268>'
        bar_f = min(int(prog / goal * 8), 8) if goal > 0 else 0
        mini_bar = '▰' * bar_f + '▱' * (8 - bar_f)
        desc += f'{icon} **{tname}**\n'
        desc += f'> _{tdesc}_\n'
        desc += f'> `{mini_bar}` `{prog}/{goal}` · <:e_skull:1519362992502997125>+{poo_contrib} · <:e_coins3:1519362621206298666>+{coin_r:,}\n\n'
    done_count = sum(1 for r in POO_ZADACI if user_tasks.get(r[0], 0) >= r[4])
    e = discord.Embed(
        title=f'<:e_skull:1519362992502997125> POO Zadaci — Stranica {stranica}/10',
        description=desc or 'Nema zadataka.',
        color=_LP,
        timestamp=datetime.now(timezone.utc)
    )
    e.set_footer(text=f'Stranica {stranica}/10 · Napredak: {done_count}/{len(POO_ZADACI)} · {BOT_NAME}')
    await i.response.send_message(embed=e, ephemeral=True)

async def poo_top_cmd(i: discord.Interaction):
    gid = i.guild.id if i.guild else 0
    poo = _get_poo_data(gid)
    contribs = poo.get('contributors', {})
    if not contribs:
        return await i.response.send_message(
            embed=em('<:e_skull:1519362992502997125> Poo Top Lista', 'Još niko nije doprinjeo Poo-u! Budi aktivan na serveru.', color=_LP))
    top = sorted(contribs.items(), key=lambda x: x[1], reverse=True)[:10]
    medals = ['<:e_star2:1519363084253266031>', '<:icon_rank2:1519358512336212091>', '<:icon_rank3:1519358517633355919>'] + [f'`#{n}`' for n in range(4, 11)]
    lines = []
    for idx, (uid_str, pts) in enumerate(top):
        m = i.guild.get_member(int(uid_str)) if i.guild else None
        uname = m.display_name if m else f'User #{uid_str[:4]}'
        lines.append(f'{medals[idx]} **{uname}** — `+{pts} Poo XP`')
    stage_idx = _poo_stage_for(poo.get('xp', 0))
    semo, snm = POO_STAGES[stage_idx][1], POO_STAGES[stage_idx][2]
    e = discord.Embed(
        title='<:e_skull:1519362992502997125> Top 10 Cuvara Poo-a',
        description='\n'.join(lines),
        color=_LP, timestamp=datetime.now(timezone.utc))
    e.add_field(name='<:e_skull:1519362992502997125> Trenutni Stage', value=f'{semo} **{snm}** (XP: {poo.get("xp",0):,})', inline=True)
    e.set_footer(text=f'Budi aktivan i hrani Poo-a! · {BOT_NAME}')
    await i.response.send_message(embed=e)

async def poo_hrani_cmd(i: discord.Interaction):
    COST = 200
    gid = i.guild.id if i.guild else 0
    eco = get_economy(i.user.id)
    if eco['balance'] < COST:
        return await i.response.send_message(
            embed=em('<:e_skull:1519362992502997125> Nemaš dovoljno',
                     f'Hranjenje Poo-a koštá **{COST} <:e_coins3:1519362621206298666>**.\nImaš samo `{eco["balance"]:,} <:e_coins3:1519362621206298666>`.',
                     color=COLORS['error']), ephemeral=True)
    eco['balance'] -= COST
    poo = _get_poo_data(gid)
    bonus = random.randint(2, 8)
    old_stage = poo.get('stage', 0)
    poo['xp'] = poo.get('xp', 0) + bonus
    poo['total_helps'] = poo.get('total_helps', 0) + 1
    uid_str = str(i.user.id)
    poo.setdefault('contributors', {})[uid_str] = poo['contributors'].get(uid_str, 0) + bonus
    new_stage = _poo_stage_for(poo['xp'])
    poo['stage'] = new_stage
    save_data()
    semo, snm = POO_STAGES[new_stage][1], POO_STAGES[new_stage][2]
    leveled = new_stage > old_stage
    desc = f'Nahranio/la si Poo-a! +**{bonus} Poo XP** <:e_plate:1519362791591378975>\nPoo XP ukupno: **{poo["xp"]:,}**'
    if leveled: desc += f'\n\n<:e_party:1519363028334674070> **POO JE NAPREDOVAO NA NOVI STAGE!**\n{semo} **{snm}**'
    await i.response.send_message(embed=em('<:e_skull:1519362992502997125> Poo je sit!', desc, color=_LP, fields=[
        ('<:e_coins3:1519362621206298666> Potrošeno', f'`{COST} <:e_coins3:1519362621206298666>`', True),
        ('<:e_bank2:1519362662515871744> Ostalo', f'`{eco["balance"]:,} <:e_coins3:1519362621206298666>`', True),
        ('<:e_skull:1519362992502997125> Stage', f'{semo} {snm}', True),
    ]))

async def poo_info_cmd(i: discord.Interaction):
    gid = i.guild.id if i.guild else 0
    poo = _get_poo_data(gid)
    uid_str = str(i.user.id)
    user_tasks = _get_poo_tasks(gid, i.user.id)
    my_contrib = poo.get('contributors', {}).get(uid_str, 0)
    done_count = sum(1 for r in POO_ZADACI if user_tasks.get(r[0], 0) >= r[4])
    total_tasks = len(POO_ZADACI)
    pct = round(done_count / total_tasks * 100, 1) if total_tasks > 0 else 0
    bar_f = int(done_count / total_tasks * 15) if total_tasks > 0 else 0
    bar = '█' * bar_f + '░' * (15 - bar_f)
    stage_idx = _poo_stage_for(poo.get('xp', 0))
    semo, snm = POO_STAGES[stage_idx][1], POO_STAGES[stage_idx][2]
    contribs = poo.get('contributors', {})
    sorted_c = sorted(contribs.items(), key=lambda x: x[1], reverse=True)
    my_rank = next((idx + 1 for idx, (uid, pts) in enumerate(sorted_c) if uid == uid_str), None)
    rank_txt = f'#{my_rank}' if my_rank else '—'
    e = discord.Embed(
        title='<:e_skull:1519362992502997125> Tvoj Poo Profil',
        description=(
            f'<:e_skull:1519362992502997125> Serverski Poo: {semo} **{snm}**\n'
            f'<:e_shake:1519362947766554737> Tvoj doprinos: **{my_contrib} Poo XP**\n'
            f'<:e_trophy2:1519362624742232146> Rang: **{rank_txt}**\n\n'
            f'<:e_clipboard:1519363052871614627> Zadaci: `{bar}` `{done_count}/{total_tasks}` ({pct}%)\n\n'
            f'<:e_idea:1519363006599794799> Koristi `/poo-zadaci` za detaljan pregled!'
        ),
        color=_LP, timestamp=datetime.now(timezone.utc)
    )
    e.set_thumbnail(url=i.user.display_avatar.url)
    e.set_footer(text=f'<:e_skull:1519362992502997125> POO igra · {BOT_NAME} · Budi aktivan i pomozi Poo-u!')
    await i.response.send_message(embed=e, ephemeral=True)

# ═══════════════════════════════════════════
#    POKRETANJE
# ═══════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{BOT_NAME} {VERSION} STARTUJE...\n")
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("POGRESAN TOKEN!")
    except Exception as e:
        print(f"Greška: {e}")
