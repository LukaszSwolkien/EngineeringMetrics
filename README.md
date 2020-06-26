README
======

The goal of this library is to provide a flexible mechanism for building dashboard(s) from components designed to observe and measure many dimentions of work. Data calculated once can be later published on the Confluance website (Jira Confluance macros are supported for dynamic data refresh). All setup can be made in jupyter notebooks.

There are many tools available, such as built-in gadgets, dashboards and reports in Jira, or macros in Confluence, or tools like eazyBI, but thanks to custom code we can do everything (without license cost). For example, we can integrate data from different sources like Jira, Git, ServiceNow, and calculate numerical measurements of key results we expect team(s) to achieve. We can put everything on one page for the whole organization.

You don't need administrator privileges in Jira or Confluence. Just use the credentials of your regular user to access data in Jira and generate a custom dashboard on the Confluence page(s). You can also add custom code to generate report in any other format

Note 1: this is in addition to DORA (DevOps Research & Assessment) metrics from which we already know how successful we are at DevOps (DF – Deployment Frequency, MLT – Mean Lead Time for changes, MTTR – Mean Time to Recover, CFR – Change Failure Rate). 

Note 2: There are also other dimmentions not covered in this library which are very important like impact done by the software on customers, profitability, and engineers motivation, engagement, satisfaction, trust, attitute. 

## Algorithms
1. __Execution metrics__ to measure the amount of work committed vs delivered. This data shows how predictable the team is. Unlike the Story Points, the percentage of work done compared to planned can be compared between teams. Such metrics can also be aggregated on the organisation level

    Available analysis:

    - Execution summary progress bar chart for the organisation
    - Execution history progress bar chart for the team
    - The last sprint details like goal, start & end dates
    - Scope churn history
    - Carry over issues that were in more than one sprint and have not yet been Done

    Example of key results:

    - 90% of sprint content committed by the team is delivered. 

    ### Example of execution metrics for active Sprints on organisation level

    <img src="./screenshots/execution in squads.png"
        alt="Execution in squads"
        style="margin-right: 10px;" />

    ### Example of squad execution history

    <img src="./screenshots/history of execution.png"
        alt="Squad execution history"
        style="margin-right: 10px;" />

    - "done on time" - work items that were actually done in the sprint.

    - "done later" - work items that were in the sprint but finished in the next iteration(s). Therefore execution history for "done later" items will change over time. In this way we can check if there are any items we never deliver due to different reasons. We can see also how much work was carry over.

    ### Example for scope churn history on squad level
    "Scope churn" chart shows the number of issues in the sprint which were added, removed, unblocked and blocked in each sprint. These may be signs of problems with the product roadmap and/or adjustment of priorities between organisations, the lack of adequate pre-planning between sprints (backlog refinement), an insufficient number of stakeholders resulting in missing requirements, production incidents etc...

    <img src="./screenshots/scope churn.png"
        alt="Scope churn"
        style="margin-right: 10px;" />

    - "Carry over" - issues that were in more than one sprint and have not yet been Done

