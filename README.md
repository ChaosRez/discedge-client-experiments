# DisCEdge Client Experiments

This repository contains the client-side implementation and evaluation scripts for **[DisCEdge](https://github.com/ChaosRez/llm-context-management)**, a distributed context management system for Edge LLMs.

These scripts were used to conduct the experiments described in the paper: *"DisCEdge: Distributed Context Management for Large Language Models at the Edge"*.
## Research

If you use this software in a publication, please cite it as:

### Text

Malekabbasi, Mohammadreza, Minghe Wang, and David Bermbach. "DisCEdge: Distributed Context Management for Large Language Models at the Edge." Proceedings of the Sixth European Workshop on Machine Learning and Systems (EuroMLSys). 2026. ([ACM Digital Library](https://dl.acm.org/doi/10.1145/3805621.3807656))

### BibTeX

```bibtex
@inproceedings{malekabbasi2026discedge,
    author = "Malekabbasi, Mohammadreza and Wang, Minghe and Bermbach, David",
    title = "DisCEdge: Distributed Context Management for Large Language Models at the Edge",
    year = 2026,
    isbn = "9798400726057",
    publisher = "Association for Computing Machinery",
    address = "New York, NY, USA",
    url = "https://doi.org/10.1145/3805621.3807656",
    doi = "10.1145/3805621.3807656",
    booktitle = "Proceedings of the Sixth European Workshop on Machine Learning and Systems",
    pages = "296--303",
    numpages = 8,
    keywords = "Edge Computing, Edge Intelligence, Geo-distributed Storage, Large Language Models (LLMs)",
    location = "Edinburgh, United Kingdom",
    series = "EuroMLSys '26"
}
```

## Overview

The client can operate in two main modes:
*   **Interactive Mode:** A standard chat interface for direct interaction with the remote LLM.
*   **Scenario Mode:** Runs automated experiments based on predefined YAML files. This mode is designed to simulate a mobile user and gather performance data for evaluation.

The client supports the following features, primarily for use in scenario mode:
*   **Context Modes:**
    *   `raw`: Sends raw text context (server manages storage).
    *   `tokenized`: Sends tokenized context (server manages storage).
    *   `client-side`: Client stores full context and sends it with every request.
*   **Mobility Simulation:** Scenario files can define a sequence of "locations," each with a different edge node API URL. The client automatically switches between these nodes to simulate a roaming user.
*   **Performance Logging:** Automatically logs detailed performance metrics for each conversation turn to a CSV file, including timings, token counts, and context information. This is needed for benchmarking different context modes.
*   **Consistency Checks:** Implements a turn-counter mechanism to validate session consistency with the edge nodes.

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
4.  If using `"scenario"` mode, make sure `SCENARIO_FILE` points to a valid scenario file (e.g., `data/test_data/example_robo_longer.yml`).

Then, from the project root, run (to run multiple times):
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

This project is licensed under the MIT License.
