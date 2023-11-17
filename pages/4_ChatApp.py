import streamlit as st
import random
import time
import openai
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from aiortc.contrib.media import MediaRecorder
import uuid
from pathlib import Path
from utils import get_ice_servers
from openai import OpenAI

st.title("Interview Chat")
client = openai.OpenAI()
recognizer = sr.Recognizer()
#openai.api_key = st.secrets["OPENAI_API_KEY"]
RECORD_DIR = Path("./records")
RECORD_DIR.mkdir(exist_ok=True)

counter = 0
if "prefix" not in st.session_state:
    st.session_state["prefix"] = str(uuid.uuid4())
prefix = st.session_state["prefix"]
in_file = RECORD_DIR / f"{prefix}_input.mp4"
out_file = RECORD_DIR / f"{prefix}_output.mp4"

def in_recorder_factory() -> MediaRecorder:
    return MediaRecorder(
        str(in_file), format="mp4"
    )  # HLS does not work. See https://github.com/aiortc/aiortc/issues/331

def out_recorder_factory() -> MediaRecorder:
    return MediaRecorder(str(out_file), format="mp4")

def send_message(transcript):
    st.session_state.messages.append({"role": "user", "content": transcript})
    with st.chat_message("user"):
        st.markdown(transcript)

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
st.divider()
webrtc_streamer(
    key="record",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration={"iceServers": get_ice_servers()},
    media_stream_constraints={
        "video": False,
        "audio": True,
    },
    in_recorder_factory=in_recorder_factory,
)

if in_file.exists():
    audio_file= open(in_file, "rb")
    transcript = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    print(transcript)
    with in_file.open("rb") as f:
        st.button(
            transcript.text, on_click=send_message, args=['transcript.text']
        )
if out_file.exists():
    with out_file.open("rb") as f:
        st.download_button(
            "Download the recorded video with video filter", f, "output.flv"
        )