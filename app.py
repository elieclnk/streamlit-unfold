import streamlit as st
# from streamlit_chat import message
from google.cloud import firestore
from datetime import datetime
import openai
import json
from google.oauth2 import service_account

st.set_page_config(page_title="Home", page_icon="📈")

### Load the Firestore Database ###
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

### Login to OpenAI ###
openai.api_key=st.secrets["openai_key"]

### Make a list of users registered in the DB ###
list_users = []
users = db.collection("users")
for doc in users.stream():
	list_users.append(doc.to_dict()['uid'])

### Functions to use in the main script ###
def compute_time():
    currentDateAndTime = datetime.now()
    currentTime = currentDateAndTime.strftime("%Y-%m-%d--%H:%M:%S")
    return currentTime

### OpenAI functions ###
def extract_todos(prompt):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=f"Extract a todo-list from the following text. The list extracts the mains tasks and ranks them by priority. \n\n {prompt}",
    temperature=0.4,
    max_tokens=150,
    top_p=1,
    frequency_penalty=1.02,
    presence_penalty=1.03
    )
    return response["choices"][0]["text"]

def extract_pos(prompt):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=f"Extract 3 positive thoughts from the following text \n\n {prompt}",
    temperature=0.4,
    max_tokens=150,
    top_p=1,
    frequency_penalty=1.02,
    presence_penalty=1.03
    )
    return response["choices"][0]["text"]

def refine_todos(prompt):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt=f"Break down the task and give 3 short action items to achieve it.\n\n {prompt}",
    temperature=0.4,
    max_tokens=150,
    top_p=1,
    frequency_penalty=1.02,
    presence_penalty=1.03
    )
    return response["choices"][0]["text"]


### Beginning of the streamlit interface

st.title('Unfold :brain: ')

if 'login' not in st.session_state:
    st.session_state['login'] = False

### If user is not signed in ###
if st.session_state.login == False:

    placeholder = st.empty()
    with placeholder.form("log"):
        st.subheader("Log In")
        input_id = st.text_input("Please input your ID", key="login_id")
        st.session_state['uid'] = input_id
        login_button = st.form_submit_button("Submit")
        if login_button and input_id in list_users:
            st.session_state['login'] = True
            placeholder.empty()

### If user is signed in ###
if st.session_state.login == True:

    col1, col2 = st.columns([65, 35])

    with col1:
        ### Journal part ###
        st.subheader("Journal")
        list_todos=[]
        list_pos=[]
        with st.form("journal"):
            journal = st.text_area('Daily brain dump', "", height=300)
            submitted = st.form_submit_button("Submit")
            if submitted:
                date = compute_time()
                record = {
                    u'uid': st.session_state.uid,
                    u'date': date,
                    u'entry': journal
                }
                # save the entry in the DB
                db.collection(u'journals').document(str(date)).set(record)
                # extract the todos
                todos = extract_todos(journal)
                # extract the positive thoughts
                pos = extract_pos(journal)

                ### Make a list out of the todos ###
                list_todos = todos.split("\n")
                list_todos = list(filter(None, list_todos))
                list_todos = [l[2:] for l in list_todos]

                # save todos in the DB
                record_todos = {
                    u'uid': st.session_state.uid,
                    u'date': date,
                    u'todos': list_todos
                }
                db.collection(u'todos').document(str(date)).set(record_todos)

                ### Make a list out of the positive thougts ###
                list_pos = pos.split("\n")
                list_pos = list(filter(None, list_pos))
                list_pos = [l[2:] for l in list_pos]

                # save pos in the DB
                record_pos = {
                    u'uid': st.session_state.uid,
                    u'date': date,
                    u'pos': list_pos
                }

                db.collection(u'positives').document(str(date)).set(record_pos)
                


        # st.subheader("Chatbot")
        # if 'generated' not in st.session_state:
        #     st.session_state['generated'] = []
        # if 'past' not in st.session_state:
        #     st.session_state['past'] = []
        # if "chat" not in st.session_state:
        #     st.session_state['chat'] = []
        
        # user_input = st.text_input("You: ","Hey", key="input")

        # if user_input:
        #     output = "Hi"

        # st.session_state.past.append(user_input)
        # st.session_state.generated.append(output)
        # st.session_state.chat.append("You :"+ user_input)
        # st.session_state.chat.append("AI :"+ output)

        # if st.session_state['generated']:
        #     for i in range(len(st.session_state['generated'])-1, -1, -1):
        #         message(st.session_state["generated"][i], key=str(i))
        #         message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

    with col2:
        st.subheader("Action Items")
        c=0
        for i,td in enumerate(list_todos):
            if td:
                c+=1
                st.checkbox(label=td)
                # with st.expander(f"Action {c} : {td}"):
                    # st.write(refine_todos(td))
        st.subheader("Positive thoughts")
        for po in list_pos:
            if po:
                st.markdown(f"- {po}")
            

    
    # st.sidebar.subheader("Past entries")

    # list_dates = []
    # list_entries = []
    # entries = db.collection("journals").where(u"uid","==",st.session_state.uid)

    # for doc in entries.stream():
    #     list_dates.append(doc.id)
    #     list_entries.append(doc.to_dict()['entry'])

    # for date,entry in zip(list_dates, list_entries):
    #     # st.sidebar.markdown("- " + date)
    #     with st.sidebar.expander(date):
    #         st.write(entry)
    
        



