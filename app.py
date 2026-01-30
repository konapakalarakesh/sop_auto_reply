import streamlit as st
from groq import Groq
from pypdf import PdfReader

st.set_page_config(page_title="SOP Agent", page_icon="📑")

# 1. Function to extract text from your uploaded PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# 2. Load the SOP (Make sure 'sop.pdf' is in your GitHub repo)
@st.cache_data # This saves memory so it doesn't reload every click
def get_sop_content():
    return extract_text_from_pdf("sop.pdf")

sop_context = get_sop_content()

# 3. Setup Groq AI
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("🤖 Internal SOP Assistant")
st.markdown("Ask me anything about the company procedures.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Chat Logic
if prompt := st.chat_input("How do I handle..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a precise corporate assistant. Use the following SOP text to answer questions. If the answer is not in the text, say 'I do not have information on that specific scenario.'\n\nSOP CONTENT:\n{sop_context}"
                },
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0, # Keeps it factual
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})