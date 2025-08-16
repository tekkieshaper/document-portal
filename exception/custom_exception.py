import sys
import traceback
from logger.custom_logger import CustomLogger
from typing import Optional, cast
logger=CustomLogger().get_logger(__file__)

class DocumentPortalException(Exception):
    """Custom exception for Document Portal"""
    def __init__(self,error_message,error_details:Optional[object]=None):

        #Normalize message
        if isinstance(error_message, BaseException):
            norm_msg = str(error_message)
        else:
            norm_msg = str(error_message)
        
        exc_type = exc_value = exc_tb = None
        if error_details is None:
            exc_type, exc_value, exc_tb = sys.exc_info()
        else:
            if hasattr(error_details, "exc_info"):
                exc_info_obj = cast(sys, error_details)                
                exc_type, exc_value, exc_tb =exc_info_obj.exc_info()
            elif isinstance(error_details,BaseException):
                exc_type, exc_value,exc_tb= type(error_details), error_details, error_details.__traceback__
            else:
                exc_type, exc_value, exc_tb = sys.exc_info()
        
        #walk to the last frame to retrieve the most relevant file from where the exception occured
        last_tb = exc_tb
        while last_tb and last_tb.tb_next:
            last_tb = last_tb.tb_next
        self.file_name = last_tb.tb_frame.f_code.co_filename if last_tb else "<unknown>"
        self.lineno = last_tb.tb_lineno if last_tb else -1
        self.error_message = norm_msg

        if exc_type and exc_tb:
            self.traceback_str = ''.join(traceback.format_exception(exc_type,exc_value,exc_tb))
        else:
            self.traceback_str = ""
        super().__init__(self.__str__())
    
    def __str__(self):
        base = f"Error in [{self.file_name}] at line [{self.lineno} | Error Message : {self.error_message}]"
        if self.traceback_str:
            return f"{base} \n Traceback: \n {self.traceback_str}"
        return base
    
    def __repr__(self):  # !r ==> make it as string constant by adding single quote. r => repr() representation
        return f"DocumentPortalException(file={self.file_name!r}, line={self.lineno}, message={self.error_message!r})"
                
    
if __name__ == "__main__":
    # Demo 1: generic exception -> wrap
    # try:
    #     a = 1 / 0
    #     print(a)
    # except Exception as e:
    #     raise DocumentPortalException("Division failed",e) from e
    
    # Demo 2 : using sys which is also supported
    try:
        a = int("hello")
    except Exception as e:
        raise DocumentPortalException(e,sys)
