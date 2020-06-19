import ia.common.jira.issue as ticket
import collections
import re


class ExecutionMetrics:
    def __init__(self, all_issues, done_in_sprint, done_by_now, sprint):
        self._all_issues = all_issues
        self._done_in_sprint = done_in_sprint
        self._done_by_now = done_by_now
        self._sprint = sprint

    def get_progress_in_sprint(self):
        c_all = len(self._all_issues)
        c_done_in_sprint = len(self._done_in_sprint)
        return round(c_done_in_sprint*100/c_all, 0) if c_all else 0

    def get_progress_by_now(self):
        c_all = len(self._all_issues)
        c_done_by_now = len(self._done_by_now)
        return round(c_done_by_now*100/c_all, 0) if c_all else 0

    def get_sprint(self):
        return self._sprint

    def get_done_in_sprint_count(self):
        return len(self._done_in_sprint)

    def get_done_by_now_count(self):
        return len(self._done_by_now)

    def get_done_late_count(self):
        return self.count_done_by_now - self.count_done_in_sprint

    progress_in_sprint = property(get_progress_in_sprint)
    progress_by_now = property(get_progress_by_now)
    sprint = property(get_sprint)
    count_done_in_sprint = property(get_done_in_sprint_count)
    count_done_by_now = property(get_done_by_now_count)
    count_done_late = property(get_done_late_count)


def progress(jira_access, JQL, status_done=('Done', 'Waiting for production')):
    all_issues = ticket.search_issues(jira_access, JQL)
    c_all = len(all_issues)
    done_issues = [i for i in all_issues if i.fields.status.name in status_done]
    c_done = len(done_issues)
    percentage = round(c_done*100/c_all, 0) if c_all else 0
    return percentage, all_issues, done_issues 


def active_sprint_progress(
        jira_access, 
        project_key, 
        issuetype=("User Story", "Task", "Bug", "User Story Bug", "Technical Debt"), 
        status_done=('Done', 'Waiting for production')
    ):
    JQL = f'project = "{project_key}" and sprint in OpenSprints() and issuetype in {issuetype}'
    return progress(jira_access, JQL, status_done)


def all_sprints(jira_access, board_id, state='closed'):
    sprints = []
    startAt = 0
    max_results = 50
    while True:
        batch = jira_access.sprints(board_id=board_id, state=state, startAt=startAt, maxResults=max_results)
        sprints += batch
        if len(batch) < max_results:
            break
        startAt += len(batch)
    return sprints


def last_sprints(jira_access, board_name, last_sprints=5, sprint_name_prefix=None):
    board = jira_access.boards(type="scrum", name=board_name)[0]

    active_sprints = jira_access.sprints(board_id=board.id, state='active')
    current_sprint = []
    if len(active_sprints) > 0:
        current_sprint.append(active_sprints[0])
    closed_sprints = all_sprints(jira_access, board.id, 'closed')

    if sprint_name_prefix:
        filtered_closed_sprints = [s for s in closed_sprints if s.name.startswith(sprint_name_prefix)]
        sprints = filtered_closed_sprints[-last_sprints-1:] + current_sprint
    else:
        sprints = closed_sprints[-last_sprints-1:] + current_sprint
    return sprints


def progress_history(
        jira_access, 
        project_key,
        sprints, 
        issuetype=("User Story", "Task", "Bug", "User Story Bug", "Technical Debt"), 
        status_done=('Done', 'Waiting for production')
    ):
    
    history = collections.OrderedDict()
    for s in sprints:
        sprint_name = s.name
        sprint_end_date = s.endDate

        JQL = f'project = {project_key} and sprint = "{sprint_name}" and issuetype in {issuetype}'

        all_issues = ticket.search_issues(jira_access, JQL)

        done_by_now = []
        done_in_sprint = []
        not_done_yet = []

        for i in all_issues:
            if i.fields.status.name in status_done:
                done_by_now.append(i)
                if i.fields.resolutiondate and i.fields.resolutiondate <= sprint_end_date:
                    done_in_sprint.append(i)
            else:
                not_done_yet.append(i)


        history[sprint_name] = ExecutionMetrics(all_issues, done_in_sprint, done_by_now, s)
    return history






