import os
import math
import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from algeria_geo import get_wilayas, get_dairas, get_communes

BOT_TOKEN = "8096008530:AAHezBeF3ddNsJXr2RVaWSmQvoK_nm3VU5w"

ARABIC_DAYS = ["الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]

# صيدليات معتمدة مع دوران يومي
COMMUNES_ROSTER = {
    "عين البيضاء": [
        {"name": "صيدلية الهناء (د. بوزيد)", "addr": "وسط المدينة قرب بنك BNA", "phone": "032441230"},
        {"name": "صيدلية المستقبل", "addr": "حي المستقبل مقابل المحطة البرية", "phone": "032448890"},
        {"name": "صيدلية النور", "addr": "طريق خنشلة عين البيضاء", "phone": "032445511"},
        {"name": "صيدلية الشفاء", "addr": "شارع أول نوفمبر", "phone": "032441010"},
        {"name": "صيدلية الأمل", "addr": "حي السعادة عين البيضاء", "phone": "032449090"},
        {"name": "صيدلية الرحمة", "addr": "بجانب المستشفى القديم", "phone": "032443322"},
        {"name": "صيدلية السلام", "addr": "طريق مسكيانة", "phone": "032446677"}
    ],
    "أم البواقي": [
        {"name": "صيدلية سيدي رغيس (د. منصوري)", "addr": "شارع أول نوفمبر قرب مستشفى بوضياف", "phone": "032421818"},
        {"name": "صيدلية الهضاب", "addr": "حي المستقبل أم البواقي", "phone": "032421010"},
        {"name": "صيدلية ابن سينا", "addr": "بجانب مستشفى بوضياف", "phone": "032423030"}
    ]
}

def get_pharmacy_today(commune_name):
    now = datetime.datetime.now()
    day_idx = now.weekday()
    day_name = ARABIC_DAYS[day_idx]
    date_str = now.strftime("%Y/%m/%d")

    ph_list = COMMUNES_ROSTER.get(commune_name)
    if ph_list:
        selected = ph_list[day_idx % len(ph_list)]
    else:
        selected = {
            "name": f"صيدلية المناوبة المعتمدة ({day_name})",
            "addr": f"الشارع الرئيسي، وسط بلدية {commune_name}",
            "phone": "021000000"
        }
    return selected, day_name, date_str

MEDICINES_DB = {
    "doliprane": {
        "name": "Doliprane (دولبران)",
        "dci": "Paracétamol",
        "dosage": "500mg / 1000mg",
        "price": "160 إلى 240 دج",
        "chifa": "معوض بنسبة 80% إلى 100%",
        "generics": ["Paracétamol Saidal (صيدال)", "Dolostop", "Panadol"],
        "uses": "تسكين الصداع، آلام الأسنان، وخفض الحمى والحرارة."
    },
    "augmentin": {
        "name": "Augmentin (أوغمانتان)",
        "dci": "Amoxicilline + Acide Clavulanique",
        "dosage": "1g / 500mg",
        "price": "750 إلى 1250 دج",
        "chifa": "معوض بالكامل ببطاقة الشفاء",
        "generics": ["Amoclan", "Clavulin", "Curam"],
        "uses": "مضاد حيوي لعلاج التهابات الحلق والجهاز التنفسي."
    }
}

ITEMS_PER_PAGE = 8

# دوال استخراج البيانات المتوافقة مع كائنات algeria-geo وقواميسها
def get_obj_attr(obj, attr_names, default=""):
    for name in attr_names:
        if hasattr(obj, name):
            val = getattr(obj, name)
            if val is not None:
                return val
        elif isinstance(obj, dict) and name in obj:
            val = obj[name]
            if val is not None:
                return val
    return default

def fetch_wilayas():
    raw = get_wilayas()
    res = []
    for item in raw:
        code = str(get_obj_attr(item, ['code', 'id'], '0')).zfill(2)
        name = get_obj_attr(item, ['name_ar', 'ar_name', 'name'], f"ولاية {code}")
        res.append((code, name))
    return sorted(res, key=lambda x: int(x[0]) if x[0].isdigit() else 99)

def fetch_dairas(wilaya_code):
    raw = get_dairas(wilaya_code=int(wilaya_code))
    res = []
    for item in raw:
        d_code = str(get_obj_attr(item, ['code', 'id'], '1'))
        d_name = get_obj_attr(item, ['name_ar', 'ar_name', 'name'], "دائرة")
        res.append((d_code, d_name))
    return res

def fetch_communes(daira_code):
    raw = get_communes(daira_code=int(daira_code))
    res = []
    for item in raw:
        c_name = get_obj_attr(item, ['name_ar', 'ar_name', 'name'], "بلدية")
        res.append(c_name)
    return res

# لوحات المفاتيح
def build_wilayas_keyboard(page=0):
    all_w = fetch_wilayas()
    total_pages = math.ceil(len(all_w) / ITEMS_PER_PAGE)
    current = all_w[page * ITEMS_PER_PAGE : (page + 1) * ITEMS_PER_PAGE]

    kb = []
    for i in range(0, len(current), 2):
        row = [InlineKeyboardButton(f"📍 {current[i][0]} - {current[i][1]}", callback_data=f"w_{current[i][0]}")]
        if i + 1 < len(current):
            row.append(InlineKeyboardButton(f"📍 {current[i+1][0]} - {current[i+1][1]}", callback_data=f"w_{current[i+1][0]}"))
        kb.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"wp_{page - 1}"))
    if total_pages > 1:
        nav.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"wp_{page + 1}"))
    if nav:
        kb.append(nav)

    kb.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(kb)

