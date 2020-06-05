from confluence.client import Confluence, ContentType, ConfluenceError
import uuid

"""
'<p>task&nbsp;
<ac:link>
    <ri:user ri:userkey="ff8081815eb91d5b015ecd131a180011" />
</ac:link>
</p>


<ac:link>
    <ri:page ri:content-title="SDP Features - Dependencies after refinement" />
    <ac:plain-text-link-body><![CDATA[SDP Features]]></ac:plain-text-link-body>
</ac:link>

<p><br /></p>

<p>Pie</p>
<p>
    <ac:structured-macro ac:name="jirachart" ac:schema-version="1" ac:macro-id="f36229e5-be43-4d97-84f7-00f8c22211f1">
        <ac:parameter ac:name="border">false</ac:parameter>
        <ac:parameter ac:name="showinfor">false</ac:parameter>
        <ac:parameter ac:name="server">Jira</ac:parameter>
        <ac:parameter ac:name="jql">project%20%3D%20danmr</ac:parameter>
        <ac:parameter ac:name="statType">statuses</ac:parameter>
        <ac:parameter ac:name="chartType">pie</ac:parameter>
        <ac:parameter ac:name="width">500</ac:parameter>
        <ac:parameter ac:name="isAuthenticated">true</ac:parameter>
        <ac:parameter ac:name="serverId">d753b24c-57c4-3424-ad99-05d1c0e9e64c</ac:parameter>
    </ac:structured-macro>
</p>'


'<p>
task&nbsp;
<ac:link>
    <ri:user ri:userkey="ff8081815eb91d5b015ecd131a180011" />
</ac:link>
</p>


'<p>task&nbsp;<ac:link><ri:user ri:userkey="ff8081815eb91d5b015ecd131a180011" /></ac:link></p>

<p>
    <ac:structured-macro ac:name="include" ac:schema-version="1" ac:macro-id="8bce3bad-37d2-49ef-a51b-134eef909c94">
        <ac:parameter ac:name="">
            <ac:link>
                <ri:page ri:content-title="Test2" />
            </ac:link>
        </ac:parameter>
    </ac:structured-macro>
</p>
'

'<p class="auto-cursor-target"><br /></p>
<table class="relative-table" style="width: 50%;">
    <colgroup>
        <col style="width: 40%;" />
        <col style="width: 20%;" />
        <col style="width: 20%;" />
        <col style="width: 20%;" />
    </colgroup>
    
    <tbody>
        <tr>
            <th>Squad</th>
            <th>Factor</th>
            <th>Date</th>
            <th>Trend</th>
        </tr>
        <tr>
            <td>
                <ac:link><ri:page ri:content-title="SDP Features - Dependencies after refinement" />
                    <ac:plain-text-link-body><![CDATA[SDP Features]]></ac:plain-text-link-body>
                </ac:link>
            </td>

            <td>80%</td>
            <td>25/05/2020</td>
            <td>
            <strong><span style="color: rgb(0,255,0);">&uarr;</span></strong>
            </td>
        </tr>
        <tr>
            <td>SDP compliance</td>
            <td>90%</td>
            <td>25/05/2020</td>
            <td><strong><span style="color: rgb(0,0,255);">&rarr;</span></strong></td>
        </tr>
        <tr><td>SDP Core</td>
            <td>75%</td>
            <td>25/05/2020</td>
            <td><span style="color: rgb(255,0,0);"><strong>&darr;</strong></span></td>
        </tr>
        <tr>
            <td><br /></td>
            <td><br /></td>
            <td><br /></td>
            <td><br /></td>
        </tr>
        <tr>
            <td><br /></td>
            <td><br /></td>
            <td><br /></td>
            <td><br /></td>
        </tr>
    </tbody>
</table>
<p class="auto-cursor-target"></p>'
"""


def rightwards_arrow(color='rgb(0,0,255)'):
    return f'<span style="font-weight: bold; color: {color};">&rarr;</span>'


def upwards_arrow(color='rgb(0,255,0)'):
    return f'<span style="font-weight: bold; color: {color};">&uarr;</span>'


def downwards_arrow(color='rgb(255,0,0)'):
    return f'<span style="font-weight: bold; color: {color};">&darr;</span>'


def format_table(data, width=50):
    # data is an dict with keys representing collums anv values is a list of values for the collumn

    def _colgroup(no_col):
        colgroup = '<colgroup>'
        width = 100/(no_col+1)
        for i in range(no_col):
            w = width if i > 0 else 2*width
            colgroup += f'<col style="width: {w}%;" />'
        colgroup += '</colgroup>'
        return colgroup
    
    def _header(column_names):
        header = '<tr>'
        for k in column_names:
            header += f'<th>{k}</th>'
        header += '</tr>'
        return header

    table = '<p class="auto-cursor-target"><br /></p>'
    table += f'<table class="relative-table" style="width: {width}%;">'
    column_names = data.keys()
    no_col = len(column_names)
    table += _colgroup(no_col)

    table += '<tbody>'
    table += _header(column_names)
    rows = zip(*data.values())
    for r in rows:
        row = '<tr>'
        for v in r:
            row += f'<td>{v}</td>'
        row += '</tr>'
        table += row
    
    table += '</tbody>'

    table += '</table><p class="auto-cursor-target"><br /></p>'
    return table


def format_link(content_title, plain_text):
    return f'<ac:link>\
<ri:page ri:content-title="{content_title}" />\
<ac:plain-text-link-body><![CDATA[{plain_text}]]></ac:plain-text-link-body>\
</ac:link>'


