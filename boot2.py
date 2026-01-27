import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from difflib import get_close_matches
import nltk
import random
import os
from nltk.stem.isri import ISRIStemmer

# تحميل ملفات اللغة المطلوبة (بشكل آمن للسيرفر)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


# ----------------------------
# 1️⃣ دالة تنظيف النصوص
# ----------------------------
def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub("[إأآ]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ة", "ه", text)
    stop_words = ['شنو', 'شلون', 'هل', 'في', 'من', 'على', 'الي', 'هوه', 'هي', 'ما', 'هذا', 'لو']
    words = text.split()
    cleaned_words = [w for w in words if w not in stop_words]
    return " ".join(cleaned_words)


# ----------------------------
# 2️⃣ تحميل البيانات
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df_training = pd.read_csv(os.path.join(BASE_DIR, 'qustion.csv'), encoding='utf-8-sig')
df_departments = pd.read_csv(os.path.join(BASE_DIR, 'departments_utf8_bom.csv'), encoding='utf-8-sig')

df_training['Clean_Question'] = df_training['Question'].apply(clean_text)

# ----------------------------
# 3️⃣ نموذج ML
# ----------------------------
model = Pipeline([
    ('vectorizer', TfidfVectorizer()),
    ('classifier', LogisticRegression(max_iter=500))
])

X = df_training['Clean_Question']
y = df_training['Intent']
model.fit(X, y)

# ----------------------------
# 4️⃣ التعرف على الأقسام
# ----------------------------
department_keywords = {
    "هندسة العمارة": [
        "العماره", "عمارة", "معماري", "المعماري", "بناء", "تصميم داخلي",
        "خرائط", "تصاميم", "architecture"
    ],
    "هندسة الذكاء الاصطناعي": [
        "ذكاء", "الذكاء", "ذكاء اصطناعي", "AI", "برمجة", "تعلم الآلة",
        "machine learning", "روبوت", "أنظمة ذكية"
    ],
    "هندسة الأمن السيبراني": [
        "امن", "سيبراني", "الأمن", "الامن", "حماية", "network",
        "حماية المعلومات", "cybersecurity", "firewall", "hack", "اختراق"
    ],
    "هندسة الحوسبة المتنقلة": [
        "حوسبة", "متنقلة", "المتنقلة", "حوسبه", "موبايل", "تطبيقات",
        "app", "mobile", "برمجة موبايل", "Android", "iOS"
    ],
    "هندسة التصميم الرقمي": [
        "تصميم", "رقمي", "الرقمي", "واجهات", "UI", "UX", "graphic",
        "جرافيك", "تصميم مواقع", "web design"
    ]
}


def get_department_from_text(text):
    text = text.lower()
    for dept, keywords in department_keywords.items():
        for kw in keywords:
            if kw.lower() in text:
                return dept
    for dept in df_departments["Department"]:
        if dept.lower() in text:
            return dept
    return None


def get_department_info(dept_name):
    row = df_departments[df_departments["Department"] == dept_name]
    if not row.empty:
        return row.iloc[0]
    return None


def get_random_suggestion(dept_name, df_training, state):
    related = df_training[df_training['Question'].apply(
        lambda x: dept_name.lower().split()[-1] in x.lower() if pd.notna(x) else False
    )]['Question'].tolist()

    if related:
        suggested_q = random.choice(related)
        state["last_suggested_question"] = suggested_q
        return f"\n\n💡 تحب تعرف: {suggested_q}؟ (جاوب بـ نعم أو اي)"
    return ""


