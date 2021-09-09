import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@click.command()
@click.option('--log-each-object', help="csv file contains the hours information for each object", type=str)
@click.option('--specific-object', help="csv file contains the hours information for a specific object", type=str)
@click.option('--user-information', help="csv file contains the profiles number information per user for a trajectory",
              type=str)
@click.option('--object-type', help="name of the object type", type=str)
def plot_object_based_evaluation(log_each_object: str, specific_object, user_information, object_type):
    object_break_down_hours = pd.read_csv(log_each_object, sep=',')
    specific_object_hours = pd.read_csv(specific_object, sep=',')
    user_profiles = pd.read_csv(user_information, sep=',')
    plt.figure(1)
    plt.subplot(211)
    plt.bar(object_break_down_hours['object_type'], object_break_down_hours["duration(hrs)"])
    xticks_pos = np.arange(len(object_break_down_hours["object_type"].unique()))
    plt.xticks(xticks_pos, ha='right', rotation=30)
    plt.title("Hours spent on each object")
    plt.ylabel("Hours")
    plt.xlabel("Object type")
    ax = plt.subplot(212)
    x = np.arange(len(user_profiles["user_name"]))
    ax.bar(x, user_profiles["duration(hrs)"], width=0.2, color='b', align='center', label='duration hours')
    ax2 = ax.twinx()
    ax2.bar(x + 0.2, user_profiles["total_profiles_per_user"], width=0.2, color='g', align='center',
            label='profile number')
    ax.set_xticks(x)
    ax.set_xticklabels(user_profiles["user_name"])
    ax.set_ylabel("hours")
    ax2.set_ylabel("profile number")
    ax.legend()
    ax2.legend(loc='upper right')

    plt.figure(2)
    plt.subplot(111)
    plt.bar(specific_object_hours["profile_identifier"], specific_object_hours["duration(hrs)"])
    xticks_pos = np.arange(len(specific_object_hours["profile_identifier"].unique()))
    plt.xticks(xticks_pos, ha='right', rotation=30)
    plt.title(f"Hours spent on a {object_type}")
    plt.ylabel("Hours")
    plt.xlabel("Profile identifier")
    plt.show()


@click.command()
@click.option('--specific-object', help="csv file contains the hours information for a specific object", type=str)
@click.option('--object-type', help="the type of the object", type=str)
def plot_histogram_object(specific_object, object_type):
    specific_object_second = pd.read_csv(specific_object, sep=',')
    min_val = np.min(specific_object_second["total_session_duration(second)"])
    max_val = np.max(specific_object_second["total_session_duration(second)"])
    min_boundary = -1.0 * (min_val % 10 - min_val)
    max_boundary = max_val - max_val % 10 + 10
    n_bins = int((max_boundary - min_boundary) / 10) + 1
    bins = np.linspace(min_boundary, max_boundary, n_bins)
    plt.hist(specific_object_second["total_session_duration(second)"], density=False, bins=bins)
    plt.ylabel("profile count")
    plt.xlabel("duration(second)")
    plt.title(f"time spent on {object_type} histogram")
    plt.show()


if __name__ == '__main__':
    plot_histogram_object()
    # plot_object_based_evaluation()
