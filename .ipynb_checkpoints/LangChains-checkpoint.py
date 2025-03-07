import os
import sys
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI

# Load environment variables
load_dotenv()

# Predefined PDFs
PDF_NAMES = ["Cats.pdf", "Dogs.pdf"]  # Add all the PDF names here


def main():
    # Ensure the question is passed as an argument
    if len(sys.argv) < 2:
        print("Usage: python script.py <question>")
        sys.exit(1)

    question = sys.argv[1]
    api_key = os.getenv("OPENAI_API_KEY")

    # Validate API key
    if not api_key:
        print("Error: OpenAI API key not found. Ensure it is set in the .env file.")
        sys.exit(1)

    # Extract and combine text from all PDFs
    combined_text = ""
    for pdf_name in PDF_NAMES:
        combined_text += extract_data(pdf_name)

    # Split the combined text, vectorize, and answer the question
    docs = split_text(combined_text)
    docstorage = vectorize_and_store(docs, api_key)
    response = answer_question(question, api_key, docstorage)

    # Print the result
    if response and "result" in response:
        print(response["result"])
    else:
        print("No result found. Debugging information:", response)


def extract_data(pdf_name):
    """
    Load and extract text from a single PDF.
    """
    try:
        loader = PyPDFLoader(pdf_name)
        data = loader.load()
        policy_text = ""

        for doc in data:
            if isinstance(doc, dict) and "text" in doc:
                policy_text += doc["text"]
            elif isinstance(doc, str):
                policy_text += doc
            else:
                policy_text += repr(doc)

        return policy_text
    except Exception as e:
        print(f"Error loading PDF {pdf_name}: {e}")
        sys.exit(1)


def split_text(text):
    """
    Split text into manageable chunks using CharacterTextSplitter.
    """
    ct_splitter = CharacterTextSplitter(separator=".", chunk_size=1200, chunk_overlap=200)
    return ct_splitter.split_text(text)


def vectorize_and_store(docs, api_key):
    """
    Convert text chunks into vector embeddings and store them using FAISS.
    """
    try:
        embedding_function = OpenAIEmbeddings(openai_api_key=api_key)
        docstorage = FAISS.from_texts(docs, embedding_function)
        return docstorage
    except Exception as e:
        print(f"Error creating vectorstore: {e}")
        sys.exit(1)


def answer_question(question, api_key, docstorage):
    """
    Use a RetrievalQA chain to answer the given question.
    """
    try:
        llm = OpenAI(model_name="gpt-3.5-turbo-instruct", openai_api_key=api_key)
        qa = RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff", retriever=docstorage.as_retriever()
        )
        return qa.invoke({"query": question})
    except Exception as e:
        print(f"Error answering question: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
