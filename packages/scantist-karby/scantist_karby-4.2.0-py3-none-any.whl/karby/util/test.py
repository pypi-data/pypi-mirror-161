import re

std_output = '''
Monitoring /var/jenkins_home/jobs/ModuloTech-Test/workspace (modulotech)...

Explore this snapshot at 

Notifications about newly disclosed issues related to these dependencies will be emailed to you.


-------------------------------------------------------

Monitoring /var/jenkins_home/jobs/ModuloTech-Test/workspace (modulotech/app)...

Explore this snapshot at  

Notifications about newly disclosed issues related to these dependencies will be emailed to you.
'''
m = re.findall(
    "https://app.snyk.io/org/[0-9a-zA-Z]*/project/([0-9a-zA-Z\-]*)/history/([0-9a-zA-Z\-]*)",
    std_output,
)
project_id_list = m if m else None
print(project_id_list)