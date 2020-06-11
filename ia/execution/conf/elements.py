import ia.common.viz.conf.page as page
import ia.execution.algo as algo

def sprint_report(jira_access, board_name, project_key):
    board = jira_access.boards(type="scrum", name=board_name)[0]
    sprint = jira_access.sprints(board_id=board.id, state='active')[0]
    
    content = page.format_text("h4", f'Current Sprint: {sprint.name}')
    content += page.format_text("p", f'Start: {sprint.startDate.split("T")[0]}, End: {sprint.endDate.split("T")[0]}')
    content += page.format_text("p", f'Goal: "{sprint.goal}"')

    percentage, all_issues, done_issues = algo.active_sprint_progress(jira_access, project_key)

    content += page.format_text("p", f'Sprint execution progress: {percentage}% ({len(done_issues)}/{len(all_issues)})')

    content += page.embed_expand_macro(
        page.embed_jira_macro(f'project = "{project_key}" and sprint in OpenSprints()'), 
            "Ongoing in current sprint"
    )

    return content, []


def execution_report(history):
    # TODO - make a chart from it
    content = ''
    for sprint_name, metrics in history.items():
        content += page.format_text("p", f"Sprint: {sprint_name}")
        content += page.format_text("p", f'Sprint execution progress: {metrics.progress_in_sprint}%')
        content += page.format_text("p", f'Execution progress by now: {metrics.progress_by_now}%')

    return content, []
