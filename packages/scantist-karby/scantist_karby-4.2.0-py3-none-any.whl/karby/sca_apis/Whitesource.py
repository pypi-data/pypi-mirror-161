import os
import json
import shutil
import requests
import tempfile

from karby.sca_apis.SCAScanTool import SCAScanTool
from karby.util.helpers import (
    write_issue_report,
    write_component_report,
    exec_command,
    project_dir_analyzer,
)
from karby.util.models.ComponentReport import ComponentReport
from karby.util.models.IssueReport import IssueReport

import logging

FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("WhiteSource")


class Whitesource(SCAScanTool):
    def __init__(self, param_manager):
        super().__init__(param_manager)
        if not self.project_name:
            self.project_name = project_dir_analyzer(self.project_url)
        # Mandatory env var
        # TODO: check?
        self.apikey = os.getenv("WHITESOURCE_API_KEY", "")
        self.userkey = os.getenv("WHITESOURCE_USER_KEY", "")
        self.product_name = os.getenv("WHITESOURCE_PRODUCT_NAME", "")
        # host

        self.host = "https://saas.whitesourcesoftware.com/api/v1.3"
        self.header = {"Content-Type": "application/json", "charset": "UTF-8"}
        # cmd mode
        if self.scan_type == "cmd":
            self.path_ws_jar = os.getenv("PATH_TO_WHITESOURCE_JAR", "")
            self.path_ws_cfg = os.path.join(os.getcwd(), os.getenv("PATH_TO_WHITESOURCE_CFG", ""))
            if self.path_ws_cfg == "":
                cfg_dir = os.path.dirname(self.path_ws_jar)
                cfg_fn = (
                    os.path.splitext(os.path.basename(self.path_ws_jar))[0] + ".config"
                )
                self.path_ws_cfg = os.path.join(cfg_dir, cfg_fn)
            # make tmp dir for whitesource
            # self.tmp_dir = tempfile.mkdtemp()
            self.tmp_dir = self.project_url
        # verify keys
        self.check_auth()

    def check_auth(self):
        # verify apikey & userkey
        # request products
        logger.info(f"Finding product {self.product_name}...")
        payload = f"""
          {{
            "requestType": "getAllProducts",
            "userKey": "{self.userkey}",
            "orgToken": "{self.apikey}"
          }}
        """
        res = requests.post(self.host, headers=self.header, data=payload)
        js = res.json()
        if (
            js.__contains__("message")
            and js["message"] == "Success"
            and js.__contains__("products")
        ):
            found_flag = False
            for product in js["products"]:
                if product["productName"] == self.product_name:
                    self.product_token = product["productToken"]
                    found_flag = True
                    logger.info("Done.")
                    break
            if not found_flag:
                raise Exception(f"Product {self.product_name} not found.")
        else:
            if js.__contains__("errorCode") and js.__contains__("errorMessage"):
                if js["errorCode"] == 0x1389:
                    raise Exception(
                        f"Fail to request products. Error Code: {js['errorCode']} -- {js['errorMessage']}. Please check your user key."
                    )
                elif js["errorCode"] == 0x3EA:
                    raise Exception(
                        f"Fail to request products. Error Code: {js['errorCode']} -- {js['errorMessage']}. Please check your api key."
                    )
                else:
                    raise Exception(
                        f"Fail to request products. Error Code: {js['errorCode']} -- {js['errorMessage']}"
                    )
            else:
                raise Exception("Fail to request products.")
        return

    def scan_with_api(self):
        # request projects
        logger.info(f"Finding project {self.project_name}...")
        payload = f"""
          {{
            "requestType": "getAllProjects",
            "userKey": "{self.userkey}",
            "productToken": "{self.product_token}"
          }}
        """
        res = requests.post(self.host, headers=self.header, data=payload)
        js = res.json()
        if (
            js.__contains__("message")
            and js["message"] == "Success"
            and js.__contains__("projects")
        ):
            found_flag = False
            for prj in js["projects"]:
                if prj["projectName"] == self.project_name:
                    self.project_token = prj["projectToken"]
                    found_flag = True
                    logger.info("Done.")
                    break
            if not found_flag:
                raise Exception(f"Project {self.project_name} not found.")
        else:
            if js.__contains__("errorCode") and js.__contains__("errorMessage"):
                raise Exception(
                    f"Fail to request projects. Error Code: {js['errorCode']} -- {js['errorMessage']}"
                )
            else:
                raise Exception("Fail to request projects.")
        # request issue json
        payload_issue = f"""
          {{
            "requestType": "getProjectVulnerabilityReport",
            "userKey": "{self.userkey}",
            "projectToken": "{self.project_token}",
            "format": "json"
          }}
        """
        logger.info("Requesting issue report...")
        res_issue = requests.post(self.host, headers=self.header, data=payload_issue)
        logger.info("Done.")
        js_issue = res_issue.json()
        # request component json
        payload_component = f"""
          {{
            "requestType": "getProjectInventory",
            "userKey": "{self.userkey}",
            "projectToken": "{self.project_token}",
            "includeInHouseData" : true
          }}
        """
        logger.info("Requesting component report...")
        res_component = requests.post(
            self.host, headers=self.header, data=payload_component
        )
        logger.info("Done.")
        js_component = res_component.json()
        ret = {"js_issue": js_issue, "js_component": js_component}
        return ret

    def scan_with_cmd(self):
        # scan
        ws_args = (
            f"-c {self.path_ws_cfg}",
            f"-project {self.project_name}",
            f"-product {self.product_name}",
            f"-apiKey {self.apikey}",
            f"-userKey {self.userkey}",
            f"-d {self.project_url}",
        )
        cmd = f'java -jar {self.path_ws_jar} {" ".join(ws_args)}'
        logger.info(f"Scanning {self.project_name}...")
        logger.info(f"execute: {cmd}")
        output = exec_command(cmd, self.tmp_dir)
        if output["code"] != 0:
            raise Exception(f"scan failed. error: {output}")
        logger.info("Done." + output["output"].decode("utf-8").split("\n")[-1])
        return

    def get_report_by_api(self, scan_feedback=None):
        component_list = self.get_component_list(scan_feedback["js_component"])
        issue_list = self.get_issues_by_vulnerability(scan_feedback["js_issue"])
        # export the report to output_reports folder
        write_issue_report(
            issue_list, f"whitesource-issue-{self.project_name}", self.output_dir
        )
        logger.info(
            f"Finish writing whitesource-issue-{self.project_name} to {self.output_dir}"
        )
        write_component_report(
            component_list,
            f"whitesource-component-{self.project_name}",
            self.output_dir,
        )
        logger.info(
            f"Finish writing whitesource-component-{self.project_name} to {self.output_dir}"
        )
        pass

    def get_report_from_cmd(self, scan_feedback=None):
        # get path list of report file
        report_file_paths = []
        for f in os.listdir(os.path.join(self.tmp_dir, "whitesource")):
            if f.endswith("scan_report.json"):
                report_file_paths.append(os.path.join(self.tmp_dir, "whitesource", f))
        # get component&issue list
        component_list = {}
        issue_list = {}
        for report_file_path in report_file_paths:
            with open(report_file_path) as report_file:
                json_data = json.load(report_file)
                sub_component_list = self.get_component_list(json_data)
                sub_issue_list = self.get_issues_by_project_inventory(json_data)
                for comp in sub_component_list:
                    component_list[comp.get_hash()] = comp
                for issue in sub_issue_list:
                    issue_list[issue.get_hash()] = issue
        # export the report to output_reports folder
        write_issue_report(
            issue_list.values(), f"whitesource-issue-{self.project_name}", self.output_dir
        )
        logger.info(
            f"Finish writing whitesource-issue-{self.project_name} to {self.output_dir}"
        )
        write_component_report(
            component_list.values(),
            f"whitesource-component-{self.project_name}",
            self.output_dir,
        )
        logger.info(
            f"Finish writing whitesource-component-{self.project_name} to {self.output_dir}"
        )
        logger.info("Removing temp folder")
        # shutil.rmtree(self.tmp_dir)
        return

    def get_component_list(self, json_data):
        component_list = []
        for library in json_data["libraries"]:
            l_type = library["type"]
            if l_type == "MAVEN_ARTIFACT":
                l_name = f"{library['groupId']}:{library['artifactId']}"
            else:
               continue
            l_version = library["version"]
            tmp_component = ComponentReport(l_name.strip(), l_version)
            if library.__contains__("outdatedModel"):
                tmp_component.set_field(
                    "Latest Version", library["outdatedModel"]["newestVersion"]
                )
            if library.__contains__("licenses"):
                license_name = []
                for l in library["licenses"]:
                    license_name.append(l["name"])
                tmp_component.set_field("License", f'{", ".join(license_name)}')
            if library.__contains__("vulnerabilities"):
                vulner_name = []
                for v in library["vulnerabilities"]:
                    vulner_name.append(v["name"])
                tmp_component.set_field("Vulnerabilities", len(vulner_name))
                tmp_component.set_field(
                    "Vulnerability List", f'{", ".join(vulner_name)}'
                )
            component_list.append(tmp_component)
        return component_list

    def get_issues_by_vulnerability(
        self, json_data, v_lib_name, v_lib_verision):
        issue_list = []
        for v in json_data["vulnerabilities"]:
            v_name = v["name"]
            tmp_issue = IssueReport(v_lib_name, v_lib_verision, v_name)
            if v.__contains__("severity"):
                tmp_issue.set_field("Score", v["severity"])
            if v.__contains__("description"):
                tmp_issue.set_field("Description", v["description"])
            if v.__contains__("type"):
                tmp_issue.set_field("Issue Type", v["type"])
            issue_list.append(tmp_issue)
        return issue_list

    def get_issues_by_project_inventory(self, json_data):
        issue_list = []
        for library in json_data["libraries"]:
            l_type = library["type"]
            if l_type == "MAVEN_ARTIFACT":
                l_name = f"{library['groupId']}:{library['artifactId']}"
            else:
                continue
            l_version = library["version"]
            tmp_issue_list = self.get_issues_by_vulnerability(
                library, l_name, l_version
            )
            issue_list.extend(tmp_issue_list)
        return issue_list
