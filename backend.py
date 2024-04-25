import random
import pandas as pd
import mysql.connector
from langchain_community.llms import Ollama
from langchain_experimental.llms.ollama_functions import OllamaFunctions
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, create_extraction_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_brands():
    """
    Get the list of unique brands from the brands_products csv file
    Inputs: NA
    Outputs: 
        unique_brand_lst (list): A list of unique brands
    """
    df = pd.read_csv("brands_products.csv")
    unique_brand_lst = list(df["Brand"].unique())
    return unique_brand_lst

def get_pdts_by_brand():
    """
    Get the list of products for each brand from the brands_products csv file
    Inputs: NA
    Outputs: 
        brands_products_lst (list of lists): A list containing nested lists. Each nested list contains products of a particular brand.
    """
    df = pd.read_csv("brands_products.csv")
    brands_lst = list(df["Brand"].unique())
    brands_products_lst = []
    for brand in brands_lst:
        brand_subset = df[df["Brand"]==brand]
        products_lst = list(brand_subset["Product_Category"].unique())
        products_lst = [product.strip() for product in products_lst]
        new_products_lst = []
        for product in products_lst:
            new_products_lst.append(product)
        brands_products_lst.append(new_products_lst)
    return brands_products_lst

def csv_to_mysql():
    """
    Create tables for each product in MySQL from the product_info csv file
    Inputs: NA
    Outputs: NA
    """

    # Connect to the MySQL server
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
                                host='teamdataconnect.cp8gi20kknig.ap-southeast-1.rds.amazonaws.com',
                                database='dsa3101data')

    # Create a cursor object
    cursor = cnx.cursor()

    # Define the CREATE TABLE statement
    create_surveyee_table = """
    CREATE TABLE IF NOT EXISTS surveyee (
        id INT AUTO_INCREMENT PRIMARY KEY,
        age INT NOT NULL,
        gender VARCHAR(20) NOT NULL
    )
    """
    # Execute the CREATE TABLE statement
    cursor.execute(create_surveyee_table)

    # Create a table for other_feedback
    create_feedback_table = """
    CREATE TABLE IF NOT EXISTS feedback (
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
        product = '`' + product + '`'
        features = df.iloc[:, 1][i].split(', ')
        ft = ''
        for j in features:
            ft = ft +'\t' + '`' + j + '`' + ' VARCHAR(1000), \n'
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

def create_df():
    """
    Connect to the MySQL server and create a dataframe that contains
    two columns - products and features.
    Inputs: NA
    Outputs: 
        df (pandas DataFrame): A dataframe that contains the products and features columns
    """
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
                              host='teamdataconnect.cp8gi20kknig.ap-southeast-1.rds.amazonaws.com',
                              database='dsa3101data')
    cursor = cnx.cursor()
    cursor.execute("SHOW TABLES")
    df = pd.DataFrame(columns=['product','features'])
    count = -1
    for table in cursor.fetchall():
        table_name = table[0].decode()
        if ((table_name != "surveyee") and (table_name != "feedback")):
            count += 1
            table_name = '`' + table_name + '`'
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            feat = [column[0] for column in columns[3:-3]]
            new_row = {'product':table_name, 'features':feat}
            df.loc[count] = new_row
    df['features'] = df['features'].apply(lambda x: ', '.join(x))
    cursor.close()
    cnx.close()
    return df

def insert_surveyee(data):
    """
    Insert customer profile data into MySQL surveyee table
    Inputs: 
        data (tuple): contains responses to the customer profiling questions
    Outputs: NA
    """
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
        host='teamdataconnect.cp8gi20kknig.ap-southeast-1.rds.amazonaws.com',
        database='dsa3101data')
    cursor = cnx.cursor()
    query = "INSERT INTO surveyee (age,gender) VALUES (%s,%s)"
    cursor.execute(query, data)
    cnx.commit()
    cursor.close()
    cnx.close()

def get_row():
    """
    Get the latest row number from MySQL surveyee table
    Inputs: NA
    Outputs: 
        latest_number (str): contains the latest row number in the MySQL surveyee table
    """
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
        host='teamdataconnect.cp8gi20kknig.ap-southeast-1.rds.amazonaws.com',
        database='dsa3101data')
    cursor = cnx.cursor()
    query = "SELECT id FROM surveyee ORDER BY id DESC LIMIT 1"
    cursor.execute(query)
    row = cursor.fetchone()
    latest_number = str(row[0])
    cursor.close()
    cnx.close()
    return latest_number

def insert_data(table_name, data, num):
    """
    Insert product feedback into MySQL table
    Inputs: 
        table_name (str): name of the product
        data (tuple): contains product feedback
        num (int): length of the data tuple
    Outputs: NA
    """
    cnx = mysql.connector.connect(user='admin', password='dsa3101data',
        host='teamdataconnect.cp8gi20kknig.ap-southeast-1.rds.amazonaws.com',
        database='dsa3101data')
    cursor = cnx.cursor()
    row = get_row()
    query = "INSERT INTO " + '`' + table_name + '`' + " VALUES (" + row + "," + "%s,"*(num-1) + "%s)"
    cursor.execute(query, data)
    cnx.commit()
    cursor.close()
    cnx.close()

def rating_response(product, rating, features):
    """
    generates response to user's rating of the product
    Inputs: 
        product (str): name of the product
        rating (int): user's rating of the product
        features (list): list of features associated to the product
    Outputs: 
        response (str): chatbot's response to user's rating of the product
    """
    num = len(features)-1
    separator = " and "
    features_str = separator.join(features)
    features_str = features_str.replace(" and ", ", ", num-1)
    response = ""
    if rating == 1:
        response = f"""I'm sorry to hear that you are not satisfied with the {product}. Could you please elaborate on what specifically didn't meet your expectations for the {product} in terms of {features_str}?"""
    if rating == 2:
        response = f"""Oh it's sad to hear that your experience wasn't ideal, can you tell me the reasons why you are unhappy with the {product} in terms of {features_str}?"""
    if rating == 3:
        response = f"""I see, can you share with me the reasons why you gave such a low rating for the {product} in terms of {features_str}?"""
    if rating == 4:
        response = f"""Thank you for your rating! Can you share with me your thoughts on the {product} in terms of {features_str}?"""
    if rating == 5:
        response = f"""Thank you for the positive feedback!  Glad to know that you are pretty satisfied with the {product}. How do you think the the {product} has fared in terms of {features_str}?"""
    if rating == 6:
        response = f"""That's great to hear! Can you share with me your thoughts on the {product}'s performance in terms of {features_str}?"""
    if rating == 7:
        response = f"""Yay! Glad that you are satisfied with the {product}. Can you share with me your thoughts on the {product}'s performance in terms of {features_str}?"""
    return response