def embed_conf_page(page_name):
    macro_id = str(uuid.uuid4())
    return f'<ac:structured-macro ac:name="include" ac:schema-version="1" ac:macro-id="{macro_id}">\
<ac:parameter ac:name="">\
<ac:link>\
<ri:page ri:content-title="{page_name}" />\
</ac:link>\
</ac:parameter>\
</ac:structured-macro>'


def embed_pie_marco(jql, stat_type):
    macro_id = str(uuid.uuid4())
    return f'<ac:structured-macro ac:name="jirachart" ac:schema-version="1" ac:macro-id="{macro_id}">\
        <ac:parameter ac:name="border">false</ac:parameter>\
        <ac:parameter ac:name="showinfor">false</ac:parameter>\
        <ac:parameter ac:name="server">Jira</ac:parameter>\
        <ac:parameter ac:name="jql">{jql}</ac:parameter>\
        <ac:parameter ac:name="statType">{stat_type}</ac:parameter>\
        <ac:parameter ac:name="chartType">pie</ac:parameter>\
        <ac:parameter ac:name="width">500</ac:parameter>\
        <ac:parameter ac:name="isAuthenticated">true</ac:parameter>\
        <ac:parameter ac:name="serverId">d753b24c-57c4-3424-ad99-05d1c0e9e64c</ac:parameter>\
    </ac:structured-macro>'


def embed_expand_macro(body, title=None):
    title = title if title else "Click here to expand..." 
    macro_id = str(uuid.uuid4())
    return f'<ac:structured-macro ac:name="expand" ac:schema-version="1" ac:macro-id="{macro_id}">\
<ac:parameter ac:name="title">{title}</ac:parameter>"\
<ac:rich-text-body>\
<p>{body}</p>\
</ac:rich-text-body>\
</ac:structured-macro>'



def format_text(format, text):
    t = text.replace("&", "and")
    return f'<{format}>{t}</{format}>'


def embed_image(filename):
    # return f'<p><ac:image ac:height="{height}"><ri:attachment ri:filename="{filename}" /></ac:image></p>'
    # return f'<p><ac:image ac:width="{width}"><ri:attachment ri:filename="{filename}" /></ac:image></p>'
    return f'<p><ac:image><ri:attachment ri:filename="{filename}" /></ac:image></p>'


def embed_images(filename_list):
    imgs = ""
    for fn in filename_list:
        imgs += f'<ac:image><ri:attachment ri:filename="{fn}" /></ac:image>'

    return f'<p>{imgs}</p>'


def embed_jira_macro(jql_query, columns="key,summary,type,assignee,reporter,priority,status,issuelinks,epic name,sprint", maximum_issues=20):
    macro_id = str(uuid.uuid4())
    #project = dansdp and issuetype = &quot;User Story&quot; and status = &quot;Waiting for development&quot; order by rank asc   
    jql_query = jql_query.replace('"', "&quot;")
    return f'<p><ac:structured-macro ac:name="jira" ac:schema-version="1" ac:macro-id="{macro_id}">\
<ac:parameter ac:name="server">Jira</ac:parameter>\
<ac:parameter ac:name="columns">{columns}</ac:parameter>\
<ac:parameter ac:name="maximumIssues">{maximum_issues}</ac:parameter>\
<ac:parameter ac:name="jqlQuery">{jql_query}</ac:parameter>\
<ac:parameter ac:name="serverId">d753b24c-57c4-3424-ad99-05d1c0e9e64c</ac:parameter></ac:structured-macro></p>'


class PageBuilder:
    def __init__(self, confluence_client):
        self.cli = confluence_client

    def get_content(self, space_key, title, expand=['version', 'content']):
        pages = self.cli.get_content(space_key=space_key, title=title, expand=['version', 'content'])
        for p in pages:
            result = p # take just first element from the generator
            page = self.cli.get_content_by_id(result.id,
                            expand=['body.storage', 'body.editor', 'body.view', 'body.export_view',
                                    'body.styled_view', 'body.anonymous_export_view'])
            return page
        return None

    def create_or_update(self, space_key, title, new_content, attachments=[], parent_page_title=None):
        """
        :param space_key: The string space key of a space on the confluence
            server. Defaults to None which results in this field being ignored.
        :param title: The title of the page we're looking for. Defaults to
            None which results in this field being ignored.
        :param new_content: The new content to store.
        :param attachments: The list of file paths to attachments to be send to confluence page
        """
        result = None
        parent_content_id = None
        if parent_page_title is not None:
            pages = self.cli.get_content(space_key=space_key, title=parent_page_title, expand=['version', 'content'])
            for p in pages:
                parent_content_id = p.id # take just first element from the generator
                break
        
        
        pages = self.cli.get_content(space_key=space_key, title=title, expand=['version', 'content'])
        for p in pages:
            result = p # take just first element from the generator
            break
        
        if result:
            result = self.cli.update_content(
                result.id, 
                result.type, 
                result.version.number + 1, 
                new_content=new_content, 
                new_title=title, 
                expand=['body.storage', 'version']
                )
        else:
            # print(f'parent_content_id={parent_content_id}, parent_title={parent_page_title}, title={title}, space={space_key}')
            result = self.cli.create_content(
                ContentType.PAGE, 
                title, 
                space_key, 
                content=new_content, 
                parent_content_id=parent_content_id, 
                expand=['body.storage', 'version']
                )

        atts = self.cli.get_attachments(result.id)
        page_att = set()
        for a in atts:
            page_att.add(a.title)

        new_attachments = [item for item in attachments if item not in page_att]

        for a_path in new_attachments:
            self.cli.add_attachment(result.id, file_path=a_path)
        return result

