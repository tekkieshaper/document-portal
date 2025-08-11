from logger.custom_logger import CustomLogger
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from datetime import datetime,timezone

import sys
import uuid
from  pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader

class DocumentIngestor:
    
    SUPPORTED_FILE_TYPES = {".pdf",".docx",".txt",".md"}  #mark down file

    def __init__(self,temp_dir:str="data/multi_doc_chat", faiss_dir:str ="faiss_index",session_id: str | None = None):
        
        print("inside DocumentIngestor")
        try:
            self.log = CustomLogger().get_logger(__name__)


            self.temp_dir = Path(temp_dir)
            self.faiss_dir = Path(faiss_dir)
            self.temp_dir.mkdir(parents=True,exist_ok=True)
            self.faiss_dir.mkdir(parents=True,exist_ok=True)

            #session paths
            self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_temp_dir = self.temp_dir / self.session_id
            self.session_faiss_dir = self.faiss_dir / self.session_id
            self.session_temp_dir.mkdir(parents=True, exist_ok=True)
            self.session_faiss_dir.mkdir(parents=True, exist_ok=True)
            
            self.model_loader = ModelLoader()
            self.log.info(
                "DocumentIngestor initialized",
                temp_base=str(self.temp_dir),
                faiss_base=str(self.faiss_dir),
                session_id=self.session_id,
                temp_path=str(self.session_temp_dir),
                faiss_path=str(self.session_faiss_dir),
            )
        except Exception as e:
            self.log.error(f"error while initialize DocumentIngestor {str(e)}")
            raise DocumentPortalException("Ingestion initialization failed",sys)
            

    def ingest_file(self,uploaded_files):
        try:
            for uploaded_file in uploaded_files:
                print(f" {'###'*10} {uploaded_file} {'##'*10}")
                ext = Path(uploaded_file.name).suffix.lower()
                print(f"ext ===> {ext}")
                      
            documents=[]

            for uploaded_file in uploaded_files:
                ext = Path(uploaded_file.name).suffix.lower()
                if ext not in self.SUPPORTED_FILE_TYPES:
                    print(f"not supported... continue another file")
                    self.log.warning(f"Unsupported file skipped.  Checking next file..." )
                    continue
                
                unique_filename = f"{uuid.uuid4().hex[:8]}{ext}"
                temp_path = self.session_temp_dir / unique_filename


                with open(temp_path,"wb") as f:
                    f.write(uploaded_file.read())
                self.log.info(f"file saved for ingestion file name ={uploaded_file}")

                if ext ==".pdf":
                    print(f"{'*' * 50} PDF Loaded.  PDF File name => {temp_path}")
                    loader = PyPDFLoader(str(temp_path))
                elif ext ==".docx":
                    print(f"{'*' * 50} doc file name => {temp_path}")
                    loader = Docx2txtLoader(str(temp_path))
                elif ext ==".txt":
                    print(f"{'*' * 50} text file name => {temp_path}")
                    loader = TextLoader(str(temp_path),encoding="utf-8")
                else:
                    self.log.warning("Unsupported file type encountered")
                    continue
                    
                docs = loader.load()
                documents.extend(docs)

                if not docs:
                    raise DocumentPortalException("No valid document loaders",sys)
                
                self.log.info(f"all documents loaded. Total docs ={len(documents)} session_id = ")

            return self._create_retriever(documents)

        except Exception as e:
            print(f"error {str(e)}")
            self.log.err(f"failed to ingest files {str(e)}")
            raise DocumentPortalException("ingestion error in documentingestor",sys)

    def _create_retriever(self, documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=300)
            chunks = splitter.split_documents(documents)

            embeddings= self.model_loader.load_embeddings()
            vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
            
            #save FAISS index under session folder
            vectorstore.save_local(str(self.session_faiss_dir))
            self.log.info(f"FAISS index saved to disk. path={self.session_faiss_dir}, session_id={self.session_id}")

            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k":5})

            self.log.info(f"FAISS retriever created and ready to use session_id={self.session_id}")
            return retriever

        except Exception as e:
            self.log.error("failed to get retriever")
            raise DocumentPortalException("Retrieval error in documentingestor",sys)
            
