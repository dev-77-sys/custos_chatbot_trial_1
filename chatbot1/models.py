# custos-chatbot/bot_testing/chatbot1/models.py


import os


os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

PROVIDER = os.getenv("MODEL_PROVIDER", "openai").lower()  
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b-instruct")  
FALLBACK_MODEL_NAME = os.getenv("FALLBACK_MODEL_NAME", "facebook/opt-350m")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "140"))

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a friendly nutrition assistant. "
    "If the user asks about food, first ask ONE short clarifying question (diet or craving). "
    "Then give EXACTLY 3 meal ideas: 1 quick, 1 budget, 1 healthy. "
    "Use bullets with emojis, 1 sentence each. Keep the whole reply under 100 words. "
    "Do not roleplay, do not include dates, names, file paths, or metadata."
)

STOP_SEQS = ["\nUser:", "\nAssistant:", "\n###", "\nInstruction:", "\nResponse:", "Customer:", "Associate:"]

def _clean(text: str) -> str:
    if not text:
        return text
    cut = len(text)
    for s in STOP_SEQS:
        i = text.find(s)
        if i != -1:
            cut = min(cut, i)
    text = text[:cut]
    bad_prefixes = (
        "### Instruction:", "### Response:", "Instruction:", "Response:",
        "User:", "Assistant:", "Customer:", "Associate:",
        "Submitted by:", "Date Posted:"
    )
    lines = [
        ln for ln in text.splitlines()
        if ln.strip() and not any(ln.strip().startswith(p) for p in bad_prefixes)
    ]
    dedup = []
    for ln in lines:
        if not dedup or dedup[-1] != ln:
            dedup.append(ln)
    return "\n".join(dedup).strip()

class ChatBackend:
    def __init__(self):
        self._hf_ready = False
        self._ollama_ready = False
        self._openai_ready = False

        if PROVIDER == "openai":
            self._init_openai()
        elif PROVIDER == "ollama":
            self._init_ollama()
        elif PROVIDER == "hf":
            self._init_hf(MODEL_NAME)
        else:
            raise ValueError(f"Unknown MODEL_PROVIDER: {PROVIDER}")

    # ----- OpenAI-compatible (Groq/OpenRouter) -----
    def _init_openai(self):
        from openai import OpenAI 
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        base_url = os.getenv("OPENAI_BASE_URL")  
        self._openai = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        self._openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._openai_ready = True

    def _gen_openai(self, prompt: str) -> str:
        try:
            resp = self._openai.chat.completions.create(
                model=self._openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                top_p=0.9,
                max_tokens=MAX_NEW_TOKENS,
            )
            return _clean(resp.choices[0].message.content or "")
        except Exception as e:
            raise RuntimeError(f"openai_error: {e}")

    # ----- Ollama (local dev) -----
    def _init_ollama(self):
        self._ollama_base = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434")
        self._ollama_model = os.getenv("MODEL_NAME", MODEL_NAME)
        self._ollama_ready = True

    def _gen_ollama(self, prompt: str) -> str:
        import requests
        url = f"{self._ollama_base}/api/chat"
        payload = {
            "model": self._ollama_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {
                "temperature": 0.25,
                "top_p": 0.85,
                "top_k": 40,
                "repeat_penalty": 1.25,
                "repeat_last_n": 128,
                "presence_penalty": 0.2,
                "frequency_penalty": 0.2,
                "num_predict": MAX_NEW_TOKENS,
                "stop": ["User:", "Assistant:", "###", "Customer:", "Associate:"],
            },
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        text = (data.get("message", {}) or {}).get("content", "") or ""
        return _clean(text)

    # ----- HF (local dev) -----
    def _init_hf(self, name: str):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        self._hf_device = "cuda" if torch.cuda.is_available() else "cpu"
        self._hf_tokenizer = AutoTokenizer.from_pretrained(name)
        if self._hf_tokenizer.pad_token is None:
            self._hf_tokenizer.pad_token = self._hf_tokenizer.eos_token
        dtype = torch.float16 if self._hf_device == "cuda" else torch.float32
        self._hf_model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=dtype).to(self._hf_device)
        self._hf_ready = True

    def _format_prompt(self, prompt: str) -> str:
        tok = self._hf_tokenizer
        try:
            return tok.apply_chat_template(
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            return f"User: {prompt}\nAssistant:"

    def _gen_hf(self, prompt: str) -> str:
        from transformers import AutoTokenizer  
        tok = self._hf_tokenizer
        model = self._hf_model
        text = self._format_prompt(prompt)
        inputs = tok([text], return_tensors="pt").to(model.device)
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.35,
            top_p=0.85,
            repetition_penalty=1.25,
            eos_token_id=tok.eos_token_id,
            pad_token_id=tok.eos_token_id,
        )
        gen_ids = output_ids[0][inputs["input_ids"].shape[1]:]
        out = tok.decode(gen_ids, skip_special_tokens=True)
        return _clean(out)

    # ----- Public -----
    def generate(self, prompt: str) -> str:
        if PROVIDER == "openai":
            return self._gen_openai(prompt)
        if PROVIDER == "ollama":
            return self._gen_ollama(prompt)
        if PROVIDER == "hf":
            return self._gen_hf(prompt)
        raise RuntimeError("Unsupported provider")

class MyChatbot1:
    def __init__(self):
        self.backend = ChatBackend()
    def generate(self, prompt: str) -> str:
        return self.backend.generate(prompt)
