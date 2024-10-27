def save_output_xml(url, job_number):
    response = requests.get(url, auth=auth, verify=True)
    soup = BeautifulSoup(response.content, "html.parser")
    output_link = soup.find("a", href=True, text="output.xml")
    if output_link:
        xml_url = f"{jenkins_url}{output_link['href']}"
        xml_response = requests.get(xml_url, auth=auth, verify=False)
        xml_filename = f"{job_number}_output.xml"
        with open(xml_filename, "wb") as file:
            file.write(xml_response.content)
        
        print(f"Downloaded: {xml_filename}")
        return xml_filename

build_links = fetch_build_history()

for job_number, url in build_links:
        
    xml_filename = save_output_xml(url, job_number)
    if xml_filename:
        print(f"Job {job_number}: Saved {xml_filename}")