import os
import fitz
import uuid
from datetime import  datetime
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException


class DocumentHandler:
    """
    Handles Pdf document read and save operations
    Automatically logs all actions and support session-based organizations
    """

    def __init__(self,data_dir=None, session_id=None):
        try:
            self.log = CustomLogger().get_logger(__file__)
            self.data_dir = data_dir or os.getenv(
                "DATA_STORAGE_PATH",
                os.path.join(os.getcwd(),"data","document_analysis")
            )
            self.session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_path = os.path.join(self.data_dir, self.session_id)
            os.makedirs(self.session_path,exist_ok=True)

            self.log.info(f"PDFHander initialized {self.session_id}, {self.data_dir}, {self.session_path}")

        except Exception as e:
            self.log.error(f"Error while initialize DocumentHandler. {e}")
            raise DocumentPortalException(f"Error while initialize DocumentHandler {e}")
        
    def save_pdf(self, uploaded_file):
        try:
            file_name = os.path.basename(uploaded_file.name)

            if not file_name.lower().endswith("pdf"):
                raise DocumentPortalException(f"Its not valid PDF documennt")
            
            save_path = os.path.join(self.session_path,file_name)

            with open(save_path,"wb") as f:
                f.write(uploaded_file.getbuffer())
            
            self.log.info(f"PDF saved successfully filename={file_name}, save_path={save_path}, session_id={self.session_id}")

            return save_path
        
        except Exception as e:
            self.log.error(f"eror whle save pdf {e}")
            raise DocumentPortalException(f"error while save pdf")
        
    def read_pdf(self,pdf_path)-> str:
        try:
            text_chunks=[]

            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc, start=1):
                    text_chunks.append(f"\n-- Page {page_num} --\n {page.get_text()}")
            text = "\n".join(text_chunks)
            return text
        except Exception as e:
            self.log.error(f"error whle reading pdf file {pdf_path}");
            raise DocumentPortalException(f"error while reading pdf file {pdf_path}")
        
    if __name__=="__main__":
        from pathlib import Path
        