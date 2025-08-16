import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
import  fitz
class DocumentIngestion:
    """
    Handles saving, reading, and combining of PDFs for comparison with session-based versioning.
    """
    def __init__(self,base_dir:str="data\\document_compare",session_id=None):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True,exist_ok=True)
        self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path = self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)
        #self.log.info("DocumentComparator initialized", session_path=str(self.session_path))

    def delete_existing_files(self):
        """
        Deletes existing files at the specified paths
        """
        try:
            pass
        except Exception as e:
            self.log.error(f"error reading PDF: {e}")
            raise DocumentPortalException("An error occuring while read pdf",sys)
        
    def save_uploaded_files(self,reference_file,actual_file):
        """
        Saves uploaded file to specific directory
        """
        try:
            self.delete_existing_files()
            #self.log.info("Existing files deleted successfully")
            
            # ref_path =self.base_dir  / reference_file.name
            # act_path=self.base_dir / actual_file.name
            ref_path =self.session_path  / reference_file.name
            act_path=self.session_path / actual_file.name


            if not reference_file.name.endswith("pdf"):
                raise DocumentPortalException("its not pdf file",sys)

            with open(ref_path,"wb") as f:
                f.write(reference_file.getbuffer())
            with open(act_path,"wb") as f:
                f.write(actual_file.getbuffer())
            self.log.info("file saved")
            return ref_path,act_path

        except Exception as e:
            #self.log.error(f"error reading PDF: {e}")
            
            raise DocumentPortalException("An error occuring while read pdf",sys)
        
    def read_pdf(self,pdf_path):
        """
        Reads a pdf and extract content from each page
        """
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted: {pdf_path.name}")
                all_text =[]
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()  #type: ignore
                    if text.strip():
                        all_text.append(f"\n -- Page {page_num+1} ----\n {text}")
                # self.log.info("PDF read successfully",file=str(pdf_path), pages=len(all_text))
                return "\n".join(all_text)

        except Exception as e:
            self.log.error(f"error reading PDF: {e}")
            raise DocumentPortalException("An error occuring while read pdf",sys)
        
    def combine_documents(self)->str:
        try:
            content_dict ={}
            doc_parts=[]
            for filename in sorted(self.base_dir.iterdir()):
                if filename.is_file() and filename.suffix == ".pdf":
                    content_dict[filename.name]=self.read_pdf(filename)

            for filename,content in content_dict.items():
                doc_parts.append(f"Docuement: {filename} \n {content}")

            combined_text = "\n\n".join(doc_parts)
            return combined_text

        except Exception as e:
            self.log.error(f"Error comibining documents: {e}")
            raise DocumentPortalException("An error occured while combine document",sys)

    def clean_old_sessions(self, keep_latest: int = 3):
        """
        Optional method to delete older session folders, keeping only the latest N.
        """
        try:
            session_folders = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()],
                reverse=True
            )
            for folder in session_folders[keep_latest:]:
                for file in folder.iterdir():
                    file.unlink()
                folder.rmdir()
                self.log.info("Old session folder deleted", path=str(folder))

        except Exception as e:
            self.log.error("Error cleaning old sessions", error=str(e))
            raise DocumentPortalException("Error cleaning old sessions", sys)