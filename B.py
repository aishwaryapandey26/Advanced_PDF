import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import requests, json, os, datetime, time
from io import BytesIO 
from PyPDF2 import PdfReader


# ai assistant 

elif selected == "AI ASSISTANT"
st.header(" AI PDF Assistant")
st.write("ask anything related to your PDFs. I can help with merging, splitting , sumaarizing or analyzing docs")

#OpenAI API KEY INPUT
api_key=st.text_input("Enter your OpenAI API key", type="password")

#chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history=[]

    #display previous messages
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.chat_message("user").markdown(msg["content"])
        else:
            st.chat_message("assistant").markdown(msg["content"])

            #PDF UPLOAD
            uploaded_pdf=st.file_uploader("upload a PDF for AI analysis", type="pdf")

            user_input=st.chat_input("ask something...")

