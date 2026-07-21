import re

print("🔧 Čitam bot.py...")
with open("bot.py", "r", encoding="utf-8") as f:
    code = f.read()

original = code

# ═══════════════════════════════════════════
# POPRAVKA 1: /aktivnost — linija ~3615
# ═══════════════════════════════════════════
pattern1 = r'e\.add_field\(name="<:e_level2:1519362739749785610> Sistem", value="```ini\n\[100 poruka = 1 LVL \+ 100 XP\]\n    e\.set_footer\(text=f"<:e_bolt:1519362674717102160> \{BOT_NAME\} • Aktivnost • Svakih 100 poruka novi level!"\)\n     await i\.response\.send_message\(embed=e\)'

replacement1 = '''e.add_field(name="<:e_level2:1519362739749785610> Sistem", value="```ini\\n[100 poruka = 1 LVL + 100 XP]\\n```", inline=True)
    e.set_footer(text=f"<:e_bolt:1519362674717102160> {BOT_NAME} • Aktivnost • Svakih 100 poruka novi level!")
    await i.response.send_message(embed=e)'''

code = re.sub(pattern1, replacement1, code)

# ═══════════════════════════════════════════
# POPRAVKA 2: /help — linija ~8285
# ═══════════════════════════════════════════
pattern2 = r'f"<:e_mail:1519362754732097546> `\{px\}invite` `\{px\}spotify` `\{px\}qr`\n"'

replacement2 = r'f"<:e_mail:1519362754732097546> `{px}invite` `{px}spotify` `{px}qr`\n"'

code = re.sub(pattern2, replacement2, code)

# ═══════════════════════════════════════════
# SAČUVAJ
# ═══════════════════════════════════════════
if code != original:
    with open("bot.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ GOTOVO! bot.py je popravljen.")
    print("\n🚀 Pokreni bota sa:")
    print("   python bot.py")
else:
    print("⚠️  Nije pronađen problem — bot.py je već ispravan!")
