
from pydantic import BaseModel, Field, RootModel
from typing import List, Union
from enum import Enum

class MetaData(BaseModel):
    Summary: List[str] = Field(description="summary of the document",default_factory=list)
    Title: str
    Author:str
    DateCreated:str
    LastModifiedDate:str
    Publisher:str
    Language:str
    PageCount:Union[int,str]
    SentimentTone:str


class ChangeFormat(BaseModel):
    Page:str
    Changes:str

class SummaryResponse(RootModel[list[ChangeFormat]]):
    pass

class PromptyType(str,Enum):
    DOCUMENT_ANALYSIS ="document_analysis"
    DOCUMENT_COMPARISION ="document_comparison"
    CONTEXTUALIZE_QUESTION ="contextualize_question"
    CONTEXT_QA = "context_qa"