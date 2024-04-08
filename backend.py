import pandas as pd
import mysql.connector
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialise an llm instance
llm = Ollama(model="llama2:7b-chat", format='json', temperature=0)

# Connect to the MySQL server and create dataframe
def create_df():
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
                              host='teamdataconnect.ch6uykso0lba.ap-southeast-2.rds.amazonaws.com',
                              database='dsa3101db')
    cursor = cnx.cursor()
    cursor.execute("SHOW TABLES")
    df = pd.DataFrame(columns=['product','features'])
    count = -1
    for table in cursor.fetchall():
        table_name = table[0].decode()
        if table_name != "surveyees":
            count += 1
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            feat = [column[0] for column in columns[3:-3]]
            new_row = {'product':table_name, 'features':feat}
            df.loc[count] = new_row
    df['features'] = df['features'].apply(lambda x: ', '.join(x))
    cursor.close()
    cnx.close()
    return df

# Insert data into MySQL table
def insert_data(table_name, data, num):
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
        host='teamdataconnect.ch6uykso0lba.ap-southeast-2.rds.amazonaws.com',
        database='dsa3101db')
    cursor = cnx.cursor()
    query = "INSERT INTO " + table_name + " VALUES (" + "%s,"*(num-1) + "%s)"
    cursor.execute(query, data)
    cnx.commit()
    cursor.close()
    cnx.close()

def rating_stage(product):
    template = """
    Your job is to ask the customer questions. Please ask the customer how they find the {product}.
    Please also ask the customer to give the {product} a rating out of 5.
    Example:
    products: shampoo
    output: How much would you rate the shampoo out of 5 and could you give me some feedback on the shampoo?
    """
    prompt = PromptTemplate(template=template, input_variables=["product"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    return eval(llm_chain.invoke(input={'product': product})['text'])['description']

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

def generate_dict(feedback, features):
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

def generate_questions(product, missing_features):
    template = """
    Your job is to ask customers questions about the {selected_product} based on the {missing_features}.
    Please ask one question for each missing feature.
    """
    prompt = PromptTemplate(template=template, input_variables=["selected_product", "missing_features"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    questions = llm_chain.invoke(input={'selected_product':product, 'missing_features': missing_features})
    return eval(questions['text'])

def generate_features_questions(product, feature_dict):
    missing_features = []
    for f in feature_dict:
        if feature_dict[f] == "":
            missing_features.append(f)
    return generate_questions(product, missing_features)