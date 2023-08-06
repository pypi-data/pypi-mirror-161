import csv
import re
import subprocess
import traceback
import os
import zipfile

from karby.util.models import ComponentReport, IssueReport


def github_url_analyzer(github_url):
    """
    https://github.com/xiandanin/magnetW.git
    git@github.com:xiandanin/magnetW.git
    :type github_url: str
    :param github_url:
    :return:
    """
    tmp_url = ""
    if github_url.startswith("git@github.com"):
        tmp_url = github_url.replace("git@github.com:", "").replace(".git", "")
    elif github_url.startswith("https"):
        tmp_url = github_url.replace("https://github.com/", "").replace(".git", "")
    else:
        raise ValueError("invalid url format. Only support github urls")
    owner_name = tmp_url.split("/")
    return owner_name[0], owner_name[1]


def check_mvn_version():
    cmd = "mvn --version"
    result = exec_command(cmd)
    if result.get("code") != 0:
        if 'output' in result:
            print(result['output'].decode())
        if 'error' in result:
            print(result['error'].decode())
        raise EnvironmentError("cannot find maven executable. Need maven 3.1 or higher.")
    else:
        if 'output' in result:
            output = result['output'].decode()
            version_num = re.search("Apache Maven (\S*)", output).group(1)
            if version_num is None or version_num < '3.1.0':
                raise EnvironmentError(f"Need maven 3.1 or higher. Current maven version: {version_num}")


def check_mvn_proj_info(project_url):
    cmd = f"cd {project_url} && mvn -q" \
          " -Dexec.executable=echo" \
          " -Dexec.args='${project.groupId} ${project.artifactId} ${project.version}'" \
          " exec:exec 2>/dev/null"
    result = exec_command(cmd)
    gav_list = []
    if result.get("code") != 0:
        raise EnvironmentError("check_mvn_proj_info failed.")
    else:
        if 'output' in result:
            output = result['output'].decode()
            for line in output.split(os.linesep):
                group, artifact, version = line.split(' ')
                gav_list.append((group, artifact, version))
        else:
            raise RuntimeError("getting maven project info failed")
    return gav_list

def project_dir_analyzer(project_dir: str):
    if os.path.isdir(project_dir):
        project_name = os.path.basename(project_dir)
        return project_name
    else:
        raise AttributeError("given url is not a project dir")

def name_tag_analyzer(nameTag: str):
    if ":" in nameTag:
        project_name = nameTag.replace(":", "-")
        return project_name
    else:
        raise AttributeError("given url is not a project dir")

def write_issue_report(info_list, report_name, output_dir):
    field_names = IssueReport.field_names
    try:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        with open(f"{output_dir}/{report_name}.csv", mode="w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()
            for info in info_list:
                writer.writerow(info.info)
    except:
        raise IOError(f"write issue report for {report_name} failed.")


def write_component_report(info_list, report_name, output_dir):
    field_names = ComponentReport.field_names
    try:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        with open(f"{output_dir}/{report_name}.csv", mode="w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()
            for info in info_list:
                writer.writerow(info.info)
    except:
        raise IOError(f"write component report for {report_name} failed.")


def exec_command(cmd, work_dir="."):
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=work_dir
    )
    try:
        out, err = p.communicate()
        return_code = p.returncode
        if err:
            return {"error": err, "output": out.strip(), "code": return_code}
    except Exception as e:
        return {"error": traceback.format_exc(), "code": return_code}
    return {"output": out.strip(), "code": return_code}


def make_zip(source_dir, output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            zipf.write(pathfile, arcname)
    zipf.close()


def resolve_package_id(package_id: str):
    name_list = package_id.split('/')
    if len(name_list) == 3:
        group_id = name_list[1]
        artifact_id = name_list[2].split('@')[0]
        version = name_list[2].split('@')[1]
    elif len(name_list) == 2:
        artifact_id = name_list[1].split('@')[0]
        group_id = artifact_id
        version = name_list[1].split('@')[1]
    else:
        print(f"invalid package_id: {package_id}")
        raise
    return group_id, artifact_id, version

