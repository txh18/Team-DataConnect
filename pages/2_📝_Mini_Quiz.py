import streamlit as st
import random
import base64
import time

products = [
    ("Tide", "🧺"),
    ("Pampers", "👶"),
    ("Gillette", "🪒"),
    ("Oral-B", "🦷"),
    ("Pantene", "💇"),
    ("Bounty", "🧻"),
    ("Charmin", "🚽"),
    ("Dawn", "🧽"),
    ("Febreze", "🌸"),
    ("Gain", "🧴"),
    ("Head & Shoulders", "🚿"),
    ("Olay", "💄"),
    ("Oral-B", "🪥"),
    ("Vicks", "🤧"),
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
if 'products' not in st.session_state:
    st.session_state['products'] = products.copy()  # Make a copy of the original products list

if not st.session_state['options']:
    if not st.session_state['products']:  # Check if the list is empty
        st.markdown('<h1 style="font-size:40px;">You have answered all questions!</h1>', unsafe_allow_html=True)
    else:
        product, emoji = random.choice(st.session_state['products'])  # Choose a random product
        st.session_state['products'].remove((product, emoji))  # Remove the chosen product from the list
        st.session_state['question'] = f"Which brand do you think the icon {emoji} represents?"
        st.markdown(f'<h1 style="font-size:40px;">{st.session_state["question"]}</h1>', unsafe_allow_html=True)
        wrong_answer = random.choice([p for p, e in products if p != product])
        st.session_state['options'] = [product, wrong_answer]
        random.shuffle(st.session_state['options'])
        st.session_state['correct_answer'] = product
else:
    st.write(st.session_state['question'])

col1, col2 = st.columns(2)
answer = None
if st.session_state['options']:
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
        if st.session_state['score'] < 5:  # Check if the score is less than 5
            st.rerun()
        else:
            st.markdown(f'<h1 style="font-size:40px;">Congratulations! You answered all questions correctly. Your final score is {st.session_state["score"]} out of 5.</h1>', unsafe_allow_html=True)
            del st.session_state["score"]
            del st.session_state["options"]
            del st.session_state["question"]
            del st.session_state["correct_answer"]
            time.sleep(2)
            st.switch_page('pages/3_🤖_Survey_Chat_Bot.py')
    else:
        st.markdown('<h1 style="font-size:40px;">GAME OVER</h1>', unsafe_allow_html=True)
        st.markdown(f'<h1 style="font-size:40px;">Your final score is {st.session_state["score"]} out of 5.</h1>', unsafe_allow_html=True)
        del st.session_state["score"]
        del st.session_state["options"]
        del st.session_state["question"]
        del st.session_state["correct_answer"]
        time.sleep(2)
        st.switch_page('pages/3_🤖_Survey_Chat_Bot.py')