def generate_dict(feedback, features_lst):
    """
    extracts information from feedback that is relevant to the list of features and returns a dictionary
    Inputs: 
        feedback (str): product feedback
        features_lst (list): list of features associated to the product
    Outputs: 
        dic (dictionary): the key is the feature and the corresponding value is the information extracted from the feedback that is relevant to the feature
    """
        
    llm = OllamaFunctions(model="mistral", temperature=0, base_url="http://ollama-container:11434", verbose=True)
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
        if len(result)!=0: #if the list is not empty
            for dic in result:
                if len(dic)!=0: #if the dictionary is not empty
                    for feature in dic:
                        if feature not in new_result and feature in features_lst:
                            if dic[feature]=="not mentioned in the passage" or dic[feature]==None or dic[feature]=={}:
                                new_result[feature] = ""
                            elif type(dic[feature])==dict: #the dic[feature] here is not an empty dictionary
                                new_result[feature] = list(dic[feature].values())[0]
                            else:
                                new_result[feature] = dic[feature]
        for feature in features_lst:
            if feature not in new_result:
                new_result[feature] = ""
        return new_result
    dic = modify_outputs(features_lst, result)
    return dic

def generate_dict_empty(features_lst):
    """
    generates a dictionary where the keys are the features and the values are empty strings
    Inputs: 
        features_lst (list): list of features associated to a product
    Outputs: 
        dic (dictionary): each key is a feature and the corresponding value is an empty string
    """
    d={}
    for feature in features_lst:
        d[feature]=""
    return d

def get_missing_features(feature_dict):
    """
    returns a list of features that have not been mentioned in the product feedback
    Inputs: 
        feature_dict (dictionary): each key is a feature while its corresponding value is the 
        information extracted from the feedback that is relevant to that feature
    Outputs: 
        missing_features (list): A list of features that have not been mentioned in the product feedback.
        These features' corresponding values in the feature_dict are empty strings.
    """
    missing_features = []
    for f in feature_dict:
        if feature_dict[f] == "":
            missing_features.append(f)
    return(missing_features)


