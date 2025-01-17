import os
import pickle
import time
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from langchain_openai import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv
import json

load_dotenv()  # take environment variables from .env (especially openai api key)

file_path = "faiss_store_openai.pkl"
llm = OpenAI(temperature=0.9, max_tokens=500)

@csrf_exempt
@require_http_methods(["POST"])
def process_urls(request):
    try:
        data = json.loads(request.body)
        urls = data.get('urls', [])
        
        if not urls:
            return HttpResponseBadRequest("No URLs provided.")

        # load data
        loader = UnstructuredURLLoader(urls=urls)
        loaded_data = loader.load()

        # split data
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ','],
            chunk_size=1000
        )
        docs = text_splitter.split_documents(loaded_data)

        # create embeddings and save it to FAISS index
        embeddings = OpenAIEmbeddings()
        vectorstore_openai = FAISS.from_documents(docs, embeddings)

        # Save the FAISS index to a pickle file
        with open(file_path, "wb") as f:
            pickle.dump(vectorstore_openai, f)

        return JsonResponse({"message": "URLs processed successfully."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ask_question(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '')

        if not question:
            return HttpResponseBadRequest("No question provided.")

        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                vectorstore = pickle.load(f)
                chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())
                result = chain({"question": question}, return_only_outputs=True)
                # result will be a dictionary of this format --> {"answer": "", "sources": [] }
                
                response = {
                    "answer": result.get("answer", ""),
                    "sources": result.get("sources", "")
                }
                return JsonResponse(response)
        else:
            return JsonResponse({"error": "FAISS index file not found."}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
