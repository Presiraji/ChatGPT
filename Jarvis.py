import openai
import streamlit as st
import pandas as pd
from io import StringIO
from PIL import Image
import base64

# Configuration
OPENAI_API_KEY = "sk-balraj-KLoW4HxnPDr6efjrLIFlT3BlbkFJFey4fhZcJMWgg1zIqmyB"
MODEL = "gpt-3.5-turbo-16k-0613"
COST_PER_1K_TOKENS = 0.02  # Adjust this based on the current pricing from OpenAI

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.total_tokens_used = 0
    st.session_state.total_cost = 0.0

def display_chat():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def encode_image_to_base64(image):
    buffered = StringIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def calculate_cost(tokens):
    return (tokens / 1000) * COST_PER_1K_TOKENS

uploaded_files = st.sidebar.file_uploader("Upload images", accept_multiple_files=True, type=["png", "jpg", "jpeg"])

if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, caption=uploaded_file.name)
        encoded_image = encode_image_to_base64(image)
        st.session_state.messages.append({
            "role": "user",
            "content": f"![{uploaded_file.name}](data:image/png;base64,{encoded_image})"
        })

excel_data = st.sidebar.text_area("Paste Excel Data Here", height=10)

if excel_data:
    # Process the pasted Excel data
    try:
        df = pd.read_csv(StringIO(excel_data), sep="\t")
        st.sidebar.dataframe(df)
        st.session_state.messages.append({"role": "user", "content": df.to_markdown()})
    except Exception as e:
        st.sidebar.error(f"Error processing Excel data: {e}")

display_chat()

if prompt := st.chat_input("Enter your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        )
        response_content = response['choices'][0]['message']['content']
        response_tokens = response['usage']['total_tokens']
        
        st.session_state.total_tokens_used += response_tokens
        st.session_state.total_cost += calculate_cost(response_tokens)
        
        st.markdown(response_content)
    st.session_state.messages.append({"role": "assistant", "content": response_content})

# Display API usage cost
st.sidebar.write(f"Total Tokens Used: {st.session_state.total_tokens_used}")
st.sidebar.write(f"Total Cost: ${st.session_state.total_cost:.2f}")
