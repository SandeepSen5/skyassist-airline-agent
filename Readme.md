1. Get a free API key
Go to https://aistudio.google.com/apikey and click Create API key. No billing is needed for the free tier.
Free-tier limits are low, so use gemini-2.5-flash and avoid rapid-fire calls.
2. Set up the project

cd e:\airline_agent
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install google-genai streamlit python-dotenv
Create .env:


GEMINI_API_KEY=your_key_here
3. Mock airline data and tools: tools.py
Gemini builds the function schema from the type hints and docstrings, so keep both accurate.



4. Agent: agent.py
Creates the Gemini client and a chat with the tools attached. The model defaults to
gemini-2.5-flash; override with GEMINI_MODEL in .env. Tool calls are logged so the UI
can show them, and 429/503 errors are retried with backoff.

5. UI: app.py
Streamlit chat with image upload and voice recording.

6. Run

streamlit run app.py

Try PNRs ABC123 and XYZ789. Bookings are in-memory mock data shared by all sessions,
so changes reset when the app restarts.
