import click
import json
import logging
import io
import re
import os
from typing import Dict
from pathlib import Path
import glob
import datetime as dt
from datetime import datetime

from fugro.rail.chainage.records.writers import JsonModelFileWritingManager


class LogRecord:

    def __init__(self, time, user_name, message):
        self.time = time
        self.user_name = user_name
        self.message = message


def read_log_per_profile(path_to_log: str):
    with open(path_to_log, 'r') as f:
        all_lines = f.readlines()
        log_record = []
        for line in all_lines:
            time_name = re.findall(r"\[(.*?)]", line.strip('\n'))
            if len(time_name) != 2:
                logging.error(
                    f"The format of log file {0} is supposed to have time and name column within square bracket..." % os.path.basename(
                        path_to_log))
            log_record.append(LogRecord(time_name[0], time_name[1], 's'))


def generate_metrics_per_profile(path_to_profiles: str):
    logging.info(f"Start generating the metrics for ")


class LogMetaData:

    def __init__(self, full_path, object_name, object_type, elr, track_id, profile_identifier):
        self.full_path = full_path
        self.object_name = object_name
        self.object_type = object_type
        self.track_id = track_id
        self.elr = elr
        self.profile_identifier = profile_identifier

    def to_record(self) -> Dict[str, str]:
        return {
            "profile_identifier": self.profile_identifier,
            "full_path": self.full_path,
            "object_name": self.object_name,
            "object_type": self.object_type,
            "elr": self.elr,
            "track_id": self.track_id
        }


@click.command()
@click.option('--directory', required=True, help="the path possibly contain the log file",
              type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--json-file', type=click.Path(file_okay=True, dir_okay=False, writable=True))
def indexer(directory, json_file):
    logging.info("Start searching for profiles...")
    json_structure = {"data": []}
    json_writer = JsonModelFileWritingManager(json_file, json_structure, ['data'])
    for root, _, files in os.walk(directory, topdown=False):
        log_metadata = {}
        root_elements = Path(root).parts
        if len(files) != 0:
            object_name = root_elements[-1]     # object name
            object_type = root_elements[-2]     # object type
            track_id = root_elements[-3]        # track id
            elr = root_elements[-4]             # elr
            sc0_matchings = [file for file in files if '.sc0' in file.lower()]
            log_matchings = [file for file in files if '_log.txt' in file.lower()]
            if len(sc0_matchings) == len(log_matchings) != 0:
                log_metadata["data"] = []
                for log_match, sc0_match in zip(log_matchings, sc0_matchings):
                    full_log_path = os.path.join(root, log_match)
                    profile_identifier = Path(os.path.join(root, sc0_match)).stem
                    metadata = LogMetaData(full_log_path, object_name, object_type, elr, track_id, profile_identifier)
                    log_metadata["data"].append(metadata.to_record())
                json_writer.write_objects(log_metadata["data"])
    logging.info(f"Finish generating the indices for the given directory {directory}...")
    json_writer.close()


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
    indexer()
    # read_log_per_profile(r"D:\Test\r251\Ableton Lane Tunnel Bridge No.1050Q 10 Miles 50 Chains\01050JBM_log.txt")
    # generate_metrics_per_profile()
