from ia.common.helpers import is_num, to_num, to_str

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class Sprint(object):
    def __init__(self, data_string):
        """
        data_string: string
            A serialized data for the sprint read from Jira API.

            Example:
            data_string = 'com.atlassian.greenhopper.service.sprint.Sprint@28c838e2[id=8455,rapidViewId=3498,state=CLOSED,name=Retention Sprint 24,startDate=2020-04-22T13:58:48.202Z,endDate=2020-05-06T13:58:00.000Z,completeDate=2020-05-06T14:11:07.481Z,activatedDate=2020-04-22T13:58:48.202Z,sequence=8455,goal=Churn Journey demo for Account Balance]'
        """
        instance_data = data_string.split("[")
        self._instance_id = instance_data[0]
        attr_string = instance_data[1].replace("]", "")

        # sprint_attributes = dict(
        #     (x.strip(), y.strip())
        #     for x, y in (param.split("=") for param in attr_string.split(","))
        # )
        splitted = attr_string.split(",")

        sprint_attributes = {}
        last_key = None
        for kv in splitted:
            try:
                params = kv.split("=")
                if len(params) == 2:
                    last_key = params[0]
                    value = (
                        to_num(params[1]) if is_num(params[1]) else to_str(params[1])
                    )
                    sprint_attributes[last_key] = value
                if last_key and len(params) == 1:
                    val = sprint_attributes[last_key]
                    val += "," + to_str(params[0])
                    sprint_attributes[last_key] = val
            except Exception as e:
                print(f"{e}\nError during parsing: {kv}")
        self.__dict__.update(sprint_attributes)
