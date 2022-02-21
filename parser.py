import argparse
import re
import os
import json
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('-f', dest='file', action='store', help='Path to logfile', default='access.log')
args = parser.parse_args()

if not args.file:
    parser.error('you did not specify a log file')

total_requests = 0
dict_ip = defaultdict(
    lambda: {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "HEAD": 0}
)


def process_file(log):
    with open(log) as file:
        cmd_top_requests = 'cat %s | awk \'{print $1}\' | uniq -ci | sort -nr | head -n 3' % log
        cmd_top_long_requests = 'cat %s | awk \'{print $6, $11, $1, $NF, $4}\' | sort -nrk4 | head -n 3' \
                                % log
        out_top_requests = os.popen(cmd_top_requests).read().split('\n')
        out_top_long_requests = os.popen(cmd_top_long_requests).read().split('\n')

        idx = 0
        for line in file:
            idx += 1
            total_requests = idx
            ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
            if ip_match is not None:
                ip = ip_match.group()
                method = re.search(r"\] \"(POST|GET|PUT|DELETE|HEAD)", line)
                if method is not None:
                    dict_ip[ip][method.group(1)] += 1
                    idx += 1
    dict_ip["Amount requests"] = total_requests
    dict_ip["TOP REQUESTS"] = out_top_requests
    dict_ip["TOP LONG REQUESTS"] = out_top_long_requests
    print(json.dumps(dict_ip, indent=4))

    with open('access_log.json', 'w') as f:
        f.write(json.dumps(dict_ip))


if os.path.isfile(args.file):
    process_file(args.file)

elif os.path.isdir(args.file):
    for f in os.listdir(args.file):
        process_file(args.file + f)
