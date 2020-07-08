import ia.common.viz.charts as charts
import ia.common.viz.conf.page as page



def maintenance_report(labels, trend, active_maintenance = [], title=""):

    created_counts = [len(t[0]) for t in trend]
    resolved_counts = [len(t[1]) for t in trend]

    chart = maintenance_created_vs_resolved_chart(labels, created_counts, resolved_counts)
    content = page.embed_image(filename=chart)

    if active_maintenance:
        content += page.format_text('p', f'Active maintenance: {len(active_maintenance)}')
        content += page.embed_expand_macro(
        page.embed_jira_macro(f'issuekey in ({", ".join(active_maintenance)})'),
        "Maintenance backlog",
    )
    return content, [chart]


def maintenance_created_vs_resolved_chart(labels, created, resolved):
    data = {
        "created": created,
        "resolved": resolved,
    }

    plt = charts.multibars(
        data,
        labels=labels,
        title="Incidents",
        colors=["red", "blue"],
    )
    maintenance_chart = f"maintenance trend {id(labels)}.png"
    plt.savefig(maintenance_chart)
    plt.close()
    return maintenance_chart
