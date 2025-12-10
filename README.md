# CodexTest

A simple in-memory IT helpdesk demo built with Streamlit. Users can log new tickets, browse the ticket board, and resolve issues with resolution notes. All data is stored in memory for the active session only.

## Getting started

1. Create a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

The app starts a local server and opens in your browser. Because ticket data is stored in memory, it resets whenever the app restarts.
