#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import subprocess
import argparse
from datetime import datetime

CONFIG_PATH = "config.json"
LOG_PATH = "pingd.log"

def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)

def ping_host(host):
    try:
        output = subprocess.run(
            ['ping', '-c', '1', '-W', '2', host],
            capture_output=True,
            text=True,
            timeout=5
        )
        if output.returncode == 0:
            for line in output.stdout.split('\n'):
                if 'time=' in line:
                    latency = line.split('time=')[-1].split(' ')[0]
                    return 'UP', latency
        return 'DOWN', None
    except subprocess.TimeoutExpired:
        return 'DOWN', None
    except Exception:
        return 'DOWN', None

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()  
        ]
    )
    logger = logging.getLogger('pingd')

    try:
        config = load_config(CONFIG_PATH)
        hosts = config.get('hosts', [])
        interval = config.get('interval', 60)  
    except Exception as e:
        logger.error(f"Ошибка загрузки конфига: {e}")
        sys.exit(1)

    if not hosts:
        logger.error("Список хостов пуст")
        sys.exit(1)

    logger.info(f"Демон запущен, интервал {interval} сек, хосты: {hosts}")

    while True:
        for host in hosts:
            status, latency = ping_host(host)
            if status == 'UP':
                logger.info(f"{host} | {status} | latency={latency}ms")
            else:
                logger.warning(f"{host} | {status}")
        time.sleep(interval)

if __name__ == "__main__":
    main()
