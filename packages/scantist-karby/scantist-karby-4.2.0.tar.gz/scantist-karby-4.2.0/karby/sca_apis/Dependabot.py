import json
import logging
import os
import requests

from karby.parameter_manager import ParameterManager
from karby.sca_apis.SCAScanTool import SCAScanTool
from karby.util.helpers import resolve_package_id, write_issue_report, write_component_report
from karby.util.models.ComponentReport import ComponentReport
from karby.util.models.IssueReport import IssueReport

FORMAT = "%(asctime)s|%(name)s|%(levelname)s|%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger("Dependabot")

"""
query dependabot result by graph ql.
"""
class Dependabot(SCAScanTool):
    def __init__(self, param_manager: ParameterManager):
        super().__init__(param_manager)
        self.project_name = self.project_name.replace("/", "@")
        self.owner, self.repo_name = self.project_name.split("@")

        if not self.owner or not self.repo_name:
            raise RuntimeError("please specify owner and reponame by -name")
        else:
            logger.info(f"query deps for {self.project_name}")
        self.github_token = os.getenv("GIT_TOKEN", "")
        self.check_auth()

    def check_auth(self):
        if not self.github_token:
            raise EnvironmentError("please specify GIT_TOKEN in your environment")

    def scan_with_api(self):
        logger.info("Dependabot only support online scan. Please make sure the target repo is in the github repo" +
                    "and dependency alert is available")

    def scan_with_cmd(self):
        self.scan_with_api()

    def get_report_by_api(self, scan_feedback=None):
        """
        logic is exactly the same as get report from cmd
        :param scan_feedback:
        :return:
        """
        dep_json, status_code = self.get_dependency_list()
        if status_code != 200:
            raise RuntimeError(f"get dependency list failed, return json: {dep_json}")
        total_dep_dict = {}
        blob_list = dep_json['data']['repository']['dependencyGraphManifests']['edges']
        for edge in blob_list:
            blobPath = edge['node']['blobPath']
            if not blobPath.endswith('pom.xml'):
                continue
            dep_list = edge['node']['dependencies']['nodes']
            for node in dep_list:
                if node['packageManager'] != "MAVEN":
                    continue
                group_id, artifact_id = node['packageName'].split(':')
                version = node['requirements']
                if not version:
                    continue
                if version.startswith("= "):
                    version = version.replace("=", "").strip()
                tmp_dep = ComponentReport(f"{group_id}:{artifact_id}", version)
                total_dep_dict[tmp_dep.get_hash()] = tmp_dep

        total_issue_dict = {}
        cursor = ''
        while True:
            vul_json, status_code = self.get_vul_list(cursor)
            if status_code != 200 or 'data' not in vul_json:
                raise RuntimeError(f"get vulnerability list failed, return json: {vul_json}, statuscode {status_code}")
            vul_list = vul_json['data']['repository']['vulnerabilityAlerts']['edges']
            for edge in vul_list:
                node = edge['node']
                version = node['vulnerableRequirements']
                if version.startswith("= "):
                    version = version.replace("=", "").strip()
                public_id_list = node['securityVulnerability']['advisory']['identifiers']
                if node['securityVulnerability']['package']['ecosystem'] != "MAVEN":
                    continue
                group_id, artifact_id = node['securityVulnerability']['package']['name'].split(':')
                for public_id in public_id_list:
                    if public_id['value'].startswith("CVE") or public_id['value'].startswith("CNVD"):
                        tmp_issue = IssueReport(f"{group_id}:{artifact_id}", version, public_id['value'])
                        total_issue_dict[tmp_issue.get_hash()] = tmp_issue
            page_info = vul_json['data']['repository']['vulnerabilityAlerts']['pageInfo']
            if page_info['hasNextPage'] == "true":
                cursor = page_info['endCursor']
            else:
                break
        write_issue_report(
            list(total_issue_dict.values()), f"dependabot-issue-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing dependabot-issue-{self.project_name} to {self.output_dir}"
        )
        write_component_report(
            list(total_dep_dict.values()), f"dependabot-component-{self.project_name}", self.output_dir
        )
        logger.info(
            f"finish writing dependabot-component-{self.project_name} to {self.output_dir}"
        )

    def get_report_from_cmd(self, scan_feedback=None):
        self.get_report_by_api()

    def get_dependency_list(self):
        url = "https://api.github.com/graphql"
        payload = f"""
                {{ 
                \"query\":\
                    \"query {{\
                      repository(owner:\\\"{self.owner}\\\", name:\\\"{self.repo_name}\\\") {{\
                        dependencyGraphManifests {{\
                          totalCount\
                          nodes {{\
                            filename\
                          }}\
                          edges {{\
                            node {{\
                              blobPath\
                              dependencies {{\
                                totalCount\
                                nodes {{\
                                  packageName\
                                  requirements\
                                  hasDependencies\
                                  packageManager\
                                }}\
                              }}\
                            }}\
                          }}\
                        }}\
                      }}\
                    }}\"\
                }}
                """
        headers = {
            'Authorization': f'Bearer {self.github_token}',
            'Accept': 'application/vnd.github.hawkgirl-preview+json',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json(), response.status_code

    def get_vul_list(self, cursor):
        url = "https://api.github.com/graphql"
        after_expression = ""
        if cursor:
            after_expression = f", after: \\\"{cursor}\\\""

        payload = f"""
                {{
                \"query\":\
                    "query {{\
                       repository(owner:\\\"{self.owner}\\\", name:\\\"{self.repo_name}\\\") {{\
                        vulnerabilityAlerts(first: 100) {{\
                          pageInfo {{\
                            hasNextPage\
                            hasPreviousPage\
                            startCursor\
                            endCursor\
                          }}\
                          totalCount\
                          edges {{\
                            node {{\
                                vulnerableRequirements\
                                securityVulnerability {{\
                                    advisory {{\
                                        identifiers {{\
                                            value\
                                        }}\
                                    }}\
                                    severity\
                                    package {{\
                                        ecosystem\
                                        name\
                                    }}\
                                    updatedAt\
                                    vulnerableVersionRange\
                                }}\
                            }}\
                          }}\
                        }}\
                      }}\
                    }}\"\
                }}
                """
        headers = {
            'Authorization': f'Bearer {self.github_token}',
            'Accept': 'application/vnd.github.hawkgirl-preview+json',
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json(), response.status_code

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
            if "packages" in dependency:
                package_id = dependency['packages'][0]['id']
                group_id, artifact_id, version = resolve_package_id(package_id)
            else:
                artifact_id = dependency['fileName'].strip()
                group_id = artifact_id
                version = 'N.A.'
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
                        package_id = relatDep['packageIds'][0]['id']
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
