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
import asyncio
from streamlit.logger import get_logger
import pandas as pd
from google.oauth2 import id_token
import google.auth.transport
import requests
from utils import get_google_id_token, write_access_token, get_email
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx as get_report_ctx
from streamlit.runtime import get_instance
from streamlit.web.server.websocket_headers import _get_websocket_headers
from httpx_oauth.clients.google import GoogleOAuth2
LOGGER = get_logger(__name__)

# Handle OAuth2 callback route
AUTHORIZATION_CODE = "code"
REDIRECT_URI = "https://supreme-couscous-rr59wj6rjj2xwvv-8501.app.github.dev/"  # Replace with your redirect URI

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
    
    # Google Authentication
    st.subheader("Google Authentication")
    client_id = "264463378097-emcfg38oqfe1mbh5ut448fjvh7h09fh7.apps.googleusercontent.com"  # Replace with your OAuth client ID
 
    # Redirect the user to the Google Sign-In page
    auth_url = "https://accounts.google.com/o/oauth2/auth"
    client_id = "264463378097-emcfg38oqfe1mbh5ut448fjvh7h09fh7.apps.googleusercontent.com"  # Replace with your actual client ID
    client_secret = "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"
    client = GoogleOAuth2(client_id, client_secret)
    redirect_uri = "https://supreme-couscous-rr59wj6rjj2xwvv-8501.app.github.dev/"  # Replace with your redirect URI
    scope = "openid email"  # Replace with the desired scopes
    state = "state123"  # Replace with a unique state value
    auth_endpoint = f"{auth_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"
    #st.markdown(f'<a href="{auth_endpoint}">Click here to sign in with Google</a>', unsafe_allow_html=True)
    st.link_button("Sign in with Google", auth_endpoint)

    if st.runtime.exists():
        session_id = get_report_ctx().session_id
        runtime = get_instance()
        session_info = runtime._session_mgr.get_session_info(session_id)
        headers = _get_websocket_headers()
        access_token = headers.get("X-Access-Token")
        print(access_token)
        print(session_info)
        print(st.experimental_get_query_params())
        if "code" in st.experimental_get_query_params().keys():
            code = st.experimental_get_query_params()["code"]
            token = asyncio.run(write_access_token(client, redirect_uri, code))
            st.session_state["token"] = token["access_token"]
            print(token)
            r = requests.get(url = "https://oauth2.googleapis.com/tokeninfo", params = {"id_token":token["id_token"]})
            data = r.json()
            print(data)
            st.session_state["email"] = data["email"]
            #print(asyncio.run(get_email(client, st.session_state["token"])))
 

    st.markdown(
        """
        Welcome to my interview assistant!
        **👈 Select an interview type from the sidebar**!
        ### Choose an Interview Type
        - Behavioral: Answer questions about your past experiences
        - Case: Walk through a business situation
    """
    )
    option = st.selectbox(
        'Choose Interview Type',
        ('Behavioral', 'Case')
    )
    st.button('Set Interview Type', on_click=set_interview_type, args=[option])
    if "email" in st.session_state:
        st.markdown(
            st.session_state["email"]
        )
    st.write('\n\n')

def set_interview_type(option):
    st.session_state["interview_type"] = option

if __name__ == "__main__":
    run()
