
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.request import HTTPXRequest
import asyncio
import os

# Citim datele din variabile de mediu Railway
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# Listă simplificată pentru test - poate fi extinsă
skins = [
    "★ Karambit | Doppler (Factory New)",
    "★ Sport Gloves | Pandora's Box (Field-Tested)",
    "★ M9 Bayonet | Marble Fade (Minimal Wear)"
]

def get_csfloat_price(market_hash_name):
    url = f"https://api.csgofloat.com/listings?market_hash_name={market_hash_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if "listings" in data and data["listings"]:
        sorted_listings = sorted(data["listings"], key=lambda x: x["price"])
        lowest_price = sorted_listings[0]["price"] / 100
        return lowest_price
    return None

def get_skinbid_price(skin_name):
    formatted_name = skin_name.replace(" ", "%20").replace("|", "%7C").replace("★", "%E2%98%85")
    url = f"https://skinbid.com/market/csgo/{formatted_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    price_element = soup.find("span", class_="font-bold text-white text-xl")
    if price_element:
        price_text = price_element.text.strip().replace("$", "").replace(",", "")
        try:
            return float(price_text)
        except ValueError:
            return None
    return None

async def send_alert(skin, discount, skinbid_price, csfloat_price):
    bot = Bot(token=TELEGRAM_TOKEN, request=HTTPXRequest())
    message = f"🔔 *{skin}*\n💸 SkinBid: ${skinbid_price:.2f}\n📈 CSFloat: ${csfloat_price:.2f}\n🔻 Discount: {discount:.2f}%"
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

async def main():
    for skin in skins:
        csfloat_price = get_csfloat_price(skin)
        skinbid_price = get_skinbid_price(skin)
        if csfloat_price and skinbid_price:
            discount = ((csfloat_price - skinbid_price) / csfloat_price) * 100
            if discount >= 7:
                await send_alert(skin, discount, skinbid_price, csfloat_price)

import time
while True:
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Eroare: {e}")
    print("✅ Gata runda. Aștept 15 minute...")
    time.sleep(900)
