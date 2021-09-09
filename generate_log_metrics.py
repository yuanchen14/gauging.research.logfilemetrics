import click
import json
import logging
import re
import os
from pathlib import Path
import datetime as dt
from datetime import timedelta
import numpy as np
import pandas as pd

from fugro.rail.chainage.records.writers import JsonModelFileWritingManager

from models.log_metadata import LogMetaData
from models.log_record import LogRecord


def read_log_per_profile(path_to_log: str):
    """
        The function to read the log files which are generated from the structure gauging editor
    :param path_to_log:
    :return:
    """
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
                if len(log_metadata["data"]) == 0:
                    logging.error(f"Empty log file is found at {directory}...")
                json_writer.write_objects(log_metadata["data"])
    logging.info(f"Finish generating the indices for the given directory {directory}...")
    json_writer.close()


def generate_session_information(log_records, data):
    session_info = data["sessions"]
    sessions = calculate_duration_time(log_records)
    session_count = 0
    for s in sessions:
        if s["end_session_time"] != 0 and s["has_close_action"]:
            session_records = [record for record in log_records if
                               s["start_session_time"] <= record.time <= s["end_session_time"]]
            if len(session_records) > 3:
                session_info.append(
                    LogRecord.to_session(session_records[0].user_name, True, session_records[0].time,
                                         session_records[-1].time, session_records[1].time, session_records[-2].time))
            elif len(session_records) == 3:
                # suppose a single action session takes 2 seconds to finish editing
                session_info.append(
                    LogRecord.to_session(session_records[0].user_name, True, session_records[0].time,
                                         session_records[-1].time, session_records[1].time,
                                         session_records[1].time + timedelta(seconds=2)))
            else:
                # session without editing
                session_info.append(
                    LogRecord.to_session(session_records[0].user_name, False, session_records[0].time,
                                         session_records[-1].time, session_records[0].time, session_records[0].time))
            for session_record in session_records:
                session_info[session_count]["events"].append(
                    LogRecord.to_single_event(session_record.time, session_record.message))
        elif s["end_session_time"] != 0 and not s["has_close_action"]:
            session_records = [record for record in log_records if
                               s["start_session_time"] <= record.time < s["end_session_time"]]
            if len(session_records) == 1:
                session_info.append(LogRecord.to_session(session_records[0].user_name, False, session_records[0].time,
                                                         session_records[0].time, session_records[0].time, session_records[0].time))
            else:
                session_info.append(LogRecord.to_session(session_records[0].user_name, True, session_records[0].time,
                                                         session_records[-1].time, session_records[1].time, session_records[-1].time))

            for session_record in session_records:
                session_info[session_count]["events"].append(
                    LogRecord.to_single_event(session_record.time, session_record.message))
        else:
            session_records = [record for record in log_records if s["start_session_time"] <= record.time]
            if len(session_records) == 1:
                session_info.append(LogRecord.to_session(session_records[0].user_name, False, session_records[0].time,
                                                         session_records[0].time, session_records[0].time, session_records[0].time))
            else:
                session_info.append(LogRecord.to_session(session_records[0].user_name, True, session_records[0].time,
                                                         session_records[-1].time, session_records[1].time, session_records[-1].time))
            for session_record in session_records:
                session_info[session_count]["events"].append(
                    LogRecord.to_single_event(session_record.time, session_record.message))
        session_count += 1
        data["total_session_duration(second)"] = sum([r["session_duration(second)"] for r in session_info])
        data["total_edit_duration(second)"] = sum([r["edit_duration(second)"] for r in session_info])


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

            generate_session_information(log_records, data)

        json_structure = {"data": []}
        json_writer = JsonModelFileWritingManager(json_file, json_structure, ['data'])
        json_writer.write_objects(metadata["data"])
        json_writer.close()
        logging.info("Done")


