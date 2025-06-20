import config
import database
from llm_client import LLMClient
import logging
import os

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

def main():
    """Main application loop."""
    setup_logging()
    logger.info("Application starting.")
    database.init_db()
    user_db_id = database.add_user_if_not_exists(config.USER_ID)
    client = LLMClient(config.API_URL)

    server_session_id = None
    session_db_id = None

    print("LLM Client started. Type 'new' for a new session, 'exit' or 'quit' to stop.")

    while True:
        prompt = input("You: ")
        if prompt.lower() in ["exit", "quit"]:
            logger.info("Exiting application.")
            break
        if prompt.lower() == "new":
            server_session_id = None
            session_db_id = None
            logger.info("New session started.")
            print("--- New session started ---")
            continue

        logger.info(f"Sending prompt for session {server_session_id}: {prompt}")
        response = client.send_completion(prompt, server_session_id)

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
            database.add_message(session_db_id, "user", prompt)

            # Print and save assistant response
            content = response.get("content", "Sorry, I could not get a response.")
            logger.info(f"Assistant response: {content}")
            print(f"Assistant:{content}")
            database.add_message(session_db_id, "assistant", content.strip())
        else:
            logger.error("No response from LLM client.")

if __name__ == "__main__":
    main()
