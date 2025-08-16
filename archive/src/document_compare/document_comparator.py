import sys
from dotenv import load_dotenv
import pandas as pd
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompt.prompty_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser

class DocumentComperatorLLM:
    def __init__(self):
        load_dotenv()
        self.log = CustomLogger().get_logger(__name__)
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
        self.prompt = PROMPT_REGISTRY["document_comparision"]
        self.chain = self.prompt | self.llm | self.parser 
        self.log.info("DocumentCompareatorLLM is initialized successfully !")

    def compare_documents(self,combined_docs:str)->pd.DataFrame:
        """
        Compares two documents and returns a structured comparision
        """
        try:
            inputs={
                "combined_docs" : combined_docs,
                "format_instruction":self.parser.get_format_instructions()
            }

            # self.log.info("starting document comparision",inputs=inputs)
            print("-",30)
            print(inputs)
            print("-",30)
            response = self.chain.invoke(inputs)
            return self._format_response(response)

        except Exception as e:
            self.log.error(f"Error fromatting response into datagram {e}")
            raise DocumentPortalException("an error raised",sys)
        
    def _format_response(self,response_parsed:list[dict])->pd.DataFrame:
        """
        Formats the response from the LLM into a structured format
        """
        try:
            df=pd.DataFrame(response_parsed)
            return df
        except Exception as e:
            self.log.error(f"Error fromatting response into datagram {e}")
            raise DocumentPortalException("an error raised",sys)
