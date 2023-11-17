import streamlit as st
import random
import time
import openai
import speech_recognition as sr

st.title("Interview Chat")
client = openai.OpenAI()
recognizer = sr.Recognizer()
#openai.api_key = st.secrets["OPENAI_API_KEY"]

counter = 0

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Or Type Instead!"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        response = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],   
        )
        full_response = response.model_dump()['choices'][0]['message']['content']
        print(full_response)
        #message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
record = st.button(':violet[Record Audio] 🔍')
if record:
    with sr.Microphone() as source:
        st.caption("Say something...")
        audio = recognizer.listen(source,phrase_time_limit=3)

    # Recognize the audio
    try:
        text = recognizer.recognize_google(audio)  # You can choose a different recognition engine/API
        st.caption(f"Prompt : {text}")

    except sr.UnknownValueError:
        st.caption("Sorry, I could not understand what you said.")
    except sr.RequestError as e:
        st.caption(f"Error connecting to the recognition service: {e}")

    openai.api_key = 'YOUR_OPENAI_API_KEY'

    prompt_text = text

    response = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "user", "content": prompt_text}
            ],   
        )

    with st.spinner('Loading....'):
        time.sleep(2)
    print(response.model_dump()['choices'][0]['message']['content'])
    st.code(response['choices'][0]['text'])
    st.divider()