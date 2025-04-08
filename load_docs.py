# load_docs.py

import os
import pandas as pd
import gc
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# 🔧 Initialize embedding + vectorstore
embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
persist_directory = "db"
vectorstore = Chroma(
    embedding_function=embedding_function,
    persist_directory=persist_directory
)

#Load PDFs
pdfs = [
    "data/Financial_Literacy_Education_LowIncome.pdf",
    "data/Financial_Literacy_Demographics.pdf",
    "data/Common_Budgetary_Framework.pdf"
]

splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

for pdf in pdfs:
    try:
        loader = PyPDFLoader(pdf)
        docs = loader.load()
        chunks = splitter.split_documents(docs)
        vectorstore.add_documents(chunks)
        print(f"✅ Loaded PDF: {pdf}")
        del docs, chunks
        gc.collect()
    except Exception as e:
        print(f"❌ Error loading PDF {pdf}: {e}")

#Load Excel files
excels = [
    "data/API_JAM_DS2_en_excel_v2_15248.xls",
    "data/API_USA_DS2_en_excel_v2_1992.xls",
    "data/API_CAN_DS2_en_excel_v2_2173.xls",
    "data/API_PAK_DS2_en_excel_v2_572.xls"
]

for file in excels:
    try:
        df_dict = pd.read_excel(file, sheet_name=None)
        for sheet_name, sheet in df_dict.items():
            text = sheet.to_string(index=False)
            doc = Document(page_content=text, metadata={"source": f"{file} - {sheet_name}"})
            vectorstore.add_documents([doc])
        print(f"✅ Loaded Excel: {file}")
        gc.collect()
    except Exception as e:
        print(f"❌ Error loading Excel {file}: {e}")

# Load CSV files
csvs = [
    "data/export-2025-04-03T16_19_36.391Z.csv",
    "data/dataset_2025-04-03T16_20_25.757308815Z_DEFAULT_INTEGRATION_IMF.STA_FAS_4.0.0.csv",
    "data/cards_data.csv",
    "data/budget_allocation.csv",
    "data/expense_tracker.csv",
    "data/salary_calculation_reference.csv",
    "data/budget_planning_examples.csv",
    "data/smart_money_qna.csv",
    "data/budget_planning_examples.csv",
]

for file in csvs:
    try:
        print(f"📥 Processing CSV in chunks: {file}")
        for chunk in pd.read_csv(file, chunksize=1000, on_bad_lines='skip', low_memory=False):
            text = chunk.to_string(index=False)
            doc = Document(page_content=text, metadata={"source": file})
            vectorstore.add_documents([doc])
            gc.collect()
        print(f"✅ Loaded CSV: {file}")
    except Exception as e:
        print(f"❌ Error loading CSV {file}: {e}")

print("🎉 All documents indexed into vector DB!")
