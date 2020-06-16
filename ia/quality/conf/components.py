import ia.quality.algo as algo
import ia.common.jira.issue as jira_logs
import ia.common.viz.conf.page as page


def maintenance_report(
        created_defects,
        resolved_defects,
        title=''
    ):
    created_count = len(created_defects)
    resolved_count = len(resolved_defects)

    content = page.format_text("p", f'{title} - created defects: {created_count}, resolved defects: {resolved_count}')
    return content, []

    

