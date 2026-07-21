import re

print("🔧 Čitam bot.py...")
with open("bot.py", "r", encoding="utf-8") as f:
    code = f.read()

original_code = code

# ═══════════════════════════════════════════
# POPRAVKA 1: /aktivnost — unterminated string (linija ~3615)
# ═══════════════════════════════════════════
print("🔧 Popravljam /aktivnost komandu...")

old1 = '''e.add_field(name="<:e_level2:1519362739749785610> Sistem", value="```ini
[100 poruka = 1 LVL + 100 XP]
    e.set_footer(text=f"<:e_bolt:1519362674717102160> {BOT_NAME} • Aktivnost • Svakih 100 poruka novi level!")
     await i.response.send_message(embed=e)'''

new1 = '''e.add_field(name="<:e_level2:1519362739749785610> Sistem", value="```ini\\n[100 poruka = 1 LVL + 100 XP]\\n```", inline=True)
    e.set_footer(text=f"<:e_bolt:1519362674717102160> {BOT_NAME} • Aktivnost • Svakih 100 poruka novi level!")
    await i.response.send_message(embed=e)'''

if old1 in code:
    code = code.replace(old1, new1)
    print("✅ Popravka 1: /aktivnost — FIXED")
else:
    print("⚠️  Popravka 1: nije nađena (možda već popravljena)")

# ═══════════════════════════════════════════
# POPRAVKA 2: /help — unterminated f-string (linija ~8285)
# ═══════════════════════════════════════════
print("🔧 Popravljam /help komandu...")

# Pattern 1: f-string sa stvarnim newline-om
old2_pattern = r'(f"<:e_mail:1519362754732097546> `\{px\}invite` `\{px\}spotify` `\{px\}qr`)\n(")'
new2 = r'\1\\n"'

result = re.sub(old2_pattern, new2, code)
if result != code:
    code = result
    print("✅ Popravka 2: /help f-string — FIXED")
else:
    # Alternativni pattern
    old2b = 'f"<:e_mail:1519362754732097546> `{px}invite` `{px}spotify` `{px}qr`\n"'
    new2b = 'f"<:e_mail:1519362754732097546> `{px}invite` `{px}spotify` `{px}qr`\\n"'
    if old2b in code:
        code = code.replace(old2b, new2b)
        print("✅ Popravka 2 (alt): /help f-string — FIXED")
    else:
        print("⚠️  Popravka 2: nije nađena (možda već popravljena)")

# ═══════════════════════════════════════════
# POPRAVKA 3: Generalni fix — svi unterminated strings
# ═══════════════════════════════════════════
print("🔧 Tražim ostale unterminated strings...")

lines = code.split('\n')
fixed_count = 0
i = 0
while i < len(lines):
    line = lines[i]
    if i + 1 < len(lines):
        stripped = line.rstrip()
        next_stripped = lines[i+1].strip()
        
        # Pattern: linija završava sa ` ili tekst (bez ") + sljedeća linija je samo "
        if (stripped.endswith('`') or (stripped.endswith('text') and not stripped.endswith('"'))) and next_stripped == '"':
            # Spoji: dodaj \n na kraj trenutne linije + " i obriši sljedeću
            lines[i] = stripped + '\\n"'
            lines[i+1] = ''
            fixed_count += 1
            print(f"  ✅ Linija {i+1}: spojen unterminated string")
    i += 1

if fixed_count > 0:
    code = '\n'.join(lines)
    print(f"✅ Popravka 3: ukupno {fixed_count} dodatnih fix-ova")

# ═══════════════════════════════════════════
# SAČUVAJ
# ═══════════════════════════════════════════
if code != original_code:
    print("\n💾 Čuvam ispravljeni bot.py...")
    with open("bot.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("\n✅ GOTOVO! bot.py je potpuno ispravljen.")
    print("\n🚀 Pokreni bota sa:")
    print("   python bot.py")
else:
    print("\n⚠️  Nije bilo ništa za popraviti — bot.py je već ispravan!")
