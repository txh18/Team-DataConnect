# Team-DataConnect ✨
## Interactive Survey Interface with Chatbot 🤖

A Repository for DSA3101 Project on Interactive Customer Survey Interface.

## Description

In today’s consumer-centric market landscape, understanding customer preferences is essential for product success. Our project aims to create an engaging and interactive customer survey interface tailored for consumer products. Through innovative features such as product image selection, gamification elements, and an interactive conversational chatbot, we aim to boost participation and offer users an enjoyable experience. By empowering businesses with actionable feedback, we seek to bridge the gap between them and their customers, facilitating enhanced product development, refined marketing strategies, and a competitive edge in the consumer market.

## Getting Started
### Installing

On your device
* Install **Docker** 🐳
* Install **MySQL WorkBench** 🐬
* Clone our repository into your local device

### Executing program

1. Open up your Docker Desktop application and ensure that the Docker engine is running
2. Open up command prompt
3. Set current directory to your local repository
```
cd "path/to/local/repository"
```
4. Run the line
```
docker-compose up
```
5. After the containers are running, open up another command prompt window and run this line to pull the Mistral-7B model used for this project
```
docker exec -it ollama-container ollama run mistral
```
6. Open up http://localhost:8501 in a browser to access our survey interface
   
### Viewing stored responses in MySQL database 

1. Open up MySQL Workbench 
2. Create a new connection using the host endpoint link, username and password which can be found in the backend.py file. Replace the Hostname and Username with the endpoint url and user respectively. 

![Creating a new connection](MySQL_images/MySQL%20image%201.png)

3. Click on “Test Connection” to test the connection. If the connection is successful, click “OK”. You will then be prompted to enter the password. Afterwards, you will be able to view the database.

![Viewing the database](MySQL_images/MySQL%20image%202.png)

## Acknowledgments
* [streamlit.io](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)
* [Langchain](https://python.langchain.com/docs/expression_language/get_started/)
* [Ollama](https://ollama.com/library/mistral)
