import ia.common.jira.issue as ticket
import re


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


def last_sprints(jira_access, board_name, start_at, last_sprints=5):
    board = jira_access.boards(type="scrum", name=board_name)[0]
    current_sprint = jira_access.sprints(board_id=board.id, state='active')[0]

    numbers_in_sprint_name = [int(s) for s in re.findall(r'\b\d+\b', current_sprint.name)]
    
    index = numbers_in_sprint_name[-1]-start_at-last_sprints-1
    assert(index > 0)

    closed_sprints = jira_access.sprints(board_id=board.id, state='closed', startAt=index)

    sprints = [current_sprint] + [s for s in closed_sprints]
    return sprints


def progress_history(
        jira_access, 
        sprints, 
        issuetype=("User Story", "Task", "Bug", "User Story Bug", "Technical Debt"), 
        status_done=('Done', 'Waiting for production')
    ):
    
    history = {}
    for s in sprints:
        sprint_name = s.name
        JQL = f'sprint = "{sprint_name}" and issuetype in {issuetype}'
        pr = progress(jira_access, JQL, status_done)
        history[sprint_name] = pr

    return history

