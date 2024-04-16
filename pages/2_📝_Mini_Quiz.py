import streamlit as st
from streamlit_lottie import st_lottie
import random
import base64
import time

products = [
    ("Tide", "🧺"),
    ("Pampers", "👶"),
    ("Gillette", "🪒"),
    ("Oral-B", "🦷"),
    ("Pantene", "💇"),
]

# To set background
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("image.jpg")

with open('style.css') as f:
    css = f.read().replace("{img}", img)

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Play audio after page switched
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true" loop>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )
autoplay_audio("game_music.mp3")

# Formatting and displaying lottie
def auto_lottie(url):
    st_lottie(url,
                height=170,
                width=140,
                speed=1,
                loop=True)


st.title("Stage 🥈: Mini Quiz")

random.shuffle(products)

if 'score' not in st.session_state:
    st.session_state['score'] = 0
if 'question_number' not in st.session_state:
    st.session_state['question_number'] = 0
if 'options' not in st.session_state:
    st.session_state['options'] = []
if 'question' not in st.session_state:
    st.session_state['question'] = ""
if 'correct_answer' not in st.session_state:
    st.session_state['correct_answer'] = ""

product, emoji = products[st.session_state['question_number']]

if not st.session_state['options']:
    st.session_state['question'] = f"Q: Which brand do you think the icon {emoji} represents?"
    st.markdown(f'<h1 style="font-size:40px;">{st.session_state["question"]}</h1>', unsafe_allow_html=True)
    wrong_answer = random.choice([p for p, e in products if p != product])
    st.session_state['options'] = [product, wrong_answer]
    random.shuffle(st.session_state['options'])
    st.session_state['correct_answer'] = product
else:
    st.write(st.session_state['question'])

col1, col2 = st.columns(2)
answer = None
if col1.button(st.session_state['options'][0]):
    answer = st.session_state['options'][0]
elif col2.button(st.session_state['options'][1]):
    answer = st.session_state['options'][1]



if answer:
    if answer == st.session_state['correct_answer']:
        st.markdown('<h1 style="font-size:30px;">Correct! 🎉</h1>', unsafe_allow_html=True)
        st.session_state['score'] += 1
        st.session_state['options'] = []
        st.session_state['question'] = ""
        st.session_state['correct_answer'] = ""
        if st.session_state['question_number'] < len(products) - 1:
            st.session_state['question_number'] += 1
            #st.experimental_rerun()
            st.rerun()
        else:
            st.markdown(f'<h1 style="font-size:40px;">Congratulations! You answered all questions correctly. Your final score is {st.session_state["score"]} out of {len(products)}.</h1>', unsafe_allow_html=True)
            #st.session_state.clear()
            del st.session_state["score"]
            del st.session_state["options"]
            del st.session_state["question"]
            del st.session_state["question_number"]
            del st.session_state["correct_answer"]
            auto_lottie("https://lottie.host/7e5dfe9f-ec0f-4f8f-8797-f06b6bd0fea4/aaw25hKs6x.json")
            time.sleep(3)
            st.switch_page('pages/3_🤖_Survey_Chat_Bot.py')
    else:
        st.markdown('<h1 style="font-size:40px;">GAME OVER</h1>', unsafe_allow_html=True)
        st.markdown(f'<h1 style="font-size:40px;">Your final score is {st.session_state["score"]} out of {len(products)}.</h1>', unsafe_allow_html=True)
        #st.session_state.clear()
        del st.session_state["score"]
        del st.session_state["options"]
        del st.session_state["question"]
        del st.session_state["question_number"]
        del st.session_state["correct_answer"]
        auto_lottie("https://lottie.host/7e5dfe9f-ec0f-4f8f-8797-f06b6bd0fea4/aaw25hKs6x.json")
        time.sleep(3)
        st.switch_page('pages/3_🤖_Survey_Chat_Bot.py')

left1, mid, right1, right2 = st.columns(4)
with right2:
    auto_lottie('https://lottie.host/eee6ffd1-13ed-44e4-b2c6-317f84826997/x4iEck37Qp.json')
