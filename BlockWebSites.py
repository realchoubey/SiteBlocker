# Script to block sites during working hours to
# Run this script as root

from datetime import datetime as dt
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import ast
import ChoubsLogging
import ConfigParser
import os
import threading
import time


# Get log file
choubs_logger = ChoubsLogging.myLogger("BlockWebSites")
logger = choubs_logger.get_logger()

# Default sleep time
DEFAULT_SLEEP_TIME = 5

# change hosts path according to your OS
hosts_path = "/etc/hosts"

# localhost IP
redirect = "127.0.0.1"

restart_thread_event = threading.Event()


class ChangeDetector(FileSystemEventHandler):
    def __init__(self, thread_id, file_name):
        self.boost_thread_id = thread_id
        self.monitoring_file = file_name

    def on_modified(self, event):
        if os.path.basename(event.src_path) == self.monitoring_file:
            logger.info("Config file changed, applying changes please wait!")
            restart_thread_event.set()


def read_conf(section=None, conf_file="config.choubs"):
    conf_details = {}
    config = ConfigParser.SafeConfigParser()
    try:
        config.read(conf_file)
        for s in config.sections():
            conf_details.update(dict(config.items(s)))
    except Exception as e:
        raise Exception("Error {} in reading config file: {} "
                        .format(e, conf_file))
    return conf_details


def block_sites(website_list):
    with open(hosts_path, 'r+') as file:
        content = file.read()
        for website in website_list:
            if website in content:
                continue
            else:
                # mapping host names to your localhost IP address
                write_string = "{} {}\n".format(redirect, website)
                file.write(write_string)


def unblock_site(website_list):
    with open(hosts_path, 'r+') as file:
        content = file.readlines()
        file.seek(0)
        for line in content:
            if not any(website in line for website in website_list):
                file.write(line)

        # removing host names from host file
        file.truncate()


def boost_productivity():
    while True:
        restart_thread_event.clear()
        time.sleep(DEFAULT_SLEEP_TIME)
        reset_productivity()
        sleep_time = 30 * 60
        logger.info("Sleeping for {} seconds.".format(sleep_time))

        while sleep_time > 0:
            if not restart_thread_event.is_set():
                time.sleep(DEFAULT_SLEEP_TIME)
                sleep_time -= DEFAULT_SLEEP_TIME
            else:
                break


def reset_productivity():
    try:
        conf_details = read_conf()
        website_list = ast.literal_eval(conf_details["site_list"])
        start_time = ast.literal_eval(conf_details["start"])
        end_time = ast.literal_eval(conf_details["end"])
        day_off = ast.literal_eval(conf_details["off_days"])
        is_holiday = ast.literal_eval(conf_details["fun_day"])

        if is_holiday:
            unblock_site(website_list)
            logger.info("Seems to be holiday, enjoy your day!!!")
        else:
            if dt.now().day in day_off:
                unblock_site(website_list)

            # time of your work
            wt_start = dt(dt.now().year, dt.now().month, dt.now().day,
                          start_time[0], start_time[1])
            logger.info(wt_start)
            wt_end = dt(dt.now().year, dt.now().month, dt.now().day,
                        end_time[0], end_time[1])

            if wt_start < dt.now() and dt.now() < wt_end:
                logger.info("Working hours, please work...")
                block_sites(website_list)
            else:
                unblock_site(website_list)
                logger.info("Sites are unblocked now, enjoy your day!!!")
    except Exception as e:
        logger.exception("Got {}".format(e))


def monitor_file(thread_id):
    event_handler = ChangeDetector(thread_id, "config.choubs")
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    logger.info("Starting blocker...")
    thread_boost = threading.Thread(target=boost_productivity,
                                    name="boost_productivity")
    thread_boost.daemon = True
    thread_boost.start()
    monitor_file(thread_boost.ident)
