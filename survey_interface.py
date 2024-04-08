import streamlit as st
import random
import time
import pandas as pd
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

df = pd.read_csv('product_info.csv')
selected_product = "Fabric Softener"
features = df.loc[df['Product'] == selected_product, 'Features'].values[0]

llm = Ollama(model="llama2:7b-chat", format='json', temperature=0)

def products_stage(products):
    template = """
    Your job is to ask the customer questions. Please ask the customer how they find the {products}.
    Please also ask the customer to give the {products} a rating out of 5.
    Example:
    products: diapers
    output: How much would you rate the diapers out of 5 and could you give me some feedback on the diapers?
    """
    prompt = PromptTemplate(template=template, input_variables=["products"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    return eval(llm_chain.invoke(input={'products': products})['text'])['description']

def check_feedback(feedback):
    template = """
    Your job is to classify feedback {feedback} as "Yes" if it sounds like a product feedback from customers,
    and "No" if it does not sound like a product feedback from customers. 
    Example:
    feedback : Fantastic! The new vacuum cleaner's suction power is incredible, making cleaning effortless.
    output: Yes
    """
    prompt = PromptTemplate(template=template, input_variables=["feedback"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    return eval(llm_chain.invoke(input={'feedback': feedback})['text'])

def generate_dict(feedback):
    system = """
    Your job is to extract different features of a product from customer feedbacks. 
    Consider the following format for output, leave response as a python dictionary:
    # Feature 1: Concise review on feature 1
    # Feature 2: Concise review on feature 2
    # Feature 3: Concise review on feature 3
    # Feature 4: Concise review on feature 4

    Here is the list of features to categorise the feedback into: {features}
    If features are not mentioned, leave section as empty python string.
    Provide your output here:
    """
    human = """
    {feedback}
    """
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    chain = prompt | llm
    text = chain.invoke({
    "feedback": feedback,
    "features": features,
    })
    return eval(text)

def generate_questions(missing_features):
    template = """
    Your job is to ask customers questions about the {selected_product} based on the {missing_features}.
    Please ask one question for each missing feature.
    """
    prompt = PromptTemplate(template=template, input_variables=["selected_product", "missing_features"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    questions = llm_chain.invoke(input={'selected_product':selected_product, 'missing_features':missing_features})
    return eval(questions['text'])

def feedback_stage(feedback):
    feature_dict = generate_dict(feedback)
    missing_features = []
    for f in feature_dict:
        if feature_dict[f] == "":
            missing_features.append(f)
    return generate_questions(missing_features)
    
st.title("Survey Interface")

# Initialize chat history
if "messages" not in st.session_state:
    starting_message = """ Welcome to the P&G survey interface! I am your survey assistant. 
    To start off, please tell me which products you have purchased from P&G before. """
    st.session_state.messages = [{"role": "assistant", "content": starting_message}]

if "stage" not in st.session_state:
    st.session_state.stage = "products"
    
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Welcome to the survey interface!"):
    
    if st.session_state.stage == "feedback":
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = feedback_stage(prompt)
                st.write(response)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        if check_feedback(prompt) == "Yes":
            st.session_state.stage = "more_feedback"
            
    if st.session_state.stage == "products":
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = products_stage(prompt)
                st.write(response)
            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        #Change stage
        st.session_state.stage = "feedback"

st.write(st.session_state)
        
        