import os
import sys
from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from prompt.prompty_library  import PROMPT_REGISTRY # type: ignore

class DocumentAnalyser:
    """
    Analyzes documents using a pre-trained model.
    Automatically logs all actions and supports session-based organization.
    """
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()
            self.parser = JsonOutputParser(pydantic_object=MetaData)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser,llm=self.llm)
            self.prompt = PROMPT_REGISTRY["document_analysis"]  #document_analysis_prompt
            self.log.info("DocumentAnalyzer initialization done successfully ")

        except Exception as e:
            self.log.error(f"Error initializing DocumentAnalyser : {e}")
            raise DocumentPortalException("error in DocumentAnalyzer initialization",sys)
        
    def analyze_document(self, document_text:str)->dict:
        """
        Analyze a document's text and extract structured metadata & summary
        """
        try:
            chain = self.prompt | self.llm | self.fixing_parser
            self.log.info("Meta-data analysis chain initialized")

            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text":document_text
            })
            keys= list(response.keys())
            self.log.info(f"Metadata extraction successful. keys ={keys}")
            return response

        except Exception as e:
            self.log.error(f"error while analyze_dcoument : {e}")
            raise DocumentPortalException(f"Metadata extraction failed {e}")