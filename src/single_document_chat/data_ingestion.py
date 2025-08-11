import os
import uuid
from pathlib import Path
import sys
from datetime import datetime,timezone
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
class SingleDocIngestion:
    def __init__(self,data_dir:str = "data/single_document_chat", faiss_dir:str="faiss_index"):
        try:
            self.log = CustomLogger().get_logger(__name__)
            
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True,exist_ok=True)
            
            self.modal_loader = ModelLoader()
            
            # self.log.info(f"SingleDocIngestor initialized temp_path={str(self.data_dir)},faiss_path={str(self.faiss_dir)})

        except Exception as e:
            self.log.error("failed to initialize singledocingestor",error=str(e))
            raise DocumentPortalException("initialization error in singledocingestor|",sys)


    def ingest_files(self,uploaded_files):
        try:
            documents=[] #empty list

            for uploaded_file in uploaded_files:
                #self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                unique_filename =  f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                temp_path = self.data_dir / unique_filename
                print(f"temp_path : {temp_path}\n")
                with open(temp_path,"wb") as f_out:
                    f_out.write(uploaded_file.read())
                # self.log.info(f"PDF saved for ingestion filename={uploaded_file.name}")
                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)
                
            self.log.info(f"PDF files are loaded count= {len(documents)}")
            return self._create_retriever(documents)

        except Exception as e:
            self.log.error("failed to ingest_files",error=str(e))
            raise DocumentPortalException("initialization error in singledocingestor|",sys)


    def _create_retriever(self,documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=300)
            chunks = splitter.split_documents(documents)
            self.log.info(f"Documents split into chunks count={len(chunks)}")
            embeddings = self.modal_loader.load_embeddings()
            vectorstore = FAISS.from_documents(documents=chunks,embedding=embeddings)
            vectorstore.save_local(str(self.faiss_dir))
            self.log.info(f"FAISS index created and saved faiss_path={str(self.faiss_dir)}")
            return vectorstore

        except Exception as e:
            self.log.error(f"failed to create_retriever error={str(e)}")
            raise DocumentPortalException("initialization error in create_retriever",sys)

