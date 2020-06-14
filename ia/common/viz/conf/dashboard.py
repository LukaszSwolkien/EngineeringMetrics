import ia.common.viz.conf.page as page
import datetime

class Dashboard:
    def __init__(self, conf_url, conf_username, conf_password, conf_page_title=None, conf_space=None, conf_page_parent=None):
        self._url = conf_url
        self._username = conf_username
        self._password = conf_password
        self._page_title = conf_page_title
        self._page_space = conf_space
        self._page_parent = conf_page_parent
        

    def publish(self, elements, page_title=None, page_space=None, page_parent=None):
        content = ''
        attachments = []
        for elem in elements:
            elem_content, elem_attachments = elem()
            content += elem_content
            attachments += elem_attachments

        with page.Confluence(self._url, (self._username, self._password)) as c:
            page_builder = page.PageBuilder(c)

            page_builder.create_or_update(
                space_key=page_space or self._page_space, 
                title=page_title or self._page_title, 
                new_content=content, 
                attachments = attachments,
                parent_page_title=page_parent or self._page_parent
            )

class Component:
    def __init__(self, func, args):
        self._func = func
        self._args = args


    def __call__(self):
        return self._func(*self._args)


def report_head(title, description=None):
    content = page.format_text("h5", f"Report timestamp {datetime.datetime.now():%Y-%m-%d %H:%M}")
    content += page.format_text("h2", title)
    if description is not None:
        content += page.format_text("p", description)

    return content, []


def report_heading(tag, text):
    content = page.format_text(tag, text)
    return content, []


def report_notes(conf_page_with_notes):
    return page.embed_conf_page(conf_page_with_notes), []