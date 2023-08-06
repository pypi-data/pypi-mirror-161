import logging
import os
import re
import time

import requests as requests

from karby.sca_apis.SCAScanTool import SCAScanTool
from karby.util.helpers import (
    github_url_analyzer,
    write_issue_report,
    write_component_report,
    exec_command,
    project_dir_analyzer,
)
from karby.util.models.ComponentReport import ComponentReport
from karby.util.models.IssueReport import IssueReport

FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("Snyk")

"""
This method is deprecated.
The whole logic is based on snyk api, but now api is only available for ultimate user. 
"""
class Snyk(SCAScanTool):
    def __init__(self, param_manager):
        super().__init__(param_manager)
        self.host = "https://snyk.io/api/v1/"
        self.user_token = os.getenv("SNYK_USR_TOKEN", "")
        self.organization_id = os.getenv("SNYK_ORG_ID", "")
        self.interaction_id = os.getenv("SNYK_INTEGRATION_ID", "")
        self.header = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"token {self.user_token}",
        }
        self.check_auth()


    def check_auth(self):
        if self.scan_type == "upload":
            # https: // snyk.docs.apiary.io /  # reference/users/user-details
            r = requests.get(f"{self.host}user/me", headers=self.header)
            if r.status_code == 200:
                user_name = r.json()["username"]
                logger.info(f"Authenticate success! Hello, {user_name}")
                if not self.organization_id or not self.interaction_id:
                    raise AttributeError(
                        "organization id or interaction id is empty, please set them in the environment file."
                    )
                return True
            elif r.status_code == 401:
                raise AttributeError("fail to authenticate, please check user token")
            else:
                raise AttributeError(f"status code: {r.status_code}, {r.text}")
        else:
            output = exec_command("snyk version")
            if "error" in output:
                raise EnvironmentError(
                    "can not find snyk environment. Please config snyk environment locally."
                )
            logger.info(f"snyk version: {output['output'].decode()}")
            output = exec_command(f"snyk auth {self.user_token}")
            if output["code"] != 0:
                raise EnvironmentError(output)
            logger.info(output["output"].decode())
        return True

    def scan_with_api(self):
        # https://snyk.docs.apiary.io/#reference/integrations/import-projects/import
        # check project web url
        owner, name = github_url_analyzer(self.project_url)
        if not self.project_name:
            self.project_name = name
        values = f"""
          {{
            "target": {{
              "owner": "{owner}",
              "name": "{name}",
              "branch": "master"
            }}
          }}
        """
        import_url = f"{self.host}org/{self.organization_id}/integrations/{self.interaction_id}/import"
        r = requests.post(import_url, headers=self.header, data=values)
        logger.debug(f"posting to {import_url}")
        if r.status_code != 201:
            raise AttributeError(f"import project {owner}/{name} failed. {r.json()}")
        logger.info(f"successfully import {owner}/{name}, {r.headers['location']}.")
        return r.headers["location"]

    def scan_with_cmd(self):
        # check project dir
        project_folder_name = project_dir_analyzer(self.project_url)
        if not self.project_name:
            self.project_name = project_folder_name
        current_dir = os.getcwd()
        cmd = f"cd {self.project_url} && snyk monitor {self.options}"
        logger.info(f"execute: {cmd} at {os.getcwd()}")
        output = exec_command(cmd)
        logger.info("scan finished")
        if output["code"] != 0:
            raise Exception(output)
        std_output = output["output"].decode()
        m = re.findall(
            "https://app.snyk.io/org/[0-9a-zA-Z]*/project/([0-9a-zA-Z\-]*)/history/[0-9a-zA-Z\-]*",
            std_output,
        )
        project_id_list = m if m else None
        exec_command(f"cd {current_dir}")
        return project_id_list

    def docker_scan(self):
        # check project dir
        if self.image_name_tag is None:
            ValueError("image name tag is empty. Please specify by adding -image_name_tag")
        cmd = f"snyk container monitor {self.image_name_tag}"
        logger.info(f"execute: {cmd}")
        output = exec_command(cmd)
        logger.info("scan finished")
        if output["code"] != 0:
            raise Exception(output)
        std_output = output["output"].decode()
        m = re.findall(
            "https://app.snyk.io/org/[0-9a-zA-Z]*/project/([0-9a-zA-Z\-]*)/history/[0-9a-zA-Z\-]*",
            std_output,
        )
        project_id_list = m if m else None
        return project_id_list

    def get_docker_scan_result(self, project_id_list=None):
        if not project_id_list:
            ValueError("project_id is empty")
        total_component_list = []
        total_issue_list = []
        for project_id in project_id_list:
            logger.info(f"processing on project: {project_id}")
            total_component_list.extend(self.get_dependencies_by_project_id(project_id))
            total_issue_list.extend(self.get_issues_by_project_id(project_id))
        # export the report to output_reports folder
        write_issue_report(
            total_issue_list, f"snyk-issue-{self.image_name_tag}", self.output_dir
        )
        logger.info(
            f"finish writing snyk-issue-{self.image_name_tag} to {self.output_dir}"
        )
        write_component_report(
            total_component_list, f"snyk-component-{self.image_name_tag}", self.output_dir
        )
        logger.info(
            f"finish writing snyk-component-{self.image_name_tag} to {self.output_dir}"
        )
        return total_component_list, total_issue_list

    def get_report_by_api(self, scan_feedback=None):
        # periodically get the status of scanning project
        r_project_status = requests.get(scan_feedback, headers=self.header)
        timeout_count = 0
        while r_project_status.json()["logs"][0]["status"] == "pending":
            r_project_status = requests.get(scan_feedback, headers=self.header)
            logger.info("alive, project scanning...")
            timeout_count += 1
            if timeout_count >= 30:
                raise Exception("scan time out. Please check on snyk web page")
            time.sleep(60)
        logger.info("project scan finished")

        # after finish scanning, get all the project url from project status report
        available_subproject_id = []
        for subproject in r_project_status.json()["logs"][0]["projects"]:
            sub_project_id = subproject["projectUrl"].split("/")[-1]
            if len(sub_project_id) != 0:
                available_subproject_id.append(sub_project_id)

        # retrieve dependencies and issues by project id
        total_component_list = []
        total_issue_list = []
        for sub_project_id in available_subproject_id:
            component_list = self.get_dependencies_by_project_id(sub_project_id)
            issue_list = self.get_issues_by_project_id(sub_project_id)
            total_component_list.extend(component_list)
            total_issue_list.extend(issue_list)

        # export the report to output_reports folder
        write_issue_report(
            total_issue_list, f"snyk-issue-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing snyk-issue-{self.project_name} to {self.output_dir}"
        )
        write_component_report(
            total_component_list, f"snyk-component-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing snyk-component-{self.project_name} to {self.output_dir}"
        )
        return total_component_list, total_issue_list

    def get_report_from_cmd(self, project_id_list=None):
        if not project_id_list:
            ValueError("project_id is empty")
        total_component_list = []
        total_issue_list = []
        for project_id in project_id_list:
            logger.info(f"processing on project: {project_id}")
            total_component_list.extend(self.get_dependencies_by_project_id(project_id))
            total_issue_list.extend(self.get_issues_by_project_id(project_id))
        # export the report to output_reports folder
        write_issue_report(
            total_issue_list, f"snyk-issue-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing snyk-issue-{self.project_name} to {self.output_dir}"
        )
        write_component_report(
            total_component_list, f"snyk-component-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing snyk-component-{self.project_name} to {self.output_dir}"
        )
        return total_component_list, total_issue_list

    def get_dependencies_by_project_id(self, project_id):
        """
        get componets and parse them to the `componentReport` structure
        :param project_id:
        :return:
        """
        # https://snyk.docs.apiary.io/#reference/projects/project-dependency-graph/get-project-dependency-graph
        component_list = []
        project_dep_url = (
            f"{self.host}org/{self.organization_id}/project/{project_id}/dep-graph"
        )
        r = requests.get(project_dep_url, headers=self.header)
        if r.status_code != 200:
            raise AttributeError(f"fail to get dep-graph of {project_id}. {r.json()}")
        sub_project_components = r.json()["depGraph"]["pkgs"]
        for sub_component in sub_project_components:
            sub_p_name = sub_component["info"]["name"]
            if ":" in sub_p_name:
                group, artifact = sub_p_name.split(":")
                name = f"{artifact} {group}"
            else:
                name = sub_p_name
            if "version" in sub_component["info"]:
                sub_p_version = sub_component["info"]["version"]
            else:
                sub_p_version = "N.A."
            tmp_component = ComponentReport(name, sub_p_version)
            component_list.append(tmp_component)
        return component_list

    def get_issues_by_project_id(self, project_id):
        """
        get issues and parse them to the `issueReport` structure
        :param project_id:
        :return:
        """
        issue_list = []
        project_dep_url = f"{self.host}org/{self.organization_id}/project/{project_id}/aggregated-issues"
        values = """
          {
            "includeDescription": false,
            "filters": {
              "severities": [
                "high",
                "medium",
                "low"
              ],
              "exploitMaturity": [
                "mature",
                "proof-of-concept",
                "no-known-exploit",
                "no-data"
              ],
              "types": [
                "vuln",
                "license"
              ],
              "ignored": false,
              "patched": false,
              "priority": {
                "score": {
                  "min": 0,
                  "max": 1000
                }
              }
            }
          }
        """
        r = requests.post(project_dep_url, headers=self.header, data=values)
        if r.status_code != 200:
            raise AttributeError(f"fail to get dep-graph of {project_id}. {r.json()}")
        sub_project_issues = r.json()["issues"]
        for issue in sub_project_issues:
            issue_project_name = issue["pkgName"]
            # it returns a list, may need to create an object for each version?
            issue_project_version = issue["pkgVersions"][0]
            if "identifiers" in issue["issueData"]:
                public_id_list = issue["issueData"]["identifiers"]["CVE"]
            else:
                public_id_list = [issue["id"]]
            for public_id in public_id_list:
                tmp_issue = IssueReport(
                    issue_project_name, issue_project_version, public_id
                )
                issue_list.append(tmp_issue)
        return issue_list

