import os
import json
import gc
import time
import trafilatura
from llama_cpp import Llama

# 1. THE MASTER LOADER
def load_hnn_engine():
    config_dir = "configs"
    master_config = {}
    config_files = [
        "system_config.json", 
        "lanes_config.json", 
        "persona_config.json", 
        "templates_config.json"
    ]
    
    for filename in config_files:
        path = os.path.join(config_dir, filename)
        try:
            with open(path, "r") as f:
                master_config.update(json.load(f))
        except FileNotFoundError:
            print(f"CRITICAL: {filename} missing from /configs folder!")
            exit(1)
    return master_config

# Initialize Global Config
config = load_hnn_engine()

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
    # Pulling from system_config.json and templates_config.json
    cfg = config["models"]["auditor"]
    tmpl = config["templates"]["auditor_v1"]
    
    print(f"--- Loading Auditor ({cfg['name']}) ---")
    
    llm = Llama(
        model_path=cfg["path"], 
        n_gpu_layers=cfg["n_gpu_layers"], 
        n_ctx=cfg["n_ctx"], 
        verbose=False
    )
    
    # Using the prompt template and the persona logic
    prompt = tmpl["format"].format(
        system=config["behavioral_anchors"]["truth_filter"], 
        input=raw_news_text
    )
    
    response = llm(prompt, max_tokens=1024, stop=["<|im_end|>"])
    result = response["choices"][0]["text"]
    
    llm.close()
    del llm
    gc.collect()
    time.sleep(config["hardware_throttling"]["vram_cooldown_seconds"]) 
    return result

def run_creative(facts):
    # Pulling from system_config.json and templates_config.json
    cfg = config["models"]["creative"]
    tmpl = config["templates"]["creative_hnn_standard"]
    
    print(f"--- Loading Creative ({cfg['name']}) ---")
    
    llm = Llama(
        model_path=cfg["path"], 
        n_gpu_layers=cfg["n_gpu_layers"], 
        n_ctx=cfg["n_ctx"], 
        verbose=False
    )
    
    prompt = tmpl["format"].format(
        system=config["behavioral_anchors"]["empathy_filter"], 
        input=facts
    )
    
    response = llm(prompt, max_tokens=1024, stop=["<|eot_id|>"])
    result = response["choices"][0]["text"]
    
    llm.close()
    del llm
    gc.collect()
    return result

# --- AUTOMATED EXECUTION LOOP ---
if __name__ == "__main__":
    watch_list = [
        "https://democracyforward.org/news/press-releases/federal-court-blocks-significant-pieces-of-administrations-sweeping-immigration-appeals-rule-that-eliminates-meaningful-judicial-review/",
        "https://nationaltoday.com/us/ny/new-york/news/2026/02/22/apple-news-accused-of-excluding-conservative-outlets/"
    ]

    print(f"Starting {config['project']} v{config['version']}...")
    
    for url in watch_list:
        article_text = fetch_clean_news(url)
        
        if article_text:
            audited_facts = run_auditor(article_text)
            final_broadcast = run_creative(audited_facts)
            
            print("\n" + "="*50)
            print(f"THE SCALE BROADCAST | SOURCE: {url}")
            print("="*50)
            print(final_broadcast)
            print("="*50 + "\n")
            
            # Using the hardware_throttling value from system_config.json
            wait_time = config["hardware_throttling"]["batch_cooldown_seconds"]
            print(f"Target complete. Resting for {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print(f"Skipping {url} - No content found.")

    print("\nAll watch-list items processed. Backend standing by.")