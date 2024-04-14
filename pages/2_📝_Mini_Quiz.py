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
    st.session_state['question'] = f"What is {emoji}?"
    st.write(st.session_state['question'])
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
        st.write("Correct! 🎉")
        st.session_state['score'] += 1
        st.session_state['options'] = []
        st.session_state['question'] = ""
        st.session_state['correct_answer'] = ""
        if st.session_state['question_number'] < len(products) - 1:
            st.session_state['question_number'] += 1
            #st.experimental_rerun()
            st.rerun()
        else:
            st.write(f"Congratulations! You answered all questions correctly. Your final score is {st.session_state['score']} out of {len(products)}.")
            #st.session_state.clear()
            del st.session_state["score"]
            del st.session_state["options"]
            del st.session_state["question"]
            del st.session_state["question_number"]
            del st.session_state["correct_answer"]
            time.sleep(2)
            st.switch_page('pages/3_🤖_Survey_Chat_Bot.py')
    else:
        st.write("GAME OVER")
        st.write(f"Your final score is {st.session_state['score']} out of {len(products)}.")
        #st.session_state.clear()
        del st.session_state["score"]
        del st.session_state["options"]
        del st.session_state["question"]
        del st.session_state["question_number"]
        del st.session_state["correct_answer"]
        time.sleep(2)
        st.switch_page('pages/3_🤖_Survey_Chat_Bot.py')

