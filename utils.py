import os
import cv2
import pathlib
import streamlit as st
from pytesseract import pytesseract
from pdf2image import convert_from_path

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
    ext = pathlib.Path(uploaded_file.name).suffix
    # Store Pdf with convert_from_path function
    file_saving_path = os.path.join("temp/", uploaded_file.name)
    with open(file_saving_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    if ext == '.pdf':
        images = convert_from_path(file_saving_path, poppler_path = r'C:/Program Files/poppler-22.04.0/Library/bin' )
        for i in range(len(images)):
            # Save pages as images in the pdf
            images[i].save('temp/page'+ str(i) +'.jpg', 'JPEG')

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

def get_text():
    images = get_images('temp')
    text = ''
    for image in images:
        text += detect(image)
    return text

def chech_info(full_name, nic_or_dln, address, dob, text):
    # Checking the given full name
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
    doc = ''
    dl = ('driving licence')
    nic = ('national identity card')
    proposal_words = (
        'Union Life Plus Proposal Form')
    financial_words = ('PERSONAL FINANCIAL NEEDS REVIEW')
    if dl.lower() in text.lower():
        doc += "Driving Licence  is detected"
    elif nic.lower() in text.lower():
        doc += "NIC  is detected"
    elif proposal_words.lower() in text.lower():
        doc += "Union Life Plus Proposal Forms is detected"
    elif financial_words.lower() in text.lower():
        doc += "PERSONAL FINANCIAL NEEDS REVIEW Document  is detected"
    else: doc+= "Cannot detect the document type!"
    return doc

def show_results(full_name, nic_or_dln, address, dob):
    text = get_text()
    name, idNo, add, bday = chech_info(full_name, nic_or_dln, address, dob, text.replace(" ", ""))
    doc_type = detect_NIC_or_DLN(text)
    # st.write(text)
    st.write(doc_type)
    if name == 100.0:
        name_mark = '✅'
    else: name_mark = ''
    if idNo == 100.0:
        idNo_mark = '✅'
    else: idNo_mark = ''
    if add == 100.0:
        add_mark = '✅'
    else: add_mark = ''
    if bday == 100.0:
        bday_mark = '✅'
    else: bday_mark = ''
    st.write(name_mark, "Matching percentage of the name is", str(name)," %")
    st.write(idNo_mark, "Matching percentage of the NIC or DLN is", str(idNo)," %")
    st.write(add_mark, "Matching percentage of the address is", str(add)," %")
    st.write(bday_mark, "Matching percentage of the birthdate is", str(bday)," %")
 
def remove_files():
    try:
        for filename in os.listdir('temp'):
            file = os.path.join("temp/", filename)
            os.remove(file)
    except OSError as e:  ## if failed, report it back to the user ##
        print ("Error: %s - %s." % (e.file, e.strerror))