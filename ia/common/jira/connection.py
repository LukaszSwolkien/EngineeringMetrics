from jira import JIRA, JIRAError
from jira.resources import GreenHopperResource

import ia.common.exception as iae
from ia.common.jira.issue import IssueCache


def connect(url, basic_auth, timeout=None):
    try:
        jira = JIRA(
            server=url,
            basic_auth=basic_auth,
            timeout=timeout,
            options={"agile_rest_path": GreenHopperResource.AGILE_BASE_REST_PATH},
        )
    except JIRAError as e:
        raise iae.IAException(e.status_code, e.text, e.url)
    except ConnectionError as e:
        raise iae.IAException(text="Connection Error")
    except Exception as e:
        raise iae.IAException(text="Fatal Error")
    return jira
