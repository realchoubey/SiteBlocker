# Script to block sites during working hours to
# Run this script as root

from datetime import datetime as dt
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import ast
import ConfigParser
import os
import threading
import time


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
        print("Got it! {} ".format(event.src_path))
        if os.path.basename(event.src_path) == self.monitoring_file:
            print("Sending Exception to {}".format(self.boost_thread_id))
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
            print(line)
            if not any(website in line for website in website_list):
                print("Writing...")
                file.write(line)

        # removing host names from host file
        file.truncate()


def boost_productivity():
    while True:
        restart_thread_event.clear()
        sleep_time = reset_productivity()

        while sleep_time > 0:
            if not restart_thread_event.is_set():
                sleep_time -= 5
                time.sleep(5)
            else:
                break


def reset_productivity():
    conf_details = read_conf()
    website_list = ast.literal_eval(conf_details["site_list"])
    start_time = ast.literal_eval(conf_details["start"])
    end_time = ast.literal_eval(conf_details["end"])
    day_off = ast.literal_eval(conf_details["off_days"])
    is_holiday = ast.literal_eval(conf_details["fun_day"])

    next_day = dt(dt.now().year, dt.now().month, dt.now().day + 1,
                  start_time[0], start_time[1])
    seconds_to_sleep = 30 * 60

    if is_holiday:
        unblock_site(website_list)
        print("Seems to be holiday, enjoy your day!!!")
        seconds_to_sleep = (next_day - dt.now()).total_seconds()
    else:
        if dt.now().day in day_off:
            unblock_site(website_list)

        # time of your work
        wt_start = dt(dt.now().year, dt.now().month, dt.now().day,
                      start_time[0], start_time[1])
        print(wt_start)
        wt_end = dt(dt.now().year, dt.now().month, dt.now().day,
                    end_time[0], end_time[1])

        if wt_start < dt.now() and dt.now() < wt_end:
            print("Working hours, please work...")
            block_sites(website_list)
            seconds_to_sleep = (wt_end - dt.now()).total_seconds()
        else:
            unblock_site(website_list)
            print("Sites are unblocked now, enjoy your day!!!")

            seconds_to_sleep = (next_day - dt.now()).total_seconds()

    return int(seconds_to_sleep)


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
    thread_boost = threading.Thread(target=boost_productivity,
                                    name="boost_productivity")
    thread_boost.daemon = True
    thread_boost.start()
    monitor_file(thread_boost.ident)
