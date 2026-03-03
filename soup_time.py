import argparse
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

# TODO: make flexible
# parser = argparse.ArgumentParser()
# args = parser.parse_args()

sites_to_check = [
    "https://pandemoniumbooks.com/apps/bookthatapp/calendar",
    "https://www.tavernoftales.com/events",
    "https://bostonshows.org/",
    "https://www.remnantsomerville.com/calendar",
    "https://lamplighterbrewing.com/",
    "https://www.aeronautbrewing.com/visit/somerville/#events"
]

pages = {}
for site in sites_to_check:
    pages[site] = requests.get(site)

responses = list(pages.values())

boshows = BeautifulSoup(responses[2].text)

def parse_boshows(boshows: BeautifulSoup) -> dict:
    calendar_dict = dict()
    for thing in boshows.find_all(attrs={"class": "date-events"}):
        date = thing["data-date"]
        date_dict = {}
        for table in thing.find_all(attrs={"class": "events"}):
            for event in table.find_all(attrs={"class": "event"}):
                try:
                    event_time = event.find(attrs={"class": "event-start"}).contents[0]
                    # print(event_time)
                    divs = event.find_all("div")
                    # print(divs[0].find("a").contents[0])
                    # print(divs[1].find("a").contents[0])

                    event_name = divs[0].find("a").contents[0]
                    # print(event_name)
                    event_loc = divs[1].find("a").contents[0]
                    # print(event_loc)

                    event_dict = {
                        "Event Name": event_name,
                        "Event Loc": event_loc,
                        "Event Time": event_time
                    }
                    date_dict[event_name] = event_dict
                except AttributeError as e:
                    # TODO: unfuck this shit
                    print("shits fucked")
        calendar_dict[date] = date_dict

    return calendar_dict

boshows_events = parse_boshows(boshows)

# TODO: add sorting by loc/time

def format_dict_for_email(calendar_dict: dict) -> str:
    """
    Formats a calendar nicely for emails
    Params:
        calendar_dict (dict): dict of calendar
    Returns:
        nice_string (str): nice string
    """
    nice_string = ""
    
    for date, events in calendar_dict.items():
        nice_string += date + "\n"
        for event_name, event_details in events.items():
            for deet_name, deet in event_details.items():
                dt_string = f"\t{deet}\n"
                nice_string += dt_string
            nice_string += "\n"
    
    return nice_string


def combine_calendar_dicts(calendars: list[dict]) -> dict:
    # TODO: actually write this function maybe
    return calendars[0]


def send_josie_email(calendar_dict: dict) -> None:
    nice_string = format_dict_for_email(calendar_dict)
    msg = MIMEText(nice_string)

    me = "lolnerd@hotmail.com"
    you = "jrajodd@yahoo.com"

    msg["Subject"] = "New Events!"
    msg["From"] = me
    msg["To"] = you

    thing = smtplib.SMTP("localhost")
    thing.sendmail(me, you, msg.as_string())
    thing.quit()

send_josie_email(boshows_events)