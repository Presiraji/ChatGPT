import openai
import streamlit as st
import pandas as pd
from io import StringIO
from PIL import Image
import base64

st.set_page_config(layout="wide")

st.title("GPT-3.5-turbo-16k-0613 with Image and Excel Data Input")

# Correctly accessing the API key from secrets
client = openai.OpenAI(api_key="sk-balraj-KLoW4HxnPDr6efjrLIFlT3BlbkFJFey4fhZcJMWgg1zIqmyB")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "FRIDAY"

if "messages" not in st.session_state:
    st.session_state.messages = []

def display_chat():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def encode_image_to_base64(image):
    buffered = StringIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

st.sidebar.title("Upload and Paste Data")
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

st.sidebar.write("Copy and paste the selected cells from your Excel sheet below:")
excel_data = st.sidebar.text_area("Paste Excel Data Here", height=10)

if excel_data:
    # Process the pasted Excel data
    try:
        df = pd.read_csv(StringIO(excel_data), sep="\t")
        st.sidebar.write("Here is the data you pasted:")
        st.sidebar.dataframe(df)
        st.session_state.messages.append({"role": "user", "content": df.to_markdown()})
    except Exception as e:
        st.sidebar.error(f"Error processing Excel data: {e}")

st.subheader("Chat with GPT-3.5-turbo-16k-0613")
display_chat()

if prompt := st.chat_input("Enter your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        )
        response_content = response['choices'][0]['message']['content']
        st.markdown(response_content)
    st.session_state.messages.append({"role": "assistant", "content": response_content})

