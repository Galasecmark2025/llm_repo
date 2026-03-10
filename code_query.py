# code_query.py

from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from datetime import datetime
import ujson as json
import time

def code_query():
    start_time = time.time()
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        
    folder_path = config.get("code_loader_folder_path", '')

    # Load embedding model
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    # Load vector database
    vectorstore = Chroma(
        persist_directory=f"./{folder_path}_db",
        embedding_function=embeddings
    )

    # Load LLM
    llm = OllamaLLM(model="codellama:7b")

    # Create retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # Ask question
    with open("prompt.txt", "r", encoding="utf-8") as prompt_f:
        prompt = prompt_f.read()

    # Retrieve relevant documents
    docs = retriever.invoke(prompt)

    # Combine retrieved context
    context = "\n\n".join([doc.page_content for doc in docs])

    # Final prompt
    final_prompt = f"""
    You are a senior software engineer.

    Here is the relevant project code:
    {context}

    Now listen:
    {prompt}
    """

    # Get response
    response = llm.invoke(final_prompt)

    print("\nAI RESPONSE:\n")
    print(response)

    current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"response_{current_timestamp}.txt", "w") as f:
        f.write(response)
    end_time = time.time()

    print(f"Time took: {end_time - start_time}")
    
if __name__ == "__main__":
    code_query()