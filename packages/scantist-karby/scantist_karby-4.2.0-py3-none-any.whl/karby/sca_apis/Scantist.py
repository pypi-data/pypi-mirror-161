import csv
import logging
import os
import shutil
import re

from karby.parameter_manager import ParameterManager
from karby.sca_apis.SCAScanTool import SCAScanTool
from karby.util.helpers import exec_command, project_dir_analyzer, github_url_analyzer, make_zip, name_tag_analyzer, \
    write_component_report, write_issue_report
from karby.util.models.ComponentReport import ComponentReport
from karby.util.models.IssueReport import IssueReport

FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("Scantist")


class Scantist(SCAScanTool):
    def __init__(self, param_manager: ParameterManager):
        super().__init__(param_manager)
        self.scantist_email = os.getenv("SCANTIST_EMAIL", "")
        self.scantist_pass = os.getenv("SCANTIST_PSW", "")
        self.scantist_base_url = os.getenv(
            "SCANTIST_BASEURL", "https://api.scantist.io/"
        )
        self.scantist_home = os.getenv("SCANTIST_SBD_HOME", "")

        # self.check_auth()
        if not self.project_name:
            if self.scan_type == "docker":
                self.project_name = name_tag_analyzer(self.project_url)
            else:
                self.project_name = project_dir_analyzer(self.project_url)

    def check_auth(self):
        cmd = f"java -jar {self.scantist_home} " \
              f"--auth " \
              f"-serverUrl {self.scantist_base_url} " \
              f"-email {self.scantist_email} " \
              f"-password {self.scantist_pass}"
        logger.info(f"subprocess: {cmd}")
        result = exec_command(cmd)
        if result.get("code") != 0:
            if result.get("error") != None:
                logger.error(result.get("error").decode())
            else:
                logger.error(result)
            raise

    def scan_with_api(self):
        self.options += " -airgap "
        return self.scan_with_cmd()

    def scan_with_cmd(self):
        if not os.path.exists(self.project_url):
            logger.error(f"trigger_scan|skip, no files found for {self.project_url}")
            raise
        if "-airgap" in self.options:
            cmd = f"java -jar {self.scantist_home} " \
                  f"-airgap " \
                  f"--debug " \
                  f"-working_dir {self.project_url} " \
                  f"-report csv " \
                  f"-report_path {self.output_dir} "
        else:
            cmd = f"java -jar {self.scantist_home} " \
                  f"--debug " \
                  f"-working_dir {self.project_url} " \
                  f"-report csv " \
                  f"-report_path {self.output_dir} "
        if self.options:
            cmd = cmd + self.options
        logger.info(f"subprocess: {cmd}")
        result = exec_command(cmd)
        if result.get("code") != 0:
            if 'output' in result:
                logger.error(result['output'].decode())
            if 'error' in result:
                logger.error(result['error'].decode())
            raise RuntimeError("executing command failed")
        cmd_output = result.get("output").decode()
        logger.info(cmd_output)
        return cmd_output

    def docker_scan(self):
        cmd = f"java -jar {self.scantist_home} " \
              f"--cliScan " \
              f"-scanType docker " \
              f"-dockerImageNameTag {self.project_url} " \
              f"-report csv " \
              f"-report_path {self.output_dir} " \
              f"--bom_detect "
        logger.info(f"subprocess: {cmd}")
        result = exec_command(cmd)
        if result.get("code") != 0:
            if result.get("error") != None:
                logger.error(result.get("error").decode())
            else:
                logger.error(result)
            raise
        cmd_output = result.get("output").decode()
        logger.info(cmd_output)
        return cmd_output

    def get_docker_scan_result(self, scan_feedback=None):
        return self.get_report_from_cmd(scan_feedback)

    def get_report_by_api(self, scan_feedback=None):
        return self.get_report_from_cmd(scan_feedback)

    def get_report_from_cmd(self, scan_feedback=None):
        if not scan_feedback:
            raise AttributeError("currently, cannot use skip scan for scantist.")
        # get scan id from output
        component_list_report = re.search(
            r"Saving component report to (.+)\n", scan_feedback
        ).group(1)
        issue_list_report = re.search(
            r"Saving vulnerability report to (.+)\n", scan_feedback
        ).group(1)
        if not os.path.isfile(component_list_report):
            raise Exception(f"component report not find in {component_list_report}")
        if not os.path.isfile(issue_list_report):
            raise Exception(f"issue report not find in {issue_list_report}")
        logger.info(f"issue report found in {issue_list_report}")
        logger.info(f"component report found in {component_list_report}")

        total_component_dict = {}
        total_issue_dict = {}

        component_report = open(component_list_report, 'r')
        component_reader = csv.DictReader(component_report)
        for component in component_reader:
            match_status = component['Status']
            if match_status == "un-matched":
                continue
            scope = component['Scope'].split(' ')[0]
            language = component['Language']
            library_name = component['Library']
            library_version = component['Library Version']
            # a true dependency must have scope, filter all virtual nodes and unwanted scopes
            if scope.lower() in ['-', 'test', 'system', 'provided']:
                continue
            # filter all other deps such as js
            if language.lower() not in ['java']:
                continue
            tmp = ComponentReport(library_name, library_version)
            total_component_dict[tmp.get_hash()] = tmp

        issue_report = open(issue_list_report, 'r')
        issue_reader = csv.DictReader(issue_report)
        for issue in issue_reader:
            match_status = component['Status']
            if match_status == "un-matched":
                continue
            scope = component['Scope']
            language = component['Language']
            # a true dependency must have scope, filter all virtual nodes and unwanted scopes
            if scope.lower() in ['-', 'test', 'system', 'provided']:
                continue
            # filter all other deps such as js
            if language.lower() not in ['java']:
                continue
            library_name = issue['Library']
            library_version = issue['Library Version']
            public_id = issue['Public ID']
            tmp = IssueReport(library_name, library_version, public_id)
            total_issue_dict[tmp.get_hash()] = tmp


        # export the report to output_reports folder
        write_issue_report(
            total_issue_dict.values(), f"scantist-issue-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing scantist-issue-{self.project_name} to {self.output_dir}"
        )
        write_component_report(
            total_component_dict.values(), f"scantist-component-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing scantist-component-{self.project_name} to {self.output_dir}"
        )
        # shutil.rmtree(os.path.dirname(os.path.dirname(component_list_report)))
        return total_component_dict.values(), total_issue_dict.values()

    def remove_dummy(self, report_path, output_path):
        csvfile = open(report_path, mode='r', newline='')
        csvreader = csv.reader(csvfile)
        final_lines = []
        for line in csvreader:
            if "un-matched" not in line:
                final_lines.append(line)

        outfile = open(output_path, mode='w', newline='')
        csvwriter = csv.writer(outfile)
        csvwriter.writerows(final_lines)
        csvfile.close()
        outfile.close()

