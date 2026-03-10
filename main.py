# llama_ai.py

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from datetime import datetime
import ujson as json, time
from pathlib import Path

class LLAMA_AI:
    def __init__(self):
        with open("config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.folder_path = self.config.get("folder_path", '')
        self.language = self.config.get("language", 'general')
        self.db_path = Path(f"{self.folder_path}_db")
        self.ext = self.config.get("extension", "py")
        self.chunk_size = self.config.get("chunk_size", 1000)
        self.chunk_overlap = self.config.get("chunk_overlap", 200)
        self.text_embed_model = self.config.get("text_embed_model", "nomic-embed-text")
        self.llm = self.config.get("llm", '')
        self.tokens = self.config.get("tokens", 1500)
        self.temp = self.config.get("temperature", 0.2)
        self.top_k = self.config.get("top_k", 4)
        self.fetch_top_k = self.config.get("fetch_top_k", 20)
        self.language_map = {
            "python": Language.PYTHON,
            "java": Language.JAVA,
            "javascript": Language.JS,
            "cpp": Language.CPP,
            "go": Language.GO,
            "rust": Language.RUST
        }
    
    def code_loader(self):
        start_time = time.time()
        if self.db_path.exists():
            print(f'{self.db_path} already exists, skipping...')
            return
        # Load all .py files
        loader = DirectoryLoader(f"./{self.folder_path}", glob=f"**/*.{self.ext}", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
        documents = loader.load()
        print(f"Loaded {len(documents)} documents")

        # Split into chunks
        if self.language in self.language_map:
            text_splitter = RecursiveCharacterTextSplitter.from_language(
                language=self.language_map[self.language.lower()], 
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
        else:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
        texts = text_splitter.split_documents(documents)
        print(f"Created {len(texts)} chunks")

        # Create embeddings
        embeddings = OllamaEmbeddings(model=self.text_embed_model)

        # Store in vector DB
        Chroma.from_documents(documents=texts, embedding=embeddings, persist_directory=self.db_path)

        print("Vector database created successfully.")
        end_time = time.time()

        print(f"Vectorization time: {end_time - start_time}")

    def code_query(self):
        start_time = time.time()
        # Load embedding model
        embeddings = OllamaEmbeddings(model=self.text_embed_model)

        # Load vector database
        if not self.db_path.exists():
            print("Vector DB not found. Run code_loader() first.")
            return False
        
        vectorstore = Chroma(
            persist_directory=self.db_path,
            embedding_function=embeddings
        )

        # Load LLM
        llm = OllamaLLM(model=self.llm, num_predict=self.tokens, temperature=self.temp)

        # Create retriever
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": self.top_k})
        # retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": self.top_k, "fetch_k": self.fetch_top_k})
        # retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"score_threshold": 0.7})

        # Ask question
        with open("prompt.txt", "r", encoding="utf-8") as prompt_f:
            prompt = prompt_f.read()

        # Retrieve relevant documents
        docs = retriever.invoke(prompt)
        

        # Combine retrieved context
        context = "\n\n".join([f"File: {doc.metadata.get('source')}\n{doc.page_content}" for doc in docs])
        # seen = {}
        # for doc in docs:
        #     src = doc.metadata.get("source", "unknown")
        #     if src not in seen:
        #         seen[src] = doc.page_content
        #     else:
        #         seen[src] += "\n" + doc.page_content  # merge chunks from same file

        # context = "\n\n".join([f"File: {src}\n{content}" for src, content in seen.items()])

        # Final prompt
        final_prompt = f"""
        {prompt}
        
        Here is the relevant project code:
        {context}
        """

        # Get response
        response = llm.invoke(final_prompt)

        print("\nAI RESPONSE:\n")
        print(response)

        current_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = Path("responses") 
        output_path.mkdir(exist_ok=True)
        response_file_path = output_path / f"response_{current_timestamp}.txt"
        
        with open(response_file_path, "w", encoding="utf-8") as f:
            f.write(response)
        end_time = time.time()

        print(f"Response time: {end_time - start_time}")
        
if __name__ == "__main__":
    llama_obj = LLAMA_AI()
    llama_obj.code_loader()
    llama_obj.code_query()