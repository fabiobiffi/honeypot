from flask import Flask, request
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)


# Configure logging
def setup_logger():
    logger = logging.getLogger("honeypot")
    logger.setLevel(logging.INFO)

    # Create handlers
    file_handler = RotatingFileHandler(
        "honeypot_logs.log", maxBytes=10000000, backupCount=5
    )
    console_handler = logging.StreamHandler()

    # Create formatters and add it to handlers
    log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()


@app.before_request
def log_request():

    if request.path == "/favicon.ico":
        # Ignore favicon requests
        return "", 204

    log_message = {
        "ip": request.remote_addr,
        "path": request.path,
        "method": request.method,
        "user_agent": request.headers.get("User-Agent"),
        "query": request.query_string.decode(),
    }

    if request.method == "POST":
        log_message["post_data"] = request.get_data(as_text=True)

    logger.info(f"Request detected: {log_message}")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("HONEYPOT_PORT", 8080))
    app.run(host="0.0.0.0", port=port)
