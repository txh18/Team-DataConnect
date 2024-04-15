import pandas as pd
import mysql.connector
from langchain_community.llms import Ollama
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, create_extraction_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialise an llm instance
#llm = Ollama(model="llama2:7b-chat", format='json', temperature=0, base_url="http://ollama-container:11434", verbose=True)

# Get the list of brands
def get_brands():
    df = pd.read_csv("brands_products.csv")
    return list(df["Brand"].unique())

# Get the list of products by brand
def get_pdts_by_brand():
    df = pd.read_csv("brands_products.csv")
    brands_lst = list(df["Brand"].unique())
    brands_products_lst = []
    for brand in brands_lst:
        brand_subset = df[df["Brand"]==brand]
        products_lst = list(brand_subset["Product_Category"].unique())
        products_lst = [product.strip() for product in products_lst]
        new_products_lst = []
        for product in products_lst:
            new_products_lst.append(product.lower().replace("-"," ").replace(" ","_").replace("&","and"))
        brands_products_lst.append(new_products_lst)
    return brands_products_lst


# Create tables for each product in MySQL from csv file
def csv_to_mysql():
    # Connect to the MySQL server
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
                                host='teamdataconnect.ch6uykso0lba.ap-southeast-2.rds.amazonaws.com',
                                database='dsa3101db')

    # Create a cursor object
    cursor = cnx.cursor()

    # Define the CREATE TABLE statement
    create_surveyee_table = """
    CREATE TABLE IF NOT EXISTS surveyee (
        id INT AUTO_INCREMENT PRIMARY KEY,
        age VARCHAR(20) NOT NULL,
        gender VARCHAR(20) NOT NULL
    )
    """
    # Execute the CREATE TABLE statement
    cursor.execute(create_surveyee_table)

    # Create a table for other_feedback
    create_feedback_table = """
    CREATE TABLE IF NOT EXISTS feeback (
        id INT,
        other_feedback VARCHAR(1000)
    )
    """
    # Execute the CREATE TABLE statement
    cursor.execute(create_feedback_table)

    # Commit the changes
    cnx.commit()

    # Read csv table for product types and its corresponding features
    df = pd.read_csv('product_info.csv')
    product_types = df.iloc[:, 0].tolist()

    # Define and execute the CREATE TABLE statement for all product types
    for i in range(len(product_types)):
        product = product_types[i]
        product = product.lower().replace("-"," ").replace(" ","_").replace("&","and")
        features = df.iloc[:, 1][i].split(', ')
        ft = ''
        for j in features:
            ft = ft +'\t' + j.lower().replace(" ","_") + ' VARCHAR(1000), \n'
        create_product_table = """
        CREATE TABLE IF NOT EXISTS """ + product + """ (
            id INT,
            brand VARCHAR(255) NOT NULL,
            rating INT NOT NULL,\n""" + ft + """\timprovements VARCHAR(1000),
            repurchase VARCHAR(1000),
            other_feedback VARCHAR(1000)
        )
        """
        cursor.execute(create_product_table)

    # Commit the changes
    cnx.commit()

    # Close the cursor and connection
    cursor.close()
    cnx.close()

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

# Insert data into MySQL surveyee table
def insert_surveyee(data):
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
        host='teamdataconnect.ch6uykso0lba.ap-southeast-2.rds.amazonaws.com',
        database='dsa3101db')
    cursor = cnx.cursor()
    query = "INSERT INTO surveyee (age,gender) VALUES (%s,%s)"
    cursor.execute(query, data)
    cnx.commit()
    cursor.close()
    cnx.close()

# Get latest row number from MySQL
def get_row():
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
        host='teamdataconnect.ch6uykso0lba.ap-southeast-2.rds.amazonaws.com',
        database='dsa3101db')
    cursor = cnx.cursor()
    query = "SELECT id FROM surveyee ORDER BY id DESC LIMIT 1"
    cursor.execute(query)
    row = cursor.fetchone()
    cursor.close()
    cnx.close()
    return str(row[0])

# Insert data into MySQL table
def insert_data(table_name, data, num):
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
        host='teamdataconnect.ch6uykso0lba.ap-southeast-2.rds.amazonaws.com',
        database='dsa3101db')
    cursor = cnx.cursor()
    row = get_row()
    query = "INSERT INTO " + table_name + " VALUES (" + row + "," + "%s,"*(num-1) + "%s)"
    cursor.execute(query, data)
    cnx.commit()
    cursor.close()
    cnx.close()

