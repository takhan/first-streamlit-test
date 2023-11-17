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

from streamlit_webrtc import webrtc_streamer
import streamlit as st
import time
import queue
import pydub
import speech_recognition as sr

webrtc_ctx = webrtc_streamer(key="sample", media_stream_constraints={"video": False, "audio": True})
status_indicator = st.empty()
status_indicator.write("Loading...")
text_output = st.empty()
stream = None
recognizer = sr.Recognizer()

while True:
    if webrtc_ctx.audio_receiver:
        sound_chunk = pydub.AudioSegment.empty()
        try:
            audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
        except queue.Empty:
            time.sleep(0.1)
            status_indicator.write("No frame arrived.")
            continue

        status_indicator.write("Running. Say something!")

        for audio_frame in audio_frames:
            sound = pydub.AudioSegment(
                data=audio_frame.to_ndarray().tobytes(),
                sample_width=audio_frame.format.bytes,
                frame_rate=audio_frame.sample_rate,
                channels=len(audio_frame.layout.channels),
            )
            sound_chunk += sound
