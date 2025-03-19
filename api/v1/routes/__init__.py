from fastapi import APIRouter

api_version_one = APIRouter()

from .table_question_answering import router
from .tagging_agent import fourth_ir_tagging_agent
from .backend_builder import backend_builder
from .currency_converter import currency_converter
from .doc_splitter import doc_splitter
from .doc_splitter_2 import doc_splitter_2
from .dynamic_scrapper import dynamic_scrapper
from .excel_translator import excel_translator
from .lead_enrichment import lead_enrichment
from .lead_identifier import lead_identifier
from .sales_outreach import sales_outreach_router
from .screening_analyst import screening_analyst
from .data_cleaning import data_cleaning


api_version_one.include_router(router)
api_version_one.include_router(fourth_ir_tagging_agent)
api_version_one.include_router(backend_builder)
api_version_one.include_router(currency_converter)
api_version_one.include_router(doc_splitter)
api_version_one.include_router(doc_splitter_2)
api_version_one.include_router(dynamic_scrapper)
api_version_one.include_router(excel_translator)
api_version_one.include_router(lead_enrichment)
api_version_one.include_router(lead_identifier)
api_version_one.include_router(sales_outreach_router)
api_version_one.include_router(screening_analyst)
api_version_one.include_router(data_cleaning)