# Import necessary libraries and modules
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import SemanticSimilarityExampleSelector
from langchain.prompts import FewShotPromptTemplate
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX
from langchain.prompts.prompt import PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql.base import SQLDatabaseChain
from langchain_community.llms import GooglePalm
from langchain_google_genai import GoogleGenerativeAI


# Import local few_shots examples and load environment variables
from .few_shots import few_shots
import os
from dotenv import load_dotenv
load_dotenv()

def get_few_shot_db_chain():
    # Determine the path to the SQLite database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')

    # Initialize SQLDatabase with the path to the SQLite database and sample some rows for table info
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}", sample_rows_in_table_info=3)
    
    # Initialize the GooglePalm LLM with the API key and set the temperature
    # llm = GooglePalm(google_api_key=os.environ["GOOGLE_API_KEY"], temperature=0.1)
    llm = GoogleGenerativeAI(model="models/text-bison-001", google_api_key=os.environ["GOOGLE_API_KEY"], temperature=0.1)
    

    # Initialize the HuggingFace embeddings model
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    
    # Combine all few_shots examples into a single string for each example to create vectors
    to_vectorize = [" ".join(example.values()) for example in few_shots]
    
    try:
        # Create a vector store from the examples using Chroma
        vectorstore = Chroma.from_texts(to_vectorize, embeddings, metadatas=few_shots)
    except Exception as e:
        # Print error and raise exception if vector store creation fails
        print("Error creating vector store:", e)
        raise

    # Initialize the example selector using semantic similarity
    example_selector = SemanticSimilarityExampleSelector(
        vectorstore=vectorstore,
        k=2,
    )

    # Define the MySQL prompt template (shortened for brevity)
    mysql_prompt = """You are a Sqlite expert..."""

    # Define the template for each example in the few-shot prompt
    example_prompt = PromptTemplate(
        input_variables=["Question", "SQLQuery", "SQLResult", "Answer"],
        template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}",
    )

    # Define the few-shot prompt template using the example selector and example prompt
    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=mysql_prompt,
        suffix=PROMPT_SUFFIX,
        input_variables=["input", "table_info", "top_k"],
    )

    # Create an SQLDatabaseChain with the few-shot prompt and return it
    chain = SQLDatabaseChain.from_llm(llm, db, verbose=True, prompt=few_shot_prompt)
        
    return chain
