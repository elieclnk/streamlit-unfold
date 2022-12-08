import streamlit as st
# from streamlit_chat import message
from google.cloud import firestore
from datetime import datetime
import openai
import json
from google.oauth2 import service_account
from collections import defaultdict

st.set_page_config(page_title="Past journals", page_icon="📈")

### Load the Firestore Database ###
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

### Login to OpenAI ###
openai.api_key=st.secrets["openai_key"]

if 'login' not in st.session_state:
    st.session_state['login'] = False
    
if st.session_state.login == True:
    st.subheader("Past entries")

    list_entries = defaultdict()
    list_todos = defaultdict()
    list_pos = defaultdict()

    entries = db.collection("journals").where(u"uid","==",st.session_state.uid)
    todos = db.collection("todos").where(u"uid","==",st.session_state.uid)
    pos = db.collection("positives").where(u"uid","==",st.session_state.uid)

    for doc in entries.stream():
        list_entries[doc.to_dict()['date']] = doc.to_dict()['entry']

    for doc in todos.stream():
        list_todos[doc.to_dict()['date']] = doc.to_dict()['todos']
    
    for doc in pos.stream():
        list_pos[doc.to_dict()['date']] = doc.to_dict()['pos']
    
    common_keys = set(list_entries.keys()) & set(list_todos.keys()) & set(list_pos.keys())

    for key in common_keys:
        with st.expander(key):
            st.subheader(f"Journal : {key}")
            st.write(list_entries[key])
            st.subheader("Todos")
            for i in list_todos[key]:
                st.markdown(f"- {i}")
            st.subheader("Positive thoughts")
            for j in list_pos[key]:
                st.markdown(f"- {j}")