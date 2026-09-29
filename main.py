import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

# BotFather'dan olgan tokeningizni shu yerga yozasiz:
TOKEN = "8939098970:AAEapVCM5SU3uPR5o358jSH3JkKpoUw0MaA"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Salom! 👋\nManga Yandex xaritasidan havolani yuboring yoki Telegram orqali lokatsiya tashlang.\n"
        "Men uni WB Taxi ilovasida ochish uchun tayyorlab beraman! 🚗"
    )

# 1. Telegramdan to'g'ridan-to'g'ri LOKATSIYA yuborilganda
@dp.message(F.location)
async def handle_location(message: Message):
    lat = message.location.latitude
    lon = message.location.longitude
    await send_wb_button(message, lat, lon)

# 2. Yandex Map havolasi MATN ko'rinishida yuborilganda
@dp.message(F.text & (F.text.contains("yandex") | F.text.contains("maps") | F.text.contains("ll=")))
async def handle_yandex_link(message: Message):
    text = message.text
    lat, lon = extract_coords_from_text(text)
    
    if lat and lon:
        await send_wb_button(message, lat, lon)
    else:
        await message.answer("⚠️ Yandex havolasidan koordinatalarni topib bo'lmadi. Iltimos, boshqa havola yoki to'g'ridan-to'g'ri Telegram lokatsiyasini yuboring.")

# Koordinatalarni matndan (Yandex linkidan) sug'urib oluvchi yordamchi funksiya
DMS_REGEX = re.compile(r'[-+]?\d{1,2}\.\d+')

def extract_coords_from_text(text: str):
    # Yandex linklarida odatda ?ll=69.24,41.29 yoki center=69.24,41.29 ko'rinishida bo'ladi
    # Yoki oddiy raqamlar
    match = re.search(r'(?:ll|center|q)=([0-9.]+)[,%]([0-9.]+)', text)
    if match:
        # Yandex ko'pincha uzunlik(lng), kenglik(lat) tartibida beradi
        val1, val2 = float(match.group(1)), float(match.group(2))
        if val1 > 50:  # Demak bu Longitude (Uzunlik)
            return val2, val1
        else:
            return val1, val2
            
    # Agar maxsus qolip topilmasa, matn ichidagi dastlabki ikkita koordinataga o'xshash raqamlarni olamiz
    numbers = re.findall(r'\b(4[0-9]\.\d+),\s*(6[8-9]\.\d+)\b', text)
    if numbers:
        return float(numbers[0][0]), float(numbers[0][1])
        
    return None, None

# WB Taxi tugmasini yuboruvchi asosiy funksiya
async def send_wb_button(message: Message, lat: float, lon: float):
    # WB Taxi va umumiy xarita sxemasi bo'yicha koordinatani uzatish havolasi
    # (Agar WB ilovasi universal linkni qo'llab-quvvatlasa ishlaydi, qo'llab-quvvatlamasa brauzer/xaritaga yo'naltiradi)
    wb_taxi_url = f"https://taxify.wildberries.ru/?lat={lat}&lon={lon}"
    # Yoki yandex koordinatalarini universal ochish uchun:
    geo_url = f"https://yandex.com/maps/?pt={lon},{lat}&z=16&l=map"

    keyboard = InlineKeyboardMarkup(inline_content=[
        [InlineKeyboardButton(text="🚗 WB Taxi'da ochish", url=wb_taxi_url)],
        [InlineKeyboardButton(text="🗺 Xaritada ko'rish", url=geo_url)]
    ])

    await message.answer(
        f"✅ Manzil topildi!\n📍 Kenglik: {lat}\n📍 Uzunlik: {lon}\n\nTugmani bosing:",
        reply_markup=keyboard
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
