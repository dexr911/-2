import telebot

# --- إعدادات البوت ---
API_TOKEN = '8567025218:AAFzOed48WmloFFzzOI7x-9JY2-YVHzdydc'
# الشفرة السرية: -.. . -..- .-.
SECRET_CODE = "-.. . -..- .-." 

bot = telebot.TeleBot(API_TOKEN)

# مخازن البيانات (ستفقد عند إعادة تشغيل البوت، يفضل لاحقاً ربطها بقاعدة بيانات)
stored_emails = []
stored_files = []

# حالة المالك لإضافة البيانات
owner_add_mode = {}

# --- عند إرسال /start تظهر الخيارات مباشرة ---
@bot.message_handler(commands=['start'])
def start_command(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("ملف ايميلات txt", callback_data="show_txt")
    btn2 = telebot.types.InlineKeyboardButton("ايميلات فقط", callback_data="show_emails")
    markup.add(btn1)
    markup.add(btn2)
    bot.send_message(message.chat.id, "اختر أحد الخيارات التالية:", reply_markup=markup)

# --- التعامل مع الضغط على الخيارات ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "show_txt":
        if stored_files:
            for file_id in stored_files:
                bot.send_document(call.message.chat.id, file_id)
        else:
            bot.answer_callback_query(call.id, "لا توجد ملفات حالياً.")
            
    elif call.data == "show_emails":
        if stored_emails:
            emails_text = "\n".join(stored_emails)
            bot.send_message(call.message.chat.id, f"القائمة الشغالة:\n\n{emails_text}")
        else:
            bot.answer_callback_query(call.id, "لا توجد إيميلات حالياً.")

# --- نظام الإضافة الخاص بالمالك عن طريق الشفرة ---
@bot.message_handler(func=lambda m: m.text == SECRET_CODE)
def secret_access(message):
    owner_add_mode[message.chat.id] = True
    bot.reply_to(message, "🔓 وضع الإضافة مفعل. أرسل الآن الملفات أو الإيميلات وسأقوم بتصنيفها تلقائياً.")

# --- استقبال الإضافات وتصنيفها ---
@bot.message_handler(content_types=['document', 'text'])
def collect_data(message):
    if not owner_add_mode.get(message.chat.id):
        return

    # إذا كان المرسل ملف TXT
    if message.document and message.document.file_name.endswith('.txt'):
        stored_files.append(message.document.file_id)
        bot.reply_to(message, "✅ تم حفظ الملف في قسم (ملفات txt).")

    # إذا كان المرسل نص (إيميلات)
    elif message.text and not message.text.startswith(("/", "-")):
        import re
        found_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', message.text)
        if found_emails:
            stored_emails.extend(found_emails)
            bot.reply_to(message, f"✅ تم حفظ {len(found_emails)} إيميل في قسم (الإيميلات).")

bot.polling()
