from karby.sca_apis.Dependabot import Dependabot
from karby.sca_apis.OSSIndex import OSSIndex
from karby.sca_apis.OWASP import OWASP
from karby.parameter_manager import ParameterManager
from karby.sca_apis.SCAScanTool import SCAScanTool
from karby.sca_apis.Scantist import Scantist
from karby.sca_apis.Snyk import Snyk
from karby.sca_apis.Steady import Steady
from karby.sca_apis.Whitesource import Whitesource
from karby.util.settings import error_exit


def sca_factory(param_manager: ParameterManager) -> SCAScanTool:
    scan_tool = param_manager.get_param("sca_tool")
    if scan_tool == "snyk":
        # return Snyk(param_manager)
        raise RuntimeError("snyk is deprecated.")
    elif scan_tool == "owasp":
        return OWASP(param_manager)
    elif scan_tool == "whitesource":
        return Whitesource(param_manager)
    elif scan_tool == "steady":
        return Steady(param_manager)
    elif scan_tool == "scantist":
        return Scantist(param_manager)
    elif scan_tool == "dependabot":
        return Dependabot(param_manager)
    elif scan_tool == "ossindex":
        return OSSIndex(param_manager)
    else:
        error_exit("scan tool not supported")
