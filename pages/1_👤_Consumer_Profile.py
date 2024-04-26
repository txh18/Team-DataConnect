import streamlit as st
from streamlit_lottie import st_lottie
import mysql
import backend as b
import base64
import time
import json

# Set up database
b.csv_to_mysql()

# To set background
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("image.jpg")

# Applying style css file to consumer profile page
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

# Title
st.title("Stage 🥇: Consumer Profile")

# To keep track of which fields user has filled up
check = 0

# Customising slider colour using css
slider_thumb_color_css = """
<style>
div.st-emotion-cache-szxv3m.ew7r33m3[role="slider"] {
    background-color: #763626; /* thumb color */
}
div[data-testid="stThumbValue"] {
    color: #000000; /* font color */
}

</style>
"""

st.markdown(slider_thumb_color_css, unsafe_allow_html=True)

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

# Formatting subheader
st.subheader("Surveyee Information 👤")

# Age section
st.write("1. How old are you?")
age = st.slider("Age", 0, 100)
if age != 0: check += 1
else: st.error('This is a required field')
st.write('You selected:', age, 'Years Old')

# Gender section
st.write("2. What is your gender?")
gender = st.selectbox('Gender', 
                      ('select', 'Male', 'Female', 'Other', 'Prefer not to say'))

if gender == 'select': 
    st.error('This is a required field')
else: check += 1

st.write('You selected:', gender)

# Getting brand names and logos
brand_names = b.get_brands()
brand_logos = ['A.png', 'B.png', 'C.png', 'D.png', 'E.png', 'F.png']

# To keep track of selected brands 
selected = []
checkboxes = []
st.subheader("Product Review Selection ✔️")
st.write("You may choose up to 3 products to review. Please select the brands first then the products.")
st.write('3. Select brands:')

# Formatting checkboxes with logos as 3 columns
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

# List of products for every brand
pdts_by_brand = b.get_pdts_by_brand()

# Keeping track of options for the multiselect for part 4, selecting products 
options = []
for c in checkboxes:
    if c:
        pos = checkboxes.index(c)
        brand = brand_names[pos]
        pdt_ls = pdts_by_brand[pos]
        for item in pdt_ls:
            options.append(f"{brand}: {item}")
        checkboxes[pos] = False

# Selecting products to review
st.write("4. Select Products (Maximum of 3): ")
selected = st.multiselect('Products:', options, max_selections = 3)

if len(selected) != 0:
    check += 1 
else: st.error('Please select up to 3 products to review')

st.write('Selected products:', ', '.join(selected))

if "brand_product" not in st.session_state:
    st.session_state["brand_product"] = []
st.session_state["brand_product"] = selected

# Ensure all fields filled before moving to next section
if check < 3: 
    cont = st.button('Please fill up all fields', disabled = True)
else:
    st.write("Before we proceed to the survey questions, let's play a short quiz!")
    cont = st.button('Click to proceed', on_click=auto_lottie('checked.json'))
if cont: 
    # Insert consumer profile information into MySQL database
    data = tuple([age, gender])
    b.insert_surveyee(data)
    st.switch_page('pages/2_📝_Mini_Quiz.py')
