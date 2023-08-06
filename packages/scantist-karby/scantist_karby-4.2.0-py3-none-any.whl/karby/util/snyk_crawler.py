import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class SnykCrawler:
    def __init__(self):
        self.network_logs = []
        self.network_request_ids = set()
        self.driver = webdriver.Chrome()
        self.driver.get("https://app.snyk.io/org/zhaolida98/projects")

    def traverse_log(self, driver):
        network_finish = "Network.loadingFinished"
        network_failed = "Network.loadinaFailed"
        network_start = "Network.requestWillBeSent"
        network_cache = "Network.requestServedFromCache"
        network_send_extra = "Network.requestWillBeSentExtraInfo"
        for entry in driver.get_log('performance'):
            msg = entry["message"]
            msg = json.loads(msg)
            params = msg["message"]["params"]
            log_msg = msg["message"]["method"]
            if log_msg == network_start:
                headers = params["request"]["headers"]
                requestId = params["requestId"]
                self.network_logs.append(msg)
                if "Accept" in headers and headers["Accept"].find("json") > -1:
                    self.network_request_ids.add(requestId)
            if log_msg == network_finish:
                self.network_logs.append(msg)
                requestId = params ["requestId"]
                self.network_request_ids.discard(requestId)
            if log_msg == network_failed:
                self.network_logs.append(msg)
                requestId = params ["requestId"]
                self.network_request_ids.discard(requestId)
            if log_msg == network_cache:
                self.network_logs.append(msg)
                requestId = params ["requestId"]
                self.network_request_ids.discard(requestId)
        return self.network_request_ids.__len__()

    def get_logs(self):
        log.info("get logs")
        return self.driver.get_log('browser')

    def init_driver(self):
        try:
            if self.driver != None:
                try:
                    self.close()
                except:
                    print("close error 23333")
        except:
            pass
        # prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.set_capability('unhandledPromptBehavior', 'accept')
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_experimental_option("prefs", prefs)
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL', 'browser': "ALL", "client": "ALL"}
        caps["unhandledPromptBehavior"] = "accept"
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")
        driver = webdriver.Chrome(options=chrome_options, desired_capabilities=caps)
        # add a large timeout for page loading
        driver.set_page_load_timeout(60)
        return driver