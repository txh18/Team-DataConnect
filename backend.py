import pandas as pd
import mysql.connector
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialise an llm instance
llm = Ollama(model="llama2:7b-chat", format='json', temperature=0, base_url="http://ollama-container:11434", verbose=True)

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
    return row

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