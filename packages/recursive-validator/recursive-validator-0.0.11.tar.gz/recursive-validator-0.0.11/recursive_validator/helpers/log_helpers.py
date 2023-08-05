from loguru import logger


class LogHandler:
    def __init__(self):
        self.file_path = ""
        self.messages = {"debug": [], "error": [], "info": [], "warning": []}

    def set_file_path(self, file_path):
        self.file_path = file_path

    def add_message(self, type: str, message: str):
        if type not in self.messages:
            self.messages[type] = []

        self.messages[type].append({"file_path": self.file_path, "message": message})

    def print_messages(self):
        for type in self.messages:
            message_groups = self.messages[type]
            for message_group in message_groups:
                message = "{} in {}".format(
                    message_group["message"], message_group["file_path"]
                )

                try:
                    log_method = getattr(logger, type)
                    log_method(message)
                except AttributeError:
                    logger.error(message)
