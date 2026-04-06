import os
import sys
import asyncio
import json
import http.server
import threading
from datetime import datetime
import types

# --- 🚀 RENDER KUTUBXONA PATCH ---
# Render ba'zan kutubxonalarni topa olmaydi, shu yo'l bilan ularni majburan ulaymiz
lib_path = os.path.expanduser("~/.local/lib/python3.11/site-packages")
if lib_path not in sys.path:
    sys.path.append(lib_path)

# --- 🛠 RENDER HEALTH CHECK SERVER ---
def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server_address = ('', port)
    httpd = http.server.HTTPServer(server_address, http.server.SimpleHTTPRequestHandler)
    print(f"📡 Web-server {port}-portda ishlamoqda...")
    httpd.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# --- 🛠 PYROGRAM PATCH ---
m = types.ModuleType("pyrogram.sync")
sys.modules["pyrogram.sync"] = m

try:
    from pyrogram import Client, filters
    from pyrogram.errors import FloodWait
    print("✅ Pyrogram muvaffaqiyatli yuklandi!")
except ImportError:
    # Agar baribir topmasa, ish vaqtida o'rnatish
    os.system("pip install pyrogram tgcrypto pysocks")
    from pyrogram import Client, filters

# --- ⚙️ KONFIGURATSIYA ---
API_ID = 34915748  
API_HASH = "1fe419b5f18f72b0cfe598fc8d43395c" 
SESSION_NAME = "my_account" 
DATA_FILE = "sniper_data.json"

def load_settings():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: pass
    return {"target_id": None, "target_name": "Yo'q", "text": "1", "on": False}

def save_settings(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

async def main():
    app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH, sleep_threshold=60)
    state = load_settings()

    @app.on_message(filters.me & filters.command(["ch", "text", "on", "off", "info", "help"], prefixes="/"))
    async def commands(client, message):
        cmd = message.command[0]
        
        if cmd == "help":
            await message.edit("<b>👑 VIP SNAYPER BUYRUQLARI:</b>\n\n📍 <code>/ch @kanal</code> - Nishonni belgilash\n✍️ <code>/text Salom</code> - Xabarni sozlash\n🟢 <code>/on</code> - Yoqish\n🔴 <code>/off</code> - O'chirish\n📊 <code>/info</code> - Holat")
        
        elif cmd == "ch":
            if len(message.command) < 2: return
            target = message.command[1].replace("@", "").lower()
            try:
                chat = await client.get_chat(target)
                state["target_id"] = chat.id
                state["target_name"] = f"@{chat.username}" if chat.username else chat.title
                save_settings(state)
                await message.edit(f"🎯 <b>NISHON:</b> <code>{state['target_name']}</code>")
            except: await message.edit("❌ Kanal topilmadi!")
            
        elif cmd == "text":
            if len(message.text.split()) < 2: return
            state["text"] = message.text.split(None, 1)[1]
            save_settings(state)
            await message.edit(f"✍️ <b>MATN:</b> <code>{state['text']}</code>")
            
        elif cmd == "on":
            state["on"] = True
            save_settings(state)
            await message.edit("🚀 <b>YOQILDI! Bot poylashni boshladi.</b>")
            
        elif cmd == "off":
            state["on"] = False
            save_settings(state)
            await message.edit("🛑 <b>O'CHIRILDI. Bot to'xtadi.</b>")
            
        elif cmd == "info":
            status = "🟢 ON" if state["on"] else "🔴 OFF"
            await message.edit(f"📊 <b>HOLAT: {status}</b>\n🎯: <code>{state['target_name']}</code>\n💬: <code>{state['text']}</code>")

    @app.on_message(filters.group & ~filters.me, group=1)
    async def sniper_logic(client, message):
        if not state["on"] or not state["target_id"]: return
        
        is_hit = False
        if message.sender_chat and message.sender_chat.id == state["target_id"]: is_hit = True
        elif message.forward_from_chat and message.forward_from_chat.id == state["target_id"]: is_hit = True

        if is_hit:
            try:
                await client.send_message(message.chat.id, state["text"], reply_to_message_id=message.id)
                print(f"🔥 [{datetime.now().strftime('%H:%M:%S.%f')}] URILDI!")
            except FloodWait as e: await asyncio.sleep(e.value)
            except: pass

    print("🚀 Bot ulanmoqda..."); 
    await app.start()
    print("✅ Bot tayyor!"); await asyncio.Future()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
