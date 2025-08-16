from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from prompt.prompty_library import PROMPT_REGISTRY
from model.models import PromptyType
from utils.model_loader import ModelLoader

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage
from langchain_community.vectorstores import FAISS

import os
import sys
from operator import itemgetter
from typing import List, Optional

class ConverstationalRAG:
    def __init__(self,session_id:str, retriever=None):
        try:    
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.llm = self._load_llm()
            self.contextualize_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptyType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptyType.CONTEXT_QA.value]
            if retriever is None:
                raise ValueError("Retriever cannot be None")
            self.retriever = retriever
            self._build_lcel_chain()
            self.log.info("ConversationalRAG initialized", session_id=self.session_id)
        except Exception as e:
            raise DocumentPortalException("Error while initialize converstaionalRAG",sys)
        


    def load_retriever_from_faiss(self,index_path):
        """
        Load a FAISS vectorstore from disk and convert to retriever
        """
        try:
            embeddings= ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found {index_path}")
            vectorstore = FAISS.load_local(
                index_path,
                embeddings,
                allow_dangerous_deserialization=True,  # only if you trust the index
            )
            self.retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            self.log.info("FAISS retriever loaded successfully", index_path=index_path, session_id=self.session_id)
            return self.retriever
            
        except Exception as e:
            pass

    def invoke(self,user_input:str, chat_history:Optional[List[BaseMessage]]=None)->str:
        """
        Args:
            user_input (str): _description_
            chat_history (Optional[List[BaseMessage]], optional): _description_. Defaults to None.
        """        
        chat_history = chat_history or []
        payload= {"input":user_input, "chat_history":chat_history}
        try:
            answer = self.chain.invoke(payload)
        except Exception as e:
            print(f"while inoke=======>{str(e)}")
            return "no answer generated."

        if not answer:
            self.log.warning("No answer generator")
            return "no answer generated"
        
        self.log.info("Chain invoked successully")

        return answer


    def _load_llm(self):
        try:
            llm= ModelLoader().load_llm()
            if not llm:
                raise ValueError("LLM could not be loaded")
            self.log.info("LLM loaded successfully")
            return llm
        except Exception as e:
            self.log.error(f"Failed to load LLM {str(e)}")

    @staticmethod
    def _format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    def _build_lcel_chain(self):
        try:
            # 1) Rewrite question using chat history
            question_rewriter = (
                    {"input":itemgetter("input"), "chat_history":itemgetter("chat_history")}
                    | self.contextualize_prompt
                    | self.llm
                    | StrOutputParser()

            )
            # 2) Retrieve docs fro rewritten question
            retrieve_docs = question_rewriter | self.retriever | self._format_docs
            
            #LangChain Expression Language (lcel)
            # 3) Feed context + original input + chat history into answer prompt
            self.chain = (
                {
                    "context":retrieve_docs,
                    "input":itemgetter("input"),
                    "chat_history":itemgetter("chat_history")
                }
                |self.qa_prompt
                |self.llm
                |StrOutputParser()
            )

            self.log.info(f"LCEL graph build successfully session_id={self.session_id}")

        except Exception as e:
            self.log.error(f"Failed to build LCEL chain {str(e)}")
            raise DocumentPortalException(f"Failed to build LCEL chain",sys)



