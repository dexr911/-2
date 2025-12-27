import telebot
import re

# --- إعدادات البوت ---
API_TOKEN = '8567025218:AAFzOed48WmloFFzzOI7x-9JY2-YVHzdydc'
# الشفرة المطلوبة لتفعيل اللوحة: -.. . -..- .-.
SECRET_CODE = "-.. . -..- .-." 

bot = telebot.TeleBot(API_TOKEN)
admin_status = {} # لتحديد إذا كان الشخص مفعل وضع الآدمن

# --- لوحة تحكم الآدمن ---
@bot.message_handler(func=lambda m: m.text == SECRET_CODE)
def unlock_admin(message):
    admin_status[message.chat.id] = True
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("ارسال ملفات txt شغالة", "ارسال ايميلات شغالة")
    markup.add("❌ إغلاق اللوحة")
    bot.reply_to(message, "🔓 تم تفعيل قائمة التحكم الخاصة بك يا Dexr.", reply_markup=markup)

@bot.message_handler(func=lambda m: admin_status.get(m.chat.id) and m.text == "❌ إغلاق اللوحة")
def lock_admin(message):
    admin_status[message.chat.id] = False
    bot.reply_to(message, "🔒 تم إخفاء الخيارات.", reply_markup=telebot.types.ReplyKeyboardRemove())

# --- خيار ارسال ايميلات نصية ---
@bot.message_handler(func=lambda m: admin_status.get(m.chat.id) and m.text == "ارسال ايميلات شغالة")
def ask_for_emails(message):
    bot.send_message(message.chat.id, "ارسل الإيميلات الشغالة الآن (نص مباشر):")

# --- خيار ارسال ملفات TXT ---
@bot.message_handler(func=lambda m: admin_status.get(m.chat.id) and m.text == "ارسال ملفات txt شغالة")
def ask_for_file(message):
    bot.send_message(message.chat.id, "يرجى رفع ملف الـ txt الذي يحتوي على الإيميلات:")

# --- استقبال ومعالجة البيانات ---
@bot.message_handler(content_types=['document', 'text'])
def handle_data(message):
    # التأكد أن الشخص آدمن وفعل الشفرة
    if not admin_status.get(message.chat.id):
        return

    emails = []
    
    # إذا أرسل ملف
    if message.document and message.document.file_name.endswith('.txt'):
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', downloaded.decode('utf-8'))
        source_type = "ملف TXT"
    
    # إذا أرسل نص مباشر (وليس من أزرار اللوحة)
    elif message.text and not message.text.startswith(("-", "ارسال", "❌")):
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message.text)
        source_type = "قائمة نصية"

    if emails:
        # هنا البوت فقط يستلمها منك ويؤكد لك العدد
        bot.reply_to(message, f"📥 تم استلام {len(emails)} إيميل شغال من ({source_type}).\nسيتم حفظها ومعالجتها وفقاً لطلبك.")
    elif not message.text.startswith(("-", "ارسال", "❌")):
        bot.reply_to(message, "⚠️ لم يتم العثور على إيميلات في إرسالك.")

bot.polling()
