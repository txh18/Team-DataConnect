import streamlit as st
from streamlit_lottie import st_lottie
import mysql
import backend as b
import base64
import time

# Set up database
b.csv_to_mysql()

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


st.title("Stage 🥇: Consumer Profile")

check = 0

slider_thumb_color_css = """
<style>
div.st-emotion-cache-szxv3m.ew7r33m3[role="slider"] {
    background-color: #763626; /* thumb color */
}
div[data-testid="stThumbValue"] {
    color: #FFFFFF; /* font color */
}

</style>
"""

st.markdown(slider_thumb_color_css, unsafe_allow_html=True)

# Formatting and displaying lottie
def auto_lottie(url):
    st_lottie(url,
                height=170,
                width=140,
                speed=1,
                loop=True)

st.subheader("Surveyee Information 👤")
st.write("1. How old are you?")
age = st.slider("Age", 0, 100)
if age != 0: check += 1
else: st.error('This is a required field')
st.write('You selected:', age, 'Years Old')

st.write("2. What is your gender?")
gender = st.selectbox('Gender', 
                      ('select', 'Male', 'Female', 'Other', 'Prefer not to say'))

if gender == 'select': 
    st.error('This is a required field')
else: check += 1

st.write('You selected:', gender)

brand_names = b.get_brands()
brand_logos = ['A.png', 'B.png', 'C.png', 'D.png', 'E.png', 'F.png']

selected = []
checkboxes = []
st.subheader("Product Review Selection ✔️")
st.write("You may choose up to 3 products to review. Please select the brands first then the products.")
st.write('3. Select brands:')

# putting checkboxes w logos as columns
rows = []
for r in range(2):
    rows.append(st.columns(3))

for brand in brand_names:
    n = brand_names.index(brand)
    with st.container(border = True):
        rownum = n//3
        with rows[rownum][n%3]:
            box = st.checkbox(brand, False, st.image('images/' +  brand_logos[n]))
            checkboxes.append(box)

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

st.write("4. Select Products (Maximum of 3): ")
selected = st.multiselect('Products:', options, max_selections = 3)

if len(selected) != 0:
    check += 1 
else: st.error('Please select up to 3 products to review')

st.write('Selected products:', ', '.join(selected))

if "brand_product" not in st.session_state:
    st.session_state["brand_product"] = []
st.session_state["brand_product"] = selected

if check < 3: 
    cont = st.button('Please fill up all fields', disabled = True)
else:
    st.write("Before we proceed to the survey questions, let's play a short quiz!")
    cont = st.button('Click to proceed', on_click=auto_lottie('https://lottie.host/7e5dfe9f-ec0f-4f8f-8797-f06b6bd0fea4/aaw25hKs6x.json'))
if cont: 
    # Insert consumer profile information into MySQL database
    data = tuple([age, gender])
    b.insert_surveyee(data)
    st.switch_page('pages/2_📝_Mini_Quiz.py')
