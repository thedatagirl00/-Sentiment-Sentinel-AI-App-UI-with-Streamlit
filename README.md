## README.md for GitHub

# Sentiment Sentinel: AI-Powered Vibe Checker

 https://unscenically-providential-daleyza.ngrok-free.dev

## Project Overview

**Sentiment Sentinel** is a Streamlit web application that provides instant sentiment analysis of any text input. Whether it's a review, a message, or a diary entry, this app leverages a pre-trained machine learning model from Hugging Face's `transformers` library to classify the sentiment as either **Positive** or **Negative**.

Designed to be easily runnable within a Google Colab environment, it uses `ngrok` to tunnel the local Streamlit application to a public URL, allowing you to interact with the app directly in your notebook.

## Features

*   **Real-time Sentiment Analysis:** Get immediate feedback on the sentiment of your text.
*   **Hugging Face `transformers`:** Utilizes the efficient `distilbert` model for accurate predictions.
*   **Streamlit UI:** Intuitive and interactive web interface.
*   **Colab Integration:** Run and view the application seamlessly within your Google Colab notebook.
*   **`ngrok` Tunneling:** Exposes your local Streamlit app to the internet with a secure public URL.

## How to Run in Google Colab

Follow these steps to set up and run the Sentiment Sentinel app in your Colab environment:

### 1. Install Dependencies

First, install the necessary Python packages:

```python
!pip install streamlit transformers torch pyngrok -q
```

### 2. Create the Streamlit Application File (`app.py`)

This code defines your Streamlit app. Save it as `app.py` in your Colab environment:

```python
%%writefile app.py
import streamlit as st
from transformers import pipeline

st.title("⏳ Sentiment Sentinel")
st.write("Got a message, review, or diary entry? Paste it below, and I'll tell you if the vibe is **Positive** or **Negative**!")

@st.cache_resource
def load_model():
    return pipeline("sentiment-analysis")

with st.spinner("Loading AI Brain..."):
    classifier = load_model()

user_text = st.text_area("What's on your mind?",
                         placeholder="Type something like: 'I love coding with Python!'")

if st.button("Analyze Vibe"):
    if user_text.strip():
        result = classifier(user_text)
        
        label = result[0]['label']
        score = result[0]['score']
        
        if label == "POSITIVE":
            st.success(f"**Positive Vibe Detected!** (Confidence: {score:.2f})\n")
            st.balloons()
        else:
            st.error(f"**Negative Vibe Detected.** (Confidence: {score:.2f})\n")
    else:
        st.warning("Please enter some text first!")
```

### 3. Get Your ngrok Authtoken

To use `ngrok`, you need an authentication token:

1.  Go to the [ngrok website](https://ngrok.com/signup) and sign up for a free account.
2.  Find your Authtoken on your [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken).
3.  In Google Colab, click the '🔑' icon in the left sidebar (Secrets).
4.  Click 'Add new secret'.
5.  Set 'Name' to `NGROK_AUTH_TOKEN`.
6.  Paste your ngrok Authtoken into 'Value'.
7.  Enable 'Notebook access' for this secret.

### 4. Run the Streamlit App with ngrok

Execute the following code in a Colab cell. This will start your Streamlit app in the background and create a public `ngrok` tunnel, displaying the app within an iframe in your notebook:

```python
from pyngrok import ngrok, conf
import os
import time
from IPython.display import IFrame, display
from google.colab import userdata

# Get ngrok authtoken from Colab secrets
NGROK_AUTH_TOKEN = userdata.get('NGROK_AUTH_TOKEN')

if NGROK_AUTH_TOKEN:
    conf.get_default().auth_token = NGROK_AUTH_TOKEN
    print("ngrok authtoken configured.")

    # Kill any existing Streamlit processes (optional, for cleanup)
    !pkill streamlit || true

    # Start Streamlit in the background with nohup
    !nohup streamlit run app.py > streamlit_output.log 2>&1 &

    print("Streamlit app started in the background. Waiting for ngrok to establish tunnel...")
    time.sleep(5) # Give Streamlit a moment to start

    try:
        # Connect to ngrok
        public_url = ngrok.connect(8501, bind_tls=True).public_url
        print(f"ngrok tunnel established at: {public_url}")

        # Display the Streamlit app in an IFrame
        display(IFrame(public_url, width='100%', height=800))

    except Exception as e:
        print(f"An error occurred with ngrok: {e}")
        print("Please ensure your ngrok authtoken is correctly set and try again.")
else:
    print("NGROK_AUTH_TOKEN not found. Please add it to Colab secrets.")
```

After running this, your Streamlit app should appear embedded in the Colab output, ready for interaction!
