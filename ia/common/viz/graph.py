from ia.common.helpers import die
from functools import partial
try:
    import pygraphviz as pgv
except ImportError:
    """
    Steps to install graphviz on Mac OS:
    brew install graphviz
    pip install pygraphviz --install-option="--include-path=/usr/local/include/graphviz/" --install-option="--library-path=/usr/local/lib/graphviz"
    """
    die("Please install pygraphviz ")


def save_graph_image(graph, image_file):
    graph.layout(prog='dot')
    graph.draw(image_file)


def build_graph(issue_cache):
    seen = set() # to prevent infinite recursion in the cyclic graph

    def get_color(typename):
        if typename == 'Epic':
            return 'violet'
        if typename == 'Bug':
            return 'red'
        if typename == 'Test':
            return 'aquamarine'
        if typename == 'Release':
            return "goldenrod2"
        return 'black'

    def get_label(issue_cache):
        epic_name = issue_cache.epic_name
        return f"{issue_cache.key}\n{epic_name}" if epic_name else issue_cache.key

    def get_label_by_key(issue_cache, l_key):
        issue= issue_cache.linked_issues[l_key]
        return get_label(issue)


    def walk(issue_cache, graph):
        seen.add(issue_cache.key)
        issue = issue_cache.issue
        linked_issues = issue_cache.get_linked_issues()
        filtered_links = linked_issues.keys() #[i.key for i in linked_issues]
        fields = issue.fields

        if hasattr(fields, 'issuelinks'):
            for link in fields.issuelinks:
                if hasattr(link, 'outwardIssue'):
                    if (link.outwardIssue.key in filtered_links and (issue.key, link.outwardIssue.key) not in graph.edges()):
                        link_typename = link.outwardIssue.fields.issuetype.name
                        graph.add_node(
                            link.outwardIssue.key, 
                            color=get_color(link_typename), 
                            shape='box', 
                            label=get_label_by_key(issue_cache, link.outwardIssue.key)
                        )
                        graph.add_edge(
                            issue.key, 
                            link.outwardIssue.key, 
                            label=link.type.outward
                        )
                if hasattr(link, 'inwardIssue'):
                    if (link.inwardIssue.key in filtered_links and (link.inwardIssue.key, issue.key) not in graph.edges()):
                        link_typename = link.inwardIssue.fields.issuetype.name
                        graph.add_node(
                            link.inwardIssue.key, 
                            color=get_color(link_typename), 
                            shape='box', 
                            label=get_label_by_key(issue_cache, link.inwardIssue.key)
                        )
                        graph.add_edge(
                            link.inwardIssue.key, 
                            issue.key, 
                            label=link.type.outward
                        )
        
        for l_key, l_issue_cache in linked_issues.items():
            if l_key not in seen:
                # print(l_key)
                walk(l_issue_cache, graph)
        return graph

    graph = pgv.AGraph(strict=False, directed=True)
    
    issue = issue_cache.issue
    issue_typename = issue.fields.issuetype.name
    
    epic_name = issue_cache.epic_name
    if epic_name:
        epic_name = "| Epic: " + epic_name
    graph.graph_attr['label'] = f'{issue.key}: {issue.fields.summary} {epic_name}'
    graph.add_node(issue.key, color=get_color(issue_typename), penwidth='5.0', label=get_label(issue_cache))

    graph = walk(issue_cache, graph)
    return graph
