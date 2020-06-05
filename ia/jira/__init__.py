from jira import JIRA, JIRAError
from jira.resources import GreenHopperResource
import ia.exception as iae
from ia.jira.issue import IssueCache


def connect(url, basic_auth, timeout=None):
    try:
        jira = JIRA(
            server=url, 
            basic_auth=basic_auth, 
            timeout=timeout, 
            options={"agile_rest_path" : GreenHopperResource.AGILE_BASE_REST_PATH}
    )
    except JIRAError as e:
        raise iae.IAException(e.status_code, e.text, e.url)
    except ConnectionError as e:
        raise iae.IAException(text="Connection Error")
    except Exception as e:
        raise iae.IAException(text="Fatal Error")
    return jira


# def load(jira_access, all_issues, link_type='inward'):
#     loaded_issues_with_links = {}
#     for issue in all_issues:
#         issue_cache = IssueCache(jira_access, issue)
#         load_external_issues(issue_cache)
#         loaded_issues_with_links[issue.key] = issue_cache

#     return loaded_issues_with_links