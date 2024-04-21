# Pull python image
FROM python:3.11

# Create app directory 
WORKDIR /app

# Copy the files
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN if [ "$(uname)" = "Linux" ]; then \
        pip install -r requirements.txt; \
    else \
        pip install pywin32==306 pywinpty==2.0.13 -r requirements.txt; \
    fi

# Command 
CMD ["streamlit", "run", "App.py", "--client.showSidebarNavigation=False", "--server.port=8501", "--server.address=0.0.0.0"]

