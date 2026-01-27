import streamlit as st
from PIL import Image
from boot2 import chatbot_response
import os
st.set_page_config(
    page_title="Chatbot كلية الهندسة",
    page_icon="🧠",
    layout="wide"
)

# --- CSS الخلفية والمربعات الشفافة ---
st.markdown(
    """
    <style>
    .stApp { background-color: #248f8f; }
    .bot_msg { background-color: rgba(255,255,255,0.7); color: #0D47A1; padding:10px; border-radius:10px; margin-bottom:5px; }
    .user_msg { background-color: rgba(255,255,255,0.7); color: #1A237E; padding:10px; border-radius:10px; margin-bottom:5px; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- الصورة والنص الترحيبي ---
logo_path = "logo.png"

if not os.path.exists(logo_path):
    st.error("الصورة logo.png غير موجودة!")
else:
    logo = Image.open(logo_path)
    st.image(logo)

st.markdown(
    """
    <div style="text-align:center;">
        <h1 style='color:#6e6191; font-family:Arial;'>🤖 Chatbot كلية الهندسة</h1>
        <p style='color:#e0f7f7; font-size:16px;'>
            تقدر تسألني أي شيء عن الجامعة: القسط، المواد، المدة، أو المعدل<br>
            أو إذا تحب، أساعدك تختار القسم الأنسب لك لو محتار 😎<br><br>
            🌐 <a href="https://alzahraa.edu.iq/ar" target="_blank" style="color:#ffffff;">الموقع الرسمي</a> |
            📘 <a href="https://www.facebook.com/p/%D9%83%D9%84%D9%8A%D8%A9-%D8%A7%D9%84%D9%87%D9%86%D8%AF%D8%B3%D8%A9-%D9%88-%D8%AA%D9%83%D9%86%D9%88%D9%84%D9%88%D8%AC%D9%8A%D8%A7-%D8%A7%D9%84%D9%85%D8%B9%D9%84%D9%88%D9%85%D8%A7%D8%AA-%D8%AC%D8%A7%D9%85%D8%B9%D8%A9-%D8%A7%D9%84%D8%B2%D9%87%D8%B1%D8%A7%D8%A1-%D8%B9-%D9%84%D9%84%D8%A8%D9%86%D8%A7%D8%AA-61561659693502/" target="_blank" style="color:#ffffff;">فيسبوك</a> |
            📸 <a href="https://www.instagram.com/college.of.engineering_and_it?igsh=aGEyN2FwczAyZHM3" target="_blank" style="color:#ffffff;">انستغرام</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- قائمة اقتراحات الأسئلة ---
suggestions = [
    "عرف قسم الذكاء الاصطناعي",
    "شكد معدل الأمن السيبراني",
    "شكد قسط الحوسبة",
    " شكد مدة الدراسة التصميم ",
    "شنو المواد المهمة للحوسبة",
    "اختار لي القسم المناسب",
    "شنو الفرق بين الذكاء و الامن ",
    "شنو الفرق بين التصميم و العمارة",
"كلية الهندسة شنو بيها أقسام؟",
    "مدة الدراسه في قسم الذكاء",
]


# --- نموذج الإدخال مع اقتراحات ---
with st.form(key="chat_form", clear_on_submit=True):
    user_msg = st.selectbox(
        "أنتِ:",
        options=[""] + suggestions,
        index=0
    )
    custom_msg = st.text_input("أو اكتب سؤالك بنفسك:")
    submit_button = st.form_submit_button("إرسال")

# --- تحديد الرسالة النهائية ---
final_msg = custom_msg if custom_msg.strip() else user_msg

# --- المعالجة والتخزين ---
if submit_button and final_msg:
    reply = chatbot_response(final_msg)
    st.session_state.chat_history.append(("أنت", final_msg))
    st.session_state.chat_history.append(("🤖", reply))

# --- عرض المحادثة ---
st.markdown("---")
for sender, msg in st.session_state.chat_history:
    if sender == "أنت":
        st.markdown(f"<div class='user_msg'><b>{sender}:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot_msg'><b>{sender}:</b> {msg}</div>", unsafe_allow_html=True)






