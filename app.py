import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found. Please check your .env file.")
    st.stop()

client = Groq(api_key=api_key)

st.set_page_config(page_title="PDF Q&A Chatbot", page_icon="📄")
st.title("📄 PDF Q&A Chatbot")
st.write("Upload a PDF and ask questions about it!")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    pdf_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pdf_text += text + "\n"

    st.success(f"PDF loaded successfully! ({len(reader.pages)} pages)")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Ask a question about the PDF...")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                prompt = f"""Answer the question based only on the following PDF content.
If the answer is not in the PDF, say "I couldn't find that in the PDF."

PDF Content:
{pdf_text[:15000]}

Question: {question}
"""
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                )
                answer = response.choices[0].message.content
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
else:
    st.info("👆 Please upload a PDF file to get started.")