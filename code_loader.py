# code_loader.py

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import ujson as json
import time


def code_loader():
    start_time = time.time()

    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        
    folder_path = config.get("code_loader_folder_path", '')

    # Load all .py files
    loader = DirectoryLoader(f"./{folder_path}", glob="**/*.py", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    texts = text_splitter.split_documents(documents)
    print(f"Created {len(texts)} chunks")

    # Create embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Store in vector DB
    vectorstore = Chroma.from_documents(documents=texts, embedding=embeddings, persist_directory=f"./{folder_path}_db")
    # vectorstore.persist()

    print("Vector database created successfully.")
    end_time = time.time()

    print(f"Time took: {end_time - start_time}")
    
if __name__ == "__main__":
    code_loader()