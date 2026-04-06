import sys, asyncio, os, json
from datetime import datetime
import types

# --- 🛠 SERVER PATCH ---
m = types.ModuleType("pyrogram.sync")
sys.modules["pyrogram.sync"] = m

try:
    from pyrogram import Client, filters
    from pyrogram.errors import FloodWait, RPCError
except ImportError:
    print("❌ 'pip install pyrogram tgcrypto' yozing!")
    sys.exit()

# --- ⚙️ KONFIGURATSIYA (Skrinshotingiz asosida) ---
API_ID = 34915748  
API_HASH = "1fe419b5f18f72b0cfe598fc8d43395c" 
SESSION_NAME = "my_account" # GitHub'dagi fayl nomi bilan bir xil

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
    # Client yaratish (Frankfurt serveri uchun optimallashtirilgan)
    app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH, sleep_threshold=0)
    state = load_settings()

    @app.on_message(filters.me & filters.command(["ch", "text", "on", "off", "info", "help"], prefixes="/"))
    async def commands(client, message):
        cmd = message.command[0]
        if cmd == "help":
            await message.edit("<b>👑 VIP SNAYPER (SERVER EDITION)</b>\n\n📍 /ch @user\n✍️ /text 1\n🟢 /on\n🔴 /off\n📊 /info")
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
            await message.edit("🚀 <b>YOQILDI!</b>")
        elif cmd == "off":
            state["on"] = False
            save_settings(state)
            await message.edit("🛑 <b>O'CHIRILDI.</b>")
        elif cmd == "info":
            status = "🟢" if state["on"] else "🔴"
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

    print("\n🚀 Serverda bot ishga tushmoqda..."); 
    await app.start()
    print("✅ Bot tayyor! Telegramda /help yozing.")
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt: pass
