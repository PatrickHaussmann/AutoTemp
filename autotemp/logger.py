from telegram import Bot
import traceback
import datetime
import os


TELEGRAM_TOKEN = ""
chat_id_patrick = ""
chat_id_group = "-"


class Logger:
    def __init__(
        self, send_telegram=True, token=TELEGRAM_TOKEN, chat_id=chat_id_patrick
    ):
        self.log_counts = {}
        if send_telegram:
            self.telegram_bot = Bot(token)
            self.chat_id = chat_id

    def log(self, message):
        self._send(message, "LOG")

    def info(self, message):
        self._send(message, "INFO")

    def warning(self, message):
        self._send(message, "WARNING")

    def error(self, message):
        self._send(message, "ERROR")

    def fatal_error(self, message):
        # check if traceback is available and add it to the message
        trace = traceback.format_exc()
        if trace:
            if message:
                message += "\n" * 2
            message += trace

        self._send(message, "FATAL ERROR")
        exit(1)

    def _increment_counter(self, level):
        if not level in self.log_counts:
            self.log_counts[level] = 1
        else:
            self.log_counts[level] += 1

    def _send(self, message, level):
        assert isinstance(message, str), "Message must be a string"
        assert isinstance(level, str) and level in (
            "LOG",
            "INFO",
            "WARNING",
            "ERROR",
            "FATAL ERROR",
        ), "Invalid log level"
        self._increment_counter(level)

        text = f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}-{level}: {message}"
        if self.telegram_bot:
            self.telegram_bot.send_message(chat_id=self.chat_id, text=text)
        print(text)

    def image(self, image_path):
        assert isinstance(image_path, str) and os.path.exists(
            image_path
        ), "Invalid image path"
        assert image_path.endswith(
            (".png", ".jpg", ".jpeg")
        ), "Invalid image format. Use .png, .jpg, or .jpeg"
        if self.telegram_bot:
            self.telegram_bot.send_photo(
                chat_id=self.chat_id, photo=open(image_path, "rb")
            )
        else:
            self.error("Telegram bot not initialized. Cannot send image.")


logger = Logger()
