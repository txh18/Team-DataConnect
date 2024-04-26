import streamlit as st
from streamlit_lottie import st_lottie
import backend as b
import random
import base64
import time
import os
import json

# To set background
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_img_as_base64("image.jpg")

with open('style.css') as f:
    css = f.read().replace("{img}", img)

st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Default play audio when switched page
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

# Function to react to a rating response from user
def react(rating):
    good = ["😁", "😄", "🥳", "😊", "😎"]
    bad = ["🥺", "😓", "🥹", "😭"]
    if rating >= 4:
        return random.choice(good)
    else:
        return random.choice(bad)      

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

# Load the dataframe that contains the products and the features
df = b.create_df()

# Arranging the title together with an animation
col1, col2 = st.columns([0.85, 0.15])
with col1: st.title("Stage 🥉: Survey Chatbot")
with col2: auto_lottie("chatbot_robot.json")


# Initialize chat history
if "messages" not in st.session_state:
    starting_message = """ Hello! I am Steve, your survey assistant. Let's begin the survey! """
    st.session_state.messages = [{"role": "assistant", "content": starting_message}]

# Initialize stage of the survey, this helps to keep track of the stage of the survey.
if "stage" not in st.session_state:
    st.session_state.stage = "products"

if "rating_boolean" not in st.session_state:
    st.session_state.rating_boolean = True

# For storing rating from button interaction in chat message 
if "radio" not in st.session_state:
    st.session_state.radio = None   

