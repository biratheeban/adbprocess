import requests
from bs4 import BeautifulSoup
import os


jenkins_url = "https://jenkinsurl"
auth = ("user", "authtoken")


def fetch_build_history():
    response = requests.get(jenkins_url, auth=auth, verify=False)
    soup = BeautifulSoup(response.content, "html.parser")

    print(response.content)
    build_links = []
    build_history_div = soup.find("div", id="buildHistoryPage")
    if build_history_div:
        for a_tag in build_history_div.find_all("a", class_="build-row", href=True):
            job_number = a_tag.text.strip()
            href = a_tag["href"]
            full_url = f"{jenkins_url}{href}"
            build_links.append((job_number, full_url))

    return build_links