2. __Dependency factor__ calculates the number of issues with external dependencies to the total number of issues not Done yet, but after refinement (estimated in the backlog or already planned for the sprint).
Note that you need to specify Workload & Statuses to determine which issues are Ready for Development (after refinement) 

    The dependency factor is calculated according to the following rules:

    - searches for 'external' dependencies that can be direct or indirect (internal dependencies are ignored)
    - link type is "Is blocked by" or "Depends on".
    - related dependencies are filtered if their status is "Done". 
    - plus, Jira items in the Blocked state that don't have links. This is taken into account because there are teams that do not use Jira

    Available analysis:

    - Historical independency metrics ('all issues' vs 'issues with dependencies' - stacked bar chart with independency factor 0-100 on the Y axis and last 8 dates on the X axis)
    - External dependency by Squad (Jira external projects)
    - Issues with dependency by Initiative (Jira Epic in Squad project)
    - Dependency issues initiatives (Jira Epics in external projects)
    - Dependency graphs showing up to second level links
    - External but in DM vs external outside of DM
    - Total Independency metric:  sum(all_issues) / sum(all_with_dep)
    - Total independency history chart

    Example of key results:

    - All teams independence factor > 90% (no more than 10% stories dependent on work from other team)
    - Single team independence factor > 80%

    ### Example of independence summary on organisation level

    <img src="./screenshots/independence summary.png"
        alt="Independence summary"
        style="margin-right: 10px;" />

    ### Example of dependency split on squad level

    <img src="./screenshots/dependency split.png"
        alt="Dependency split"
        style="margin-right: 10px;" />

    ### Example of dependency graph on squad level
    Usually there is number of dependencies in the work backlog for which we can see dependency graphs. Very often, we have many user stories blocked by one or many different dependencies, and sometimes, even a chain of dependencies. To better understand the situation and then prioritise, it is important to analyse the breakdown of dependencies between teams and check the graphs of dependencies.

    <img src="./screenshots/dependency graphs.png"
        alt="Dependency graphs"
        style="margin-right: 10px;" />

3. __Project metrics__ calculates progress of the project based on number of issues done vs defined for the given epic(initiative). Execution metrics focus on sprints, not giving details on how much work was done for a given project. Project metrics focus on project progress.

    Available analysis:
    - Percentage done
    - Sprint details
    - Pie chart by issue type (Confluence Jira macro)
    - Reminding work
    - Risks
    - Blocked stories (list and dependency graphs)

    Example of key results:
    - 80% of the revenue generating use cases are delivered on time

# Code structure

ia.common - package with common stuff

- jira - package with jira access features

- viz - package with features to visualise data. 

    - conf - useful methods to upload content on Confluance page
    - charts - pie, bar, etc... chart plots
    - graph - visualise relations between jira issues

ia.dependency - algorithms and dashboard components to visualize dependency analysis

ia.project - algorithms and dashboard components to visualize project execution analysis

ia.quality - algorithms and dashboard components to visualize quality analysis

ia.execution - algorithms and dashboard components to visualize sprint execution analysis

# Usage example:

```py
import os
import ia.common.jira.connection as jira_access
import ia.common.viz.conf.dashboard as conf
import ia.dependency.conf.components as components
import ia.dependency.algo as dependency
import ia.dependency.metrics_store as metrics


# Access variables to read data from Jira and publish analysis to Confluance page
jira_url = os.environ['JIRA_URL']
jira_username = os.environ['JIRA_USERNAME']
jira_password = os.environ['JIRA_PASSWORD']

conf_url = os.environ['CONFLUENCE_URL']
conf_username = os.environ['CONFLUENCE_USERNAME']
conf_password = os.environ['CONFLUENCE_PASSWORD']

# Report variables
jira_project_id = "DANMR"
# Confluance page variables
space = "~lswolkien"
parent_page = "Reports"
page_title = "Independence report"

# connect with Jira
jira =  jira_access.connect(jira_url, basic_auth=(jira_username, jira_password))

# select issues we want to check dependencies against ('Ready for development' in jira_project_id backlog)
JQL = f'project = {jira_project_id} and status not in ("Done", "In Analysis")'
p, all_issues, all_with_dep = dependency.dependency_factor(jira, JQL)
independency_factor = 100-p

# save metrics and read past date to build history how the independence stats were changing over time
metrics.save('BacklogRefinement', jira_project_id, independency_factor, all_issues, all_with_dep)
metrics_history = metrics.read_independence_stats('BacklogRefinement', jira_project_id)

# create head component with title
report_head = conf.Component(
    conf.report_head, # callable which returns content and attachments for the dashboard element
    [page_title, "External dependencies in backlog after refinement"] # arguments for callable object
)

# create dependency report component
report_dependency = conf.Component(
    components.dependency_report, # callable which returns content and attachments for the dashboard element
    [independency_factor, all_issues, all_with_dep, metrics_history] # arguments for callable object
)

# Create or Overwrite Confluance page build from the list of components
dashboard = conf.Dashboard(conf_url, conf_username, conf_password, page_title, space, parent_page)
dashboard.publish([report_head, report_dependency])
```

