import trafilatura
import gc
import time
from llama_cpp import Llama

def fetch_clean_news(url):
    print(f"--- Scraping: {url} ---")
    downloaded = trafilatura.fetch_url(url)
    # This extract call automatically finds the main body and strips the junk
    text = trafilatura.extract(downloaded)
    return text

def run_auditor(raw_news_text):
    print("--- Spinning up Auditor (Qwen) ---")
    llm = Llama(model_path="./Qwen2.5-3B-Instruct-Q4_K_M.gguf", n_gpu_layers=-1, n_ctx=4096, verbose=False)
    
    # We use Qwen's specific ChatML format for better accuracy
    prompt = f"<|im_start|>system\nExtract facts only. Remove all bias and adjectives.<|im_end|>\n<|im_start|>user\n{raw_news_text}<|im_end|>\n<|im_start|>assistant\n"
    
    response = llm(prompt, max_tokens=1024, stop=["<|im_end|>"])
    result = response["choices"][0]["text"]
    
    llm.close()
    del llm
    gc.collect()
    return result

def run_creative(facts):
    print("--- Spinning up Creative (Llama) ---")
    llm = Llama(model_path="./Llama-3.2-3B-Instruct-Q4_K_M.gguf", n_gpu_layers=-1, n_ctx=4096, verbose=False)
    
    # Llama 3.2 uses a different prompt template
    prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nWrap these facts into a professional broadcast script for 'The Scale'.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{facts}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    
    response = llm(prompt, max_tokens=1024, stop=["<|eot_id|>"])
    result = response["choices"][0]["text"]
    
    llm.close()
    del llm
    gc.collect()
    return result

# --- EXECUTION ---
if __name__ == "__main__":
    # This lets you paste the URL in the terminal at 3 AM without editing the file
    target_url = input("Paste the news URL here: ").strip()
    
    if not target_url:
        print("No URL provided. Exiting.")
    else:
        raw_article = fetch_clean_news(target_url)

        if raw_article:
            audited_facts = run_auditor(raw_article)
            
            print("\n" + "-"*30)
            print("AUDITED FACTS (THE TRUTH):")
            print(audited_facts)
            print("-"*30 + "\n")
            
            final_broadcast = run_creative(audited_facts)
            
            print("\n" + "="*30)
            print("FINAL 'THE SCALE' BROADCAST:")
            print("="*30)
            print(final_broadcast)
        else:
            print("Error: Could not extract text from that URL. It might be blocked or empty.")