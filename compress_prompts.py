from llmlingua import PromptCompressor

# --- INPUT EXAMPLES (Customize as per your data) ---
prompt_list = [
    "This module calculates age based on the given date of birth.",
    "It uses the datetime module to parse and compare dates.",
    "Supports formats: DD-MM-YYYY and YYYY-MM-DD.",
]
question = "How does this module handle date parsing?"

# --- 1. Using LongLLMLingua ---
def use_long_llmlingua(prompt_list, question):
    print("\n--- Using LongLLMLingua ---\n")
    llm_lingua = PromptCompressor()

    compressed = llm_lingua.compress_prompt(
        prompt_list,
        question=question,
        rate=0.55,
        condition_in_question="after_condition",
        reorder_context="sort",
        dynamic_context_compression_ratio=0.3,
        condition_compare=True,
        context_budget="+100",
        rank_method="longllmlingua",
    )

    print("Compressed Prompt (LongLLMLingua):\n", compressed)
    return compressed


# --- 2. Using LLMLingua-2 (large model) ---
def use_llmlingua2_large(prompt):
    print("\n--- Using LLMLingua-2 Large ---\n")
    llm_lingua = PromptCompressor(
        model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
        use_llmlingua2=True,
    )

    compressed = llm_lingua.compress_prompt(prompt, rate=0.33, force_tokens=['\n', '?'])
    print("Compressed Prompt (LLMLingua-2 Large):\n", compressed)
    return compressed


# --- 3. Using LLMLingua-2 (small model) ---
def use_llmlingua2_small(prompt):
    print("\n--- Using LLMLingua-2 Small ---\n")
    llm_lingua = PromptCompressor(
        model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
        use_llmlingua2=True,
    )

    compressed = llm_lingua.compress_prompt(prompt, rate=0.33, force_tokens=['\n', '?'])
    print("Compressed Prompt (LLMLingua-2 Small):\n", compressed)
    return compressed


# --- MAIN FUNCTION ---
if __name__ == "__main__":
    # LongLLMLingua: Takes list of context strings + question
    compressed_long = use_long_llmlingua(prompt_list, question)

    # LLMLingua-2: Takes single prompt string
    long_prompt = "\n".join(prompt_list) + "\n" + question

    compressed_ll2_large = use_llmlingua2_large(long_prompt)
    compressed_ll2_small = use_llmlingua2_small(long_prompt)
