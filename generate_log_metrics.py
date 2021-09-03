import click
import json
import logging
import re
import os
from pathlib import Path
import datetime as dt
import pandas as pd

from fugro.rail.chainage.records.writers import JsonModelFileWritingManager

from models.log_metadata import LogMetaData
from models.log_record import LogRecord


def read_log_per_profile(path_to_log: str):
    with open(path_to_log, 'r') as f:
        all_lines = f.readlines()
        log_record = []
        for line in all_lines:
            first_two_columns = re.findall(r"\[(.*?)\]", line.strip('\n'))
            message = re.search(r"(?:^|])(?!\.)([\w\s]+)", line.strip('\n')).group(1).lstrip()
            if len(first_two_columns) != 2:
                logging.error(
                    f"The format of log file {0} is supposed to have time and name column within square bracket..." % os.path.basename(
                        path_to_log))
            log_record.append(
                LogRecord(dt.datetime.strptime(first_two_columns[0], "%m/%d/%Y %H:%M:%S"), first_two_columns[1],
                          message))
        return log_record


def generate_metrics_per_object(path_to_profiles: str):
    logging.info(f"Start generating the metrics for ")


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
            object_name = root_elements[-1]  # object name
            object_type = root_elements[-2]  # object type
            track_id = root_elements[-3]  # track id
            elr = root_elements[-4]  # elr
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


@click.command()
@click.option('--path-to-metadata', required=True, help="the path to metadata contain the log file",
              type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--json-file', required=True, help="the path to enriched json file",
              type=click.Path(file_okay=True, dir_okay=False))
def parse_log(path_to_metadata, json_file):
    with open(path_to_metadata, 'r') as file:
        metadata = json.load(file)
        # retrieve the full path to log from the metadata
        logging.info("Calculate the duration for all profiles in one specific object...")
        for data in metadata["data"]:
            path_to_log = data["full_path"]
            log_records = read_log_per_profile(path_to_log)

            start_time = sorted([record.time for record in log_records if (record.message == "Profile opened")])
            end_time = sorted([record.time for record in log_records if (record.message == "Profile closed")])
            # for the end time, there might be two closed actions w.r.t one opened action should select one of them
            if len(start_time) != len(end_time):
                count = 0
                while count < len(end_time) - 1:
                    if (end_time[count + 1] - end_time[count]).total_seconds() <= 1:
                        end_time.pop(count)
                        count += 1
                    else:
                        count += 1
                total_duration = sum([(e - s).total_seconds() / 3600 for e, s in zip(end_time, start_time)])
            else:
                total_duration = sum([(e - s).total_seconds() / 3600 for e, s in zip(end_time, start_time)])
            data["duration(hrs)"] = total_duration
        json_structure = {"data": []}
        json_writer = JsonModelFileWritingManager(json_file, json_structure, ['data'])
        json_writer.write_objects(metadata["data"])
        json_writer.close()
        logging.info("Done")


@click.command()
@click.option('--path-to-metadata', required=True, help="the path to metadata contain the log file",
              type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--csv-file', required=True, help="the path to csv file",
              type=click.Path(file_okay=True, dir_okay=False))
def generate_report(path_to_metadata, csv_file):
    with open(path_to_metadata, 'r') as file:
        metadata = json.load(file)
        metrics = pd.DataFrame(metadata['data'])
        object_based_metrics = metrics.groupby('object_type', as_index=False).sum()
        object_based_metrics.to_csv(csv_file, index=False, sep=',', encoding='utf-8')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
    # indexer()
    # parse_log()
    generate_report()
    # read_log_per_profile(r"D:\Test\r251\Ableton Lane Tunnel Bridge No.1050Q 10 Miles 50 Chains\01050JBM_log.txt")
    # generate_metrics_per_profile()
