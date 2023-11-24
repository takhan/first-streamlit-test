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

import streamlit as st
from streamlit.logger import get_logger
from audio_recorder_streamlit import audio_recorder
from st_audiorec import st_audiorec
import PyPDF2
import pandas as pd
LOGGER = get_logger(__name__)


def run():

    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )
    st.write("# :balloon: Welcome to this Interview Assistant! 👋")

    st.sidebar.success("Select an interview type.")
    uploaded_file = st.file_uploader("Upload your resume")
    if uploaded_file is not None:
        # creating a pdf reader object
        pdfReader = PyPDF2.PdfReader(uploaded_file)
        
        # printing number of pages in pdf file
        print(len(pdfReader.pages))
        
        # creating a page object
        pageObj = pdfReader.pages[0]
        
        # extracting text from page
        st.session_state["resume"] = pageObj.extract_text()
    st.markdown(
        """
        Welcome to my interview assistant!
        **👈 Select an interview type from the sidebar**!
        ### See more complex demos
        - Use a neural net to [analyze the Udacity Self-driving Car Image
          Dataset](https://github.com/streamlit/demo-self-driving)
        - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
    """
    )
    st.markdown('Implemented by '
        '[Stefan Rummer](https://www.linkedin.com/in/stefanrmmr/) - '
        'view project source code on '
                
        '[GitHub](https://github.com/stefanrmmr/streamlit-audio-recorder)')
    st.write('\n\n')

    # TUTORIAL: How to use STREAMLIT AUDIO RECORDER?
    # by calling this function an instance of the audio recorder is created
    # once a recording is completed, audio data will be saved to wav_audio_data

    wav_audio_data = st_audiorec() # tadaaaa! yes, that's it! :D

    # add some spacing and informative messages
    col_info, col_space = st.columns([0.57, 0.43])
    with col_info:
        st.write('\n')  # add vertical spacer
        st.write('\n')  # add vertical spacer
        st.write('The .wav audio data, as received in the backend Python code,'
                 ' will be displayed below this message as soon as it has'
                 ' been processed. [This informative message is not part of'
                 ' the audio recorder and can be removed easily] 🎈')

    if wav_audio_data is not None:
        # display audio data as received on the Python side
        col_playback, col_space = st.columns([0.58,0.42])
        with col_playback:
            st.audio(wav_audio_data, format='audio/wav')
if __name__ == "__main__":
    run()
