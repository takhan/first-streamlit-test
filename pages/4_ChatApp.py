import streamlit as st
import random
import time
import openai
#import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from aiortc.contrib.media import MediaRecorder
import uuid
from pathlib import Path
from utils import get_ice_servers
from openai import OpenAI

st.title("Interview Chat")
client = openai.OpenAI()
#recognizer = sr.Recognizer()
#openai.api_key = st.secrets["OPENAI_API_KEY"]
RECORD_DIR = Path("./records")
RECORD_DIR.mkdir(exist_ok=True)

counter = 0
if "prefix" not in st.session_state:
    st.session_state["prefix"] = str(uuid.uuid4())
    #print(st.session_state["resume"])
prefix = st.session_state["prefix"]
in_file = RECORD_DIR / f"{prefix}_input.mp4"
out_file = RECORD_DIR / f"{prefix}_output.mp4"

def create_questions():
    question_list = [
        "Describe a time when you had to change the mind of a client or colleague about something important?", 
        "Tell me about a time you dealt with a tough problem?",
        "Walk me through your resume?",
        "Tell me about a time you had to convince someone to change their mind about something important to them?",
        "Tell me about a time you led a team. How would you describe your leadership style?"
        ]
    sample = random.sample(question_list, 3)
    return ', '.join(sample)

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
    ai_response()
    

def ai_response():
    messenger_response = ""
    response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],   
    )
    messenger_response = response.model_dump()['choices'][0]['message']['content']
    print(messenger_response)
    print("Response to add is: "+messenger_response)
    st.session_state.messages.append({"role": "assistant", "content": messenger_response})
    with st.chat_message("assistant"):
        st.markdown(messenger_response)
 

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []
    questions = create_questions()
    st.session_state.messages.append({"role": "system", "content": f"You are interviewing me for a job. Ask me one of the following interview questions at random until you have asked 5 questions. Based on my response to the questions, ask a follow up question if appropriate and then move on to the next question. After asking all 3 questions from the list, thank me for my time and end the interview. Everything after the right arrow (->) is an interview question. Interview Questions -> [{questions}] "})
    
for message in st.session_state.messages:
    print(message)
    if message["role"] is not "system":
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
    with in_file.open("rb") as f:
        st.button(
            transcript.text, on_click=send_message, args=[transcript.text]
        )
if out_file.exists():
    with out_file.open("rb") as f:
        st.download_button(
            "Download the recorded video with video filter", f, "output.flv"
        )
