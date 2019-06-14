
import os
import logging
import time


class myLogger():
    def __init__(self, srv_name, log_timestamp=None):
        log_timestamp = log_timestamp if log_timestamp \
            else time.strftime("%Y%m%d%H%M")

        logdir_path = "/tmp/{}/".format(log_timestamp)
        if not os.path.exists(logdir_path):
            os.makedirs(logdir_path)

        logfile_name = os.path.join(logdir_path, "{}.log".format(srv_name))
        self.logger = self.get_log_context(logfile_name)

    def get_logger(self):
        return self.logger

    def get_log_context(self, log_file, level="INFO"):
        if not hasattr(logging, level):
            raise Exception("Unknown log level")

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%b %d %H:%M:%S")

        fileHandler = logging.FileHandler(log_file)
        fileHandler.setFormatter(formatter)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level))
        root_logger.addHandler(fileHandler)
        root_logger.addHandler(consoleHandler)

        logfile_path = root_logger.root.handlers[0].baseFilename
        root_logger.info("Please find detailed logs at: [%s]", logfile_path)

        return root_logger
