import ia.common.viz.confpage as page
import ia.dependency.dashboard as dependency_dashboard


def sprint_report(jira_access, board_name, project_key):
    board = jira_access.boards(type="scrum", name=board_name)[0]
    sprint = jira_access.sprints(board_id=board.id, state='active')[0]
    
    content = page.format_text("h4", f'Current Sprint: {sprint.name}')
    content += page.format_text("p", f'Start: {sprint.startDate.split("T")[0]}, End: {sprint.endDate.split("T")[0]}')
    content += page.format_text("p", f'Goal: "{sprint.goal}"')

    content += page.embed_expand_macro(
        page.embed_jira_macro(f'project = "{project_key}" and sprint in OpenSprints()'), 
            "Ongoing in current sprint"
    )

    return content


def risks_report(product_name):
    return page.embed_jira_macro(
        f'issuetype = risk and "Project / Product" ~ "{product_name}" and issuetype = Risk',
        columns="key,summary,assignee,reporter,status,rag status computed,issuelinks"
    )


def project_report(percentage, all_issues, jql_all_issues, status_done, product_name=None, board_name=None):
    content = ""
    attachments = []
    if len(all_issues) > 0:
        jira_access = all_issues[0].jira_access
        project_key = all_issues[0].project.name

        content += page.format_text("h4", f'Percentage done: {percentage}%')

        if board_name:
            content += sprint_report(jira_access, board_name, project_key)
        
        content += page.format_text("h4", f'All issues: {len(all_issues)}')
        content += page.embed_expand_macro(page.embed_jira_macro(jql_all_issues), "All issues")
        content += page.embed_pie_marco(jql=jql_all_issues, stat_type='statuses')

        content += page.format_text("h4", 'Reminding work')
        content += page.embed_expand_macro(page.embed_jira_macro(f'{jql_all_issues} and status not in ({status_done})'), "Reminding work")

        if product_name:
            content += page.format_text("h4", f'Risks')
            content += risks_report(product_name)

        issues_with_links = [i for i in all_issues if len(i.load_linked_issues())>0]
        if len(issues_with_links):
            content += page.format_text('h4', f'Blocked stories')
            content += page.embed_jira_macro(f'status = Blocked and {jql_all_issues}')
            dependency_content, dependency_graphs = dependency_dashboard.dependency_analysis(issues_with_links)
            content += dependency_content
            attachments += dependency_graphs
   
    return content, attachments


def publish_project_report(
    conf_url,
    conf_username,
    conf_password,
    conf_space_key,
    conf_page_title,
    conf_parent_page,
    jql,
    percentage_done,
    all_issues,
    status_done, 
    product_name, 
    board_name,
    report_title, 
    report_description
    ):
    new_content = page.format_text("h2", report_title)
    new_content += page.format_text("p", report_description)
    with page.Confluence(conf_url, (conf_username, conf_password)) as c:
        page_builder = page.PageBuilder(c)
        new_attachments = []

        project_content, project_attachments = project_report(percentage_done, all_issues, jql, status_done, product_name, board_name)
        new_content += project_content
        new_attachments += project_attachments

        # embed page with project notes
        new_content += page.embed_conf_page(f'{product_name} Project Issues')

        page_builder.create_or_update(
            space_key=conf_space_key, 
            title=conf_page_title, 
            new_content=new_content, 
            attachments=new_attachments,
            parent_page_title=conf_parent_page
        )
        