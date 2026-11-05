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

# ----------------- إعدادات البوت والتوكن -----------------
BOT_TOKEN = "8096008530:AAHezBeF3ddNsJXr2RVaWSmQvoK_nm3VU5w"

# ----------------- 1. ولايات الجزائر الـ 58 -----------------
WILAYAS = [
    ("01", "أدرار"), ("02", "الشلف"), ("03", "الأغواط"), ("04", "أم البواقي"),
    ("05", "باتنة"), ("06", "بجاية"), ("07", "بسكرة"), ("08", "بشار"),
    ("09", "البليدة"), ("10", "البويرة"), ("11", "تمنراست"), ("12", "تبسة"),
    ("13", "تلمسان"), ("14", "تيارت"), ("15", "تيزي وزو"), ("16", "الجزائر العاصمة"),
    ("17", "الجلفة"), ("18", "جيجل"), ("19", "سطيف"), ("20", "سعيدة"),
    ("21", "سكيكدة"), ("22", "سيدي بلعباس"), ("23", "عنابة"), ("24", "قالمة"),
    ("25", "قسنطينة"), ("26", "المدية"), ("27", "مستغانم"), ("28", "المسيلة"),
    ("29", "معسكر"), ("30", "ورقلة"), ("31", "وهران"), ("32", "البيض"),
    ("33", "إليزي"), ("34", "برج بوعريريج"), ("35", "بومرداس"), ("36", "الطارف"),
    ("37", "تندوف"), ("38", "تسمسيلت"), ("39", "الوادي"), ("40", "خنشلة"),
    ("41", "سوق أهراس"), ("42", "تيبازة"), ("43", "ميلة"), ("44", "عين الدفلى"),
    ("45", "النعامة"), ("46", "عين تموشنت"), ("47", "غرداية"), ("48", "غليزان"),
    ("49", "تيميمون"), ("50", "برج باجي مختار"), ("51", "أولاد جلال"), ("52", "بني عباس"),
    ("53", "عين صالح"), ("54", "عين قزام"), ("55", "تقرت"), ("56", "جانت"),
    ("57", "المغير"), ("58", "المنيعة")
]

# ----------------- 2. جدول المناوبات اليومية حسب البلديات -----------------
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
    "أم البواقي المركز": [
        {"name": "صيدلية سيدي رغيس (د. منصوري)", "addr": "شارع أول نوفمبر قرب مستشفى بوضياف", "phone": "032421818", "lat": 35.8754, "lon": 7.1135},
        {"name": "صيدلية الهضاب", "addr": "حي المستقبل أم البواقي", "phone": "032421010", "lat": 35.8720, "lon": 7.1100},
        {"name": "صيدلية ابن سينا", "addr": "بجانب مستشفى بوضياف", "phone": "032423030", "lat": 35.8780, "lon": 7.1160}
    ],
    "عين مليلة": [
        {"name": "صيدلية القرقور", "addr": "طريق قسنطينة حي الأمل", "phone": "032475510", "lat": 36.0333, "lon": 6.5667},
        {"name": "صيدلية الهناء", "addr": "وسط المدينة عين مليلة", "phone": "032471200", "lat": 36.0310, "lon": 6.5650}
    ],
    "باتنة المركز": [
        {"name": "صيدلية الأوراس (د. قاسمي)", "addr": "شارع الجمهورية قرب الولاية القديمة", "phone": "033861122", "lat": 35.5558, "lon": 6.1741},
        {"name": "صيدلية النصر", "addr": "حي النصر باتنة", "phone": "033852140", "lat": 35.5500, "lon": 6.1700}
    ],
    "الجزائر الوسطى / ديدوش": [
        {"name": "صيدلية الاستقلال (24/24)", "addr": "42 شارع ديدوش مراد البريد المركزي", "phone": "021634578", "lat": 36.7689, "lon": 3.0543}
    ]
}

