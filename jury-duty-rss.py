import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# URL of the jury reporting instructions
URL = "https://sf.courts.ca.gov/divisions/jury-services/jury-reporting-instructions"

def fetch_jury_instructions():
    response = requests.get(URL)
    response.raise_for_status()
    return response.text

def parse_group_status(html_content, group_number):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n')

    # Normalize text
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    status = "Status unknown"
    details = ""

    # Search for group number and determine status
    for i, line in enumerate(lines):
        if f"Group Number(s):" in line:
            if str(group_number) in line:
                # Look ahead for details
                details_lines = []
                for j in range(i+1, min(i+6, len(lines))):
                    if lines[j].startswith("Group Number(s):") or lines[j].startswith("Groups On Standby:"):
                        break
                    details_lines.append(lines[j])
                details = "\n".join(details_lines).strip()
                status = "Report in person"
                return status, details
        elif "Groups On Standby:" in line:
            if str(group_number) in line:
                status = "Standby"
                details = "You are not needed to report in person at this time. Please check back after 4:30 p.m. on Next Day."
                return status, details
    return status, details

def generate_rss_feed(status, details):
    fg = FeedGenerator()
    fg.title('Shiqi\'s SF Jury Duty Status for the week of May 5, 2025')
    fg.link(href=URL, rel='alternate')
    fg.description('Automated updates for San Francisco jury group 609 reporting instructions.')
    fg.language('en')

    fe = fg.add_entry()
    fe.title(f'Group 609: {status}')
    fe.link(href=URL)
    fe.description(details)
    fe.pubDate(datetime.now(timezone.utc))

    return fg.rss_str(pretty=True)

if __name__ == "__main__":
    html_content = fetch_jury_instructions()
    status, details = parse_group_status(html_content, 609)
    rss_feed = generate_rss_feed(status, details)
    print(rss_feed.decode('utf-8'))
