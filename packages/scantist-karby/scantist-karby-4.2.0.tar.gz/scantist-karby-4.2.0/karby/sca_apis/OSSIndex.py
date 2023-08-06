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
logger = logging.getLogger("OSSIndex")

class OSSIndex(SCAScanTool):
    def __init__(self, param_manager: ParameterManager):
        super().__init__(param_manager)
        self.report_json = os.path.join(self.project_url, 'target', 'audit-report.json')
        self.origin_pom = os.path.join(self.project_url, 'pom.xml')

    def check_auth(self):
        """
        OSSIndex don't need authentication
        :return:
        """
        pass

    def scan_with_api(self):
        logger.info("tool do not have api scan, use cmd scan instead")
        self.scan_with_cmd()

    def scan_with_cmd(self):
        check_mvn_version()
        cmd = f'cd {self.project_url} &&' \
              f'  mvn org.sonatype.ossindex.maven:ossindex-maven-plugin:audit-aggregate' \
              f' -Dossindex.fail=false' \
              f' -Dossindex.reportFile=target/audit-report.json'
        logger.info(f"subprocess: {cmd}")
        result = exec_command(cmd)
        if result.get("code") != 0:
            if 'output' in result:
                logger.info(result['output'].decode())
            if 'error' in result:
                logger.info(result['error'].decode())
            raise RuntimeError("owasp mvn dependency check failed.")
        return

    def get_report_by_api(self, scan_feedback=None):
        """
        logic is exactly the same as get report from cmd
        :param scan_feedback:
        :return:
        """
        self.parse_audit_json()

    def get_report_from_cmd(self, scan_feedback=None):
        self.parse_audit_json()

    def parse_audit_json(self):
        if not os.path.isfile(self.report_json):
            raise RuntimeError(f"autit.json not found in {self.report_json}")
        file = open(self.report_json, 'r')
        audit_report = json.loads(file.read())
        component_list = {}
        issue_list = []
        for dependency in audit_report['reports']:
            dependency_detail = audit_report['reports'][dependency]
            scope = dependency.split(':')[-1]
            if scope in ['test', 'provided', 'system']:
               continue
            assert 'coordinates' in dependency_detail
            group, artifact, version = resolve_package_id(dependency_detail['coordinates'])
            cmp_name = f'{group}:{artifact}'
            tmp_cmp = ComponentReport(cmp_name, version)
            component_list[tmp_cmp.get_hash()] = tmp_cmp
            if 'vulnerabilities' in dependency_detail:
                vul_list = dependency_detail['vulnerabilities']
                for vul in vul_list:
                    tmp_cmp.get_vul_list().append(vul['displayName'])
                    tmp_issue = IssueReport(cmp_name, version, vul['displayName'])
                    issue_list.append(tmp_issue)
        write_issue_report(
            issue_list, f"ossindex-issue-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing ossindex-issue-{self.project_name} to {self.output_dir}"
        )
        write_component_report(
            list(component_list.values()), f"ossindex-component-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing ossindex-component-{self.project_name} to {self.output_dir}"
        )
