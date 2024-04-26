import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_extras.let_it_rain import rain
import time
import base64
import json

# Page configuration
st.set_page_config(
    page_title='Welcome to Company Survey!',
    page_icon = '🤖',
    menu_items = {
        'About': '# Company Consumer Survey. This is a survey aimed at collecting consumer feedback to better improve P&G\'s products. Thank you for your help! 😊 '}
)

st.header('Company Consumer Feedback 🎮', divider='blue')

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

# Custom robot rain animation
def robot_rain():
    rain(
        emoji = "🎮",
        font_size = 20,
        falling_speed = 10,
        animation_length = 1
    )

# Formatting and displaying lottie animation
def auto_lottie(filepath: str):
    with open(filepath, "r") as  f:
        loaded = json.load(f)

    st_lottie(
        loaded,
        height=170,
        width=140,
        speed=1,
        loop=True)

# Including robot animation
# st_lottie(lottie_url, key="user")

left1, left2, mid, right1, right2 = st.columns(5)
with mid:
    auto_lottie("welcome_robot.json")


robot_rain()

# Button to start survey
if st.button(label='START', help='click to begin', type='primary', use_container_width = True):
    st.balloons() # animation
    time.sleep(1) # allow time for animation to be completed before moving to next section
    st.switch_page('pages/1_👤_Consumer_Profile.py') # Switching to consumer profile page once user clicked on button

autoplay_audio("game_music.mp3") 