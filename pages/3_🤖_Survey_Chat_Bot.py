import streamlit as st
import backend as b
import random
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
    if rating >= 3:
        return random.choice(good)
    else:
        return random.choice(bad)      

# Create dataframe
df = b.create_df()
    
st.title("Survey Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    starting_message = """ Welcome to the P&G survey interface! I am your survey assistant. """
    st.session_state.messages = [{"role": "assistant", "content": starting_message}]

if "stage" not in st.session_state:
    st.session_state.stage = "products"

if "rating_boolean" not in st.session_state:
    st.session_state.rating_boolean = True

# for storing rating from widget in chat message 
if "radio" not in st.session_state:
    st.session_state.radio = 1    
    
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Welcome to the survey interface!") or st.session_state.stage=="products" or st.session_state.stage=="rating" or st.session_state.stage=="repurchase":
    st.session_state.rating_boolean = True

    if st.session_state.stage == "final_feedback":
        with st.chat_message("user"):
            st.markdown(prompt) 
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Insert response into MySQL
        row = b.get_row()
        data = tuple(row, prompt)
        b.insert_data("feedback", data, 2)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = "I see! This is the end of the survey! Thank you for your time and effort!"
                st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.balloons()
    
    if st.session_state.stage == "other_feedback":
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.responses.append(prompt)

        # Insert responses into MySQL database
        data = tuple(st.session_state.responses)
        b.insert_data(st.session_state.current_product[1], data, len(st.session_state.responses))

        #Remove the first brand_product from the brand_product list
        st.session_state.brand_product.pop(0) 

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if len(st.session_state.brand_product)==0: # No more products in the brand_product list
                    response = "Before we end the survey, any last feedback?"
                    st.session_state.stage = "final_feedback"
                else: #Still got products in the brand_product list
                    st.session_state.current_product = st.session_state.brand_product[0]
                    response = f"""Let's move on to the next product, which is {st.session_state.current_product[1]}
                    from {st.session_state.current_product[0]}.
                    How would you rate {st.session_state.current_product[1]} out of 5? (1 being very unhappy with 
                    the product and 5 being very happy with the product)"""
                    st.radio("Rating", [1,2,3,4,5], horizontal=True, key="radio")
                    st.session_state.stage = "rating"
                    st.session_state.rating_boolean = False #so that we will not go to the rating stage straight away
                    
        st.write(response)       
        st.session_state.messages.append({"role": "assistant", "content": response})

    if st.session_state.stage == "repurchase":
        with st.chat_message("user"):
            st.markdown(st.session_state.radio)
        st.session_state.messages.append({"role": "user", "content": st.session_state.radio})
        st.session_state.responses.append(st.session_state.radio)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                st.write(react(st.session_state.radio))
                response = f"I see! Any other feedback for the {st.session_state.current_product[1]} from {st.session_state.current_product[0]}?"
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
                response = f"""I see! We will take your suggestion into consideration! Next, how likely will you repurchase the
                {st.session_state.current_product[1]} from {st.session_state.current_product[0]} on a scale of 1 to 5? (1 being very unlikely to repurchase the product and 5 being very likely to 
                repurchase the product)"""
                st.write(response)
                st.radio("Repurchase Rating", [1,2,3,4,5], horizontal=True, key="radio")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.stage = "repurchase"      
            
    if st.session_state.stage == "more_feedback":
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                current_feature = list(st.session_state.features_questions.keys())[0]
                st.session_state.features_dict[current_feature] = prompt
                del st.session_state.features_questions[current_feature]
                if len(st.session_state.features_questions)==0:
                    response = f"I see! Now, what kind of improvements would you like to see in the {st.session_state.current_product[1]} from {st.session_state.current_product[0]}?"
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
                features = df[df["product"]==st.session_state.current_product[1]]["features"].values[0]
                features_lst = features.split(",")
                features_lst = [f.strip() for f in features_lst]
                features_dict = b.generate_dict(prompt, features_lst)
                if st.session_state.current_product[1] == "fabric_softener":
                    product = "Fabric Softener" #For some reason, if the input is fabric_softener, the function generate_features_questions will not work
                    features_questions = b.generate_features_questions(product, features_dict)
                else:
                    features_questions = b.generate_features_questions(st.session_state.current_product[1], features_dict) #features_questions should be a dictionary
                if len(features_questions)==0: #When there are no missing features already
                    response = f"I see! Now, what kind of improvements would you like to see in the {st.session_state.current_product[1]} from {st.session_state.current_product[0]}?"
                    st.session_state.stage = "improvements"
                    for f in features_lst:
                        st.session_state.responses.append(features_dict[f])
                else:
                    response = list(features_questions.values())[0] #Get the first question from the dictionary
                    if "features_questions" not in st.session_state:
                        st.session_state.features_questions = []
                    st.session_state.features_questions = features_questions
                    if "features_dict" not in st.session_state:
                        st.session_state.features_dict = []
                    st.session_state.features_dict = features_dict
                    if "features_lst" not in st.session_state:
                        st.session_state.features_lst = []
                    st.session_state.features_lst = features_lst
                    st.session_state.stage = "more_feedback"
                st.write(response)
      
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.stage = "more_feedback"

    if st.session_state.stage == "rating" and st.session_state.rating_boolean:
        with st.chat_message("user"):
            st.markdown(st.session_state.radio)
        st.session_state.messages.append({"role": "user", "content": st.session_state.radio})
        
        if "responses" not in st.session_state:
            st.session_state.responses = []
        st.session_state.responses = [b.get_row(), st.session_state.current_product[0], st.session_state.radio] #These will be stored in the database later
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                st.write(react(st.session_state.radio))
                response = f"Any reasons for giving {st.session_state.current_product[1]} from {st.session_state.current_product[0]} this rating?"
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
            brand = item[0]
            product = item[1]
            new_brand_product.append((brand, product))
        st.session_state.brand_product = new_brand_product

        # Get the current product
        if "current_product" not in st.session_state:
            st.session_state.current_product = st.session_state.brand_product[0]
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = f"""Let's start with the {st.session_state.current_product[1]} from {st.session_state.current_product[0]}! How would you rate the {st.session_state.current_product[1]} out of 5? (1
                being very unhappy with the product and 5 being very happy with the product)"""
                st.write(response)
                st.radio("Product Rating", [1,2,3,4,5], horizontal=True, key="radio")
        st.session_state.messages.append({"role": "assistant", "content": response}) 
        st.session_state.stage = "rating"

# uncomment the following line to view session state on every response in app
st.write(st.session_state)


        
        