import datetime
import streamlit as st
from utils import save_uploadedfile, show_results, remove_files

st.set_page_config(
    page_title = "CUSTOMER PROFILER | KAINOVATION TECHNOLOGIES",
    # page_icon = r"static\favicon.png",
    layout = "wide",
    initial_sidebar_state = "expanded",
    menu_items = None 
)

st.title("CUSTOMER PROFILER")

with st.form("form", clear_on_submit=False):
    st.write("Please enter your details.")
    full_name = st.text_input("Full Name")
    nic_or_dln = st.text_input("NIC/DL number")
    address = st.text_input('Address')
    dob = st.date_input("Date of Birth", value=datetime.date(2000, 1, 1),
                        min_value=datetime.date(1940, 1, 1),
                        max_value=datetime.date(2022, 12, 31))
    uploaded_file = st.file_uploader(
        "Choose a file", accept_multiple_files=True)
    if uploaded_file is not None:
        for files in uploaded_file:
            save_uploadedfile(files)
    else:
        st.write('please upload documents first')
    submitted = st.form_submit_button("Submit")
    if full_name and nic_or_dln and address and dob and uploaded_file and submitted:
        st.success("Form submited successfully")
    elif submitted:
        st.error('Please fill all the fields!')

if full_name and nic_or_dln and address and dob and uploaded_file and submitted:
    show_results(full_name, nic_or_dln, address, dob)    
    remove_files()