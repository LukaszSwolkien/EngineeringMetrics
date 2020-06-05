from ia.confluence import page
from ia.jira import issue as ticket
from ia.confluence import helpers
from ia.algo import dependency as dep
import ia.viz.graph as graph
import ia.viz.charts as charts
from ia.db import metrics
import datetime


def metrics_history_chart(metrics_history, title='Independence factor', days=8):
    dates = metrics_history.get_sorted_dates()[-days:]
    values = metrics_history.get_values(dates)[-days:]
    total_counts = [len(i.get('all_issues')) for i in values]
    part_counts = [len(i.get('all_with_dep')) for i in values]
    plt = charts.bar_chart_percent_stacked(dates, total_counts, part_counts)
    # values = [i.get('independence') for i in metrics_history.history.values()]
    # plt = charts.bar_chart_by_dates(dates, values)
    bar_chart_filename = f'{title} chart {datetime.datetime.utcnow():%Y-%m-%d %H_%M_%S}.png'
    plt.savefig(bar_chart_filename)
    plt.close()
    return bar_chart_filename  


def stats_pie_charts(stats_list, title, sub_titles):
    plt = charts.pie_charts(stats_list, title=title, sub_titles=sub_titles)
    pie_chart_filename = f'{title} chart {datetime.datetime.utcnow():%Y-%m-%d %H_%M_%S}.png'
    plt.savefig(pie_chart_filename)
    plt.close()
    return pie_chart_filename  


def inter_extern_stats_pie_chart(stats, title=None):
    plt = charts.pie_chart(stats.keys(), [len(l) for l in stats.values()], title, (0.01,)*len(stats.keys()))
    pie_chart_filename = f'inter_extern_stats_chart {datetime.datetime.utcnow():%Y-%m-%d %H_%M_%S}.png'
    plt.savefig(pie_chart_filename)
    plt.close()
    return pie_chart_filename  


def dependency_graph(issue_cache):
    g = graph.build_graph(issue_cache)
    filename = f"{issue_cache.key}_{datetime.datetime.utcnow():%Y-%m-%d %H_%M_%S}.png"
    graph.save_graph_image(g, filename)
    return filename


def dependency_analysis(issues_with_links):
    attachments = []
    content = ""
    if len(issues_with_links):
        page_content = ""
        for issue_cache in issues_with_links:
            graph_filename = dependency_graph(issue_cache)
            attachments.append(graph_filename)
            page_content += page.embed_image(graph_filename)
            deps = issue_cache.linked_issues.keys()
            page_content += page.embed_jira_macro(f'issuekey in ({", ".join(deps)})')
            page_content += '<hr />'
        content += page_content # page.embed_expand_macro(page_content, "Dependency graphs")
    return content, attachments


def dependency_report(independence, all_issues, all_with_dep, metrics_history=None):
    content = page.format_text("h3", f'Independence factor = {round(independence)}% ')
    attachments = []
    if metrics_history:
        chart_file = metrics_history_chart(metrics_history)
        attachments.append(chart_file)
        content += page.embed_image(filename = chart_file)

    if len(all_with_dep):
        # dependency charts
        content += page.format_text("h2","External dependency split")
        stats_list = dep.count_stats(all_with_dep)
        att = []
        att.append(
            stats_pie_charts(
                stats_list, 
                title=None,
                sub_titles=("By projects", "By Epic", "By external epic")
            )
        )
        content += page.embed_images(filename_list = att)
        attachments += att
        # dependency graphs
        dependency_content, dependency_graphs = dependency_analysis(all_with_dep)
        content += dependency_content
        attachments += dependency_graphs

    return content, attachments


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
        # content += page.format_text("h5", 'Open issues split')
        # content += page.embed_pie_marco(jql=f'{jql_all_issues} and status=Open', stat_type='issuetype')

        if product_name:
            content += page.format_text("h4", f'Risks')
            content += risks_report(product_name)

        issues_with_links = [i for i in all_issues if len(i.load_linked_issues())>0]
        if len(issues_with_links):
            content += page.format_text('h4', f'Blocked stories')
            content += page.embed_jira_macro(f'status = Blocked and {jql_all_issues}')
            dependency_content, dependency_graphs = dependency_analysis(issues_with_links)
            content += dependency_content
            attachments += dependency_graphs
   
    return content, attachments
    