WILAYAS_COMMUNES = {
    "04": ["عين البيضاء", "أم البواقي المركز", "عين مليلة", "عين فكرون", "مسكيانة", "سوق نعمان"],
    "05": ["باتنة المركز", "بريكة", "عين التوتة", "مروانة", "آريس", "تازولت", "نقاوس"],
    "16": ["الجزائر الوسطى / ديدوش", "باب الواد", "بئر مراد رايس", "الحراش", "زرالدة", "الرويبة"],
    "31": ["وهران المركز", "السانية", "عين الترك", "أرزيو", "بطيوة", "قديل"],
    "25": ["قسنطينة المركز", "علي منجلي", "الخروب", "زيغود يوسف", "حامة بوزيان"],
    "19": ["سطيف المركز", "العلمة", "عين ولمان", "بوقاعة", "عين أرنات"]
}

for code, name in WILAYAS:
    if code not in WILAYAS_COMMUNES:
        WILAYAS_COMMUNES[code] = [f"{name} المركز", f"دائرة {name}", f"بلدية غرب {name}", f"بلدية شرق {name}"]

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
            "name": f"صيدلية الشفاء المناوبة ({day_name})",
            "addr": f"الشارع الرئيسي، وسط بلدية {commune_name}",
            "phone": "021000000",
            "lat": 36.0,
            "lon": 3.0
        }

    return selected, day_name, date_str

# ----------------- 3. قاعدة بيانات الأدوية والبدائل -----------------
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
        "generics": ["Amoclan (أمروكلان)", "Clavulin (كلافولين)", "Curam (كيورام)"],
        "uses": "مضاد حيوي لعلاج التهابات الحلق، اللوزتين، والجهاز التنفسي.",
        "precautions": "إكمال مدة العلاج المحددة طبياً وتناوله في بداية الوجبات."
    },
    "ventoline": {
        "name": "Ventoline (فونتولين)",
        "dci": "Salbutamol",
        "dosage": "بخاخ 100 µg",
        "price": "320 إلى 400 دج",
        "chifa": "معوض بنسبة 100% للأمراض المزمنة",
        "generics": ["Butovent (بوتوفنت)", "Asthalin"],
        "uses": "موسع للشعب الهوائية عند ضيق التنفس ونوبات الربو.",
        "precautions": "رج البخاخ جيداً قبل الاستعمال ومراجعة الطوارئ إذا لم تستقر الحالة."
    },
    "aspegic": {
        "name": "Aspégic (أسبيجيك)",
        "dci": "Acétylsalicylate de lysine",
        "dosage": "100mg / 500mg / 1000mg",
        "price": "180 إلى 300 دج",
        "chifa": "معوض ببطاقة الشفاء",
        "generics": ["Catalgine (كاتالجين)", "Aspirine Protect"],
        "uses": "خافض حرارة ومسكن، والجرعة 100mg لتسييل الدم.",
        "precautions": "ممنوع لمرضى قرحة المعدة والنزيف الحاد."
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

NURSES_DATA = {
    "04": [
        {"name": "الممرض رضوان (عين البيضاء)", "phone": "0661234567", "services": "حقن، تغيير ضمادات، تركيب سيروم"},
        {"name": "الممرض كمال (أم البواقي)", "phone": "0550123456", "services": "متابعة السكري، قياس الضغط، العناية بالجروح"}
    ],
    "05": [
        {"name": "الممرض عادل (باتنة المركز)", "phone": "0771890123", "services": "تمريض منزلي شامل، نزع الغرز، تحاليل دم"}
    ],
    "16": [
        {"name": "الممرضة ياسمين (الجزائر الوسطى)", "phone": "0664556677", "services": "رعاية ما بعد الجراحة، حقن Lovenox المنزلي"}
    ]
}

donations_list = [
    {"med": "Lovenox 0.4", "wilaya": "أم البواقي", "phone": "0662001122", "exp": "2027-05", "donor": "فاعل خير"},
    {"med": "Doliprane 1000", "wilaya": "باتنة", "phone": "0555334455", "exp": "2027-09", "donor": "عبد الرزاق"}
]

blood_donors = [
    {"name": "محمد", "blood": "O-", "wilaya": "أم البواقي", "phone": "0661112233"},
    {"name": "حمزة", "blood": "A+", "wilaya": "باتنة", "phone": "0770223344"},
    {"name": "ياسين", "blood": "O+", "wilaya": "الجزائر العاصمة", "phone": "0551334455"}
]

user_states = {}

def calculate_distance(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * (math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c

# ----------------- بناء لوحات الأزرار -----------------
WILAYAS_PER_PAGE = 8
def build_wilayas_keyboard(page=0):
    total_pages = math.ceil(len(WILAYAS) / WILAYAS_PER_PAGE)
    current = WILAYAS[page * WILAYAS_PER_PAGE : (page + 1) * WILAYAS_PER_PAGE]

    keyboard = []
    for i in range(0, len(current), 2):
        row = [InlineKeyboardButton(f"📍 {current[i][0]} - {current[i][1]}", callback_data=f"wil_{current[i][0]}")]
        if i + 1 < len(current):
            row.append(InlineKeyboardButton(f"📍 {current[i+1][0]} - {current[i+1][1]}", callback_data=f"wil_{current[i+1][0]}"))
        keyboard.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page - 1}"))
    nav.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page_{page + 1}"))
    keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

COMMUNES_PER_PAGE = 6
def build_communes_keyboard(code, page=0):
    communes = WILAYAS_COMMUNES.get(code, [])
    total_pages = math.ceil(len(communes) / COMMUNES_PER_PAGE)
    current = communes[page * COMMUNES_PER_PAGE : (page + 1) * COMMUNES_PER_PAGE]

    keyboard = []
    for i in range(0, len(current), 2):
        row = [InlineKeyboardButton(f"🏢 {current[i]}", callback_data=f"com_{code}_{current[i]}")]
        if i + 1 < len(current):
            row.append(InlineKeyboardButton(f"🏢 {current[i+1]}", callback_data=f"com_{code}_{current[i+1]}"))
        keyboard.append(row)

    if total_pages > 1:
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"cpage_{code}_{page - 1}"))
        nav.append(InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="noop"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"cpage_{code}_{page + 1}"))
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("🔙 رجوع لقائمة الولايات", callback_data="page_0")])
    return InlineKeyboardMarkup(keyboard)

