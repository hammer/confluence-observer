#! /usr/bin/env python3
import argparse
import logging
import os

from lxml import html
import requests


LOGIN_URL = "https://hammerlab.atlassian.net/login"
STATUS_REPORTS_URL = "https://hammerlab.atlassian.net/wiki/display/MSL/Status+Reports"
CONFLUENCE_USERNAME = os.environ.get("CONFLUENCE_USERNAME")
CONFLUENCE_PASSWORD = os.environ.get("CONFLUENCE_PASSWORD")

# XPath for parsing the status report wiki page
XPATH_WEEKS = "//h1[string-length(text())=8]/text()"
# NB: for some reason <thead> is folded into <tbody>
XPATH_WEEK_HEADER = "//h1[text()='{week}']/following-sibling::div[@class='table-wrap'][1]/table/tbody/tr/th"
XPATH_WEEK_ROWS = "//h1[text()='{week}']/following-sibling::div[@class='table-wrap'][1]/table/tbody/tr/td[1]/.."

# XPath for parsing an individual status report
XPATH_NAME = "descendant::a/text()"
PROJECTS = [
    "Management Overhead",
    "Demeter",
    "Genomics Data Management",
    "Cancer",
    "HAI",
    "IBD",
    "Alzheimer's", # Needs double quotes!
    "Other",
]
PROJECTS_CONDITIONAL = " or ".join(['text()="{0}"'.format(project) for project in PROJECTS])
XPATH_PROJECTS = "descendant::*[{conditional}]/text()".format(conditional=PROJECTS_CONDITIONAL)
XPATH_SNIPPETS = 'descendant::*[text()="{project}"]/following::ul[1]/li/text()'


def get_status_reports_el(username, password):
    login_data = dict(username=username, password=password)
    session = requests.session()
    session.post(LOGIN_URL, data=login_data)
    req = session.get(STATUS_REPORTS_URL)
    return html.fromstring(req.text)


def get_per_project_snippets(column_el):
    per_project_snippets = {}
    projects = [project.strip() for project in column_el.xpath(XPATH_PROJECTS)]
    for project in projects:
        logging.info("Parsing snippets from project {0}".format(project))
        per_project_snippets[project] = column_el.xpath(XPATH_SNIPPETS.format(project=project))
    return per_project_snippets


def get_sr_info_from_status_reports_el(status_reports_el):
    sr_info = {}
    for week in status_reports_el.xpath(XPATH_WEEKS):
        sr_info[week] = []

        header = [th.text for th in status_reports_el.xpath(XPATH_WEEK_HEADER.format(week=week))]
        sr_info[week].append(header)

        row_els = status_reports_el.xpath(XPATH_WEEK_ROWS.format(week=week))
        for row_el in row_els:
            row = []
            column_els = row_el.xpath("td")
            # Handle Name column
            name = column_els[0].xpath(XPATH_NAME)[0]
            row.append(name)
            logging.info("Parsing snippets from week {week} for {name}".format(week=week, name=name))
            # Handle Last Week, This Week
            for i, column_el in enumerate(column_els[1:3], 1):
                row.append(get_per_project_snippets(column_el))
            # TODO(hammer): handle Roadblocks
            sr_info[week].append(row)
    return sr_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pull status reports off of Confluence.")
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose: logging.basicConfig(level=logging.DEBUG)

    status_reports_el = get_status_reports_el(CONFLUENCE_USERNAME, CONFLUENCE_PASSWORD)
    sr_info = get_sr_info_from_status_reports_el(status_reports_el)
    logging.info("Final results: {0}".format(sr_info))