# ============================
# ⭐ الدالة المصححة
# ============================
def chatbot_response(user_input, state):
    cleaned = clean_text(user_input)
    dept_name = get_department_from_text(user_input)

    # 🔹 تحديث القسم الحالي ومسح الاقتراح القديم
    if dept_name:
        if dept_name != state["active_department"]:
            state["active_department"] = dept_name
            state["last_suggested_question"] = None

    # إذا وافق المستخدم على السؤال المقترح
    if state["last_suggested_question"] and any(word in cleaned for word in ["نعم", "اي", "أكيد", "طبعا"]):
        match = get_close_matches(
            clean_text(state["last_suggested_question"]),
            df_training['Clean_Question'],
            n=1,
            cutoff=0.6
        )
        state["last_suggested_question"] = None
        if match:
            return df_training[df_training['Clean_Question'] == match[0]]['Answer'].values[0]
        else:
            return "❌ لم أجد إجابة مناسبة لهذا السؤال."

    # ===============================
    # 🧠 تفعيل الاختيار الذكي
    # ===============================
    if any(word in cleaned for word in [
        "اختيار ذكي", "اختار لي", "ساعدني اختار", "اختار قسم", "اريد اختار قسم",
        "ساعدني في اختيار القسم", "مساعدة في الاختيار", "شنو القسم المناسب",
        "شنو اختار", "اقترح قسم", "أريد مساعدة في اختيار القسم", "اقترح لي قسم",
        "اختيار قسم", "اختر لي قسم"
    ]):
        state["smart_mode"] = True
        state["user_profile"] = {}
        return ("خلينا نختار أفضل قسمين لك خطوة خطوة 👇\n"
                "السؤال الأول:\n"
                "تحب أكثر:\n"
                "1️⃣ البرمجة والتفكير المنطقي\n"
                "2️⃣ التصميم والرسم\n"
                "3️⃣ الشبكات والحماية\n"
                "4️⃣ الرياضيات والتحليل\n"
                "5️⃣ العمارة والبناء\n"
                "اكتب الرقم أو الوصف")

    # ===============================
    # 🧠 مراحل الاختيار الذكي
    # ===============================
    if state["smart_mode"]:
        # السؤال الأول: الاهتمامات
        if "interest" not in state["user_profile"]:
            interests_map = {
                "1": "programming", "برمجة": "programming",
                "2": "design", "تصميم": "design", "رسم": "design",
                "3": "security", "شبكات": "security", "حماية": "security",
                "4": "math", "رياضيات": "math", "تحليل": "math",
                "5": "architecture", "عمارة": "architecture", "بناء": "architecture"
            }
            for key, value in interests_map.items():
                if key in cleaned:
                    state["user_profile"]["interest"] = value
                    break

            if "interest" not in state["user_profile"]:
                return "جاوبني: تحب برمجة، تصميم، شبكات، رياضيات، أو عمارة؟"

            return ("السؤال الثاني:\n"
                    "تفضل الدراسة تكون:\n"
                    "1️⃣ عملية (تطبيق ومشاريع)\n"
                    "2️⃣ نظرية (تحليل ودراسة)\n"
                    "اكتب 1 أو 2")

        # السؤال الثاني: نوع الدراسة
        elif "study_type" not in state["user_profile"]:
            if "1" in cleaned or "عملي" in cleaned:
                state["user_profile"]["study_type"] = "practical"
            elif "2" in cleaned or "نظري" in cleaned:
                state["user_profile"]["study_type"] = "theoretical"
            else:
                return "جاوبني: تفضل عملي لو نظري؟"

            return ("السؤال الثالث:\n"
                    "تحب تشتغل مستقبلاً أكثر مع:\n"
                    "1️⃣ أجهزة وأنظمة\n"
                    "2️⃣ برامج وتطبيقات\n"
                    "3️⃣ تصاميم وواجهات\n"
                    "اكتب الرقم")

        # السؤال الثالث: نوع العمل
        elif "work_type" not in state["user_profile"]:
            if "1" in cleaned:
                state["user_profile"]["work_type"] = "hardware"
            elif "2" in cleaned:
                state["user_profile"]["work_type"] = "software"
            elif "3" in cleaned:
                state["user_profile"]["work_type"] = "design"
            else:
                return "جاوبني: 1 أجهزة، 2 برامج، 3 تصميم؟"

            state["smart_mode"] = False
            interest = state["user_profile"]["interest"]
            work = state["user_profile"]["work_type"]
            recommendations = []

            if interest == "programming":
                if work == "software":
                    recommendations = ["هندسة الذكاء الاصطناعي", "هندسة الحوسبة المتنقلة"]
                else:
                    recommendations = ["هندسة الحوسبة المتنقلة", "هندسة الأمن السيبراني"]
            elif interest == "design":
                recommendations = ["هندسة التصميم الرقمي", "هندسة العمارة"]
            elif interest == "security":
                recommendations = ["هندسة الأمن السيبراني", "هندسة الحوسبة المتنقلة"]
            elif interest == "math":
                recommendations = ["هندسة الذكاء الاصطناعي", "هندسة الحوسبة المتنقلة"]
            elif interest == "architecture":
                recommendations = ["هندسة العمارة", "هندسة التصميم الرقمي"]

            state["user_profile"]["recommended"] = recommendations
            return ("أفضل قسمين لك هما 🎓:\n" + " و ".join(recommendations))

    # ===============================
    # ❓ الأسئلة العادية
    # ===============================

    if any(word in cleaned for word in ["قسط ", "مبلغ", "مال", "فلوس"]):
        if not dept_name:
            return "رجاءً حدّد القسم حتى أحسب لك القسط."
        info = get_department_info(dept_name)
        if info is None:
            return "ما لقيت معلومات عن هذا القسم."

        gpa_match = re.search(r'\d+', cleaned)
        suggestion = get_random_suggestion(dept_name, df_training, state)

        if gpa_match:
            gpa = int(gpa_match.group())
            if gpa >= 85:
                return f"القسط في {dept_name} هو {info['Fee_Above_85']} 💵{suggestion}"
            else:
                return f"القسط في {dept_name} هو {info['Fee_Below_85']} 💵{suggestion}"
        else:
            return (f"القسط في {dept_name} حسب بيانات الجامعة:\n"
                    f"إذا معدلك 85 أو أكثر: {info['Fee_Above_85']}\n"
                    f"إذا معدلك أقل من 85: {info['Fee_Below_85']}"
                    f"{suggestion}")

    elif any(word in cleaned for word in [
        "مهارات", "مواد", "مقررات", "دورات", "المواد الدراسية",
        "المهارات المطلوبة", "الكورسات", "المقررات الدراسية"
    ]):
        if dept_name:
            info = get_department_info(dept_name)
            suggestion = get_random_suggestion(dept_name, df_training, state)
            return (f"{dept_name}:\nالمهارات والمواد:\n{info['Key_Courses']}{suggestion}")
        else:
            return "رجاءً حدّد القسم حتى أعطيك المهارات والمواد."

    else:
        match = get_close_matches(cleaned, df_training['Clean_Question'], n=1, cutoff=0.5)
        if match:
            return df_training[df_training['Clean_Question'] == match[0]]['Answer'].values[0]

        return "ما فهمت قصدك تماماً، تكدر تسألني عن مهارات قسم معين أو القسط أو الفرق بين الأقسام."
