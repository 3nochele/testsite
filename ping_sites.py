import requests
import random
import time
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

SITES_FILE = 'sites.txt'
REPORT_FILE = 'report.csv'
MAX_WORKERS = 5 

def ping_url(url):
    if not url.startswith('http'):
        url = 'http://' + url
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    time.sleep(random.uniform(2, 5)) 
    try:
        response = requests.get(url, headers=headers, timeout=15)
        return url, response.status_code, "Success"
    except Exception:
        return url, 0, "Error"

def start_process():
    try:
        with open(SITES_FILE, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        random.shuffle(urls)
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(ping_url, urls))
        
        success_count = sum(1 for _, _, status in results if status == "Success")
        fail_count = len(urls) - success_count
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        file_exists = False
        try:
            with open(REPORT_FILE, 'r') as f: file_exists = True
        except FileNotFoundError: pass

        with open(REPORT_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists: writer.writerow(["Date", "Total", "Success", "Failed"])
            writer.writerow([now, len(urls), success_count, fail_count])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_process()
