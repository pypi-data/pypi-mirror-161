#!/usr/bin/python3

import logging
from pprint import pprint
import yjira as yj
from yjira import viewer
from jira import JIRA

logging.basicConfig(
    format='%(asctime)s %(module)s[%(process)d] - %(message)s %(funcName)s@%(filename)s:%(lineno)d',
    level=logging.ERROR
)

jira = JIRA(server=yj.URL, token_auth=yj.TOKEN)

def main():
    logging.info('start')
    issues = jira.search_issues(
        'Sprint in openSprints() and assignee = currentUser() order by priority desc',
        maxResults=5)
    viewer.show(issues)
    logging.info('stop')


if __name__ == "__main__":
    main()
