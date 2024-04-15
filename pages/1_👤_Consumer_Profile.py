import streamlit as st
import mysql
import backend as b
import base64

# To set background
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("image.jpg")

with open('style.css') as f:
    css = f.read().replace("{img}", img)

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Play audio after page switch
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


st.title("Consumer Profile")

name = st.text_input(
    "What is your name?"
    )
st.write('Your name:', name)

age = st.slider("How old are you?", 0, 100)

gender = st.selectbox('What is your gender?', 
                      ('Male', 'Female', 'Other', 'Prefer not to say'))
st.write('You selected:', gender)

brand_names = b.get_brands()
brand_logos = ['Pampers.png', 'Downy.png', 'Gain.jpg', 'Tide.png', 'Bounty.png', 'Charmin.png', 
               'Always.jpg', 'This_is_L..jpg', 'Gillette.png', 'Venus.png', 'Pantene.png', 
               'head & shoulders.png', 'febreze.png', 'ambi-pur.png', 'Dawn.jpg', 'Oral-B.png',
               'Crest.jpg', 'Olay.png', 'Native.png']

selected = []
checkboxes = []
st.write('Please select the brands and products you would like to review.')
st.write('Select brands:')
# putting checkboxes w logos as columns
c1, c2, c3 = st.columns(3)
with st.container():
    for brand in brand_names:
        n = brand_names.index(brand)
        if n<7: 
            with c1:
                checkboxes.append(st.checkbox(brand, st.image('images/' +  brand_logos[n])))
        elif n<13:
            with c2: 
                checkboxes.append(st.checkbox(brand, st.image('images/' +  brand_logos[n])))
        else: 
            with c3: 
                checkboxes.append(st.checkbox(brand, st.image('images/' +  brand_logos[n])))

# list of products for every brand
pdts_by_brand = b.get_pdts_by_brand()

options = []
for c in checkboxes:
    if c:
        pos = checkboxes.index(c)
        brand = brand_names[pos]
        pdt_ls = pdts_by_brand[pos]
        for item in pdt_ls:
            options.append(f"{brand}: {item}")
        checkboxes[pos] = False

selected = st.multiselect('Select Products:', options, max_selections = 3)
st.write('Selected products:', ', '.join(selected))
st.write("Before we proceed to the survey questions, let's play a short quiz game!")

if "brand_product" not in st.session_state:
    st.session_state["brand_product"] = []
st.session_state["brand_product"] = selected

st.write(st.session_state)

if st.button('Ready for a short quiz game?'): 
    # Insert consumer profile information into MySQL database
    data = tuple([age, gender])
    b.insert_surveyee(data)
    st.switch_page('pages/2_📝_Mini_Quiz.py')







