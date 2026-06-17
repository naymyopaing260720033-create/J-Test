import os
import requests
import telebot
from bs4 import BeautifulSoup
import html
from flask import Flask
from threading import Thread

# Flask App (Render အတွက်)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# Bot Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

def scrape_jav_details(id_code):
    # Website ရဲ့ URL တည်ဆောက်ပုံကို ပိုသေချာအောင်လုပ်ခြင်း
    url = f"https://www.javdatabase.com/movies/{id_code.lower()}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return {"error": "❌ ID ကို ရှာမတွေ့ပါ။ (သို့) Website ပိတ်ထားပါသည်။"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Title (H1 tag ကို ရှာခြင်း)
        title = "N/A"
        h1 = soup.find('h1')
        if h1:
            title = h1.text.strip()
            
        # 2. အချက်အလက်များကို ရှာဖွေခြင်း (Website တိုင်းမှာ class တွေ အမြဲမတူနိုင်လို့ အားလုံးကို စစ်ပေးခြင်း)
        info_text = soup.get_text()
        release_date = "N/A"
        studio = "N/A"
        
        for line in info_text.split('\n'):
            if 'Release Date:' in line:
                release_date = line.replace('Release Date:', '').strip()
            if 'Studio:' in line:
                studio = line.replace('Studio:', '').strip()

        message = (
            f"🌟 <b>JAV DETAILS</b> 🌟\n\n"
            f"🆔 <b>ID : {id_code.upper()}</b>\n"
            f"🏢 <b>STUDIO : {studio}</b>\n"
            f"📅 <b>RELEASE : {release_date}</b>\n\n"
            f"📝 <b>TITLE :</b> {html.escape(title)}"
        )
        
        return {"message": message}
    except Exception as e:
        return {"error": f"⚠️ Error: {str(e)}"}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 ID ပို့ပေးလိုက်ပါ။ ရှာဖွေပေးပါမယ်။")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.strip()
    result = scrape_jav_details(user_input)
    
    if "error" in result:
        bot.reply_to(message, result["error"])
    else:
        bot.reply_to(message, result["message"], parse_mode="HTML")

if __name__ == "__main__":
    # Flask Server Thread
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Bot Polling
    bot.remove_webhook()
    print("🤖 Bot is starting...")
    bot.infinity_polling(skip_pending=True)