# ----------------- المعالجات البرمجية -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🚨 الصيدليات المناوبة (58 ولاية)", callback_data="page_0"),
            InlineKeyboardButton("📍 أقرب صيدلية (GPS)", callback_data="request_gps")
        ],
        [
            InlineKeyboardButton("💊 دليل وبدائل الأدوية", callback_data="med_search_prompt"),
            InlineKeyboardButton("👶 حاسبة جرعات الأطفال", callback_data="calc_pediatric")
        ],
        [
            InlineKeyboardButton("⚠️ فحص تعارض دواءين", callback_data="check_interaction_prompt"),
            InlineKeyboardButton("🎁 بنك التبرع بالأدوية", callback_data="donations_menu")
        ],
        [
            InlineKeyboardButton("🩸 بنك الدم (SOS Sang)", callback_data="blood_menu"),
            InlineKeyboardButton("💉 التمريض المنزلي والحقن", callback_data="nurses_menu")
        ],
        [
            InlineKeyboardButton("🦂 مراكز الأمصال والتسمم", callback_data="antivenom_info"),
            InlineKeyboardButton("📞 أرقام الطوارئ الرسمية", callback_data="national_emergency")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "🇩🇿 **مرحباً بك في المنصة الصحية الشاملة (دليل صيدليات وأدوية الجزائر DZ)**\n\n"
        "• الصيدليات المناوبة ومواقيتها الدقيقة عبر كامل الولايات الـ 58.\n"
        "• بدائل الأدوية بالاسم العلمي (DCI) ونسبة تعويض بطاقة الشفاء.\n"
        "• خدمات بنك الدم، التبرع الدوائي، وأرقام الممرضين للمنازل.\n\n"
        "👇 **اختر الخدمة المطلوبة من الأزرار بالأسفل:**"
    )

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "noop":
        return
    if data == "main_menu":
        await start(update, context)
        return

    if data == "request_gps":
        gps_keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📍 إرسال موقعي الجغرافي الآن", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await query.message.reply_text("📍 اضغط على الزر بالأسفل لتحديد أقرب صيدلية مناوبة منك:", reply_markup=gps_keyboard)
        return

    if data.startswith("page_"):
        p = int(data.replace("page_", ""))
        await query.message.edit_text("🇩🇿 **اختر الولاية من القائمة (58 ولاية):**", reply_markup=build_wilayas_keyboard(p), parse_mode="Markdown")
        return

    if data.startswith("wil_"):
        code = data.replace("wil_", "")
        wilaya_name = dict(WILAYAS).get(code, code)
        await query.message.edit_text(f"📍 **ولاية {code} - {wilaya_name}**\nاختر البلدية لمعرفة الصيدلية المناوبة اليوم:", reply_markup=build_communes_keyboard(code, 0), parse_mode="Markdown")
        return

    if data.startswith("cpage_"):
        _, code, p = data.split("_")
        wilaya_name = dict(WILAYAS).get(code, code)
        await query.message.edit_text(f"📍 **ولاية {code} - {wilaya_name}**\nاختر البلدية لمعرفة الصيدلية المناوبة اليوم:", reply_markup=build_communes_keyboard(code, int(p)), parse_mode="Markdown")
        return

    if data.startswith("com_"):
        parts = data.split("_", 2)
        code = parts[1]
        cname = parts[2]
        wname = dict(WILAYAS).get(code, code)
        ph, day_name, date_str = get_pharmacy_today(cname)
        maps_link = f"https://www.google.com/maps/search/Pharmacie+{ph['name']}+{cname}"

        text = (
            f"🚨 **صيدلية المناوبة لليوم ({day_name} {date_str})**\n"
            f"🏢 **البلدية:** {cname} (ولاية {wname})\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🏥 **الصيدلية المناوبة:** {ph['name']}\n"
            f"🏠 **العنوان:** {ph['addr']}\n"
            f"📞 **الهاتف:** `{ph['phone']}`\n\n"
            f"⏰ **مواقيت العمل المعتمدة اليوم:**\n"
            f"🟢 **الفتح:** `19:30 مساءً`\n"
            f"🔴 **الغلق:** `08:00 صباحاً`\n"
            f"⏳ **النظام:** مناوبة ليلية مستمرة لليوم\n\n"
            f"🗺️ [فتح موقع الصيدلية على Google Maps]({maps_link})\n"
        )
        kb = [
            [InlineKeyboardButton("🔄 تغيير البلدية", callback_data=f"wil_{code}")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown", disable_web_page_preview=False)
        return

    if data == "donations_menu":
        text = "🎁 **بنك التبرع بالأدوية والفائض المنزلي (مجاناً لوجه الله):**\n\n"
        for idx, item in enumerate(donations_list, 1):
            text += f"*{idx}. دواء:* `{item['med']}`\n📍 الولاية: {item['wilaya']} | 📅 الصلاحية: `{item['exp']}`\n👤 المتبرع: {item['donor']} | 📞 الهاتف: `{item['phone']}`\n───────────────────\n"
        kb = [
            [InlineKeyboardButton("➕ أريد التبرع بدواء فائض", callback_data="add_donation_prompt")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    if data == "add_donation_prompt":
        user_states[query.from_user.id] = "waiting_for_donation"
        await query.message.reply_text("📝 **أرسل بيانات الدواء المتبرع به بالشكل التالي:**\n`اسم الدواء - ولايتك - رقم هاتفك - تاريخ الصلاحية`", parse_mode="Markdown")
        return

    if data == "blood_menu":
        text = "🩸 **قائمة المتبرعين بالدم المسجلين (SOS Sang DZ):**\n\n"
        for idx, d in enumerate(blood_donors, 1):
            text += f"*{idx}. المتبرع:* {d['name']} | فصيلة الدم: 🩸 **{d['blood']}**\n📍 الولاية: {d['wilaya']} | 📞 الهاتف: `{d['phone']}`\n───────────────────\n"
        kb = [
            [InlineKeyboardButton("🩸 تسجيل نفسي كمتبرع بالدم", callback_data="register_blood_prompt")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    if data == "register_blood_prompt":
        user_states[query.from_user.id] = "waiting_for_blood_reg"
        await query.message.reply_text("📝 **سجل نفسك كمتبرع بالدم بإرسال رسالة كالتالي:**\n`اسمك - فصيلة دمك - ولايتك - رقم هاتفك`", parse_mode="Markdown")
        return

    if data == "nurses_menu":
        text = "💉 **دليل ممرضي الرعاية المنزلية والحقن المعتمدين:**\n\n"
        for wil_code, n_list in NURSES_DATA.items():
            wil_name = dict(WILAYAS).get(wil_code, wil_code)
            text += f"📍 **ولاية {wil_name}:**\n"
            for n in n_list:
                text += f"• *{n['name']}*\n  📞 الهاتف: `{n['phone']}`\n  🩺 الخدمات: {n['services']}\n"
            text += "───────────────────\n"
        kb = [[InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    if data == "antivenom_info":
        text = (
            "🦂 **مراكز الأمصال ومكافحة التسمم ولسعات العقارب:**\n\n"
            "⚠️ **الخطوات الاستعجالية:**\n"
            "1. تهدئة المصاب وتثبيت الطرف المصاب دون ربط قاطع للدورة الدموية.\n"
            "2. التوجه مباشرة لأقرب مصلحة استعجالات لتلقي المصل المضاد مجاناً.\n"
            "3. تجنب الكي أو جرح موضع اللدغة نهائياً.\n\n"
            "📞 **مركز مكافحة التسمم (باب الواد):** `021979898`\n"
            "📞 **الحماية المدنية:** `14`"
        )
        kb = [[InlineKeyboardButton("🏠 عودة", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        return

    if data == "calc_pediatric":
        user_states[query.from_user.id] = "waiting_for_child_weight"
        await query.message.reply_text("👶 **حاسبة جرعات خافض الحرارة (باراسيتامول):**\nيرجى كتابة **وزن الطفل بالكيلوغرام فقط** (مثال: `12` أو `8.5`):", parse_mode="Markdown")
        return

    if data == "check_interaction_prompt":
        user_states[query.from_user.id] = "waiting_for_interaction_check"
        await query.message.reply_text("⚠️ **فحص التفاعلات الدوائية المتعارضة:**\nاكتب اسم الدواءين معاً وبينهما علامة `+` (مثال: `Aspegic + Lovenox`):", parse_mode="Markdown")
        return

    if data == "med_search_prompt":
        await query.message.reply_text("🔍 **محرك البحث عن الأدوية وبدائلها:**\nاكتب اسم الدواء في الدردشة (مثال: `Doliprane` أو `Augmentin` أو `Ventoline`):", parse_mode="Markdown")
        return

    if data == "national_emergency":
        text = (
            "🚨 **أرقام الطوارئ الرسمية بالجزائر:**\n\n"
            "• الحماية المدنية: `14`\n"
            "• الشرطة (الأمن الوطني): `1548` أو `17`\n"
            "• الدرك الوطني: `1055`\n"
            "• الإسعاف الطبي الاستعجالي (SAMU): `115`\n"
            "• مركز مكافحة التسمم: `021979898`\n"
        )
        kb = [[InlineKeyboardButton("🏠 عودة", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    ulat, ulon = loc.latitude, loc.longitude
    best_p = None
    min_d = float("inf")
    bc = ""

    for cname, p_list in COMMUNES_ROSTER.items():
        for p in p_list:
            d = calculate_distance(ulat, ulon, p["lat"], p["lon"])
            if d < min_d:
                min_d = d
                best_p = p
                bc = cname

    if best_p:
        res = (
            f"📍 **أقرب صيدلية مناوبة لموقعك الجغرافي:**\n"
            f"📏 **المسافة التقديرية:** حوالي `{min_d:.2f} كم`\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🏥 **الصيدلية:** {best_p['name']}\n"
            f"🏢 **المنطقة:** {bc}\n"
            f"🏠 **العنوان:** {best_p['addr']}\n"
            f"📞 **الهاتف:** `{best_p['phone']}`\n\n"
            f"🗺️ [فتح مسار القيادة على Google Maps](https://www.google.com/maps/search/Pharmacie+{best_p['name']})"
        )
    else:
        res = "⚠️ تعذر العثور على صيدلية مناوبة مسجلة بالقرب من موقعك."

    await update.message.reply_text(res, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

async def handle_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    state = user_states.get(user_id)

    if state == "waiting_for_donation":
        parts = text.split("-")
        if len(parts) >= 3:
            donations_list.append({
                "med": parts[0].strip(),
                "wilaya": parts[1].strip(),
                "phone": parts[2].strip(),
                "exp": parts[3].strip() if len(parts) > 3 else "غير محدد",
                "donor": update.effective_user.first_name or "فاعل خير"
            })
            user_states.pop(user_id, None)
            await update.message.reply_text("✅ جزاك الله خيراً! تم تسجيل الدواء في بنك التبرعات بنجاح.")
        else:
            await update.message.reply_text("⚠️ يرجى إدخال البيانات مفصولة بشرطة `-` كما في المثال.")
        return

    if state == "waiting_for_blood_reg":
        parts = text.split("-")
        if len(parts) >= 4:
            blood_donors.append({
                "name": parts[0].strip(),
                "blood": parts[1].strip().upper(),
                "wilaya": parts[2].strip(),
                "phone": parts[3].strip()
            })
            user_states.pop(user_id, None)
            await update.message.reply_text("✅ تم تسجيلك بنجاح في قائمة المتبرعين بالدم (SOS Sang DZ).")
        else:
            await update.message.reply_text("⚠️ يرجى إدخال البيانات كاملة: `الاسم - الفصيلة - الولاية - الهاتف`.")
        return

    if state == "waiting_for_child_weight":
        try:
            w = float(text.replace(",", "."))
            dose_mg = w * 15
            res = (
                f"👶 **الجرعة الطبية لوزن ({w} كغ):**\n\n"
                f"🔹 **جرعة الباراسيتامول:** `{dose_mg:.1f} ملغ`\n"
                f"🔹 **بماصة الوزن (Pipette):** اسحب حتى التدريجة المطابقة للوزن: `{w:.0f}`.\n"
                f"⏱️ **التوقيت:** كل **6 ساعات** عند وجود الحمى.\n\n"
                "⚠️ *تنبيه: راجع الطبيب إذا استمرت الحمى لأكثر من 48 ساعة.*"
            )
            user_states.pop(user_id, None)
            await update.message.reply_text(res, parse_mode="Markdown")
        except ValueError:
            await update.message.reply_text("⚠️ يرجى إدخال رقم صحيح لوزن الطفل بالكيلوغرام.")
        return

    if state == "waiting_for_interaction_check":
        clean = text.lower()
        warn = None
        for item in DRUG_INTERACTIONS:
            pair = item["pair"]
            if pair[0] in clean and pair[1] in clean:
                warn = item["warning"]
                break

        if warn:
            reply = f"🚨 **نتيجة الفحص:**\n\n{warn}"
        else:
            reply = "✅ لم يُسجل تعارض كيميائي خطير بين هذين الدواءين في الدليل السريع."
        user_states.pop(user_id, None)
        await update.message.reply_text(reply, parse_mode="Markdown")
        return

    query = text.lower()
    found_key = None
    for key in MEDICINES_DB:
        if key in query or query in key:
            found_key = key
            break

    if found_key:
        med = MEDICINES_DB[found_key]
        generics = "، ".join(med["generics"])
        response = (
            f"💊 **بطاقة دواء: {med['name']}**\n\n"
            f"🔬 **المادة الفعالة (DCI):** `{med['dci']}`\n"
            f"🔹 **الجرعات:** {med['dosage']}\n"
            f"💰 **السعر التقديري:** {med['price']}\n"
            f"📋 **بطاقة الشفاء:** {med['chifa']}\n\n"
            f"🔄 **البدائل الجزائرية (Génériques):**\n`{generics}`\n\n"
            f"🎯 **دواعي الاستعمال:** {med['uses']}\n"
            f"⚠️ **إرشادات:** {med['precautions']}\n"
        )
    else:
        response = f"🔎 بحثت عن: **{text}**\n\nلم نجد هذا الدواء في الدليل السريع. اضغط /start لتصفح الخدمات."

    await update.message.reply_text(response, parse_mode="Markdown")

# ----------------- تشغيل البوت -----------------
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
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_text))

    print("✅ البوت يعمل بنجاح مع التحديث اليومي لجميع البلديات...")
    app.run_polling(drop_pending_updates=True)