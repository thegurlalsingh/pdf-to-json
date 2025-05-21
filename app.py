import streamlit as st
import fitz  
import pdfplumber
import json
import pandas as pd
import os

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_tables_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            for table in extracted_tables:
                if table:
                    headers = table[0]
                    for row in table[1:]:
                        row_dict = dict(zip(headers, row))
                        tables.append(row_dict)
    return tables

def structure_data(text, tables):
    lines = text.split("\n")
    data = {}
    current_header = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.isupper() or line.endswith(":"):
            current_header = line.replace(":", "").strip()
            data[current_header] = ""
        elif current_header:
            data[current_header] += line + " "

    if tables:
        data["List_items"] = tables

    return data

st.title("PDF Document Extractor to JSON")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    st.success("PDF uploaded successfully!")

    with st.spinner("Extracting text and tables..."):
        text = extract_text_from_pdf("temp.pdf")
        tables = extract_tables_from_pdf("temp.pdf")
        result = structure_data(text, tables)

    st.subheader("Extracted JSON Preview")
    st.json(result)

    json_filename = uploaded_file.name.replace(".pdf", ".json")
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    with open(json_filename, "rb") as f:
        st.download_button(
            label="Download JSON",
            data=f,
            file_name=json_filename,
            mime="application/json"
        )

    os.remove("temp.pdf")
    os.remove(json_filename)
