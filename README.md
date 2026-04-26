# 🚀 Premium SMM & SMS Bot

Professional SMM xizmatlari va Virtual raqamlar (SMS) sotish uchun Telegram bot.

## 📌 Xususiyatlari
- ✅ **SMM Panel Integratsiyasi**: Instagram, Telegram, TikTok va boshqalar.
- ✅ **Virtual Raqamlar**: SMS-Activate API orqali dunyo davlatlaridan raqamlar.
- ✅ **To'lov Tizimi**: Card-to-Card va admin tasdiqli to'lov oqimi.
- ✅ **Referal Tizimi**: Taklif qilingan do'stlar uchun bonus berish.
- ✅ **Admin Panel**: Statistika, balans boshqarish va xabar yuborish.

## 🛠 O'rnatish

1. **Repozitoriyani yuklab oling yoki fayllarni nusxalang.**
2. **Virtual muhit yarating va faollashtiring:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. **Zaruriy kutubxonalarni o'rnating:**
   ```bash
   pip install -r requirements.txt
   ```
4. **`.env` faylini to'ldiring:**
   ```env
   BOT_TOKEN=7123456789:ABCDefgh...
   ADMINS=123456789,987654321
   SMM_API_KEY=your_key
   SMS_API_KEY=your_key
   CARD_NUMBER=8600...
   CARD_HOLDER=I. FAMILIYA
   ```
5. **Botni ishga tushiring:**
   ```bash
   python bot.py
   ```

## 📂 Loyiha Strukturasi
- `bot.py` - Asosiy fayl.
- `handlers/` - Bot funksiyalari (SMM, SMS, To'lov, Admin).
- `database/` - Ma'lumotlar bazasi (Aiosqlite).
- `keyboards/` - Tugmalar (Reply va Inline).
- `utils/` - API mijozlari.
- `states/` - FSM holatlari.

---
**Dasturchi:** [Antigravity AI]
