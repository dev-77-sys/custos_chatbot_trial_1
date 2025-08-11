# custos-chatbot/bot_testing/chatbot1/alignment.py

import os
from dotenv import load_dotenv
import custos 

# Load .env so we don't hardcode any secrets in code
load_dotenv()

# Hand the key to Custos (reads backend URL from env automatically)
custos.set_api_key(os.getenv("CUSTOS_API_KEY", ""))

# Create the guardian. This auto-starts HRV heartbeats in the simulator.
guardian = custos.guardian()