# For keeping track of the number of times the bot asks the user to give another feedback, when the user's response is not a product feedback
if "retries" not in st.session_state:
    st.session_state.retries = 0 
    
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type your response here") or st.session_state.stage=="products" or st.session_state.stage=="rating" or st.session_state.stage=="repurchase":
    st.session_state.rating_boolean = True

    if st.session_state.stage == "final_feedback":
        with st.chat_message("user"):
            st.markdown(prompt) 
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Insert response into MySQL
        data = tuple([prompt])
        b.insert_data("feedback", data, len(data))
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = "I see! This is the end of the survey! Thank you for your time and effort!"
                st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.balloons()
        st.toast("App closing in a few seconds")
        # Give a bit of delay for user experience
        time.sleep(5)
        # Redirect to home page after survey ends
        st.switch_page("App.py")
    
    if st.session_state.stage == "other_feedback":
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.responses.append(prompt)

        # Insert responses into MySQL database
        data = tuple(st.session_state.responses)
        b.insert_data(st.session_state.current_product[1], data, len(data))

        #Remove the first brand_product from the brand_product list
        st.session_state.brand_product.pop(0) 

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                # No more products in the brand_product list
                if len(st.session_state.brand_product)==0: 
                    response = "Before we end the survey, any last feedback?"
                    st.write(response)  
                    st.session_state.stage = "final_feedback"

                #Still got products in the brand_product list
                else: 
                    st.session_state.current_product = st.session_state.brand_product[0]
                    brand = st.session_state.current_product[0]
                    product = ' '.join(st.session_state.current_product[1].split("_"))
                    response = f"""Let's move on to the next product, which is {product}
                    from {brand}.
                    How would you rate the {product} out of 7? (1 being very unhappy with 
                    the product and 7 being very happy with the product)"""
                    st.write(response)
                    st.radio("Rating", [1,2,3,4,5,6,7], horizontal=True, index= None, key="radio")
                    st.session_state.stage = "rating"
                    st.session_state.rating_boolean = False #so that we will not go to the rating stage straight away
                         
        st.session_state.messages.append({"role": "assistant", "content": response})

    if st.session_state.stage == "repurchase":
        with st.chat_message("user"):
            st.markdown(st.session_state.radio)
        st.session_state.messages.append({"role": "user", "content": st.session_state.radio})
        st.session_state.responses.append(st.session_state.radio)
        
        with st.chat_message("assistant"):
            rating = react(st.session_state.radio)
            st.write(rating)
            with st.spinner("Thinking..."):
                brand = st.session_state.current_product[0]
                product = ' '.join(st.session_state.current_product[1].split("_"))
                response = b.generate_repurchase_response(product, brand, rating)
                # response = f"I see! Any other feedback for the {st.session_state.current_product[1]} from {st.session_state.current_product[0]}?"
                st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.stage = "other_feedback" 
        
    if st.session_state.stage == "improvements":
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.responses.append(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                product = ' '.join(st.session_state.current_product[1].split("_"))
                brand = st.session_state.current_product[0]
                response = f"""I see, we will work on improving the product. Next, how likely will you repurchase the
                {product} from {brand} on a scale of 1 to 7? (1 being very unlikely to repurchase the product and 7 being very likely to 
                repurchase the product)"""
                st.write(response)
                st.radio("Repurchase Rating", [1,2,3,4,5,6,7], horizontal=True, index= None, key="radio")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.stage = "repurchase"      
            
    if st.session_state.stage == "more_feedback":
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                current_feature = list(st.session_state.features_questions.keys())[0]

                # Store the user's response into features_dict
                st.session_state.features_dict[current_feature] = prompt
                del st.session_state.features_questions[current_feature]

                # When all the features have been mentioned by the user
                if len(st.session_state.features_questions)==0:
                    product = ' '.join(st.session_state.current_product[1].split("_"))
                    brand = st.session_state.current_product[0]
                    response = b.generate_improvement_qns(product, brand)
                    st.session_state.stage = "improvements"  
                    for f in st.session_state.features_lst:
                        st.session_state.responses.append(st.session_state.features_dict[f])
                else:
                    response = list(st.session_state.features_questions.values())[0] # Get the first question from the dictionary
                st.write(response)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

    
    if st.session_state.stage == "feedback":
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_to_feedback = b.response_to_feedback(prompt)

                # If the user is not providing product feedback and the bot has not asked the user to give another feedback,
                # the bot will ask the user to provide another feedback.
                if list(response_to_feedback.keys())[0]!="Yes" and st.session_state.retries==0:
                    response = list(response_to_feedback.values())[0]
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.retries+=1
                    
                # If the bot asked the user to give another feedback previously or the user is providing relevant feedback
                else: 
                    # If the user is not providing product feedback and the bot has already asked the user to give another feedback previously,
                    # the bot will just move on to other questions.
                    if list(response_to_feedback.keys())[0]!="Yes" and st.session_state.retries==1:
                        response = """Your feedback does not seem to be providing a review about our product but nevermind,
                        let's move on to the other questions!"""
                        st.write(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.session_state.retries=0 

                    # If the user is providing product feedback
                    else:
                        st.session_state.retries=0
                        response = list(response_to_feedback.values())[0]+" Now, let's move on to the other questions!"
                        st.write(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                
                    # Get the predefined list of features for the product 
                    features = df[df["product"]=='`' + st.session_state.current_product[1] + '`']["features"].values[0]
                    features_lst = features.split(",")
                    features_lst = [f.strip() for f in features_lst]

                    # generates features_dict, where each key is a feature and each value is the information extracted from the user's feedback relevant to that feature
                    if list(response_to_feedback.keys())[0]!="Yes":
                        features_dict = b.generate_dict_empty(features_lst)
                    else:
                        features_dict = b.generate_dict(prompt, features_lst)

                    # generates the features_questions dictionary, where each key is a feature of the product not mentioned by the user's first feedback but is inside the predefined features list
                    # and each value is a question relevant to that feature that the bot wants to ask the user
                    features_questions = b.generate_features_questions(st.session_state.current_product[1], features_dict) #features_questions should be a dictionary
                
                    # When there are no missing features, move on to the next stage
                    if len(features_questions)==0: 
                        product = ' '.join(st.session_state.current_product[1].split("_"))
                        brand = st.session_state.current_product[0]
                        response = b.generate_improvement_qns(product, brand)
                        st.write(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.session_state.stage = "improvements"

                        # Adds the extracted information from user's feedback in the features_dict to the responses variable
                        for f in features_lst:
                            st.session_state.responses.append(features_dict[f])
                    else:
                        # Get the first question from the features_questions dictionary
                        response = list(features_questions.values())[0] 
                        st.write(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})

                        # Initialize features_questions variable
                        if "features_questions" not in st.session_state:
                            st.session_state.features_questions = []
                        st.session_state.features_questions = features_questions

                        # Initialize features_dict variable
                        if "features_dict" not in st.session_state:
                            st.session_state.features_dict = []
                        st.session_state.features_dict = features_dict

                        # Initialize features_lst variable
                        if "features_lst" not in st.session_state:
                            st.session_state.features_lst = []
                        st.session_state.features_lst = features_lst

                        st.session_state.stage = "more_feedback"

    if st.session_state.stage == "rating" and st.session_state.rating_boolean:

        # Display user response in chat message container
        with st.chat_message("user"):
            st.markdown(st.session_state.radio)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": st.session_state.radio})
        
        # Initialize the response variable, which will be used to keep track of user's responses.
        # These will be stored in the mySQL database later
        if "responses" not in st.session_state:
            st.session_state.responses = []
        product_brand = st.session_state.current_product[0][-1]
        st.session_state.responses = [product_brand, st.session_state.radio] 

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            rating = st.session_state.radio
            st.write(react(rating))
            with st.spinner("Thinking..."):
                features = df[df["product"]=='`' + st.session_state.current_product[1] + '`']["features"].values[0]
                features_lst = features.split(",")
                features_lst = [f.strip() for f in features_lst]
                product = ' '.join(st.session_state.current_product[1].split("_"))
                response = b.rating_response(product, rating, features_lst)
                st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.stage = "feedback"       
        
    if st.session_state.stage == "products":

        # Change the st.session_state.brand_product variable to another format
        brand_product = st.session_state.brand_product
        new_brand_product = []
        for item in brand_product:
            item = item.split(":")
            item = [i.strip() for i in item]
            brand = "Brand "+item[0]
            product = item[1]
            new_brand_product.append((brand, product))
        st.session_state.brand_product = new_brand_product

        # Get the current product
        if "current_product" not in st.session_state:
            st.session_state.current_product = st.session_state.brand_product[0]
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                # Removes the underscore in the product name
                brand = st.session_state.current_product[0]
                product = ' '.join(st.session_state.current_product[1].split("_"))
                response = f"""I see that you have selected {product} from {brand}! How would you rate the {product} out of 7? (1
                being very unhappy with the product and 7 being very happy with the product)"""
                st.write(response)
                st.radio("Product Rating", [1,2,3,4,5,6,7], horizontal=True, index= None, key="radio") # buttons for user to click to rate
        st.session_state.messages.append({"role": "assistant", "content": response}) 
        st.session_state.stage = "rating"

# Uncomment the following line to view session state on every response in app
#st.write(st.session_state) 


        
        