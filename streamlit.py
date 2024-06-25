import streamlit as st
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Load environment variables
groq_api_key = os.getenv('GROQ_API_KEY')
google_api_key = os.getenv('GOOGLE_API_KEY')

# Initialize Streamlit app title
st.title("Gemma Model Document Q&A")

# Initialize session state variables
def initialize_session_state():
    if 'vectors' not in st.session_state:
        st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        st.session_state.loader = PyPDFDirectoryLoader("./pdfFiles")  # Data Ingestion
        st.session_state.docs = st.session_state.loader.load()  # Document Loading
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # Chunk Creation
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs[:20])  # Splitting
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)  # Vector creation
llm=ChatGroq(groq_api_key=groq_api_key,
             model_name="gemma-7b-it")
prompt = ChatPromptTemplate.from_template(
    """
        Answer the questions based on the provided context only.
        Please provide the most accurate response based on the question
        <context>
            {context}
        <context>
        Questions:{input}
    """
)
# Function to handle vector embedding initialization
def vector_embedding():
    initialize_session_state()

# Function to handle document retrieval and response
def retrieve_documents(input_prompt):
    initialize_session_state()

    # Create document chain and retrieval chain
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = st.session_state.vectors.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # Measure response time
    start = time.process_time()
    response = retrieval_chain.invoke({'input': input_prompt})
    response_time = time.process_time() - start

    # Display response
    st.write(f"Response time: {response_time} seconds")
    st.write(response['answer'])

    # Display document similarity search
    with st.expander("Document Similarity Search"):
        for i, doc in enumerate(response["context"]):
            st.write(doc.page_content)
            st.write("--------------------------------")

# Main Streamlit app logic
if __name__ == "__main__":
    input_prompt = st.text_input("Enter Your Question From Documents")

    if st.button("Documents Embedding"):
        vector_embedding()
        st.write("Vector Store DB Is Ready")

    if input_prompt:
        retrieve_documents(input_prompt)
