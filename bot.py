import os, json, uuid
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Ambil dari Environment Variable Railway biar aman
TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")  # tanpa @, contoh: filestorekamu_bot
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DB_FILE = "database.json"

if os.path.exists(DB_FILE):
    with open(DB_FILE, 'r') as f:
        FILE_DB = json.load(f)
else:
    FILE_DB = {}

def save_db():
    with open(DB_FILE, 'w') as f:
        json.dump(FILE_DB, f)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    file_obj = update.message.video or update.message.document or update.message.photo
    if not file_obj:
        return
    if update.message.video:
        file_id = update.message.video.file_id
    elif update.message.document:
        file_id = update.message.document.file_id
    else:
        file_id = update.message.photo[-1].file_id

    code = uuid.uuid4().hex[:8]
    FILE_DB[code] = file_id
    save_db()
    link = f"https://t.me/{BOT_USERNAME}?start={code}"
    await update.message.reply_text(f"✅ Link jadi:\n`{link}`", parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        code = context.args[0]
        file_id = FILE_DB.get(code)
        if file_id:
            try:
                await context.bot.send_document(chat_id=update.effective_chat.id, document=file_id)
            except:
                await context.bot.send_video(chat_id=update.effective_chat.id, video=file_id)
        else:
            await update.message.reply_text("Link tidak ditemukan / expired.")
    else:
        await update.message.reply_text("Bot File Store aktif 24 jam!")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL | filters.PHOTO, handle_file))
app.run_polling()