def generate_questions(product, missing_feature):
    """
    generates a question to get the customer who have purchased the product to review about the missing_feature 
    Inputs: 
        product (str): name of the product
        missing_feature (str): a feature that has not been mentioned in the product feedback
    Outputs: 
        questions['text'] (str): a question to ask the customer to get the customer to review about the product
        in terms of the missing_feature
    """
        
    template = """
    You are a survey chatbot.
    Your job is to ask a question to get the customer who have purchased a product to review about the {missing_feature} of the {purchased_product}.
    Ask only open-ended questions.
    
    Example:
    missing feature: price
    product: shampoo
    output: Do you think that the price that you paid for the shampoo is worth it? 
    """
    llm = OllamaFunctions(model="mistral", temperature=0, base_url="http://ollama-container:11434", verbose=True)
    prompt = PromptTemplate(template=template, input_variables=["purchased_product", "missing_feature"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    questions = llm_chain({'purchased_product':product, 'missing_feature': missing_feature})
    return questions['text']

def generate_features_questions(product, feature_dict):
    """
    generates a question for each missing feature and compiles them in a dictionary
    Inputs: 
        product (str): name of the product
        feature_dict (dictionary): the key is the feature and the corresponding value is the 
        information extracted from the feedback that is relevant to the feature
    Outputs: 
        output_dict (dictionary): each key is a feature that has not been mentioned in the product feedback
        while its corresponding value is a question to ask the customer regarding the particular feature
        of the product
    """

    missing_features = get_missing_features(feature_dict)
    output_dict = {}
    for i in missing_features:
        ques = generate_questions(product, i)
        output_dict[i] = ques
    return(output_dict)

def generate_improvement_qns(product, brand):
    """
    randomly selects a question from the predefined list of questions to get the customer to suggest improvements
    to the product
    Inputs: 
        product (str): name of the product
        brand (str): name of the brand of the product
    Outputs: 
        response (str): a randomly selected question to get the customer to suggest improvements to the product
    """
    qns_list =  [f"Next, what kind of improvements would you like to see in the {product} from {brand}?", 
                 f"Moving on, are there any improvements you would like the {product} from {brand} have in the future?",
                 f"Moving on, how do you think the {product} from {brand} can improve?"]
    response = random.choice(qns_list)
    return response

def generate_repurchase_response(product, brand, rating):
    """
    generates response to user's repurchase rating of the product
    Inputs: 
        product (str): name of the product
        brand (str): name of the brand of the product
        rating (int): user's repurchase rating of the product
    Outputs: 
        response (str): chatbot's response to user's repurchase rating of the product
    """

    template = """
    You are a survey chatbot assistant that helps to conduct survey on consumer products while engaging the respondents.
    The respondent would give a rating out of 7, on how likely will they repurchase the {product} from {brand}.
    Based on the rating given, generate a customised response and ask the respondent if they have other feedbacks about it.

    Consider the following as examples for output:
        - If rating is 1, "Oh it's sad to hear that, would you like to give us any last feedback on this product for us to improve?"
        - If rating is 2, ""Oh that's sad to hear. Do you have any more thoughts and comments about this product?"
        - If rating is 3, "I see, do you have anything else to feedback on for this product?"
        - If rating is 4, "I see, do you have anything else to feedback on for this product?"
        - If rating is 5, "Nice, any last feedback and thoughts about this product that you would like to share?
        - If rating is 6, "That's great to hear! Any last feedback that you would like to give?"
        - If rating is 7, "Yay! Glad to hear that. Any last feedback you would like to give?

    Here is the rating: {rating}
    Leave your response as a string.
    Your response begins here:
    """
    llm = OllamaFunctions(model="mistral", temperature=0.5, base_url="http://ollama-container:11434", verbose=True)
    prompt = PromptTemplate(template=template, input_variables=["product", "brand", "rating"])
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    response = llm_chain({'product':product, 'brand': brand, 'rating': rating})
    return response['text']       

def is_feedback(feedback):
    """
    returns "Yes" if the user's response sounds like product feedback and "No" if the user's response  
    does not sound like product feedback
    Inputs: 
        feedback (str): product feedback
    Outputs: 
        answer (str): "Yes" or "No"
    """

    template = """
    Determine if the following feedback {feedback} sounds like a product feedback. Answer one word "Yes", if is sounds like a product feedback, answer one word "No" if it does not sound like a feedback about a product.
    Example:
    feedback : Fantastic! The new vacuum cleaner's suction power is incredible, making cleaning effortless.
    output: Yes
    Example:
    feedback: Hello, I'm fine how about you?
    output: No
    feedback: Hello, can you explain what you mean?
    output: No
    feedback: Hello, I don't quite understand your question.
    output: No
    feedback: NA
    output: No
    """
    llm = OllamaFunctions(model="mistral", temperature=0, base_url="http://ollama-container:11434", verbose=True)
    prompt = PromptTemplate(input_variables=["feedback"],
                        template = template)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = chain.run(feedback)
    return(answer)


def responding_feedback(feedback):
    """
    generates response to user's product feedback
    Inputs: 
        feedback (str): product feedback
    Outputs: 
        answer (str): response to user's product feedback
    """

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
    llm = OllamaFunctions(model="mistral", temperature=0, base_url="http://ollama-container:11434", verbose=True)
    prompt = PromptTemplate(input_variables=["feedback"],
                        template = template)
    chain = LLMChain(llm=llm, prompt=prompt)
    answer = chain.run(feedback)
    return(answer)


def response_to_feedback(feedback):
    """
    combines the outputs of is_feedback function and responding_feedback function into a dictionary
    Inputs: 
        feedback (str): product feedback
    Outputs: 
        answer (dictionary): the key is either "Yes" or "No" while the value contains the chatbot's response to the user's reply
    """

    fb = is_feedback(feedback)
    answer = {}
    if fb=="Yes":
        out = responding_feedback(feedback)
        answer[fb] = out
    else:
        out = "Your feedback does not seem to be providing a review about our product. Could you provide another feedback?"
        answer[fb] = out
    return(answer)