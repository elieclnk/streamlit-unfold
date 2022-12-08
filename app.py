import streamlit as st
# from streamlit_chat import message
from google.cloud import firestore
from datetime import datetime
import openai
import config

# Authenticate to Firestore with the JSON account key.
db = firestore.Client.from_service_account_json("firestore-key.json")
#openai api key
openai.api_key=config.API_KEY_OPENAI

list_users = []
users = db.collection("users")
for doc in users.stream():
	list_users.append(doc.to_dict()['uid'])

def compute_time():
    currentDateAndTime = datetime.now()
    currentTime = currentDateAndTime.strftime("%Y-%m-%d--%H:%M:%S")
    return currentTime

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

st.title('Unfold :page_with_curl: ')

if 'login' not in st.session_state:
    st.session_state['login'] = False

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

if st.session_state.login == True:

    col1, col2 = st.columns([65, 35])

    with col1:

        st.subheader("Journal")
        list_todos=[]
        list_pos=[]
        with st.form("journal"):
            journal = st.text_area('Daily brain dump', "", height=300)
            submitted = st.form_submit_button("Submit")
            if submitted:
                #compute the todos with GPT3
                #save the journal entry
                date = compute_time()
                data = {
                    u'uid': st.session_state.uid,
                    u'date': date,
                    u'entry': journal
                }
                print(data)
                db.collection(u'journals').document(str(date)).set(data)
                todos = extract_todos(journal)
                pos = extract_pos(journal)
                # st.write(todos)
                # st.write(pos)
                list_todos = todos.split("\n")
                list_todos = list(filter(None, list_todos))
                list_todos = [l[2:] for l in list_todos]

                list_pos = pos.split("\n")
                list_pos = list(filter(None, list_pos))
                list_pos = [l[2:] for l in list_pos]
                


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
            

    
    st.sidebar.subheader("Past entries")

    list_dates = []
    list_entries = []
    entries = db.collection("journals").where(u"uid","==",st.session_state.uid)

    for doc in entries.stream():
        list_dates.append(doc.id)
        list_entries.append(doc.to_dict()['entry'])

    for date,entry in zip(list_dates, list_entries):
        # st.sidebar.markdown("- " + date)
        with st.sidebar.expander(date):
            st.write(entry)
    
        