def publish_dependency_report(
    conf_url,
    conf_username,
    conf_password,
    conf_space_key,
    conf_page_title,
    conf_parent_page,
    independency_factor,
    all_issues,
    all_with_dep,
    metrics_history=None,
    report_title='External dependency factor for issues after refinement', 
    report_description="The number of issues with external dependencies to the total number of issues not Done yet, but after refinement (in the backlog or in the sprint)"
    ):
    new_content = page.format_text("h5", f"Report timestamp {datetime.datetime.now():%Y-%m-%d %H:%M}")
    new_content += page.format_text("h2", report_title)
    new_content += page.format_text("p", report_description)
    
    page_content, page_attachments = dependency_report(independency_factor, all_issues, all_with_dep, metrics_history) 
    
    new_content += page_content
    with page.Confluence(conf_url, (conf_username, conf_password)) as c:
        page_builder = page.PageBuilder(c)
        page_builder.create_or_update(
            space_key=conf_space_key, 
            title=conf_page_title, 
            new_content=new_content, 
            attachments = page_attachments,
            parent_page_title=conf_parent_page
        )


def internal_vs_external_dependencies(jira_access, projects_list, metrics, title="Internal vs external dependencies"):
    attachments = []
    dm_all_with_dep = [ticket.get_issue_by_key(jira_access, issue_key) for issue_key in metrics.latest["all_with_dep"]]
    inter_extern_stats = dep.count_internal(dm_all_with_dep, projects_list)  
    chart_file = inter_extern_stats_pie_chart(inter_extern_stats, title)
    attachments.append(chart_file)
    content = page.embed_image(filename = chart_file)
    
    issues_with_internal_dep = inter_extern_stats['internal']
    issues_with_external_dep = inter_extern_stats['external']
    content += page.embed_expand_macro(page.embed_jira_macro(f'issuekey in ({", ".join(issues_with_internal_dep)})'), 'Issues with internal dependencies')
    content += page.embed_expand_macro(page.embed_jira_macro(f'issuekey in ({", ".join(issues_with_external_dep)})'), 'Issues with external dependencies')    

    return content, attachments


def publish_dependency_summary_report(
        conf_url,
        conf_username,
        conf_password,
        conf_space_key,
        conf_parent_page,
        conf_summary_page,
        projects, 
        metrics_history,
        jira_access=None # needed only to display more analysis for merged metrics
    ):
    attachments = []
        
    new_content = page.format_text("h5", f"Report timestamp {datetime.datetime.now():%Y-%m-%d %H:%M}")
    new_content += page.format_text("h2", "Independence after refinement")

    table = {
        'Squad': [],
        'Factor': [],
        'Date': [],
        'Trend': []
    }
    for k,v in metrics_history.items():
        table['Squad'].append(page.format_link(f'{k} - Dependencies after refinement', k))
        table['Factor'].append(f'{round(v.latest["independence"])}%')
        table['Date'].append(datetime.datetime.fromtimestamp(v.latest['timestamp']).date())
        trend = v.trend
        trend_arrow = page.rightwards_arrow()
        if trend > 0:
            trend_arrow = page.upwards_arrow()
        elif trend < 0:
            trend_arrow = page.downwards_arrow()
            
        table['Trend'].append(trend_arrow)

    total_m = metrics.merge(metrics_history.values())

    new_content += page.format_text("h3", f'DM factor = {total_m.latest["independence"]}% ')

    chart_file = metrics_history_chart(total_m)
    attachments.append(chart_file)
    new_content += page.embed_image(filename = chart_file)

    if jira_access is not None:
        more_analysis_content, more_att = internal_vs_external_dependencies(jira_access, projects.keys(), total_m)
        new_content += page.embed_expand_macro(more_analysis_content, "More analysis...")
        attachments += more_att

    new_content += page.format_table(table)

    with page.Confluence(conf_url, (conf_username, conf_password)) as c:
        page_builder = page.PageBuilder(c)

        page_builder.create_or_update(
            space_key=conf_space_key, 
            title=conf_summary_page, 
            new_content=new_content, 
            attachments = attachments,
            parent_page_title=conf_parent_page
        )