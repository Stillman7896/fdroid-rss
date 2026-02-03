import requests
import os
from datetime import datetime


# Configuration
PACKAGES_FILE = "packages.txt"
FEEDS_DIR = "feeds"
F_DROID_API = "https://f-droid.org/api/v1/packages/{}"


def load_packages():
    with open(PACKAGES_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def fetch_package_data(package):
    try:
        response = requests.get(F_DROID_API.format(package), timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {package}: {e}")
        return None


def generate_rss(package, data):
    latest = data["packages"][0]  # Most recent version first
    version = latest["versionName"]
    version_code = latest["versionCode"]
    
    # Construct direct download URL using the observed pattern
    direct_download_url = f"https://f-droid.org/repo/{package}_{version_code}.apk"
    
    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>F-Droid Updates: {package}</title>
  <link>https://f-droid.org/packages/{package}/</link>
  <description>RSS feed for {package} updates on F-Droid</description>
  <lastBuildDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
  <item>
    <title>Version {version} (Code: {version_code})</title>
    <link>https://f-droid.org/packages/{package}/</link>
    <enclosure url="{direct_download_url}" length="1" type="application/vnd.android.package-archive" />
    <guid>https://f-droid.org/packages/{package}/#{version}</guid>
    <pubDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
    <description>New version {version} released for {package}. Direct download: {direct_download_url}</description>
  </item>
</channel>
</rss>"""
    
    os.makedirs(FEEDS_DIR, exist_ok=True)
    with open(f"{FEEDS_DIR}/{package}.xml", 'w') as f:
        f.write(rss_content)
    print(f"Updated RSS feed for {package} (direct download: {direct_download_url})")


def main():
    packages = load_packages()
    for package in packages:
        data = fetch_package_data(package)
        if data:
            generate_rss(package, data)


if __name__ == "__main__":
    main()
