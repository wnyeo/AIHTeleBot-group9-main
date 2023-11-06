import os
import openai
import sys
import numpy as np
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain

load_dotenv('./.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
loader = PyPDFDirectoryLoader("./docs/")
pages = loader.load()
print("successfully loaded PDFs")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len
)

splits = text_splitter.split_documents(pages)

print("successfully split documents")


def getResponse(question: str) -> str:
    """
    A repeated implementation of the langchain code in Week 5
    This code is purposely built to be inefficient! 
    Refer to project requirements and Week 5 Lab if you need help
    """


    # Your experiment can start from this code block which loads the vector store into variable vectordb
    embedding = OpenAIEmbeddings()

    # Reference https://github.com/hwchase17/chroma-langchain/blob/master/persistent-qa.ipynb
    persist_directory = './docs/vectordb'

    # Perform embeddings and store the vectors
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        persist_directory=persist_directory
    )
    print("successfully created vector store")

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        input_key='question',
        output_key='answer'
    )

    # Code below will enable tracing so we can take a deeper look into the chain
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.langchain.plus"
    os.environ["LANGCHAIN_PROJECT"] = "Chatbot"

    # Define parameters for retrival
    retriever=vectordb.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": .5, "k": 2})

    # Define llm model

    llm_name = "gpt-3.5-turbo-16k"
    llm = ChatOpenAI(model_name=llm_name, temperature=0)
    # Define template prompt
    template = """You are a friendly chatbot that helps to answer queries of volunteers serving migrant workers in Singapore.
    Use the following pieces of context to answer the question at the end.
    {context}
    Question: {question}
    Helpful Answer:"""

    your_prompt = PromptTemplate.from_template(template)

    # Execute chain
    qa = ConversationalRetrievalChain.from_llm(
        llm,
        combine_docs_chain_kwargs={"prompt": your_prompt},
        retriever=retriever,
        return_source_documents=True,
        return_generated_question=True,
        memory=memory
    )

    # Evaluate your chatbot with questions
    result = qa({"question": question})

    print(result)
    return result['answer']