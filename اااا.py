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
logo_path = os.path.join("images", "logo.png")
logo = Image.open(logo_path)

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

# --- المحادثة ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# --- نموذج الإدخال مع زر إرسال ---
with st.form(key="chat_form", clear_on_submit=True):
    user_msg = st.text_input("أنت ")
    submit_button = st.form_submit_button("إرسال")

if submit_button and user_msg:
    reply = chatbot_response(user_msg)
    st.session_state["chat_history"].append(("أنت", user_msg))
    st.session_state["chat_history"].append(("🤖", reply))

# --- عرض المحادثة (آخر رسالة فوق) ---
for sender, msg in reversed(st.session_state["chat_history"]):
    if sender == "🤖":
        st.markdown(f'<div class="bot_msg"><b>{sender}:</b> {msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="user_msg"><b>{sender}:</b> {msg}</div>', unsafe_allow_html=True)

# streamlit run اااا.py


