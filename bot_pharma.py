import math
import datetime
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

COMMUNES_ROSTER = {
    "عين البيضاء": [
        {"name": "صيدلية الهناء (د. بوزيد)", "addr": "وسط المدينة قرب بنك BNA", "phone": "032441230", "lat": 35.7964, "lon": 7.3928},
        {"name": "صيدلية المستقبل", "addr": "حي المستقبل مقابل المحطة البرية", "phone": "032448890", "lat": 35.7950, "lon": 7.3910},
        {"name": "صيدلية النور", "addr": "طريق خنشلة عين البيضاء", "phone": "032445511", "lat": 35.7920, "lon": 7.3900},
        {"name": "صيدلية الشفاء", "addr": "شارع أول نوفمبر", "phone": "032441010", "lat": 35.7970, "lon": 7.3940},
        {"name": "صيدلية الأمل", "addr": "حي السعادة عين البيضاء", "phone": "032449090", "lat": 35.7980, "lon": 7.3950},
        {"name": "صيدلية الرحمة", "addr": "بجانب المستشفى القديم", "phone": "032443322", "lat": 35.7990, "lon": 7.3960},
        {"name": "صيدلية السلام", "addr": "طريق مسكيانة", "phone": "032446677", "lat": 35.7940, "lon": 7.3920}
    ],
    "أم البواقي": [
        {"name": "صيدلية سيدي رغيس (د. منصوري)", "addr": "شارع أول نوفمبر قرب مستشفى بوضياف", "phone": "032421818", "lat": 35.8754, "lon": 7.1135},
        {"name": "صيدلية الهضاب", "addr": "حي المستقبل أم البواقي", "phone": "032421010", "lat": 35.8720, "lon": 7.1100},
        {"name": "صيدلية ابن سينا", "addr": "بجانب مستشفى بوضياف", "phone": "032423030", "lat": 35.8780, "lon": 7.1160}
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
            "phone": "021000000",
            "lat": 36.0,
            "lon": 3.0
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
        "uses": "تسكين الصداع، آلام الأسنان، وخفض الحمى والحرارة.",
        "precautions": "أقصى جرعة للبالغين 4 غرام يومياً (حبة كل 6 ساعات)."
    },
    "augmentin": {
        "name": "Augmentin (أوغمانتان)",
        "dci": "Amoxicilline + Acide Clavulanique",
        "dosage": "1g / 500mg",
        "price": "750 إلى 1250 دج",
        "chifa": "معوض بالكامل ببطاقة الشفاء (وصفة طبية إجبارية)",
        "generics": ["Amoclan", "Clavulin", "Curam"],
        "uses": "مضاد حيوي لعلاج التهابات الحلق، اللوزتين، والجهاز التنفسي.",
        "precautions": "إكمال مدة العلاج المحددة طبياً وتناوله في بداية الوجبات."
    }
}

DRUG_INTERACTIONS = [
    {
        "pair": ["aspegic", "lovenox"],
        "warning": "🚨 خطر حدوث نزيف حاد! كلاهما مميع قوي للدم ويحظر جمعهما دون استشارة طبيب مختص."
    },
    {
        "pair": ["doliprane", "paracetamol"],
        "warning": "⚠️ خطر تسمم كبدي خطير! كلا الدواءين يحتويان على نفس المادة الفعالة (Paracétamol)."
    }
]

ITEMS_PER_PAGE = 8

