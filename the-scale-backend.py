import json
import gc
import time
import trafilatura
from llama_cpp import Llama

# 1. LOAD CONFIGURATION
# This pulls your Truth & Empathy prompts from config.json
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print("Error: config.json not found! Please create it in the same folder.")
    exit()

def fetch_clean_news(url):
    print(f"\n[SCALING] Accessing: {url}")
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        return text
    except Exception as e:
        print(f"Scraping Error: {e}")
        return None

def run_auditor(raw_news_text):
    cfg = config["models"]["auditor"]
    print(f"--- Loading Auditor ({cfg['name']}) to RTX 3050 ---")
    
    # n_gpu_layers=-1 ensures the 3050 handles the work
    llm = Llama(
        model_path=cfg["path"], 
        n_gpu_layers=-1, 
        n_ctx=4096, 
        verbose=False
    )
    
    # Format the ChatML prompt from config
    prompt = cfg["template"].format(system=cfg["system_prompt"], input=raw_news_text)
    
    response = llm(prompt, max_tokens=1024, stop=["<|im_end|>"])
    result = response["choices"][0]["text"]
    
    # KILL MODEL & CLEAR VRAM
    llm.close()
    del llm
    gc.collect()
    time.sleep(2) # Give the GPU a breath
    return result

def run_creative(facts):
    cfg = config["models"]["creative"]
    print(f"--- Loading Creative ({cfg['name']}) to RTX 3050 ---")
    
    llm = Llama(
        model_path=cfg["path"], 
        n_gpu_layers=-1, 
        n_ctx=4096, 
        verbose=False
    )
    
    # Format the Llama prompt from config
    prompt = cfg["template"].format(system=cfg["system_prompt"], input=facts)
    
    response = llm(prompt, max_tokens=1024, stop=["<|eot_id|>"])
    result = response["choices"][0]["text"]
    
    # FINAL VRAM CLEANUP
    llm.close()
    del llm
    gc.collect()
    return result

# --- AUTOMATED EXECUTION LOOP ---
if __name__ == "__main__":
    # Add your URLs here to process them all at once
    watch_list = [
        "https://democracyforward.org/news/press-releases/federal-court-blocks-significant-pieces-of-administrations-sweeping-immigration-appeals-rule-that-eliminates-meaningful-judicial-review/",
        "https://nationaltoday.com/us/ny/new-york/news/2026/02/22/apple-news-accused-of-excluding-conservative-outlets/"
    ]

    print(f"Starting {config['project']} v{config['version']}...")
    
    for url in watch_list:
        article_text = fetch_clean_news(url)
        
        if article_text:
            # Stage 1: Audit
            audited_facts = run_auditor(article_text)
            
            # Stage 2: Create
            final_broadcast = run_creative(audited_facts)
            
            # OUTPUT TO CONSOLE
            print("\n" + "="*50)
            print(f"THE SCALE BROADCAST | SOURCE: {url}")
            print("="*50)
            print(final_broadcast)
            print("="*50 + "\n")
            
            # Pause to prevent overheating/overloading
            print("Target complete. Resting VRAM for 10 seconds...")
            time.sleep(10)
        else:
            print(f"Skipping {url} - No content found.")

    print("\nAll watch-list items processed. Backend standing by.")