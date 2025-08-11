############################################
# 1.Testing code to test document analysis
#############################################
# import os
# from pathlib import Path
# from src.document_analyser.data_analysis import DocumentAnalyser
# from src.document_analyser.data_ingestion import DocumentHandler


# PDF_PATH = r"D:\\MyData\\Learnings\\AI\\LLMOps\\document_portal\\github\\document-portal\\notebook\\data\\Internal Research Memo.pdf"

# class DummyFile:
#     def __init__(self,file_path):
#         self.name = Path(file_path).name
#         self._file_path = file_path
#     def getbuffer(self):
#         return open(self._file_path,"rb").read()

# def main():
#     try:
#         print("Starting PDF ingestion....")
#         dummy_pdf = DummyFile(PDF_PATH)
#         handler = DocumentHandler(session_id="test_ingestion_analyser")
#         saved_path = handler.save_pdf(dummy_pdf)
#         print(f"PDF saved at: {saved_path} \n")

#         text_content = handler.read_pdf(saved_path)
#         print(f"Extracted text length : {len(text_content)} chars \n")

#         analyzer = DocumentAnalyser()
#         analysis_result = analyzer.analyze_document(text_content)

#         print("\n == METADATA ANALYSIS RESULT ===")
#         for key, value in analysis_result.items():
#             print(f"{key} : {value}")

#     except Exception as e:
#         print(f"Test failed : {e}")
        

# if __name__ =="__main__":
#     main()

############################################
# 2.Testing code to test document comparision
#############################################

# import io
# from pathlib import Path
# from src.document_compare.data_ingestion import DocumentIngestion
# from src.document_compare.document_comparator import DocumentComperatorLLM

# def load_fake_uploaded_file(file_path:Path):
#     return io.BytesIO(file_path.read_bytes())

# def test_compare_docuemnts():
#     ref_path = Path("D:\MyData\Learnings\AI\LLMOps\document_portal\github\document-portal\data\document_compare\\Long_Report_V1.pdf")
#     act_path = Path("D:\MyData\Learnings\AI\LLMOps\document_portal\github\document-portal\data\document_compare\\Long_Report_V2.pdf")
    
#     class FakeUpload:
#         def __init__(self,file_path:Path):
#             self.name = file_path.name
#             self._buffer =  file_path.read_bytes()

#         def getbuffer(self):
#            return self._buffer
       
#     comparator = DocumentIngestion("D:\\MyData\\Learnings\\AI\\LLMOps\\document_portal\\github\\document-portal\\data\\document_compare")
#     ref_upload = FakeUpload(ref_path)
#     act_upload = FakeUpload(act_path)
    
#     ref_file, act_file = comparator.save_uploaded_files(ref_upload, act_upload)
#     combined_text = comparator.combine_documents()
    
#     comparator.clean_old_sessions(keep_latest=3)
    
#     print("\n Combined Text Preview (First 1000 chars):\n")
#     print(combined_text[:5000])
    
#     llm_comparator = DocumentComperatorLLM()
#     comparison_df = llm_comparator.compare_documents(combined_text)
    
#     print("\n=== COMPARISON RESULT ===")
#     print(comparison_df.head())
    
# if __name__ == "__main__":
#     test_compare_docuemnts()

####################################
# 3.Testing for single document chat
####################################    
    
# import sys
# from pathlib import Path
# from langchain_community.vectorstores import FAISS
# from src.single_document_chat.data_ingestion import SingleDocIngestion
# from src.single_document_chat.retrieval import ConversationalRAG
# from utils.model_loader import ModelLoader

# FAISS_INDEX_PATH = Path("faiss_index")

# def test_converstational_rag_on_pdf(pdf_path:str, question:str):
#     try:
#         model_loader = ModelLoader()

#         if FAISS_INDEX_PATH.exists():
#             print("Loading existing FAISS index...")
#             embeddings = model_loader.load_embeddings()
#             vectorstore = FAISS.load_local(folder_path=str(FAISS_INDEX_PATH),embeddings=embeddings, allow_dangerous_deserialization=True)
#             retriever = vectorstore.as_retriever(search_type="similarity", search_kwards={"k":5})
#         else:
#             print("FAISS index not found. Ingesting PDF and creating index...")
#             with open(pdf_path,"rb") as f:
#                 uploaded_files=[f]
#                 ingestor = SingleDocIngestion()
#                 print(uploaded_files)
#                 retriever = ingestor.ingest_files(uploaded_files)
            
        
#         print("Running conversational RAG...")
#         session_id = "test_conversational_rag"
#         rag = ConversationalRAG(retriever=retriever, session_id=session_id)
#         print("after rag initiated")
#         response = rag.invoke(question)
#         print(f"Question: {question} \n Answer:{response}")


#     except Exception as e:
#         print(f"Test failed : {e}")
#         sys.exit(1)

# if __name__ =="__main__":
#     pdf_path="data\single_document_chat\\NIPS-2017-attention-is-all-you-need-Paper.pdf"
#     question="what is the main topic of the document?"

#     if not Path(pdf_path).exists():
#         print(f"PDF file doesn't exists at : {pdf_path}")
#         sys.exit(1)
#     #Run the test
#     test_converstational_rag_on_pdf(pdf_path, question=question)


####################################
# 4.Testing for multi docchat
####################################

import os, sys
from pathlib import Path
from src.multi_document_chat.data_ingestion import DocumentIngestor
from src.multi_document_chat.retrieval import ConverstationalRAG

def test_document_integstion_and_rag():
    try:
        test_files=[
            "data\\multi_doc_chat\\market_analysis_report.docx",
            "data\\multi_doc_chat\\NIPS-2017-attention-is-all-you-need-Paper.pdf",
            "data\\multi_doc_chat\\sample.pdf",
            "data\\multi_doc_chat\\state_of_the_union.txt"
        ]
        
        uploaded_files=[]
        for file_path in test_files:
            if Path(file_path).exists():
                uploaded_files.append(open(file_path,"rb"))
            else:
                print(f"File doesnt exists {file_path}")
            
        if not uploaded_files:
            print("No valid files to upload.")
            sys.exit(1)

        ingestor = DocumentIngestor()

        print("before ingest_file")

        retriever = ingestor.ingest_file(uploaded_files)

        print("after  ingest_file call")

        for f in uploaded_files:
            f.close()

        session_id="test_multi_doc_chat"

        rag=ConverstationalRAG(session_id=session_id, retriever=retriever)
        question = "what is President Zelenskyy said in their speech in parliament?"
        print("before invoke....................................")
        answer = rag.invoke(question)
        print(f"\nQuestion :{question}")
        print(f"\nAnswer :{answer}")

        if not uploaded_files:
            print("No valid files to upload.")
            sys.exit(1)


    except Exception as e:
        print(f"Test failed: {str(e)}")
        sys.exit(1)
        

if __name__ =="__main__":
    test_document_integstion_and_rag()

