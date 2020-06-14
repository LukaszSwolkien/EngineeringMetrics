import ia.common.viz.conf.page as page
import ia.execution.algo as algo
import ia.common.viz.charts as charts
import datetime


def execution_progress_chart(history):
    labels = []
    done_on_time = []
    done_later = []
    for sprint_name, metrics in history.items():
        labels.append(sprint_name)
        p_in_sprint = round(metrics.progress_in_sprint)
        p_by_now = round(metrics.progress_by_now - p_in_sprint)
        done_on_time.append(p_in_sprint)
        done_later.append(p_by_now)

    plt = charts.barh_progress(labels, done_on_time, done_later, "History of execution")
    barh_chart_filename = f'execution barh {datetime.datetime.utcnow():%Y-%m-%d %H_%M_%S}.png'
    plt.savefig(barh_chart_filename)
    plt.close()
    return barh_chart_filename


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


def history_execution_report(history):
    barh_chart_filename = execution_progress_chart(history)
    content = page.embed_image(filename = barh_chart_filename)
    return content, [barh_chart_filename]


def execution_report(projetcs_progress):
    labels = []
    progress = []
    all_stories_count = 0
    done_stories_count = 0
    for project_key, sprint_progress in projetcs_progress.items():
        labels.append(project_key)
        p = round(sprint_progress[0])
        all_stories_count += len(sprint_progress[1])
        done_stories_count += len(sprint_progress[2])
        progress.append(p)

    labels.append("Total")
    progress.append(round(done_stories_count*100/all_stories_count, 0) if all_stories_count else 0)

    plt = charts.barh_progress(labels, progress, None, "DM execution status", invert_labels=False)
    barh_chart_filename = f'DM execution barh {datetime.datetime.utcnow():%Y-%m-%d %H_%M_%S}.png'
    plt.savefig(barh_chart_filename)
    plt.close()
    content = page.embed_image(filename = barh_chart_filename)
    return content, [barh_chart_filename]