def rating_stage(product):
    llm = Ollama(model="llama2:7b-chat", format='json', temperature=0, base_url="http://ollama-container:11434", verbose=True)
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

def generate_dict(feedback, features_lst):
    llm = OllamaFunctions(model="mistral", temperature=0)
    def create_schema(features_lst):
        schema = {"properties": {}}
        for feature in features_lst:
            schema["properties"][feature] = {"type": "string"}
        schema["required"] = features_lst
        return schema
    schema = create_schema(features_lst)    
    chain = create_extraction_chain(schema=schema, llm=llm)
    result = chain.run(feedback) #Convert from a string to a list
    def modify_outputs(features_lst, result):
        new_result = {}
        for dic in result:
            for feature in dic:
                if feature not in new_result:
                    if type(dic[feature])==dict:
                        dic[feature] = list(dic[feature].values())[0]
                    if dic[feature]=="not mentioned in the passage" or dic[feature]==None:
                        new_result[feature] = ""
                    else:
                        new_result[feature] = dic[feature]
        for feature in features_lst:
            if feature not in new_result:
                new_result[feature] = ""
        return new_result
    dic = modify_outputs(features_lst, result)
    return dic


def get_missing_features(feature_dict):
    missing_features = []
    for f in feature_dict:
        if feature_dict[f] == "":
            missing_features.append(f)
    return(missing_features)


def generate_questions(product, missing_feature):
    template = """
    Your job is to ask a question to get the customer to review about the {missing_feature} of the {selected_product}.
    
    Example:
    missing feature: price
    product: shampoo
    output: Do you think that the price that you paid for the shampoo is worth it? 
    """
    llm = OllamaFunctions(model="mistral", temperature=0)
    prompt = PromptTemplate(template=template, input_variables=["selected_product", "missing_feature"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    questions = llm_chain({'selected_product':product, 'missing_feature': missing_feature})
    return questions['text']

def generate_features_questions(product, feature_dict):
    missing_features = get_missing_features(feature_dict)
    output_dict = {}
    for i in missing_features:
        ques = generate_questions(product, i)
        output_dict[i] = ques
    return(output_dict)


def is_feedback(feedback):
    template = """
    Determine if the following feedback {feedback} sounds like a product feedback. Answer one word "Yes", if is sounds like a product feedback, answer one word "No" if it does not sound like a feedback about a product.
    Example:
    feedback : Fantastic! The new vacuum cleaner's suction power is incredible, making cleaning effortless.
    output: Yes
    Example:
    feedback: Hello, I'm fine how about you?
    output: No
    feedback: NA
    output: No
    """
    llm = OllamaFunctions(model="mistral", temperature=0)
    prompt = PromptTemplate(input_variables=["feedback"],
                        template = template)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = chain.run(feedback)
    return(answer)


def responding_feedback(feedback):
    template = """
    Determine if the following feedback {feedback} sounds like a product feedback. 
    If it sounds like a product feedback, give a short response to this feedback. 
    Respond positively to positive feedback. 
    If feedback is negative, say that you are sorry and will try to improve that part of the product in the future.
    Do not offer help such as : I'm here to help answer any questions you have about the feedback.
    Do not ask for additional input and do not ask for additional feedback.
    
    Example:
    feedback: it absorbs well, big enough, but can be stronger so that it does not tear so easily
    output: I'm glad that the product size and absorbance met your expectations. I'm sorry to hear that the strength of the product did not meet your expectations, we will work on improving our product.
    Example:
    feedback: I enjoyed using the conditioner. It smelled nice and it helped soften my hair.
    output: Thank you for sharing your positive experience with the conditioner! I'm glad to hear that it not only smelled nice but also helped soften your hair.
    Example: 
    feedback: it was good, could be cheaper, smell is normal, cleans decently
    output: I'm glad that you enjoyed using the product. I understand your concerns on the price, your feedback will be taken into consideration.
    """
    llm = OllamaFunctions(model="mistral", temperature=0)
    prompt = PromptTemplate(input_variables=["feedback"],
                        template = template)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = chain.run(feedback)
    return(answer)


def checking_feedback(feedback):
    fb = is_feedback(feedback)
    answer = {}
    if fb == "No":
        out = "Your feedback does not seem to be providing a review about our product. Could you provide another feedback?"
        answer[fb] = out
    else:
        out = responding_feedback(feedback)
        answer[fb] = out
    return(answer)