import os
import cv2
import glob
import pathlib
import shutil
import pandas as pd
import streamlit as st
from pytesseract import pytesseract
from pdf2image import convert_from_path

nic, dl, pp, proposal, fin_doc, sign, add_doc = False, False, False, False, False, False, False
nic_saved, dl_saved, pp_saved, proposal_saved, fin_doc_saved, sign_saved, add_doc_saved = False, False, False, False, False, False, False
messages = []
os.mkdir('temp/data')
def detect(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU |
                                            cv2.THRESH_BINARY_INV)
    # cv2.imwrite('output/threshold_image.jpg',thresh1)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (12, 12))
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 3)
    # cv2.imwrite('output/dilation_image.jpg',dilation)
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                                cv2.CHAIN_APPROX_NONE)
    im2 = img.copy()
    crop_number=0 
    full_text = ''
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Draw the bounding box on the text area
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Crop the bounding box area
        cropped = im2[y:y + h, x:x + w]
        
        # cv2.imwrite("output/crop"+str(crop_number)+".jpeg",cropped)
        crop_number+=1
        
        # cv2.imwrite('output/rectanglebox.jpg',rect)
        
        # open the text file
        # file = open("output/text_output.txt", "a")
        
        # Using tesseract on the cropped image area to get text
        text = pytesseract.image_to_string(cropped)
        if text != '':
            full_text += text
        # full_text.append(text)
        # Adding the text to the file
        # file.write(text)
        # file.write("\n")
        
        # # Closing the file
        # file.close
    return full_text

def split_text(txt):
    txt = txt.replace("," , "")
    return txt.split()

def check_in_text(splitted_text, detected_text):
    matching_count = 0
    for i in splitted_text:
        if i.lower() in detected_text.lower():
            matching_count+=1
    return (matching_count / len(splitted_text)*100)

