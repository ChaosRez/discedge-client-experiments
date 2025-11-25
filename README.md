# DisCEdge Client Experiments

This repository contains the client-side implementation and evaluation scripts for **DisCEdge**, a distributed context management system for Edge LLMs.

These scripts were used to conduct the experiments described in the paper: *"DisCEdge: Distributed Context Management for Large Language Models at the Edge"*.

## Overview

The client is designed to simulate a mobile user interacting with geo-distributed edge nodes. It supports:
*   **Context Modes:**
    *   `raw`: Sends raw text context (server manages storage).
    *   `tokenized`: Sends tokenized context (server manages storage).
    *   `client-side`: Client stores full context and sends it with every request.
*   **Mobility Simulation:** Automatically switches between configured edge nodes after a set number of conversation turns to simulate roaming.
*   **Consistency Checks:** Implements a turn-counter mechanism to validate session consistency with the edge nodes.


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
3.  Set the `CONTEXT_MODE` variable. Options are:
    *   `"tokenized"` or `"raw"`: The server manages the session context.
    *   `"client-side"`: The client manages the session context, sending the full history with each request.
4.  If using `"scenario"` mode, make sure `SCENARIO_FILE` points to a valid scenario file.

Then, from the project root, run:
```bash
source .venv/bin/activate
for i in {1..3}; do python3 src/main.py; done
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.