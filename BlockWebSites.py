# Script to block sites during working hours to
# Run this script as root

from datetime import datetime as dt
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import ast
import ConfigParser
import json
import sys
import threading
import time


class ChangeDetector(FileSystemEventHandler):
    def on_modified(self, event):
        print("Got it! {} ".format(event.src_path))
        if event.src_path == "config.choubs":
            print("Read the file again...")


# change hosts path according to your OS
hosts_path = "/etc/hosts"

# localhost IP
redirect = "127.0.0.1"


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
                pass
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
    conf_details = read_conf()
    print("Configuration file: {}".format(
          json.dumps(conf_details, indent=4, sort_keys=True)))

    website_list = ast.literal_eval(conf_details["site_list"])
    start_time = ast.literal_eval(conf_details["start"])
    end_time = ast.literal_eval(conf_details["end"])
    is_holiday = ast.literal_eval(conf_details["fun_day"]) \
        or (dt.today().weekday() > 4)

    if is_holiday:
        unblock_site(website_list)
        print("See you tomorrow...")
        sys.exit(0)
    else:
        while True:
            # time of your work
            wt_start = dt(dt.now().year, dt.now().month, dt.now().day,
                          start_time[0], start_time[1])
            wt_end = dt(dt.now().year, dt.now().month, dt.now().day,
                        end_time[0], end_time[1])

            if wt_start < dt.now() and dt.now() < wt_end:
                print("Working hours, please work...")
                block_sites(website_list)
                time.sleep(30 * 60)
            else:
                unblock_site(website_list)
                print("Sites are unblocked now, enjoy your day!!!")
                time.sleep(30 * 60)


def monitor_file(file_name="config.choubs"):
    event_handler = ChangeDetector()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    thread_monitor = threading.Thread(target=monitor_file, name="monitor_file")
    thread_boost = threading.Thread(target=boost_productivity, name="boost_productivity")

    thread_monitor.start()
    thread_boost.start()