def save_uploadedfile(uploaded_file):
    global nic, dl, pp, proposal, fin_doc, sign, add_doc
    text = ''
    images_to_save = []
    # Store Pdf with convert_from_path function
    pathname, extension = os.path.splitext(uploaded_file.name)
    filename = pathname.split('/')
    file_saving_path = os.path.join("temp/data/"+ str(filename[-1]), uploaded_file.name)
    os.mkdir('temp/data/'+ str(filename[-1]))
    with open(file_saving_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        if extension == '.pdf':
            images = convert_from_path(file_saving_path, poppler_path = r'C:/Program Files/poppler-22.04.0/Library/bin' )
            for i in range(len(images)):
                # Save pages as images in the pdf
                images[i].save('temp/data/'+ str(filename[-1])+ '/page'+ str(i) +'.jpg', 'JPEG')
                img = cv2.imread(os.path.join('temp/data/'+ str(filename[-1])+ '/page'+ str(i) +'.jpg'))
                text += detect(img)
                images_to_save.append(img)
            dl, nic, proposal, fin_doc = detect_NIC_or_DLN(text)
            check_and_save_file(nic, dl, pp, proposal, fin_doc, sign, add_doc, images_to_save)
            nic, dl, pp, proposal, fin_doc, sign, add_doc = False, False, False, False, False, False, False
        else:
            img = cv2.imread(file_saving_path)
            images_to_save.append(img)
            text += detect(img)
            dl, nic, proposal, fin_doc = detect_NIC_or_DLN(text)
            check_and_save_file(nic, dl, pp, proposal, fin_doc, sign, add_doc, images_to_save)
            nic, dl, pp, proposal, fin_doc, sign, add_doc = False, False, False, False, False, False, False

def check_and_save_file(nic, dl, pp, proposal, fin_doc, sign, add_doc, images):
    if nic:
        for i in range(len(images)):
            cv2.imwrite('temp/nic/'+ str(i) +'.jpg',images[i])
    elif dl:
        for i in range(len(images)):
            cv2.imwrite('temp/dl/'+ str(i) +'.jpg',images[i])
    elif pp:
        for i in range(len(images)):
            cv2.imwrite('temp/pp/'+ str(i) +'.jpg',images[i])
    elif proposal:
        for i in range(len(images)):
            cv2.imwrite('temp/proposal/'+ str(i) +'.jpg',images[i])
    elif fin_doc:
        for i in range(len(images)):
            cv2.imwrite('temp/fin_doc/'+ str(i) +'.jpg',images[i])
    elif sign:
        for i in range(len(images)):
            cv2.imwrite('temp/sign_card/'+ str(i) +'.jpg',images[i])
    elif add_doc:
        for i in range(len(images)):
            cv2.imwrite('temp/address_proof/'+ str(i) +'.jpg',images[i])
    else:
        for i in range(len(images)):
            cv2.imwrite('temp/other/'+ str(i) +'.jpg',images[i])

def get_images(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            images.append(img)
    return images

def drop_v (txt):
    txt = txt.lower().replace("v" , "")
    return txt

def get_text(filepath):
    images = get_images(filepath)
    text = ''
    for image in images:
        text += detect(image)
    return text

def chech_info(full_name, nic_or_dln, address, dob, text):
    # Checking the given full name for dl
    splitted_name = split_text(full_name)
    name_matched_percentage = check_in_text(splitted_name, text)

    # Checking the given NIC or DLN
    nic_or_dln = drop_v(nic_or_dln)
    splitted_nic = split_text(nic_or_dln)
    nic_matched_percentage = check_in_text(splitted_nic, text)

    # Checking the given address
    splitted_address = split_text(address)
    address_matched_percentage = check_in_text(splitted_address, text)

    # Checking the given DOB
    dob1 = dob.strftime('%d.%m.%Y')
    dob2 = dob.strftime('%d/%m/%Y')
    dob3 = dob.strftime('%d-%m-%Y')
    dob4 = dob.strftime('%Y.%m.%d')
    dob5 = dob.strftime('%Y/%m/%d')
    dob6 = dob.strftime('%Y-%m-%d')
    dob1_mp = check_in_text([dob1], text)
    dob2_mp = check_in_text([dob2], text)
    dob3_mp = check_in_text([dob3], text)
    dob4_mp = check_in_text([dob4], text)
    dob5_mp = check_in_text([dob5], text)
    dob6_mp = check_in_text([dob6], text)
    dob_matched_percentage = max([dob1_mp, dob2_mp, dob3_mp,dob4_mp, dob5_mp, dob6_mp])
    return name_matched_percentage, nic_matched_percentage, address_matched_percentage, dob_matched_percentage

def detect_NIC_or_DLN(text):
    global nic, dl, pp, proposal, fin_doc, sign, add_doc
    global nic_saved, dl_saved, pp_saved, proposal_saved, fin_doc_saved, sign_saved, add_doc_saved
    dl_words = ('driving licence')
    nic_words = ('national identity card')
    proposal_words = (
        'Union Life Plus Proposal Form')
    financial_words = ('PERSONAL FINANCIAL NEEDS REVIEW')
    if dl_words.lower() in text.lower():
        dl = True
        messages.append("Driving Licence")
        dl_saved = True
    elif nic_words.lower() in text.lower():
        nic = True
        messages.append("NIC")
        nic_saved = True
    elif proposal_words.lower() in text.lower():
        proposal = True
        messages.append("Proposal form")
        proposal_saved = True
    elif financial_words.lower() in text.lower():
        fin_doc = True
        messages.append("Personal financial needs document")
        fin_doc_saved =True
    # else: doc+= "Cannot detect the document type!"
    print("Ok")
    print(dl_saved, proposal_saved, fin_doc_saved)
    return dl, nic, proposal, fin_doc

def check_dl(name,nic_or_dln, address, dob):
    text = get_text('temp/dl')
    return chech_info(name, nic_or_dln, address, dob, text.replace(" ", ""))

def check_proposal(name,nic_or_dln, address, dob):
    text = get_text('temp/proposal')
    return chech_info(name, nic_or_dln, address, dob, text.replace(" ", ""))

def check_fin_doc(name,nic_or_dln, address, dob):
    text = get_text('temp/fin_doc')
    return chech_info(name, nic_or_dln, address, dob, text.replace(" ", ""))
    
def show_results(full_name, nic_or_dln, address, dob):
    # global nic_saved, dl_saved, pp_saved, proposal_saved, fin_doc_saved, sign_saved, add_doc_saved
    # for i in messages:
    #     st.write(str(i)+" detected. ")
    print(dl_saved, proposal_saved, fin_doc_saved)
    if dl_saved:
        name, idNo, add, bday = check_dl(full_name,nic_or_dln, address, dob)
        name_mark, idNo_mark, add_mark, bday_mark = results(name, idNo, add, bday)
        dl_col = ['✅',name_mark, idNo_mark, add_mark, bday_mark]
    if proposal_saved:
        name, idNo, add, bday = check_proposal(full_name,nic_or_dln, address, dob)
        name_mark, idNo_mark, add_mark, bday_mark = results(name, idNo, add, bday)
        proposal_col = ['✅', name_mark, idNo_mark, add_mark, bday_mark]
    if fin_doc_saved:
        name, idNo, add, bday = check_fin_doc(full_name,nic_or_dln, address, dob)
        name_mark, idNo_mark, add_mark, bday_mark = results(name, idNo, add, bday)
        fin_col = ['✅',name_mark, idNo_mark, add_mark, bday_mark]
    df = pd.DataFrame(
        {
            "Verification": ['Detected Document', 'Name verification','NIC number verification', 'Address verification', 'Date of birth verification'],
            "Driving Licence": dl_col,
            "Proposal":proposal_col,
            "Personal financial needs":fin_col
        }
    )
    st.dataframe(df)

def results(name, idNo, add, bday):
    if name == 100.0:
        name_mark = '✅'
    elif name <= 50.0:
        name_mark = '❌'
    else: name_mark = str(name)+'%'

    if idNo == 100.0:
        idNo_mark = '✅'
    elif idNo <= 50.0:
        idNo_mark = '❌'
    else: idNo_mark = str(idNo)+'%'

    if add == 100.0:
        add_mark = '✅'
    elif add <= 50.0:
        add_mark = '❌'
    else: add_mark = str(add)+'%'

    if bday == 100.0:
        bday_mark = '✅'
    elif bday <= 50.0:
        bday_mark = '❌'
    else: bday_mark = str(bday)+'%'

    return name_mark, idNo_mark, add_mark, bday_mark


def remove_files(folder):
    try:
        files = glob.glob(os.path.join(folder, "*"))
        for f in files:
            os.remove(f)
    except OSError as e:  ## if failed, report it back to the user ##
        print ("Error:")

def clean():
    shutil.rmtree('temp/data/', ignore_errors=False)
    remove_files('temp/dl')
    remove_files('temp/address_proof')
    remove_files('temp/fin_doc')
    remove_files('temp/nic')
    remove_files('temp/other')
    remove_files('temp/pp')
    remove_files('temp/proposal')
    remove_files('temp/sign_card')