def calculate_duration_time(log_records):
    start_time = sorted([record.time for record in log_records if ("Profile opened" in record.message)])
    end_time = sorted([record.time for record in log_records if ("Profile closed" in record.message)])
    session_start_end = []
    count = 0
    while count < len(end_time) - 1:
        # If two close actions are too close to each other, remove the first one
        # Reason: open a new directory and close the profile will result in two
        # close actions
        if (end_time[count + 1] - end_time[count]).total_seconds() <= 3:
            for r in log_records:
                if r.time == end_time[count]:
                    log_records.remove(r)
                    break
            end_time.pop(count)
            count += 1
        else:
            count += 1
    if len(start_time) == len(end_time):
        for s, e in zip(start_time, end_time):
            session_start_end.append({"start_session_time": s, "end_session_time": e, "has_close_action": True})
    else:
        time_count = 0
        for time in start_time:
            # one open action doesn't have close action
            # if can't find the close action time after 20mins of open action time, this start time
            # doesn't have end time
            after_start_time = time + timedelta(minutes=20)
            if len(end_time) !=0:
                time_between = [e for e in end_time if time < e < after_start_time]
                if len(time_between) == 0 and time_count < len(start_time) - 1:
                    session_start_end.append({"start_session_time": time, "end_session_time": start_time[time_count + 1],
                                              "has_close_action": False})
                elif len(time_between) == 0 and len(end_time) < len(start_time):
                    session_start_end.append({"start_session_time": time, "end_session_time": 0, "has_close_action": False})
                else:
                    session_start_end.append(
                        {"start_session_time": time, "end_session_time": sorted(time_between)[0], "has_close_action": True})
            else:
                session_start_end.append(
                    {"start_session_time": time, "end_session_time": 0, "has_close_action": False})
            time_count += 1

    return session_start_end


@click.command()
@click.option('--path-to-metadata', required=True, help="the path to metadata contain the log file",
              type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--csv-file-object', required=True, help="the path to object based output csv file",
              type=click.Path(file_okay=True, dir_okay=False))
@click.option('--csv-file-profile', required=True, help="the path to profile based csv file",
              type=click.Path(file_okay=True, dir_okay=False))
@click.option('--csv-file-user', required=True, help="the path to user name based csv file",
              type=click.Path(file_okay=True, dir_okay=False))
@click.option('--project-information', help="project level information from the given directory information", type=str)
def generate_report(path_to_metadata, csv_file_object, csv_file_profile, csv_file_user, project_information):
    logging.info("Start generating the csv file metrics using metadata json file...")
    with open(path_to_metadata, 'r') as file:
        metadata = json.load(file)
        metrics = pd.DataFrame(metadata['data'])
        # Generate project level of the information
        project_level = {}
        project_level["number_of_object_types"] = len(metrics.groupby("object_type", as_index=False))
        project_level["total_objects"] = len(metrics.groupby("object_name", as_index=False))
        project_level["percentage_long_objects"] = (sum(
            [int(len(r) > 1) for r in metrics.groupby("object_name", as_index=False).groups.values()]) / project_level[
                                                        "total_objects"]) * 100.0
        project_level["percentage_short_objects"] = 100 - project_level["percentage_long_objects"]
        project_level["total_session_durations"] = sum(metrics["total_session_duration(second)"])
        project_level["total_edit_duration"] = len(metrics["total_edit_duration(second)"])
        object_profile_based_metrics = metrics[metrics['object_type'] == 'Tunnel'].groupby('profile_identifier',
                                                                                           as_index=False).sum()
        object_based_metrics = metrics.groupby('object_type', as_index=False).sum()

        object_based_metrics.to_csv(csv_file_object, index=False, sep=',', encoding='utf-8')
        object_profile_based_metrics.to_csv(csv_file_profile, index=False, sep=',', encoding='utf-8')
        pd.DataFrame([project_level]).to_csv(project_information, index=False, sep=',', encoding='utf-8')
        logging.info("Done.")


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
    # indexer()
    parse_log()
    # generate_report()
    # calculate_duration_time(r"R:\02 Projects\2019\9219-0021-000_Western Region\B_Sites\TOR_214_222\04_Structure_Gauging\01_Processing\02_From_FALB\2021-05-11\TOR_214_222\Sc0\TOR\1100\S&T\S&T Equipment 219 Miles 63 Chains\21963QBM_log.txt")
    # generate_metrics_per_profile()
