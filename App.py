import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_extras.let_it_rain import rain
import time
import base64

#page config
st.set_page_config(
    page_title='Welcome to P&G Survey!',
    page_icon = '🤖',
    menu_items = {
        'About': '# P&G Consumer Survey. This is a survey aimed at collecting consumer feedback to better improve P&G\'s products. Thank you for your help! 😊 '}
)

st.header('P&G Consumer Feedback Survey', divider='blue')


# To set background
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("image.jpg")

with open('style.css') as f:
    css = f.read().replace("{img}", img)

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Play audio
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

# Custom robot rain animation
def robot_rain():
    rain(
        emoji = "🤖",
        font_size = 54,
        falling_speed = 10,
        animation_length = 1
    )

# Including robot animation
# lottie_url = 'https://assets5.lottiefiles.com/packages/lf20_V9t630.json'
# st_lottie(lottie_url, key="user")

robot_url = 'https://lottie.host/f0d1c12b-0ae9-495c-943c-c7949c331928/xUGcwnw9eA.json'
st_lottie(robot_url)
robot_rain()

chat = st.chat_message("ai", avatar="🤖")
chat.write("Are you ready?")
if st.button(label='START', help='click to begin', type='primary', use_container_width = True):
    st.balloons()
    time.sleep(1)
    st.switch_page('pages/1_👤_Consumer_Profile.py')

