import ia.common.viz.conf.page as page
import ia.dependency.conf.components as dependency_components
import ia.common.viz.conf.dashboard as confboard
import ia.execution.conf.components as sprint_components


def risks_report(product_name):
    return page.embed_jira_macro(
        f'issuetype = risk and "Project / Product" ~ "{product_name}" and issuetype = Risk',
        columns="key,summary,assignee,reporter,status,rag status computed,issuelinks"
    ), []


def project_report(percentage, all_issues, jql_all_issues, status_done, product_name=None, board_name=None):
    content = ""
    attachments = []
    if len(all_issues) > 0:
        jira_access = all_issues[0].jira_access
        project_key = all_issues[0].project.name

        content += page.format_text("h4", f'Percentage done: {percentage}%')

        if board_name:
            content += sprint_components.sprint_report(jira_access, board_name, project_key)[0]
        
        content += page.format_text("h4", f'All issues: {len(all_issues)}')
        content += page.embed_expand_macro(page.embed_jira_macro(jql_all_issues), "All issues")
        content += page.embed_pie_marco(jql=jql_all_issues, stat_type='statuses')

        content += page.format_text("h4", 'Reminding work')
        content += page.embed_expand_macro(page.embed_jira_macro(f'{jql_all_issues} and status not in ({status_done})'), "Reminding work")

        if product_name:
            content += page.format_text("h4", f'Risks')
            content += risks_report(product_name)[0]

        issues_with_links = [i for i in all_issues if len(i.load_linked_issues())>0]
        if len(issues_with_links):
            content += page.format_text('h4', f'Blocked stories')
            content += page.embed_jira_macro(f'status = Blocked and {jql_all_issues}')
            dependency_content, dependency_graphs = dependency_components.dependency_analysis(issues_with_links)
            content += dependency_content
            attachments += dependency_graphs
   
    return content, attachments


        