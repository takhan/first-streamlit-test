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
import speech_recognition as sr
from aiortc.contrib.media import MediaRecorder
import uuid
from pathlib import Path
from utils import get_ice_servers
from openai import OpenAI

RECORD_DIR = Path("./records")
RECORD_DIR.mkdir(exist_ok=True)
client = OpenAI()
#webrtc_ctx = webrtc_streamer(key="sample", media_stream_constraints={"video": False, "audio": True})
#status_indicator = st.empty()
#status_indicator.write("Loading...")
#text_output = st.empty()
#stream = None
#recognizer = sr.Recognizer()

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
        st.download_button(
            "Download the recorded video without video filter", f, "input.mp4"
        )
if out_file.exists():
    with out_file.open("rb") as f:
        st.download_button(
            "Download the recorded video with video filter", f, "output.flv"
        )
#while True:
#if webrtc_ctx.audio_receiver:
    #sound_chunk = pydub.AudioSegment.empty()
    #try:
        #audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
    #except queue.Empty:
        #time.sleep(0.1)
        #status_indicator.write("No frame arrived.")
        #continue

    #status_indicator.write("Running. Say something!")

    #for audio_frame in audio_frames:
        #sound = pydub.AudioSegment(
            #data=audio_frame.to_ndarray().tobytes(),
            #sample_width=audio_frame.format.bytes,
            #frame_rate=audio_frame.sample_rate,
            #channels=len(audio_frame.layout.channels),
        #)
        #sound_chunk += sound
