import requests
import random
import time
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# কনফিগারেশন
SITES_FILE = 'sites.txt'
SUMMARY_REPORT = 'report.csv'
PROBLEM_REPORT = 'detailed_status.csv' # এখানে শুধু সমস্যা থাকা সাইটগুলো থাকবে
MAX_WORKERS = 5 

SUB_PAGES = ['', '/about-us', '/contact-us']

def ping_url(url):
    url = url.strip()
    if not url.startswith('http'):
        url = 'http://' + url
    if url.endswith('/'):
        url = url[:-1]
    
    random_page = random.choice(SUB_PAGES)
    target_url = f"{url}{random_page}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    time.sleep(random.uniform(2, 5)) 
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15, allow_redirects=True)
        is_redirected = len(response.history) > 0
        final_url = response.url.lower()

        # সাসপেন্ডেড হলে
        if is_redirected and ("suspended" in final_url or "limit" in final_url or "notify" in final_url):
            return url, response.status_code, "Suspended"
        # সাকসেস হলে (এটি আমরা ডিটেইল রিপোর্টে লিখব না)
        elif response.status_code == 200:
            return url, response.status_code, "Success"
        # অন্য কোনো এরর (যেমন 403, 500 ইত্যাদি)
        else:
            return url, response.status_code, f"Error_{response.status_code}"
    except Exception:
        # সাইট ডাউন বা ইনভ্যালিড হলে
        return url, 0, "Invalid/Down"

def start_process():
    try:
        with open(SITES_FILE, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        print(f"Checking {len(urls)} sites for issues...")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(ping_url, urls))
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ১. শুধুমাত্র সমস্যা থাকা সাইটগুলোর রিপোর্ট তৈরি
        # এটি প্রতিবার নতুন করে তৈরি হবে (Overwrite), যাতে আপনি ফ্রেশ লিস্ট পান
        with open(PROBLEM_REPORT, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Problematic_URL", "Status_Code", "Issue_Type", "Checked_At"])
            
            for url, code, status in results:
                # যদি স্ট্যাটাস "Success" না হয়, তবেই এটি ফাইলে লিখবে
                if status != "Success":
                    writer.writerow([url, code, status, now])

        # ২. সামারি রিপোর্ট (আগের মতোই থাকবে যাতে আপনি গ্রোথ বুঝতে পারেন)
        success_count = sum(1 for _, _, s in results if s == "Success")
        suspended_count = sum(1 for _, _, s in results if s == "Suspended")
        failed_count = len(urls) - (success_count + suspended_count)

        file_exists = False
        try:
            with open(SUMMARY_REPORT, 'r') as f: file_exists = True
        except FileNotFoundError: pass

        with open(SUMMARY_REPORT, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists: 
                writer.writerow(["Date", "Total", "Success", "Suspended", "Failed"])
            writer.writerow([now, len(urls), success_count, suspended_count, failed_count])
            
        print(f"Done! Problem list saved in {PROBLEM_REPORT}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_process()
