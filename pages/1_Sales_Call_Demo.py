# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from streamlit_webrtc import webrtc_streamer, WebRtcMode
import streamlit as st
import time
import queue
import pydub
#import speech_recognition as sr
from aiortc.contrib.media import MediaRecorder
import uuid
from pathlib import Path
from utils import get_ice_servers
from openai import OpenAI

RECORD_DIR = Path("./records")
RECORD_DIR.mkdir(exist_ok=True)
client = OpenAI()
st.session_state["openai_model"] = "gpt-4"
uploaded_file = st.file_uploader("Upload Call Recording")
if st.button("Get Information"):
    if uploaded_file is not None:
        print(uploaded_file)
        call_transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=uploaded_file
                )
        response = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": f"Use the below transcript from a sales call to answer the following question: Does this person have the budget, authority, and need to be a realistic prospect for our product?\n {call_transcript}" }
                ],   
            )
        messenger_response = response.model_dump()['choices'][0]['message']['content']
        st.write(messenger_response)

transcript = st.text_area("Copy call transcript here")
if st.button("Extract Information"):
    response = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": f"Use the below transcript from a sales call to answer the following question: Does this person have the budget, authority, and need to be a realistic prospect for our product?\n {transcript}" }
            ],   
        )
    messenger_response = response.model_dump()['choices'][0]['message']['content']
    st.write(messenger_response)