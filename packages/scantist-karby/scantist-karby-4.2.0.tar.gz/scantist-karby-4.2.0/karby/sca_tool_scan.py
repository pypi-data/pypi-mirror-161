import argparse
import os
import sys

from karby.parameter_manager import ParameterManager
from karby.sca_apis.SCAFactory import sca_factory
from karby.util.constants import SCA_TOOLS, SCAN_TYPE, version
from karby.util.settings import error_exit


def trigger_scan(argv):
    if argv.sca_tool not in SCA_TOOLS:
        error_exit(f"unsupported tool, choices available: {SCA_TOOLS}")

    if argv.scan_type not in SCAN_TYPE:
        error_exit(f"invalid scan type, choices available: {SCAN_TYPE}")

    if not argv.url:
        error_exit(f"please at specify project url.")

    param_manager = ParameterManager()
    param_manager.put_param("sca_tool", argv.sca_tool)
    param_manager.put_param("scan_type", argv.scan_type)
    param_manager.put_param("url", argv.url)
    param_manager.put_param("name", argv.name)
    param_manager.put_param("output", argv.output)
    param_manager.put_param("options", argv.options)
    param_manager.put_param("image_name_tag", argv.url)
    param_manager.put_param("skip_scan", argv.skip_scan)

    sca_obj = sca_factory(param_manager)
    scan_feedback = None
    if argv.skip_scan == "false":
        scan_feedback = sca_obj.scan_project()
    sca_obj.get_result(scan_feedback)


def main():
    parser = argparse.ArgumentParser(description=f"Karby-{version}: an assemble tool for multiple SCA tools.")
    parser.add_argument(
        "sca_tool", type=str, help=f'available choices are: {", ".join(SCA_TOOLS)}'
    )
    parser.add_argument(
        "scan_type",
        type=str,
        help=f'scan type could be "cmd" and "upload" scan, default is "upload"',
    )
    parser.add_argument(
        "url",
        type=str,
        help=f"url of the project, could be a web url or a local directory. "
             f"If scan type is docker, then it should be the <name>:<tag>",
    )
    parser.add_argument(
        "-name",
        type=str,
        help="report name, will be the folder name or owner/name by default",
    )

    parser.add_argument(
        "-output", type=str, help="project report output directory", default=os.getcwd()
    )

    parser.add_argument(
        "-options", type=str, default=""
    )
    parser.add_argument(
        "-skip_scan", type=str, default="false"
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    trigger_scan(args)
    # example: python sca_tool_scan.py whitesource cmd /home/nryet/Scantist/testProjects/efdaTest/efda/scala/sbt/sbt-basic -output output

if __name__ == '__main__':
    main()