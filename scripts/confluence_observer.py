#! /usr/bin/env python3
import os
import requests


LOGIN_URL = "https://hammerlab.atlassian.net/login"
STATUS_REPORTS_URL = "https://hammerlab.atlassian.net/wiki/display/MSL/Status+Reports"
CONFLUENCE_USERNAME = os.environ.get("CONFLUENCE_USERNAME")
CONFLUENCE_PASSWORD = os.environ.get("CONFLUENCE_PASSWORD")


if __name__ == "__main__":
    login_data = dict(username=CONFLUENCE_USERNAME, password=CONFLUENCE_PASSWORD)
    session = requests.session()
    session.post(LOGIN_URL, data=login_data)
    req = session.get(STATUS_REPORTS_URL)


