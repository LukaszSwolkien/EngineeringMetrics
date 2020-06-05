import datetime


def to_timestamp(dt, epoch=datetime.datetime(1970, 1, 1)):
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 86400) * 10**6) / 10**6


def utc_timestamp():
    ''' timestamp in seconds '''
    dt = datetime.datetime.utcnow()
    return to_timestamp(dt)


def get_project_name(jira_obj, project_id):
    project = jira_obj.project(project_id)
    return project.name #.replace("Data + Analytics - ","").replace("Data + Analytics – ", "") if project else project_id


