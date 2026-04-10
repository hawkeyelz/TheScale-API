import os
import json
import gc
import time
import trafilatura
from llama_cpp import Llama

def load_hnn_engine():
    config_dir = "configs"
    master_config = {}
    config_files = ["system_config.json", "lanes_config.json", "persona_config.json", "templates_config.json"]
    for filename in config_files:
        with open(os.path.join(config_dir, filename), "r") as f:
            master_config.update(json.load(f))
    return master_config

class HNNInferenceEngine:
    def __init__(self, config):
        self.config = config
        self.auditor = None
        self.creative = None

    def _fetch_clean_news(self, url):
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            result = trafilatura.extract(downloaded)
            return result
        return None

    def _load_models(self):
        # Load Auditor (Qwen)
        self.auditor = Llama(
            model_path=self.config["models"]["auditor"]["path"],
            n_gpu_layers=self.config["models"]["auditor"]["n_gpu_layers"],
            n_ctx=self.config["models"]["auditor"]["n_ctx"]
        )
        # Load Creative (Llama)
        self.creative = Llama(
            model_path=self.config["models"]["creative"]["path"],
            n_gpu_layers=self.config["models"]["creative"]["n_gpu_layers"],
            n_ctx=self.config["models"]["creative"]["n_ctx"]
        )

    def generate_broadcast(self, url):
        article_text = self._fetch_clean_news(url)
        if not article_text:
            return None

        if not self.auditor or not self.creative:
            self._load_models()

        # Auditor Phase
        audit_prompt = self.config["templates"]["auditor_v1"]["format"].format(
            system=self.config["behavioral_anchors"]["truth_filter"],
            input=f"Analyze this: {article_text[:2000]}"
        )
        audit_output = self.auditor(audit_prompt, max_tokens=500)
        facts = audit_output["choices"][0]["text"]

        # Hardware Cooldown
        time.sleep(self.config["hardware_throttling"]["vram_cooldown_seconds"])

        # Creative Phase
        creative_prompt = self.config["templates"]["creative_hnn_standard"]["format"].format(
            system=self.config["behavioral_anchors"]["empathy_filter"],
            input=f"Facts: {facts}"
        )
        creative_output = self.creative(creative_prompt, max_tokens=1000)
        final_script = creative_output["choices"][0]["text"]

        # Cleanup for VRAM
        gc.collect()
        return final_script