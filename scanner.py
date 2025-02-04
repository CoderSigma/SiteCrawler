import requests
import threading
import re

GREEN = "\033[92m"
ORANGE = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

found_files = []

def banner():
    print(GREEN + r"""
  ██████ ██▄▄▄█████▓█████ ▄████▄  ██▀███  ▄▄▄      █     █░██▓   ▓█████ ██▀███  
▒██    ▒▓██▓  ██▒ ▓▓█   ▀▒██▀ ▀█ ▓██ ▒ ██▒████▄   ▓█░ █ ░█▓██▒   ▓█   ▀▓██ ▒ ██▒
░ ▓██▄  ▒██▒ ▓██░ ▒▒███  ▒▓█    ▄▓██ ░▄█ ▒██  ▀█▄ ▒█░ █ ░█▒██░   ▒███  ▓██ ░▄█ ▒
  ▒   ██░██░ ▓██▓ ░▒▓█  ▄▒▓▓▄ ▄██▒██▀▀█▄ ░██▄▄▄▄██░█░ █ ░█▒██░   ▒▓█  ▄▒██▀▀█▄  
▒██████▒░██░ ▒██▒ ░░▒████▒ ▓███▀ ░██▓ ▒██▒▓█   ▓██░░██▒██▓░██████░▒████░██▓ ▒██▒
▒ ▒▓▒ ▒ ░▓   ▒ ░░  ░░ ▒░ ░ ░▒ ▒  ░ ▒▓ ░▒▓░▒▒   ▓▒█░ ▓░▒ ▒ ░ ▒░▓  ░░ ▒░ ░ ▒▓ ░▒▓░
░ ░▒  ░ ░▒ ░   ░    ░ ░  ░ ░  ▒    ░▒ ░ ▒░ ▒   ▒▒ ░ ▒ ░ ░ ░ ░ ▒  ░░ ░  ░ ░▒ ░ ▒░
░  ░  ░  ▒ ░ ░        ░  ░         ░░   ░  ░   ▒    ░   ░   ░ ░     ░    ░░   ░ 
      ░  ░            ░  ░ ░        ░          ░  ░   ░       ░  ░  ░  ░  ░     
                         ░                                                      
                                    SiteCrawler v1.0
                                      -CoderSigma
    """ + RESET)

def check_file(base_url, path):
    url = base_url.rstrip("/") + "/" + path
    try:
        response = requests.get(url, timeout=5)
        status_code = response.status_code

        if status_code == 200:
            message = f"[FOUND] {url} - {status_code}"
            print(GREEN + message + RESET)
            found_files.append(message)
        elif status_code == 403:
            message = f"[FORBIDDEN] {url} - {status_code}"
            print(ORANGE + message + RESET)
            found_files.append(message)
        elif status_code == 404:
            pass
        else:
            message = f"[ERROR] {url} - {status_code}"
            print(RED + message + RESET)
            found_files.append(message)

    except requests.exceptions.RequestException:
        message = f"[ERROR] {url} - Connection Failed"
        print(RED + message + RESET)
        found_files.append(message)

def deep_scan(base_url):
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            urls = re.findall(r'href=["\'](.*?)["\']', response.text)
            images = re.findall(r'src=["\'](.*?)["\']', response.text)
            all_links = set(urls + images)

            for link in all_links:
                if not link.startswith("http"):
                    link = base_url.rstrip("/") + "/" + link.lstrip("/")
                check_file(base_url, link.replace(base_url, ""))

    except requests.exceptions.RequestException:
        print(RED + "[ERROR] Failed to scan website." + RESET)

def normal_scan(base_url):
    wordlist_file = "wordlist.txt"
    try:
        with open(wordlist_file, "r") as f:
            wordlist = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(RED + f"[ERROR] Wordlist file '{wordlist_file}' not found." + RESET)
        exit()

    threads = []
    for file in wordlist:
        t = threading.Thread(target=check_file, args=(base_url, file))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def main():
    banner()
    print("Choose an option:")
    print("1. Normal Scan (Uses wordlist.txt)")
    print("2. Deep Scan (Crawls all accessible pages, images, and files)")
    print("3. Hybrid Scan (Combines both scans)")

    choice = input("Enter your choice (1, 2, or 3): ").strip()
    base_url = input("Enter the website URL (e.g., https://example.com): ").strip()

    if choice == "1":
        normal_scan(base_url)
    elif choice == "2":
        deep_scan(base_url)
    elif choice == "3":
        normal_scan(base_url)
        deep_scan(base_url)
    else:
        print(RED + "[ERROR] Invalid choice. Exiting..." + RESET)
        exit()

    if found_files:
        with open("result.txt", "w") as result_file:
            result_file.write("\n".join(found_files))
        print(GREEN + f"\n[SCAN COMPLETE] Results saved to 'result.txt'." + RESET)
    else:
        print(RED + "\n[SCAN COMPLETE] No files found." + RESET)

if __name__ == "__main__":
    main()

