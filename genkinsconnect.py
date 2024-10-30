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

def save_build_link_to_db(job_number, url):
    is_exist=false
    connection = mysql.connector.connect(db_config)
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM build_history WHERE job_number = %s", (job_number,))
    (count,) = cursor.fetchone()  

    if count == 0:
        cursor.execute("INSERT INTO build_history (job_number, url) VALUES (%s, %s)", (job_number, url))
        connection.commit()
        is_exist=false
    else:
        is_exist=true

    cursor.close()
    connection.close()
    return is_exist
