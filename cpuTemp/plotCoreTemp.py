#! /usr/bin/env python3
# coding=utf-8

import argparse
from collections import namedtuple
import csv
from datetime import datetime
from itertools import groupby
import logging
import os
import os.path
from statistics import mean, median
import matplotlib
matplotlib.use("Agg") # needed when script is executed by cron
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


Params = namedtuple("Params", ["log_dir", "out_dir", "log_file"])
LogEntry = namedtuple("LogEntry", ["datetime", "core_1_temp", "core_2_temp"])
DataSummary = namedtuple("DataSummary", ["min", "max", "mean", "median"])
LogSummary = namedtuple("LogSummary", ["datetime_group", "core_1_summary", "core_2_summary"])


def main():
    cl_params = parse_args()
    init_logging(cl_params.log_file)
    temp_data = read_temp_data(cl_params.log_dir)
    summarized_temp_data = summarize(temp_data)
    plot(summarized_temp_data, cl_params)


def parse_args():
    parser = argparse.ArgumentParser(description="Plot logged CPU temperatures.")
    parser.add_argument("--log-dir" , help="Directory containing temperature logs")
    parser.add_argument("--out-dir" , help="Output directory")
    parser.add_argument("--log-file" , help="File where to log errors encountered when reading and plotting the data", default=None)
    args = parser.parse_args()

    return Params(args.log_dir, args.out_dir, args.log_file)


def init_logging(log_file):
    if log_file:
        logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', level=logging.WARN)

def read_temp_data(log_dir):
    log_entries = []

    def get_datetime(time_string):
        return datetime.strptime(time_string, "%Y%m%d%H%M%S")

    def get_temp(temp_string):
        return float(temp_string[1:-2])

    for file in sorted(os.listdir(log_dir)):
        with open(os.path.join(log_dir, file), "r") as csvfile:
            reader = csv.reader(csvfile, delimiter=" ")
            next(reader) # skip header
            try:
                for i, row in enumerate(reader):
                    log_entries.append(LogEntry(get_datetime(file + row[0]),
                                               get_temp(row[1]),
                                               get_temp(row[2])))
            except Exception as err:
                logging.warn('Error reading data (file: %s; row: %s): %s', file, i, err)
    return log_entries


def summarize(data):
    data_summary = []

    def summarize_logs(temps):
        return DataSummary(min(temps), max(temps), mean(temps), median(temps))

    for k, g in groupby(data, lambda log: log.datetime.replace(hour=0, minute=0, second=0)):
        group_logs = list(g)
        core_1_summary = summarize_logs([log.core_1_temp for log in group_logs])
        core_2_summary = summarize_logs([log.core_2_temp for log in group_logs])
        data_summary.append(LogSummary(k, core_1_summary, core_2_summary))
   
    return data_summary


def plot(summarized_temp_data, cl_params):
    dates = [mdates.date2num(d.datetime_group) for d in summarized_temp_data]
    core_1 = [d.core_1_summary for d in summarized_temp_data]
    core_2 = [d.core_2_summary for d in summarized_temp_data]

    def plot_temps(dates, core_1, core_2, file_name):
        months = mdates.MonthLocator(interval=2)
        monthsFmt = mdates.DateFormatter("%Y %b")
        fig, ax = plt.subplots()
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(monthsFmt)
        ax.set_ylim([20, 80])
        plt.plot(dates, core_1, "-")
        plt.plot(dates, core_2, "-")
        fig.autofmt_xdate()

        plt.legend(["Core 1", "Core 2"], loc="upper left")
        ax.set_ylabel("°C", rotation="horizontal", labelpad=20)
        # plt.show()
        plt.savefig(file_name)

    out_dir = cl_params.out_dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    os.path.join(out_dir, "daily_min.png")
    plot_temps(dates, [d.min for d in core_1], [d.min for d in core_2], os.path.join(out_dir, "daily_min.png"))
    plot_temps(dates, [d.max for d in core_1], [d.max for d in core_2], os.path.join(out_dir, "daily_max.png"))
    plot_temps(dates, [d.mean for d in core_1], [d.mean for d in core_2], os.path.join(out_dir, "daily_mean.png"))
    plot_temps(dates, [d.median for d in core_1], [d.median for d in core_2], os.path.join(out_dir, "daily_median.png"))


if __name__ == "__main__":
    main()