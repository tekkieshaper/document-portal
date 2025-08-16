
import os
import sys
from  dotenv import load_dotenv

from langchain_core.chat_history import BaseChatMessageHistory
#from langchain.chains import create_history
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import streamlit as st


from logger.custom_logger import CustomLogger
from utils.model_loader import ModelLoader
from prompt.prompty_library import PROMPT_REGISTRY
from model.models import PromptyType

from exception.custom_exception import DocumentPortalException

class ConversationalRAG:
    def __init__(self,session_id:str,retriever):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.retriever = retriever
            self.llm = self._load_llm()
            self.contextualize_prompt = PROMPT_REGISTRY[PromptyType.CONTEXTUALIZE_QUESTION.value]  #one more level of validation
            self.qa_prompt = PROMPT_REGISTRY[PromptyType.CONTEXT_QA.value]
            self.history_aware_retriver = create_history_aware_retriever(self.llm, self.retriever, self.contextualize_prompt)    
            #self.log.info("Created history-aware retriever",session_id= session_id)
            self.qa_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
            self.rag_chain = create_retrieval_chain(self.history_aware_retriver, self.qa_chain)
            self.chain = RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer"
            )

        except Exception as e:
            self.log.error("failed to initialize singledocingestor error=str(e)")
            raise DocumentPortalException("initialization error in singledocingestor|",sys)

    def _load_llm(self):
        try:
            print("instie _load_llm")
            llm = ModelLoader().load_llm()
            return llm
        except Exception as e:
            self.log.error("failed to load_llm error=str({e})")
            raise DocumentPortalException("initialization error in load_llm",sys)


    def _get_session_history(self,session_id:str) -> BaseChatMessageHistory:
        try:
            if "store" not in st.session_state:
                st.session_state.store = {}

            if session_id not in st.session_state.store:
                st.session_state.store[session_id] = ChatMessageHistory()
                self.log.info("New chat session history created session_id {session_id}")

            return st.session_state.store[session_id]

        except Exception as e:
            self.log.error(f"failed to get session history session_id= {session_id} error={str(e)}")
            raise DocumentPortalException("exception while  to get session history",sys)


    def load_retriever_from_faiss(self,index_path:str):
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")

            vectorestor = FAISS.load_local(index_path, embeddings=embeddings)
            return vectorestor.as_retriever(search_type="similarity", search_kwargs={"k":5})
        
        except Exception as e:
            self.log.error("failed to from faiss",error=str(e))
            raise DocumentPortalException("exception while  retrieve from faiss",sys)

    def invoke(self,user_input:str)->str:
        try:
            response = self.chain.invoke(
                {"input":user_input},
                config={"configurable":{"session_id":self.session_id}})
                
            answer = response.get("answer", "No answer.")

            if not answer:
                self.log.warning(f"Empty answer received session_id={self.session_id}")

            # self.log.info("Chain invoked successfully", session_id=self.session_id, user_input=user_input, answer_preview=answer[:150])
            return answer

        except Exception as e:
            self.log.error(f"failed to invoke conversational RAG error={str(e)}")
            raise DocumentPortalException("exception while  retrieve from faiss",sys)

# starts from _ is private