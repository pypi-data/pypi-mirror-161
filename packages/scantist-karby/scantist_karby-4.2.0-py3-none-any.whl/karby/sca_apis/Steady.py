import logging
import os
from abc import ABC

import requests

from karby.parameter_manager import ParameterManager
from karby.sca_apis.SCAScanTool import SCAScanTool
from karby.util.helpers import project_dir_analyzer, check_mvn_version, exec_command, write_issue_report, \
    write_component_report, check_mvn_proj_info
from karby.util.models.ComponentReport import ComponentReport
from karby.util.models.IssueReport import IssueReport

FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("Eclipse Steady")

class Steady(SCAScanTool):
    def __init__(self, param_manager: ParameterManager):
        logger.info("eclipse steady only support maven now")
        super().__init__(param_manager)
        self.space_token = os.getenv("STEADY_SPACE_TOKEN", "")
        self.backend_url = os.getenv("STEADY_BACKEND_URL", "http://localhost:8033/backend")
        if not self.space_token:
            raise EnvironmentError("please provide STEADY_SPACE_TOKEN in environment variables")
        self.header = {
            "X-Vulas-Space": self.space_token,
        }

    def check_auth(self):
        """
        eclipase steady don't need authentication
        :return:
        """
        pass

    def scan_with_api(self):
        pass

    def scan_with_cmd(self):
        check_mvn_version()
        cmd = f'cd {self.project_url} &&' \
              f' mvn org.eclipse.steady:plugin-maven:3.2.0:app' \
              f' -Dvulas.core.space.token={self.space_token}' \
              f' -Dvulas.shared.backend.serviceUrl={self.backend_url}'
        logger.info(f"subprocess: {cmd}")
        result = exec_command(cmd)
        if result.get("code") != 0:
            if 'output' in result:
                logger.info(result['output'].decode())
            if 'error' in result:
                logger.info(result['error'].decode())
            raise RuntimeError("steady mvn dependency check failed.")
        return


    def get_report_by_api(self, scan_feedback=None):
        pass

    def get_report_from_cmd(self, scan_feedback=None):
        module_list = check_mvn_proj_info(self.project_url)
        total_module_list = self.get_modules()
        total_component_dict = {}
        total_issue_dict = {}
        for module in module_list:
            if not self.module_exists(total_module_list, module):
                continue
            dep_list = self.get_deps(module)
            vuln_list = self.get_vulndeps(module)
            for dep in dep_list:
                total_component_dict[dep.get_hash()] = dep
            for vul in vuln_list:
                total_issue_dict[vul.get_hash()] = vul

        # export the report to output_reports folder
        write_issue_report(
            total_issue_dict.values(), f"steady-issue-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing steady-issue-{self.project_name} to {self.output_dir}"
        )
        write_component_report(
            total_component_dict.values(), f"steady-component-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing steady-component-{self.project_name} to {self.output_dir}"
        )
        return total_component_dict.values(), total_issue_dict.values()

    def get_modules(self):
        get_module_url = f"{self.backend_url}/apps"
        logger.info(f"start to get modules from {get_module_url}")
        r = requests.get(get_module_url, headers=self.header)
        if r.status_code == 200:
            module_list_json = r.json()
            return module_list_json
        else:
            raise AttributeError(f"status code: {r.status_code}, {r.text}")

    def module_exists(self,module_list_json,module):
        group = module[0]
        artifact = module[1]
        version = module[2]
        for m in module_list_json:
            if m['group'] == group and m['artifact'] == artifact and m['version'] == version:
                return True
        return False

    def get_deps(self, module):
        group = module[0]
        artifact = module[1]
        version = module[2]
        get_deps_url = f"{self.backend_url}/apps/{group}/{artifact}/{version}/deps"
        logger.info(f"start to get modules from {get_deps_url}")
        r = requests.get(get_deps_url, headers=self.header)
        dep_list = []
        if r.status_code == 200:
            deps_list_json = r.json()
            for dep in deps_list_json:
                if dep['scope'] in ['TEST', 'SYSTEM','PROVIDED']:
                    continue
                if not dep['lib']['digestVerificationUrl']:
                    continue
                tmp_library = f"{dep['lib']['libraryId']['group']}:{dep['lib']['libraryId']['artifact']}"
                tmp_version = dep['lib']['libraryId']['version']
                tmp_dep = ComponentReport(tmp_library, tmp_version)
                dep_list.append(tmp_dep)
            return dep_list
        else:
            raise AttributeError(f"status code: {r.status_code}, {r.text}")

    def get_vulndeps(self, module):
        group = module[0]
        artifact = module[1]
        version = module[2]
        get_vuln_dep_url = f"{self.backend_url}/apps/{group}/{artifact}/{version}/vulndeps"
        logger.info(f"start to get modules from {get_vuln_dep_url}")
        r = requests.get(get_vuln_dep_url, headers=self.header)
        vulndep_list = []
        if r.status_code == 200:
            vulndeps_list_json = r.json()
            for dep in vulndeps_list_json:
                if dep['dep']['scope'] in ['TEST', 'PROVIDED', 'SYSTEM']:
                    continue
                if not dep['dep']['lib']['digestVerificationUrl']:
                    continue
                tmp_library = f"{dep['dep']['lib']['libraryId']['group']}:{dep['dep']['lib']['libraryId']['artifact']}"
                tmp_version = dep['dep']['lib']['libraryId']['version']
                tmp_public_id = dep['bug']['bugId'] if dep['bug']['bugId'] else dep['bug']['bugIdAlt']
                tmp_vulndep = IssueReport(tmp_library, tmp_version,tmp_public_id)
                vulndep_list.append(tmp_vulndep)
            return vulndep_list
        else:
            raise AttributeError(f"status code: {r.status_code}, {r.text}")