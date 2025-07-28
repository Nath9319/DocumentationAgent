import os
import json
import pickle
import networkx as nx
import asyncio
import logging
import re
import sys
from datetime import datetime
from typing import TypedDict, List, Dict, Optional
from dotenv import load_dotenv
# --- tqdm for progress bar ---
from tqdm import tqdm
import threading
from datetime import datetime, timedelta  # timedelta is new, datetime already exists
import asyncio  # if not already imported
from diagrams import Diagram
from diagrams.programming.language import Python
from diagrams.generic.compute import Rack

# Much cleaner code, better visuals

# Set UTF-8 encoding for Windows console to handle emojis
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Load environment variables from .env file
load_dotenv()

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.output_parsers.json import JsonOutputParser
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, END
import sys
# --- Custom StreamHandler to handle UTF-8 encoding ---
class StreamHandlerUTF8(logging.StreamHandler):
    def __init__(self, stream=None):
        if stream is None:
            stream = sys.stdout
        # Wrap the stream with UTF-8 encoding if possible
        try:
            stream = open(stream.fileno(), mode='w', encoding='utf-8', buffering=1)
        except Exception:
            pass  # fallback to default if not possible
        super().__init__(stream)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('documentation_generation.log', encoding='utf-8'),
        StreamHandlerUTF8()
    ]
)
logger = logging.getLogger(__name__)

# --- Create output directory for incremental saves ---
INCREMENTAL_SAVE_DIR = "incremental_saves"
os.makedirs(INCREMENTAL_SAVE_DIR, exist_ok=True)

# --- Global progress bar variable ---
progress_bar = None

# --- 1. Environment Setup & Model Initialization ---
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-01"),
    temperature=0.1, # Increased for more creative and better-structured writing
    # max_tokens=40000
)