# script to analyze centralized log files to be uploaded to offsite
# archival location

import os
import glob
import sys
import datetime
import gzip
import shutil
import subprocess
import re


# build list of log files based on command line target directory and
# search pattern if no pattern arguments supplied then return all files in
# target directory
# old code searchs entire filesystem:
# logfile_list = glob.glob('**/*.LOGG', recursive=True)
try:
    assert os.path.isdir(sys.argv[1])
    target_directory = os.path.abspath(sys.argv[1])
except Exception:
    while True:
        target_directory = input('Please enter valid target directory: ')
        if os.path.isdir(target_directory):
            break

if len(sys.argv) == 3:
    search_pattern = sys.argv[2]
elif len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
    search_pattern = '*'
else:
    print('Incorrect search pattern argument.')
    print('Enter a log file search pattern or leave blank to select all '
          'contents of current directory:')
    search_pattern = input()
    if search_pattern == '':
        search_pattern = '*'

logfile_list = glob.glob(target_directory + os.sep + '*' + search_pattern + '*')

# Filter file list to include only log files up to 7 days old
today = datetime.date.today()
filtered_list = []
day_first = today - datetime.timedelta(days=8)
day_last = today - datetime.timedelta(days=1)
for log in logfile_list:
    fileDate = datetime.date.fromtimestamp(os.path.getmtime(log))
    print(fileDate)
    if day_first <= fileDate <= day_last:
        filtered_list.append(log)
logfile_list = filtered_list

# get amount and size of files
file_count = len(logfile_list)
log_meta = {log: os.path.getsize(log) for log in logfile_list
            if not log.endswith('.gz')}
total_size = sum([int(log_meta[l]) for l in log_meta])

# Unpack .gz files, calculate size, delete unpacked files
freespace = shutil.disk_usage('/').free
for log in logfile_list:
    if log.endswith('.gz'):
        gunzip_out = subprocess.check_output(['gunzip', '-l', log])
        regex_pattern = re.compile(r'(\d+)')
        regex_matches = regex_pattern.findall(gunzip_out.decode())
        estimated_unpacked_size = int(regex_matches[1])
        if freespace < estimated_unpacked_size:
            print('Not enough free diskspace to unpack .gz files')
            exit()
        with gzip.GzipFile(log, 'rb') as f_in:
            with open('temp', 'wb') as temp:
                s = f_in.read()
                temp.write(s)
        gz_size = os.path.getsize('temp')
        total_size += gz_size
        log_meta[log] = gz_size
        os.remove('temp')

# Format file size
size_format = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']


def human_readable_size(file_size):
    '''Convert a file size to human readable'''

    for size in size_format:
        if file_size < 1000:
            return '{0:.1f} {1}'.format(file_size, size)
        file_size /= 1000


def daily_average(input_size):
    return str(human_readable_size(input_size / 7) + ' daily average')


def logfiles_sum_size(files_size):
    return str(human_readable_size(files_size)) + ' total'

# print to command line for now to test
print(log_meta.items())
print(str(file_count) + ' log files')
print(daily_average(total_size))
print(logfiles_sum_size(total_size))