# Setup project

Create virtual environment
`python3 -m venv venv`

### MAC OS
Activate venv

`. ./venv/bin/activate`

`pip install -r requirements.txt `

in case of `error: Error locating graphviz` on Mac OS do following:

`brew install graphviz`

`pip install pygraphviz --install-option="--include-path=/usr/local/include/graphviz/" --install-option="--library-path=/usr/local/lib/graphviz"`

### Windows 10

`pip install -r requirements_win10.txt `

Graphviz

Step 1: Download and install Graphviz

`https://graphviz.gitlab.io/_pages/Download/Download_windows.html`

Step 2: Add below path to your PATH environment variable

`C:\Program Files (x86)\Graphviz2.38\bin`

Step 3: Re-open command line and activate venv

`venv\Scripts\activate`

Step 4: Download binaries for pygraphviz and install in active venv

`https://github.com/CristiFati/Prebuilt-Binaries/tree/master/PyGraphviz/v1.5/Graphviz-2.42.2`

For example:

In case of python 3.7

`pip install pygraphviz-1.5-cp37-cp37m-win_amd64.whl`

In case of python 3.8

`pip install pygraphviz-1.5-cp38-cp38-win_amd64.whl`

# Environment settings

Please remember to define following parameters in your ENV variables, example:

vim ~/.bash_profile  

```
export JIRA_USERNAME=lswolkien
export JIRA_PASSWORD=TopS3cr3t
export JIRA_URL=https://jira.mycompany.com/
export CONFLUENCE_USERNAME=lswolkien
export CONFLUENCE_PASSWORD=TopS3cr3t
export CONFLUENCE_URL=https://conf.mycompany.com/
```
Note! There are better ways of managing secrets. Use above example on your own risk!

# Run jupyter notebook(s) to calculate and publish metrics

`jupyter notebook`


if you have notebooks setup you can execute all of them from the command line using below script

`./gen_dashboards.sh`

Go to your Confluance page to see generated dashboard(s)

# Roadmap

Add more engineering metrics:

1. Add Quality metrics on different levels.
    The goal is to monitor:
    - Incidents found on production with negative impact on end user (software works differently than expected)
    - An Error budget means that we can push the features until SLO is met, but no new features are allowed until the budget is rebalanced. SLOs must be defined for each service, measured to count non-compliant requests, for example, if the service latency increases, the budget will decrease.
    - Manual versus automated testing balance. There are certain cases which require human to test a system (Usability testing, UI/UX, exploratory testing or ad-hoc testing which is not a part of regression). From the other hand test cases in regression suite should be automated as much as possible.

    Example of key results:

    - 1 incident found on production for 10 releases
    - 10% or less effort on BAU is enough to keep maintenance backlog stable (SLO is met)
    - 90% or more of test cases executed at least once a week

2. Add to __Execution metrics__ code churn analysis.

    How much % of code is rewritten or deleted shortly after being written. Code churn depends on types of projects and where those projects are in the development lifecycle. There may be different causes of Code Churn:
    - project prototyping,
    - unclear requierements,
    - learning new technology or solving difficult problem,
    - perfectionism versus "good enough",

    There is no "bad" code churn. This is additional context for the execution and project metrics.
    This requires integration with GitLab.

3. Add to __Dependency factor__ new blocking issues discovered during the sprint lifespan.

    How many problems were ready to be developed, but we discovered blocking dependencies during a sprint that is related to the work that another team has to do (we don't take into account things that we can't predict, such as instability of environments etc.)
    
Note: This is in addition to DORA (DevOps Research & Assessment) metrics from which we already know how successful we are at DevOps (DF – Deployment Frequency, MLT – Mean Lead Time for changes, MTTR – Mean Time to Recover, CFR – Change Failure Rate). Since we already have them available, I have not added them to this library.