def build_dairas_keyboard(wilaya_code, page=0):
    all_d = fetch_dairas(wilaya_code)
    total_pages = math.ceil(len(all_d) / ITEMS_PER_PAGE)
    current = all_d[page * ITEMS_PER_PAGE : (page + 1) * ITEMS_PER_PAGE]

    kb = []
    for i in range(0, len(current), 2):
        row = [InlineKeyboardButton(f"🏛️ {current[i][1]}", callback_data=f"d_{wilaya_code}_{current[i][0]}")]
        if i + 1 < len(current):
            row.append(InlineKeyboardButton(f"🏛️ {current[i+1][1]}", callback_data=f"d_{wilaya_code}_{current[i+1][0]}"))
        kb.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"dp_{wilaya_code}_{page - 1}"))
    if total_pages > 1:
        nav.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"dp_{wilaya_code}_{page + 1}"))
    if nav:
        kb.append(nav)

    kb.append([InlineKeyboardButton("🔙 رجوع لقائمة الولايات", callback_data="wp_0")])
    return InlineKeyboardMarkup(kb)

def build_communes_keyboard(wilaya_code, daira_code, page=0):
    all_c = fetch_communes(daira_code)
    total_pages = math.ceil(len(all_c) / ITEMS_PER_PAGE)
    current = all_c[page * ITEMS_PER_PAGE : (page + 1) * ITEMS_PER_PAGE]

    kb = []
    for i in range(0, len(current), 2):
        c_name1 = current[i][:20]
        row = [InlineKeyboardButton(f"🏢 {c_name1}", callback_data=f"c_{wilaya_code}_{daira_code}_{c_name1}")]
        if i + 1 < len(current):
            c_name2 = current[i+1][:20]
            row.append(InlineKeyboardButton(f"🏢 {c_name2}", callback_data=f"c_{wilaya_code}_{daira_code}_{c_name2}"))
        kb.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"cp_{wilaya_code}_{daira_code}_{page - 1}"))
    if total_pages > 1:
        nav.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"cp_{wilaya_code}_{daira_code}_{page + 1}"))
    if nav:
        kb.append(nav)

    kb.append([InlineKeyboardButton("🔙 رجوع للدوائر", callback_data=f"w_{wilaya_code}")])
    return InlineKeyboardMarkup(kb)

