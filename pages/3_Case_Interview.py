import streamlit as st
import random
import time
import openai
#import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoHTMLAttributes, AudioHTMLAttributes
from aiortc.contrib.media import MediaRecorder
import uuid
from pathlib import Path
from utils import get_ice_servers
from utils import show_audio_player, generate_audio
from openai import OpenAI
from streamlit_modal import Modal
#from audio_recorder_streamlit import audio_recorder
#from st_audiorec import st_audiorec

st.title("Interview Chat")
client = openai.OpenAI()
#recognizer = sr.Recognizer()
#openai.api_key = st.secrets["OPENAI_API_KEY"]
RECORD_DIR = Path("./records")
RECORD_DIR.mkdir(exist_ok=True)

case = "You are interviewing me by asking the following case style interview question. "+\
"Question: Our client is an ice Skating Rink whose revenue has Decreased by 30% compared to last year. How would you go about figuring out where the problem is? "+\
"If they start by describing how they would approach the problem, tell them if their approach makes sense and then ask what component they would look at first. "+\
"If they have no idea how to approach this problem, suggest that they look at one of the two components of revenue which are average spend and volume. "+\
"If they ask for specific data, mention that there is no specific data available and you’re just interested in seeing how they would approach this problem. "+\
"As they describe factors that might be causing the problem, continue asking them if there’s anything else that could explain it. Once they no longer have any more ideas, thank them for their time and end the interview. "

if "prefix" not in st.session_state:
    st.session_state["prefix"] = str(uuid.uuid4())
    #print(st.session_state["resume"])
prefix = st.session_state["prefix"]
in_file = RECORD_DIR / f"{prefix}_input.mp4"
out_file = RECORD_DIR / f"{prefix}_output.mp4"

if "counter" not in st.session_state:
    st.session_state["counter"] = 0
else:
    st.session_state["counter"] += 1

message_container = st.container()

def create_questions():
    question_list = [
        "Tell me about a time you had to work on a challenging problem involving user acquisition?", 
        "Tell me something you’ve worked on that you are very proud of?",
        "Walk me through your resume?",
        "What is a product you use that you are a fan and what makes it a good product?",
        "Why are you interested in this role?"
        ]
    rippling_list = [
        "Why are you interested in this role?",
        "Tell me about one of your past experiences that would be most relevant to working on growth and user acquisition?",
        "What's one way you've grown or matured in the past year?",
        "Tell me about a time where you had to give difficult feedback to someone",
        "Tell me about a time where you used a growth hack?",
        "How do you handle working in cross-functional teams?",
        "Why do you want to work and Rippling and why now?"
    ]
    sample = random.sample(rippling_list, 3)
    return ', '.join(sample)

def evaluate(transcript):
    criteria = "You are a hiring manager tasked with evaluating an interview transcript to determine how the candidate performed on an interview. When the user sends you an interview transcript, respond with an evaluation of the candidate's performance based on the following criteria. Criteria -> Did the candidate show evidence of impressive, tangible accomplishments? Did the candidate communicate clearly, concisely, and confidently? Did the candidate demonstrate their personality and values? For each of the parts of the criteria, provide feedback about what the candidate did well as well as areas for improvement."
    interview = "Transcript:\n"
    for message in transcript:
        if message["role"] == "user":
            interview += "Candidate: "
            interview += message["content"]
            interview += "\n"
        if message["role"] == "assistant":
            interview += "Interviewer: "
            interview += message["content"]
            interview += "\n"
    #print(interview)
    response = client.chat.completions.create(
        model="gpt-4",
        messages = [{"role":"system", "content":criteria}, {"role":"user", "content":interview}]
    )
    
    st.session_state.evaluation = response.model_dump()['choices'][0]['message']['content']
    #return response.model_dump()['choices'][0]['message']['content']

def in_recorder_factory() -> MediaRecorder:
    return MediaRecorder(
        str(in_file), format="mp4"
    )  # HLS does not work. See https://github.com/aiortc/aiortc/issues/331

def out_recorder_factory() -> MediaRecorder:
    return MediaRecorder(str(out_file), format="mp4")


def send_message(transcript):
    st.session_state.messages.append({"role": "user", "content": transcript})
    #with st.chat_message("user"):
        #st.markdown(transcript)
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
  
    st.session_state.messages.append({"role": "assistant", "content": messenger_response})
    #with st.chat_message("assistant"):
        #st.markdown(messenger_response)
        #st.divider()
        #generate_audio(messenger_response)
 
def markdown_messages():
    with st.container():
        for message in st.session_state.messages:
            if message["role"] != "system" and not message["content"].startswith("///"):
                if message["role"] == "assistant":
                    with message_container.chat_message(message["role"]):
                        st.markdown(message["content"])
                        #st.divider()
                        #audio = generate_audio(message["content"])
                        #st.markdown("To Hear The Voice Of AI Press Play")
                        #st.audio(audio)
                else:
                    with message_container.chat_message(message["role"]):
                        st.markdown(message["content"])


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []
    questions = create_questions()
    st.session_state.messages.append({"role": "system", "content": case})
    st.session_state.messages.append({"role": "user", "content":"/// Hello! I'm ready to get started when you are"})
    ai_response()
    #response = client.chat.completions.create(
            #model=st.session_state["openai_model"],
            #messages=[
                #{"role": m["role"], "content": m["content"]}
                #for m in st.session_state.messages
            #],   
        #)
    #full_response = response.model_dump()['choices'][0]['message']['content']
    #print(full_response)
    #message_placeholder.markdown(full_response + "▌")
    #with st.chat_message("assistant"):
        #st.markdown(full_response)


#for message in st.session_state.messages:
    #print(message)
    #if message["role"] != "system" and not message["content"].startswith("///"):
        #with st.chat_message(message["role"]):
            #st.markdown(message["content"])

#if prompt := st.chat_input("Or Type Instead!"):
    #send_message(prompt)
#audio_bytes = audio_recorder(energy_threshold=(-1.0, 1.0),
  #pause_threshold=3.0,)
#audio_bytes = st_audiorec()
#if audio_bytes and audio_bytes is not None and st.session_state["counter"]>2:
    #markdown_messages()
    #st.audio(audio_bytes, format="audio/wav")
    #transcript = client.audio.transcriptions.create(
    #model="whisper-1", 
    #file=audio_bytes
    #)
    #send_message(transcript.text)

webrtc_streamer(
    key="record",
    mode=WebRtcMode.SENDRECV,
    audio_html_attrs=AudioHTMLAttributes(
        muted=True
    ),
  
    rtc_configuration={"iceServers": get_ice_servers()},
    media_stream_constraints={
        "video": False,
        "audio": True,
    },
    in_recorder_factory=in_recorder_factory,
)  
markdown_messages()

if in_file.exists():
    audio_file= open(in_file, "rb")
    try:
        transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
        )
        st.markdown(transcript.text)
        st.button(
            "Send Message", on_click=send_message, args=[transcript.text]
        )
    except Exception as err:
        print(err)
if out_file.exists():
    with out_file.open("rb") as f:
        st.download_button(
            "Download the recorded video with video filter", f, "output.flv"
        )
open_modal = st.button("Evaluate Me!", on_click=evaluate, args=[st.session_state.messages])
modal = Modal(key="Evaluation", title="Evaluation")
if open_modal:
    with modal.container():
                st.markdown(st.session_state.evaluation)
