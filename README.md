# LLM Moving Client

This is a client to interact with the LLM Context Management System. It maintains conversation history in a locally to also provide a client-side session management mode.

## Project Structure

```
.
├── README.md
├── requirements.txt
├── data
│   └── test_data
└── src
    ├── config.py
    ├── database.py
    ├── llm_client.py
    └── main.py
```

The `data/` directory will be created automatically to store the `chat.db` SQLite file.

## Setup

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Ensure the LLM server is running** and accessible at the URL specified in `src/config.py` (default: `http://localhost:8081/completion`).

## How to Run

The client's behavior is controlled by settings in `src/config.py`.

1.  Open `src/config.py`.
2.  Set the `MODE` variable to `"interactive"` or `"scenario"`.
3.  If using `"scenario"` mode, make sure `SCENARIO_FILE` points to a valid scenario file.

Then, from the project root, run:
```bash
python -m src.main
```

### Interactive Mode
When `MODE` is set to `"interactive"`, the client will start in a mode where you can chat with the LLM.

#### Usage

-   Enter your prompt and press Enter to get a response from the LLM.
-   Type `new` to start a new conversation session.
-   Type `exit` or `quit` to close the application.

The client will automatically handle session IDs. The first message in a conversation will establish a new session, and subsequent messages will reuse the same session ID until you start a `new` one.

### Scenario Mode
When `MODE` is set to `"scenario"`, the client will automatically run the conversation defined in the `SCENARIO_FILE` specified in `src/config.py`.