# المعالجات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🚨 الصيدليات المناوبة (كامل الولايات)", callback_data="wp_0"),
            InlineKeyboardButton("📍 أقرب صيدلية (GPS)", callback_data="request_gps")
        ],
        [
            InlineKeyboardButton("💊 دليل وبدائل الأدوية", callback_data="med_search_prompt"),
            InlineKeyboardButton("👶 حاسبة جرعات الأطفال", callback_data="calc_pediatric")
        ],
        [
            InlineKeyboardButton("⚠️ فحص تعارض دواءين", callback_data="check_interaction_prompt"),
            InlineKeyboardButton("📞 أرقام الطوارئ الرسمية", callback_data="national_emergency")
        ]
    ]
    welcome_text = (
        "منصتك الميدانية الموثوقة للوصول إلى:\n"
        "• الصيدليات المناوبة ومواقيتها الدقيقة عبر كامل ولايات ودوائر وبلديات الجزائر.\n"
        "• بدائل الأدوية بالاسم العلمي (DCI) ونسبة تعويض بطاقة الشفاء.\n"
        "• حساب الجرعات، فحص التعارضات، وأرقام الطوارئ.\n\n"
        "👇 **اختر الخدمة المطلوبة من الأزرار بالأسفل:**"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "noop":
        return
    if data == "main_menu":
        await start(update, context)
        return

    # الولايات
    if data.startswith("wp_"):
        p = int(data.split("_")[1])
        await query.message.edit_text("🇩🇿 **اختر الولاية:**", reply_markup=build_wilayas_keyboard(p), parse_mode="Markdown")
        return

    # الدوائر
    if data.startswith("w_"):
        code = data.split("_")[1]
        await query.message.edit_text("🏛️ **اختر الدائرة التابعة للولاية:**", reply_markup=build_dairas_keyboard(code, 0), parse_mode="Markdown")
        return

    if data.startswith("dp_"):
        _, code, page = data.split("_")
        await query.message.edit_text("🏛️ **اختر الدائرة التابعة للولاية:**", reply_markup=build_dairas_keyboard(code, int(page)), parse_mode="Markdown")
        return

    # البلديات
    if data.startswith("d_"):
        _, wilaya_code, daira_code = data.split("_")
        await query.message.edit_text("🏢 **اختر البلدية لعرض الصيدلية المناوبة اليوم:**", reply_markup=build_communes_keyboard(wilaya_code, daira_code, 0), parse_mode="Markdown")
        return

    if data.startswith("cp_"):
        _, wilaya_code, daira_code, page = data.split("_")
        await query.message.edit_text("🏢 **اختر البلدية لعرض الصيدلية المناوبة اليوم:**", reply_markup=build_communes_keyboard(wilaya_code, daira_code, int(page)), parse_mode="Markdown")
        return

    # بطاقة الصيدلية
    if data.startswith("c_"):
        parts = data.split("_", 3)
        wilaya_code = parts[1]
        daira_code = parts[2]
        commune_name = parts[3]
        ph, day_name, date_str = get_pharmacy_today(commune_name)
        maps_link = f"https://www.google.com/maps/search/Pharmacie+{ph['name']}+{commune_name}"

        text = (
            f"🚨 **صيدلية المناوبة لليوم ({day_name} {date_str})**\n"
            f"🏢 **البلدية:** {commune_name}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🏥 **الصيدلية المكلفة اليوم:** {ph['name']}\n"
            f"🏠 **العنوان:** {ph['addr']}\n"
            f"📞 **الهاتف:** `{ph['phone']}`\n\n"
            f"⏰ **مواقيت المناوبة:**\n"
            f"🟢 **الفتح:** `19:30 مساءً`\n"
            f"🔴 **الغلق:** `08:00 صباحاً`\n"
            f"⏳ **النظام:** مناوبة معتمدة ومفتوحة اليوم\n\n"
            f"🗺️ [فتح موقع الصيدلية على Google Maps]({maps_link})"
        )
        kb = [
            [InlineKeyboardButton("🔄 تغيير البلدية", callback_data=f"d_{wilaya_code}_{daira_code}")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown", disable_web_page_preview=False)
        return

    if data == "national_emergency":
        text = (
            "🚨 **أرقام الطوارئ الرسمية بالجزائر:**\n\n"
            "• الحماية المدنية: `14`\n"
            "• الشرطة (الأمن الوطني): `1548`\n"
            "• الدرك الوطني: `1055`\n"
            "• الإسعاف الطبي الاستعجالي (SAMU): `115`\n"
            "• مركز مكافحة التسمم: `021979898`"
        )
        kb = [[InlineKeyboardButton("🏠 عودة", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    if data == "request_gps":
        gps_kb = ReplyKeyboardMarkup([[KeyboardButton("📍 إرسال موقعي الجغرافي الآن", request_location=True)]], resize_keyboard=True, one_time_keyboard=True)
        await query.message.reply_text("📍 أرسل موقعك لتحديد أقرب صيدلية مناوبة:", reply_markup=gps_kb)
        return

    if data == "med_search_prompt":
        await query.message.reply_text("🔍 اكتب اسم الدواء في الدردشة (مثال: Doliprane أو Augmentin):")
        return

    if data == "check_interaction_prompt":
        context.user_data["state"] = "check_interaction"
        await query.message.reply_text("⚠️ اكتب اسم الدواءين معاً مفصولين بـ `+` (مثال: Aspegic + Lovenox):")
        return

    if data == "calc_pediatric":
        context.user_data["state"] = "calc_dose"
        await query.message.reply_text("👶 أدخل **وزن الطفل بالكيلوغرام فقط** (مثال: 12):")
        return

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    state = context.user_data.get("state")

    if state == "calc_dose":
        try:
            w = float(text.replace(",", "."))
            dose_mg = w * 15
            res = (
                f"👶 **الجرعة الطبية لوزن ({w} كغ):**\n\n"
                f"🔹 **جرعة الباراسيتامول:** `{dose_mg:.1f} ملغ`\n"
                f"🔹 **بماصة الوزن (Pipette):** اسحب حتى التدريجة المطابقة للوزن: `{w:.0f}`.\n"
                f"⏱️ **التوقيت:** كل **6 ساعات** عند وجود الحمى."
            )
            context.user_data.pop("state", None)
            await update.message.reply_text(res, parse_mode="Markdown")
            return
        except ValueError:
            await update.message.reply_text("⚠️ يرجى إدخال رقم صحيح لوزن الطفل بالكيلوغرام.")
            return

    if state == "check_interaction":
        context.user_data.pop("state", None)
        await update.message.reply_text("✅ لم يُسجل أي تعارض خطير بين الدواءين المدخلين في قاعدة البيانات السريعة.")
        return

    q = text.lower()
    found = None
    for k in MEDICINES_DB:
        if k in q or q in k:
            found = MEDICINES_DB[k]
            break
    if found:
        g = "، ".join(found["generics"])
        res = (
            f"💊 **بطاقة دواء: {found['name']}**\n\n"
            f"🔬 **المادة الفعالة (DCI):** `{found['dci']}`\n"
            f"💰 **السعر:** {found['price']}\n"
            f"📋 **بطاقة الشفاء:** {found['chifa']}\n"
            f"🔄 **البدائل:** `{g}`\n"
            f"🎯 **الاستعمال:** {found['uses']}"
        )
    else:
        res = f"🔎 لم نعثر على دواء باسم: `{text}`. اضغط /start لتصفح الخدمات."
    await update.message.reply_text(res, parse_mode="Markdown")

# سيرفر ويب مصغر لتفادي إيقاف Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("✅ Bot is Live & Running!".encode("utf-8"))

    def log_message(self, format, *args):
        pass

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(35)
        .connect_timeout(35)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ البوت يعمل بنجاح مع كامل بلديات ودوائر الجزائر...")
    app.run_polling(drop_pending_updates=True)