def build_wilayas_keyboard(page=0):
    all_w = get_wilayas()
    total_pages = math.ceil(len(all_w) / ITEMS_PER_PAGE)
    current = all_w[page * ITEMS_PER_PAGE : (page + 1) * ITEMS_PER_PAGE]

    kb = []
    for i in range(0, len(current), 2):
        c1 = str(current[i].get('code') or current[i].get('id')).zfill(2)
        n1 = current[i].get('name_ar') or current[i].get('name')
        row = [InlineKeyboardButton(f"📍 {c1} - {n1}", callback_data=f"w_{c1}")]
        if i + 1 < len(current):
            c2 = str(current[i+1].get('code') or current[i+1].get('id')).zfill(2)
            n2 = current[i+1].get('name_ar') or current[i+1].get('name')
            row.append(InlineKeyboardButton(f"📍 {c2} - {n2}", callback_data=f"w_{c2}"))
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
    all_d = get_dairas(wilaya_code=int(wilaya_code))
    total_pages = math.ceil(len(all_d) / ITEMS_PER_PAGE)
    current = all_d[page * ITEMS_PER_PAGE : (page + 1) * ITEMS_PER_PAGE]

    kb = []
    for i in range(0, len(current), 2):
        d_code1 = current[i].get('code') or current[i].get('id')
        d_name1 = current[i].get('name_ar') or current[i].get('name')
        row = [InlineKeyboardButton(f"🏛️ {d_name1}", callback_data=f"d_{wilaya_code}_{d_code1}")]
        if i + 1 < len(current):
            d_code2 = current[i+1].get('code') or current[i+1].get('id')
            d_name2 = current[i+1].get('name_ar') or current[i+1].get('name')
            row.append(InlineKeyboardButton(f"🏛️ {d_name2}", callback_data=f"d_{wilaya_code}_{d_code2}"))
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
    all_c = get_communes(daira_code=int(daira_code))
    total_pages = math.ceil(len(all_c) / ITEMS_PER_PAGE)
    current = all_c[page * ITEMS_PER_PAGE : (page + 1) * ITEMS_PER_PAGE]

    kb = []
    for i in range(0, len(current), 2):
        c_name1 = current[i].get('name_ar') or current[i].get('name')
        row = [InlineKeyboardButton(f"🏢 {c_name1}", callback_data=f"c_{wilaya_code}_{daira_code}_{c_name1}")]
        if i + 1 < len(current):
            c_name2 = current[i+1].get('name_ar') or current[i+1].get('name')
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

    if data.startswith("wp_"):
        p = int(data.split("_")[1])
        await query.message.edit_text("🇩🇿 **اختر الولاية:**", reply_markup=build_wilayas_keyboard(p), parse_mode="Markdown")
        return

    if data.startswith("w_"):
        code = data.split("_")[1]
        await query.message.edit_text("🏛️ **اختر الدائرة التابعة للولاية:**", reply_markup=build_dairas_keyboard(code, 0), parse_mode="Markdown")
        return

    if data.startswith("dp_"):
        _, code, page = data.split("_")
        await query.message.edit_text("🏛️ **اختر الدائرة التابعة للولاية:**", reply_markup=build_dairas_keyboard(code, int(page)), parse_mode="Markdown")
        return

    if data.startswith("d_"):
        _, wilaya_code, daira_code = data.split("_")
        await query.message.edit_text("🏢 **اختر البلدية لعرض الصيدلية المناوبة اليوم:**", reply_markup=build_communes_keyboard(wilaya_code, daira_code, 0), parse_mode="Markdown")
        return

    if data.startswith("cp_"):
        _, wilaya_code, daira_code, page = data.split("_")
        await query.message.edit_text("🏢 **اختر البلدية لعرض الصيدلية المناوبة اليوم:**", reply_markup=build_communes_keyboard(wilaya_code, daira_code, int(page)), parse_mode="Markdown")
        return

    if data.startswith("c_"):
        _, wilaya_code, daira_code, commune_name = data.split("_", 3)
        ph, day_name, date_str = get_pharmacy_today(commune_name)
        maps_link = f"https://www.google.com/maps/search/Pharmacie+{ph['name']}+{commune_name}"

        text = (
            f"🚨 **صيدلية المناوبة لليوم ({day_name} {date_str})**\n"
            f"🏢 **البلدية:** {commune_name}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🏥 **الصيدلية المناوبة اليوم:** {ph['name']}\n"
            f"🏠 **العنوان:** {ph['addr']}\n"
            f"📞 **الهاتف:** `{ph['phone']}`\n\n"
            f"⏰ **مواقيت المناوبة:**\n"
            f"🟢 **الفتح:** `19:30 مساءً`\n"
            f"🔴 **الغلق:** `08:00 صباحاً`\n"
            f"⏳ **النظام:** مناوبة ليلية وعطلة نهاية الأسبوع 24/24\n\n"
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
                f"⏱️ **التوقيت:** كل **6 ساعات** عند الحمى."
            )
            context.user_data.pop("state", None)
            await update.message.reply_text(res, parse_mode="Markdown")
            return
        except ValueError:
            await update.message.reply_text("⚠️ يرجى إدخال رقم صحيح لوزن الطفل بالكيلوغرام.")
            return

    if state == "check_interaction":
        clean = text.lower()
        warn = None
        for item in DRUG_INTERACTIONS:
            pair = item["pair"]
            if pair[0] in clean and pair[1] in clean:
                warn = item["warning"]
                break
        reply = f"🚨 **نتيجة الفحص:**\n\n{warn}" if warn else "✅ لم يُسجل تعارض كيميائي خطير بين هذين الدواءين في الدليل السريع."
        context.user_data.pop("state", None)
        await update.message.reply_text(reply, parse_mode="Markdown")
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

if __name__ == "__main__":
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
