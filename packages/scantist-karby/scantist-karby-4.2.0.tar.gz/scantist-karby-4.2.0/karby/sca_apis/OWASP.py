import json
import logging
import os

from karby.parameter_manager import ParameterManager
from karby.sca_apis.SCAScanTool import SCAScanTool
from karby.util.helpers import exec_command, resolve_package_id, write_issue_report, write_component_report, \
     check_mvn_version
from karby.util.models.ComponentReport import ComponentReport
from karby.util.models.IssueReport import IssueReport

FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("OWASP")

class OWASP(SCAScanTool):
    def __init__(self, param_manager: ParameterManager):
        super().__init__(param_manager)
        self.report_json = os.path.join(self.project_url, 'target', 'dependency-check-report.json')
        self.origin_pom = os.path.join(self.project_url, 'pom.xml')
        self.owasp_script = os.getenv("OWASP_SH", "")

    def check_auth(self):
        """
        OWASP don't need authentication
        :return:
        """
        pass

    def scan_with_api(self):
        if not self.owasp_script:
            raise AttributeError("please specify owasp script path to OWASP_SH in environment")
        cmd = f"{self.owasp_script} -s {self.project_url} -out {self.project_url} -f JSON --disableAssembly"
        logger.info(f"subprocess: {cmd}")
        result = exec_command(cmd)
        if result.get("code") != 0:
            if 'output' in result:
                logger.info(result['output'].decode())
            if 'error' in result:
                logger.info(result['error'].decode())
            raise RuntimeError("owasp mvn dependency check failed.")
        return

    def scan_with_cmd(self):
        logger.info("OWASP cmd scan is only applicable for Maven. For other language, pls use upload scan.")
        check_mvn_version()
        cmd = f'cd {self.project_url} &&' \
              f' mvn org.owasp:dependency-check-maven:aggregate' \
              f' -DassemblyAnalyzerEnabled=false' \
              f' -DnugetconfAnalyzerEnabled=false' \
              f' -DnuspecAnalyzerEnabled=false' \
              f' -DskipTestScope=true' \
              f' -DskipProvidedScope=true' \
              f' -DskipSystemScope=true' \
              f' -Dformat=JSON'
        logger.info(f"subprocess: {cmd}")
        result = exec_command(cmd)
        if result.get("code") != 0:
            if 'output' in result:
                logger.info(result['output'].decode())
            if 'error' in result:
                logger.info(result['error'].decode())
        return

    def get_report_by_api(self, scan_feedback=None):
        """
        logic is exactly the same as get report from cmd
        :param scan_feedback:
        :return:
        """
        self.parse_dependency_json()

    def get_report_from_cmd(self, scan_feedback=None):
        self.parse_dependency_json()

    def parse_dependency_json(self):
        if not os.path.isfile(self.report_json):
            self.report_json = os.path.join(self.project_url, 'dependency-check-report.json')
        if not os.path.isfile(self.report_json):
            raise RuntimeError(f"dependency-check-report.json not found in {self.report_json}")
        file = open(self.report_json, 'r')
        dc_report = json.loads(file.read())
        component_list = {}
        issue_list = []
        for dependency in dc_report['dependencies']:
            # only has "packages", then we can tell it is matched
            # only accept maven package
            if "packages" in dependency:
                package_id = dependency['packages'][-1]['id']
                if not package_id.startswith("pkg:maven"):
                    continue
                group_id, artifact_id, version = resolve_package_id(package_id)
            else:
                continue
            component_report_lib = f'{group_id}:{artifact_id}'
            issue_report_lib = f'{group_id}:{artifact_id}'
            tmp_component = ComponentReport(component_report_lib, version)
            if 'sha256' in dependency:
                sha256 = dependency['sha256']
            else:
                sha256 = tmp_component.get_hash()
            component_list[sha256] = tmp_component
            if 'vulnerabilities' in dependency:
                vul_list = dependency['vulnerabilities']
                for vul in vul_list:
                    tmp_component.get_vul_list().append(vul['name'])
                    tmp_issue = IssueReport(issue_report_lib, version, vul['name'])
                    issue_list.append(tmp_issue)
            if 'relatedDependencies' in dependency:
                for relatDep in dependency['relatedDependencies']:
                    if "packageIds" in relatDep:
                        package_id = relatDep['packageIds'][-1]['id']
                        if not package_id.startswith("pkg:maven"):
                            continue
                        group_id, artifact_id, version = resolve_package_id(package_id)
                        tmp_component = ComponentReport(f'{group_id}:{artifact_id}', version)
                        if 'sha256' in relatDep:
                            sha256 = relatDep['sha256']
                        else:
                            sha256 = tmp_component.get_hash()
                        component_list[sha256] = tmp_component
        write_issue_report(
            issue_list, f"owasp-issue-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing owasp-issue-{self.project_name} to {self.output_dir}"
        )
        write_component_report(
            list(component_list.values()), f"owasp-component-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing owasp-component-{self.project_name} to {self.output_dir}"
        )
