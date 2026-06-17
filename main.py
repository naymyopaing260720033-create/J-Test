import os
import cloudscraper
import telebot
from bs4 import BeautifulSoup
import html
from flask import Flask
from threading import Thread

# Flask App တည်ဆောက်ခြင်း
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# Bot Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'android', 'desktop': False}
)

def scrape_jav_details(id_code):
    url = f"https://www.javdatabase.com/movies/{id_code.lower()}/"
    try:
        response = scraper.get(url, timeout=15)
        if response.status_code == 404:
            return {"error": "❌ မတွေ့ပါသဖြင့် JAV ID မှန်မမှန် ပြန်စစ်ပေးပါ။"}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('h1')
        title = html.escape(title_tag.text.strip()) if title_tag else "N/A"
        
        # အချက်အလက်များ ရှာဖွေခြင်း
        details_box = soup.find('div', {'id': 'movie-details'}) or soup
        # (သင့်မူလ logic အတိုင်း ဆက်လက်အသုံးပြုနိုင်ပါတယ်)
        
        message = f"🌟 <b>JAV DETAILS</b> 🌟\n\n🆔 <b>ID : {id_code.upper()}</b>\n📝 <b>TITLE :</b> {title}"
        return {"message": message, "cover": None}
    except Exception as e:
        return {"error": f"⚠️ Error: {str(e)}"}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 ID ပို့ပေးလိုက်ပါ။")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    result = scrape_jav_details(message.text.strip())
    if "error" in result:
        bot.reply_to(message, result["error"])
    else:
        bot.reply_to(message, result["message"], parse_mode="HTML")

if __name__ == "__main__":
    # Flask ကို Thread အနေနဲ့ စတင်ခြင်း
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # 409 Error မတက်စေရန် Webhook ကို အရင်ရှင်းထုတ်ခြင်း
    bot.remove_webhook()
    
    print("🤖 Bot is polling...")
    bot.infinity_polling(skip_pending=True)
    
