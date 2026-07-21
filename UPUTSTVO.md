# SQUAD Bot v3.0 — Uputstvo za pokretanje

---

## Sadržaj

- `bot.py` — glavni bot fajl
- `UPUTSTVO.md` — ovo uputstvo
- `KOMANDE.md` — lista svih komandi
- `requirements.txt` — Python paketi

---

## Zahtjevi

- Python 3.10 ili noviji
- pip paketi (instaliraj jednom):

```
pip install -r requirements.txt
```

---

## Postavljanje

### 1. Bot token

Idi na [Discord Developer Portal](https://discord.com/developers/applications), napravi novu aplikaciju, idi na **Bot** tab i kopiraj token.

U terminalu postavi environment varijablu:

```bash
# Linux/Mac
export DISCORD_TOKEN="tvoj_token_ovdje"

# Windows (CMD)
set DISCORD_TOKEN=tvoj_token_ovdje

# Windows (PowerShell)
$env:DISCORD_TOKEN="tvoj_token_ovdje"
```

Ili napravi `.env` fajl:

```
DISCORD_TOKEN=tvoj_token_ovdje
```

### 2. Intents

U Discord Developer Portalu, pod **Bot → Privileged Gateway Intents**, uključi:

- ✅ Server Members Intent
- ✅ Message Content Intent
- ✅ Presence Intent

### 3. Pokretanje

```bash
python bot.py
```

---

## Konfiguracija servera (admin komande)

Sve setup komande su grupisane pod `/set`:

| Komanda | Opis |
|---|---|
| `/set all` | Postavi sve odjednom (welcome, log, starboard, autorole...) |
| `/set welcome` | Kanal za dobrodošlicu novih članova |
| `/set leave` | Kanal za odlaske |
| `/set log` | Log kanal (edit, delete, join, ban) |
| `/set starboard` | Starboard kanal + broj zvjezdica |
| `/set autorole` | Automatska uloga za nove članove |
| `/set levelrole` | Uloga za određeni XP level |
| `/set aktivnost` | Level-up kanal + XP rank kanal |
| `/set config` | Pregled cijele konfiguracije |
| `/set kanal` | Postavi confess/report/birthday/staff-apps kanal |
| `/set level` | Ručno postavi level korisniku (OWNER) |
| `/set roles` | Kreiraj sve GIAN uloge odjednom |
| `/set brojanje` | Postavi kanal za brojanje |
| `/set brojanje-reset` | Resetuj brojanje na 0 |

---

## Embed dizajn

Bot koristi **bez colour bar** dizajn — svi embedi nemaju lijevu obojenu traku.

Opisi su automatski formatirani kao Discord **blockquote** (`> tekst`) sa **bold** stilizacijom.

Ovo se postiže kroz `discord.Embed.__init__` monkey-patch koji djeluje na **sve** embede automatski.

---

## Podaci

Bot čuva podatke u `data.json`. Fajl se kreira automatski pri prvom pokretanju.

Preporučuje se redovni backup `data.json`.

---

## Resetovanje

Ako želiš potpuni reset:

```bash
rm data.json
python bot.py
```

---

## Kontakt

Bot kreirao: **GIAN Team**
Verzija: **SQUAD Bot v3.0**
