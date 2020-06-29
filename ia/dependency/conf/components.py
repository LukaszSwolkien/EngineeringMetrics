import datetime

import ia.common.jira.issue as ticket
import ia.common.viz.charts as charts
import ia.common.viz.conf.dashboard as confboard
import ia.common.viz.conf.page as page
import ia.common.viz.graph as graph
import ia.dependency.algo as dep
import ia.dependency.metrics_store as metrics_store


def metrics_history_chart(metrics_history, title="Independence factor", days=8):
    dates = metrics_history.get_sorted_dates()[-days:]
    values = metrics_history.get_values(dates)[-days:]
    total_counts = [len(i.get("all_issues")) for i in values]
    part_counts = [len(i.get("all_with_dep")) for i in values]
    plt = charts.bar_chart_percent_stacked(dates, total_counts, part_counts)
    bar_chart_filename = (
        f"{title} chart {datetime.datetime.utcnow():%Y-%m-%d %H_%M_%S}.png"
    )
    plt.savefig(bar_chart_filename)
    plt.close()
    return bar_chart_filename


def stats_pie_charts(stats_list, title, sub_titles):
    plt = charts.pie_charts(stats_list, title=title, sub_titles=sub_titles)
    pie_chart_filename = (
        f"{title} chart {datetime.datetime.utcnow():%Y-%m-%d %H_%M_%S}.png"
    )
    plt.savefig(pie_chart_filename)
    plt.close()
    return pie_chart_filename


def inter_extern_stats_pie_chart(stats, title=None):
    plt = charts.pie_chart(
        stats.keys(),
        [len(l) for l in stats.values()],
        title,
        (0.01,) * len(stats.keys()),
    )
    pie_chart_filename = (
        f"inter_extern_stats_chart {datetime.datetime.utcnow():%Y-%m-%d %H_%M_%S}.png"
    )
    plt.savefig(pie_chart_filename)
    plt.close()
    return pie_chart_filename


def internal_vs_external_dependencies(
    jira_access, projects_list, metrics, title="Internal vs external dependencies"
):
    attachments = []
    dm_all_with_dep = [
        ticket.get_issue_by_key(jira_access, issue_key)
        for issue_key in metrics.latest["all_with_dep"]
    ]
    inter_extern_stats = dep.count_internal(dm_all_with_dep, projects_list)
    chart_file = inter_extern_stats_pie_chart(inter_extern_stats, title)
    attachments.append(chart_file)
    content = page.embed_image(filename=chart_file)

    issues_with_internal_dep = inter_extern_stats["internal"]
    issues_with_external_dep = inter_extern_stats["external"]
    content += page.embed_expand_macro(
        page.embed_jira_macro(f'issuekey in ({", ".join(issues_with_internal_dep)})'),
        "Issues with internal dependencies",
    )
    content += page.embed_expand_macro(
        page.embed_jira_macro(f'issuekey in ({", ".join(issues_with_external_dep)})'),
        "Issues with external dependencies",
    )

    return content, attachments


def dependency_graph(issue_cache):
    g = graph.build_graph(issue_cache)
    filename = f"{issue_cache.key}_{datetime.datetime.utcnow():%Y-%m-%d %H_%M_%S}.png"
    graph.save_graph_image(g, filename)
    return filename


def dependency_analysis(issues_with_dep):
    attachments = []
    content = ""
    if len(issues_with_dep):
        page_content = ""
        for issue_cache in issues_with_dep:
            graph_filename = dependency_graph(issue_cache)
            attachments.append(graph_filename)
            page_content += page.embed_image(graph_filename)
            deps = [*issue_cache.linked_issues]
            deps.append(issue_cache.key)
            page_content += page.embed_jira_macro(f'issuekey in ({", ".join(deps)})')
            page_content += "<hr />"
        content += (
            page_content  # page.embed_expand_macro(page_content, "Dependency graphs")
        )
    return content, attachments


def dependency_report(independence, all_issues, all_with_dep, metrics_history=None):
    content = page.format_text("h3", f"Independence factor = {round(independence)}% ")
    attachments = []
    if metrics_history:
        chart_file = metrics_history_chart(metrics_history)
        attachments.append(chart_file)
        content += page.embed_image(filename=chart_file)

    if len(all_with_dep):
        # dependency charts
        content += page.format_text("h2", "External dependency split")
        count_stats = dep.count_stats(all_with_dep)
        stats_list = [i for i in count_stats if len(i) > 0]
        att = []
        att.append(
            stats_pie_charts(
                stats_list,
                title=None,
                sub_titles=("By team", "By Epic", "By external epic"),
            )
        )
        content += page.embed_images(filename_list=att)
        attachments += att
        # dependency graphs
        dependency_content, dependency_graphs = dependency_analysis(all_with_dep)
        content += dependency_content
        attachments += dependency_graphs

    return content, attachments


def dependency_summary(jira_access, metrics_history, project_list):
    new_content = ""
    attachments = []
    table = {"Squad": [], "Factor": [], "Date": [], "Trend": []}
    for k, v in metrics_history.items():
        table["Squad"].append(
            page.format_link(f"{k} - Dependencies after refinement", k)
        )
        table["Factor"].append(f'{round(v.latest["independence"])}%')
        table["Date"].append(
            datetime.datetime.fromtimestamp(v.latest["timestamp"]).date()
        )
        trend = v.trend
        trend_arrow = page.rightwards_arrow()
        if trend > 0:
            trend_arrow = page.upwards_arrow()
        elif trend < 0:
            trend_arrow = page.downwards_arrow()

        table["Trend"].append(trend_arrow)

    total_m = metrics_store.merge(metrics_history.values())

    new_content += page.format_text(
        "h3", f'Total factor = {total_m.latest["independence"]}% '
    )

    chart_file = metrics_history_chart(total_m)
    attachments.append(chart_file)
    new_content += page.embed_image(filename=chart_file)

    if jira_access is not None:
        more_analysis_content, more_att = internal_vs_external_dependencies(
            jira_access, project_list, total_m
        )
        new_content += page.embed_expand_macro(
            more_analysis_content, "More analysis..."
        )
        attachments += more_att

    new_content += page.format_table(table)

    return new_content, attachments
