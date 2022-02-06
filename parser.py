import argparse
import re
import os
import json
import subprocess
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

# todo: Должна быть возможность обработки всех логов внутри одного директория (статистика по каждому логу
#       должна выводиться отдельно и должна быть сохранена в отдельном json-файле)
if os.path.isfile(args.file):
    with open(args.file) as file:
        # вот здесь мне не нравится передавать access.log, мне бы хотелось передать переменную file,
        # но я не нашла как сделать, чтобы os.system или os.popen ее принимало,
        # переменные принимает subprocess, но он не проглотил такую сложную строку
        cmd_top_requests = 'tail -n 10 access.log | awk \'{print $1}\' | uniq -ci | sort -nr | head -n 3'
        cmd_top_long_requests = 'tail -n 10 access.log | awk \'{print $6, $11, $1, $NF, $4}\' | sort -nrk4 | head -n 3'
        out_top_requests = os.popen(cmd_top_requests).read().split('\n')
        out_top_long_requests = os.popen(cmd_top_long_requests).read().split('\n')

        idx = 0
        for line in file:
            if idx > 99:
                break
            idx += 1
            total_requests = idx
            ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
            if ip_match is not None:
                ip = ip_match.group()
                method = re.search(r"\] \"(POST|GET|PUT|DELETE|HEAD)", line)
                if method is not None:
                    dict_ip[ip][method.group(1)] += 1
                    idx += 1

elif os.path.isdir(args.file):
    directory = subprocess.run(['find', args.file, '-name', '*.log'])
    # тут по идее, наверное надо итерироваться по списку файлов и с каждым делать то же самое,
    # но TypeError: 'CompletedProcess' object is not iterable
    # и у меня пока нет идей, как его сделать итерируемым

dict_ip["Amount requests"] = total_requests
dict_ip["TOP REQUESTS"] = out_top_requests
dict_ip["TOP LONG REQUESTS"] = out_top_long_requests
print(json.dumps(dict_ip, indent=4))

with open('access_log.json', 'w') as f:
    f.write(json.dumps(dict_ip))
