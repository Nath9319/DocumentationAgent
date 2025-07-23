# run_template_compression.py

import importlib.util
import os
import sys
from prompt_compression import SemanticCompressor

# Load templates.py dynamically
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), 'prompts', 'templates.py')

spec = importlib.util.spec_from_file_location("templates", TEMPLATE_PATH)
templates_module = importlib.util.module_from_spec(spec)
sys.modules["templates"] = templates_module
spec.loader.exec_module(templates_module)

compressor = SemanticCompressor()

def summarize(text, max_len=300):
    return text[:max_len].strip().replace('\n', ' ') + ('...' if len(text) > max_len else '')

# Loop through all uppercase variables (your prompt templates)
for name in dir(templates_module):
    if name.isupper() and name.endswith("_TEMPLATE"):
        raw_prompt = getattr(templates_module, name)

        result = compressor.compress(raw_prompt)

        print("=" * 80)
        print(f" TEMPLATE: {name}")
        print(f" Original length: {result.original_length}")
        print(f" Compressed length: {result.compressed_length}")
        print(f" Compression ratio: {result.compression_ratio:.2%}")
        print(f" Techniques applied: {result.metadata.get('techniques_applied')}")
        print("\n Before:\n", summarize(raw_prompt))
        print("\n After:\n", summarize(result.compressed_prompt))
        print("=" * 80 + "\n\n")
