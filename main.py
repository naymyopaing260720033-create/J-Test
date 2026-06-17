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
    return "Bot is running successfully!"

def run_flask():
    # Render ကပေးသော Port ကို အသုံးပြုခြင်း
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Config ---
# Render Environment ထဲမှာ BOT_TOKEN ကို ထည့်ထားပေးရန် လိုအပ်သည်
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Scraper ကို Global အနေဖြင့် တစ်ကြိမ်သာ တည်ဆောက်ခြင်း
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
        
        # 1. Title
        title_tag = soup.find('h1')
        title = html.escape(title_tag.text.strip()) if title_tag else "N/A"
        
        # 2. ID
        id_tag = soup.find('span', {'class': 'movieid'})
        real_id = id_tag.text.strip() if id_tag else id_code.upper()
        
        # 3. Studio/Release
        release_date = "N/A"
        studio = "N/A"
        details_box = soup.find('div', {'id': 'movie-details'}) or soup
        for p in details_box.find_all(['p', 'span', 'td']):
            text = p.text.lower()
            if 'release date:' in text:
                release_date = p.text.split(':')[-1].strip()
            if 'studio:' in text or 'maker:' in text:
                studio = p.text.split(':')[-1].strip()
                
        # 4. Actress
        actress_list = []
        actress_tags = soup.find_all('a', href=lambda href: href and '/idols/' in href)
        for act in actress_tags:
            name = act.text.strip()
            if name and "idols" not in name.lower():
                if name not in actress_list:
                    actress_list.append(name)
        actresses = ", ".join(actress_list) if actress_list else "Unknown"
        
        # 5. Image/Samples
        img_tag = soup.find('img', {'class': 'wp-post-image'})
        cover_url = img_tag.get('src') if img_tag else None
        
        message = (
            f"🌟 <b>JAV DETAILS</b> 🌟\n\n"
            f"🆔 <b>ID : {real_id}</b>\n"
            f"👩‍🎤 <b>ACTRESS : {actresses}</b>\n"
            f"🏢 <b>STUDIO : {studio}</b>\n"
            f"📅 <b>RELEASE : {release_date}</b>\n\n"
            f"📝 <b>TITLE :</b> {title}"
        )
        
        return {"message": message, "cover": cover_url}
    except Exception as e:
        return {"error": f"⚠️ Error: {str(e)}"}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 JAV ID ကို ပို့ပေးလိုက်ပါ။ ရှာဖွေပေးပါမယ်။")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text.strip()
    result = scrape_jav_details(user_input)
    
    if "error" in result:
        bot.reply_to(message, result["error"])
    else:
        if result["cover"]:
            bot.send_photo(message.chat.id, result["cover"], caption=result["message"], parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, result["message"], parse_mode="HTML")

if __name__ == "__main__":
    print("🤖 Flask Server starting...")
    # Flask ကို Thread အနေဖြင့် စတင်ခြင်း
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("🤖 Bot is polling...")
    bot.infinity_polling(skip_pending=True)
        
