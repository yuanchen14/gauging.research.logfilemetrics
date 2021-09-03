import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@click.command()
@click.option('--log-metrics-file', help="csv file contains the hours information for each object", type=str)
def plot_object_based_evaluation(log_metrics_file: str):
    object_break_down_hours = pd.read_csv(log_metrics_file, sep=',')

    plt.figure(1)

    plt.bar(object_break_down_hours["object_type"], object_break_down_hours["duration(hrs)"])

    xticks_pos = np.arange(len(object_break_down_hours["object_type"].unique()))
    plt.xticks(xticks_pos, ha='right', rotation=30)
    plt.ylabel("Total core hours spent on one object")
    plt.xlabel("Object type")
    plt.show()


if __name__ == '__main__':
    plot_object_based_evaluation()
