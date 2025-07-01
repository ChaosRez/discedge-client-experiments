import config
import database
from llm_client import LLMClient
import logging
import os
import yaml
import sys
import time
from scenario_perf_logger import PerformanceLogger

def setup_logging():
    """Sets up logging configuration."""
    os.makedirs(config.LOG_DIRECTORY, exist_ok=True)
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

def run_scenario(scenario_path: str):
    """Runs a pre-defined scenario from a YAML file."""
    logger.info(f"Starting scenario mode with file: {scenario_path}")
    try:
        with open(scenario_path, 'r') as f:
            scenario = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Scenario file not found: {scenario_path}")
        print(f"Error: Scenario file not found at {scenario_path}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        print(f"Error: Could not parse scenario file: {e}", file=sys.stderr)
        sys.exit(1)

    scenario_name = scenario.get("name", "Unnamed Scenario")
    user_id = scenario.get("user_id", config.USER_ID)
    config.USER_ID = user_id  # NOTE monkey patching config.DEFAULT_USER_ID
    model_name = scenario.get("model_name")
    if model_name:
        config.MODEL = model_name # NOTE: monkey patching config.MODEL
        logger.debug(f"Using model from scenario: {config.MODEL}")

    # Support both single message list and location-based scenarios
    messages = scenario.get("messages", [])
    locations = scenario.get("locations")

    if not messages and not locations:
        logger.warning(f"No messages or locations found in scenario file: {scenario_path}")
        print("Scenario file contains no messages or locations. Exiting.")
        return

    logger.info(f"Running scenario: '{scenario_name}' for user: '{user_id}'")
    print(f"--- Running scenario: {scenario_name} ---")

    perf_logger = PerformanceLogger(inference_mode=config.CONTEXT_MODE, scenario_name=scenario_name)

    user_db_id = database.add_user_if_not_exists(user_id)

    server_session_id = None
    session_db_id = None
    turn_counter = 0

    # Normalize to location-based structure for unified processing
    if not locations:
        locations = [{"name": "DefaultLocation", "api_url": config.DEFAULT_API_URL, "messages": messages}]

    # Instantiate the client once
    client = LLMClient(locations[0].get("api_url"))

    for location in locations:
        location_name = location.get("name", "UnnamedLocation")
        api_url = location.get("api_url")
        location_messages = location.get("messages", [])
        if not api_url or not location_messages:
            logger.warning(f"Skipping invalid location in scenario: {location}")
            continue

        client.set_api_url(api_url)
        print(f"--- Moving to new location: {location_name} ({api_url}) ---")

        for prompt in location_messages:
            turn_counter += 1
            print(f"You: {prompt}")
            logger.info(f"Sending prompt for session {server_session_id}: {prompt}")

            start_time = time.perf_counter()
            response, status_code = client.send_completion(prompt, server_session_id, turn=turn_counter)
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            if response:
                if server_session_id is None:
                    server_session_id = response.get("session_id")
                    perf_logger.set_session_id(server_session_id)
                    logger.info(f"New session ID from server: {server_session_id}")
                    if server_session_id:
                        session_db_id = database.create_session(server_session_id, user_db_id)
                    else:
                        logger.error("Did not receive session_id from server.")
                        print("Error: Did not receive session_id from server.")
                        log_details = {
                            "turn": turn_counter,
                            "prompt_length": len(prompt),
                            "error": "No session_id received",
                            "http_status_code": status_code,
                            "api_url": api_url,
                            "location_name": location_name
                        }
                        perf_logger.log("send_completion", duration_ms, log_details)
                        continue

                database.add_message(session_db_id, "user", prompt, model_name=config.MODEL, scenario_name=scenario_name)

                content = response.get("content", "Sorry, I could not get a response.")
                logger.info(f"Assistant response: {content}")
                print(f"Assistant:{content.strip()}")
                database.add_message(session_db_id, "assistant", content.strip(), model_name=config.MODEL, scenario_name=scenario_name)

                timings = response.get("timings", {})
                log_details = {
                    "turn": turn_counter,
                    "prompt_length": len(prompt),
                    "prompt_tokens": timings.get("prompt_n"),
                    "prompt_proc_ms": timings.get("prompt_ms"),
                    "prompt_per_second": timings.get("prompt_per_second"),
                    "predicted_tokens": timings.get("predicted_n"),
                    "predicted_ms": timings.get("predicted_ms"),
                    "predicted_per_second": timings.get("predicted_per_second"),
                    "tokens_cached": response.get("tokens_cached"),
                    "tokens_evaluated": response.get("tokens_evaluated"),
                    "context_processed": response.get("processed_context"),
                    "retries": response.get("retries"),
                    "http_status_code": status_code,
                    "api_url": api_url,
                    "location_name": location_name
                }
                perf_logger.log("send_completion", duration_ms, log_details)
            else:
                logger.fatal("No response from LLM client.")
                log_details = {
                    "turn": turn_counter,
                    "prompt_length": len(prompt),
                    "error": "No response from client",
                    "http_status_code": status_code,
                    "api_url": api_url,
                    "location_name": location_name
                }
                perf_logger.log("send_completion", duration_ms, log_details)
                break
        else: # continue if inner loop wasn't broken
            continue
        break # break outer loop if inner loop was broken

    perf_logger.close()

def run_interactive_mode():
    """Handles the interactive chat session."""
    logger.info("Starting interactive mode.")
    user_db_id = database.add_user_if_not_exists(config.USER_ID)
    client = LLMClient(config.DEFAULT_API_URL)

    server_session_id = None
    session_db_id = None
    turn = 0

    print("LLM Client started. Type 'new' for a new session, 'exit' or 'quit' to stop.")

    while True:
        prompt = input("You: ")
        if prompt.lower() in ["exit", "quit"]:
            logger.info("Exiting application.")
            break
        if prompt.lower() == "new":
            server_session_id = None
            session_db_id = None
            turn = 0
            logger.info("New session started.")
            print("--- New session started ---")
            continue

        turn += 1
        logger.info(f"Sending prompt for session {server_session_id}: {prompt}")
        response, status_code = client.send_completion(prompt, server_session_id, turn=turn)

        if response:
            # If this is the first message, create a new session in the DB
            if server_session_id is None:
                server_session_id = response.get("session_id")
                logger.info(f"New session ID from server: {server_session_id}")
                if server_session_id:
                    session_db_id = database.create_session(server_session_id, user_db_id)
                else:
                    logger.error("Did not receive session_id from server.")
                    print("Error: Did not receive session_id from server.")
                    continue

            # Save user message
            database.add_message(session_db_id, "user", prompt, model_name=config.MODEL)

            # Print and save assistant response
            content = response.get("content", "Sorry, I could not get a response.")
            logger.info(f"Assistant response: {content}")
            print(f"Assistant:{content}")
            database.add_message(session_db_id, "assistant", content.strip(), model_name=config.MODEL)
        else:
            logger.fatal(f"No response from LLM client. Status: {status_code}")
            break

def main():
    """Main application loop."""
    setup_logging()

    logger.info("Application starting.")
    database.init_db()

    if config.MODE == "interactive":
        run_interactive_mode()
    elif config.MODE == "scenario":
        if not config.SCENARIO_FILE or not os.path.exists(config.SCENARIO_FILE):
            logger.error(f"Scenario file not found or not configured: {config.SCENARIO_FILE}")
            print("Error: Scenario file not found or not configured in src/config.py.", file=sys.stderr)
            sys.exit(1)
        run_scenario(config.SCENARIO_FILE)
    else:
        logger.error(f"Invalid mode in config: '{config.MODE}'. Use 'interactive' or 'scenario'.")
        print(f"Error: Invalid mode '{config.MODE}' in config.py. Use 'interactive' or 'scenario'.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
