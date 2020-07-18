import numpy as np

import ia.common.viz.charts as charts
import ia.common.viz.conf.page as page


def maintenance_report(labels, trend, active_maintenance=[], title=""):

    created_counts = [len(t[0]) for t in trend]
    resolved_counts = [len(t[1]) for t in trend]

    mntc_chart = maintenance_created_vs_resolved_chart(labels, created_counts, resolved_counts)
    content = page.embed_image(filename=mntc_chart)

    averages = []
    stds = []

    for t in trend:
        resolved = t[1]
        lead_time = []
        for i in resolved:
            lead_time.append(i.calc_lead_time())
        averages.append(int(round(np.average(lead_time), 0)))
        stds.append(round(np.std(lead_time), 0))

    lt_chart = resolved_issues_lead_times(labels, averages, stds)
    content += page.embed_image(filename=lt_chart)

    if active_maintenance:
        content += page.format_text("p", f"Active maintenance: {len(active_maintenance)}")
        content += page.embed_expand_macro(
            page.embed_jira_macro(f'issuekey in ({", ".join(active_maintenance)})'),
            "Maintenance backlog",
        )
    return content, [mntc_chart, lt_chart]


def resolved_issues_lead_times(labels, averages, stds):
    err = [[0]*len(stds), stds]
    plt = charts.errorbar(labels=labels, values=averages, errors=err, title="Lead times (business days an issue took to resolve)")
    lt_chart = f"lead times {id(labels)}.png"
    plt.savefig(lt_chart)
    plt.close()
    return lt_chart


def maintenance_created_vs_resolved_chart(labels, created, resolved):
    data = {
        "created": created,
        "resolved": resolved,
    }

    plt = charts.multibars(data, labels=labels, title="Incidents", colors=["red", "blue"],)
    maintenance_chart = f"maintenance trend {id(labels)}.png"
    plt.savefig(maintenance_chart)
    plt.close()
    return maintenance_chart
