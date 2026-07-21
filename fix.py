import re
import os

print("=" * 60)
print("🔧 SQUAD Bot Auto-Fix Skripta")
print("=" * 60)

# Backup
if not os.path.exists("bot.py.backup"):
    import shutil
    shutil.copy("bot.py", "bot.py.backup")
    print("✅ Backup kreiran: bot.py.backup")

with open("bot.py", "r", encoding="utf-8") as f:
    code = f.read()

original = code
fixed_count = 0

# ═══════════════════════════════════════════
# POPRAVKA 1: /aktivnost - linija ~3615
# Problem: value="```ini\n... bez zatvorenog stringa
# ═══════════════════════════════════════════
print("\n🔍 Tražim problem u /aktivnost komandi...")

# Pattern 1: tačan match
pattern1 = r'e\.add_field\(name="<:e_level2:1519362739749785610> Sistem",\s*value="```ini\s*\n\s*\[100 poruka = 1 LVL \+ 100 XP\]\s*\n\s*e\.set_footer\(text=f"<:e_bolt:1519362674717102160> \{BOT_NAME\} • Aktivnost • Svakih 100 poruka novi level!"\)\s*\n\s*await i\.response\.send_message\(embed=e\)'

replacement1 = '''e.add_field(name="<:e_level2:1519362739749785610> Sistem", value="```ini\\n[100 poruka = 1 LVL + 100 XP]\\n```", inline=True)
    e.set_footer(text=f"<:e_bolt:1519362674717102160> {BOT_NAME} • Aktivnost • Svakih 100 poruka novi level!")
    await i.response.send_message(embed=e)'''

new_code, count1 = re.subn(pattern1, replacement1, code)
if count1 > 0:
    code = new_code
    fixed_count += 1
    print(f"✅ POPRAVKA 1: /aktivnost — FIXED ({count1} mesto)")
else:
    print("⚠️  Popravka 1: pattern 1 nije nađen, probam alternativni...")
    # Alternativni pattern - jednostavniji
    alt1 = re.compile(
        r'value="```ini\s*\n\s*\[100 poruka = 1 LVL \+ 100 XP\]\s*\n\s*e\.set_footer',
        re.MULTILINE
    )
    if alt1.search(code):
        # Nađi ceo blok i zameni
        block_pattern = re.compile(
            r'(e\.add_field\(name="<:e_level2:1519362739749785610> Sistem",\s*value="```ini)\s*\n\s*\[100 poruka = 1 LVL \+ 100 XP\]\s*\n\s*(e\.set_footer\(text=f"<:e_bolt:1519362674717102160> \{BOT_NAME\} • Aktivnost • Svakih 100 poruka novi level!"\))\s*\n\s*(await i\.response\.send_message\(embed=e\))',
            re.MULTILINE
        )
        new_code = block_pattern.sub(
            r'\1\\n[100 poruka = 1 LVL + 100 XP]\\n```", inline=True)\n    \2\n    \3',
            code
        )
        if new_code != code:
            code = new_code
            fixed_count += 1
            print("✅ POPRAVKA 1 (alt): /aktivnost — FIXED")
        else:
            print("❌ Popravka 1: ne mogu automatski popraviti")
    else:
        print("ℹ️  Popravka 1: već popravljena ili nije pronađena")

# ═══════════════════════════════════════════
# POPRAVKA 2: /help - linija ~8285
# Problem: f-string sa stvarnim newline-om
# ═══════════════════════════════════════════
print("\n🔍 Tražim problem u /help komandi...")

# Pattern: f"....`qr`\n"  (stvarni newline između ` i ")
pattern2 = re.compile(
    r'(f"<:e_mail:1519362754732097546> `\{px\}invite` `\{px\}spotify` `\{px\}qr`)\s*\n(\s*)"',
    re.MULTILINE
)

def fix_fstring(m):
    indent = m.group(2)
    return f'{m.group(1)}\\n"\n{indent}'

new_code, count2 = pattern2.subn(fix_fstring, code)
if count2 > 0:
    code = new_code
    fixed_count += 1
    print(f"✅ POPRAVKA 2: /help f-string — FIXED ({count2} mesto)")
else:
    print("⚠️  Popravka 2: pattern nije nađen, probam alternativni...")
    # Jednostavniji pattern
    alt2 = re.compile(r'`\{px\}qr`\s*\n\s*"')
    if alt2.search(code):
        code = alt2.sub('`{px}qr`\\n"', code)
        fixed_count += 1
        print("✅ POPRAVKA 2 (alt): /help f-string — FIXED")
    else:
        print("ℹ️  Popravka 2: već popravljena ili nije pronađena")

# ═══════════════════════════════════════════
# POPRAVKA 3: Generički - svi unterminated strings
# ═══════════════════════════════════════════
print("\n🔍 Tražim ostale unterminated stringove...")

lines = code.split('\n')
extra_fixed = 0
i = 0
while i < len(lines) - 1:
    line = lines[i]
    next_line = lines[i+1]
    
    # Ako je sledeća linija samo whitespace + "
    if next_line.strip() == '"':
        # Spoji
        lines[i] = line.rstrip() + '\\n"'
        lines[i+1] = ''
        extra_fixed += 1
        print(f"  🔧 Linija {i+1}: spojen unterminated string")
    i += 1

if extra_fixed > 0:
    code = '\n'.join(lines)
    fixed_count += extra_fixed
    print(f"✅ POPRAVKA 3: još {extra_fixed} dodatnih fix-ova")

# ═══════════════════════════════════════════
# SAČUVAJ
# ═══════════════════════════════════════════
print("\n" + "=" * 60)
if fixed_count > 0:
    with open("bot.py", "w", encoding="utf-8") as f:
        f.write(code)
    print(f"🎉 GOTOVO! Popravljeno {fixed_count} problema.")
    print("\n🚀 Sada pokreni:")
    print("   python bot.py")
else:
    print("⚠️  Nije bilo ništa za popraviti!")
    print("   Možda su problemi već popravljeni.")

print("=" * 60)
