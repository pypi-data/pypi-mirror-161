import json

import yaml
from loguru import logger
import requests
from requests import RequestException
from urllib3.exceptions import InsecureRequestWarning
from yaml.composer import ComposerError
from generic_crawler.config import settings
from generic_crawler.actions import ActionSchema


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


"""
endpoint = "http://localhost:33718"
with open(f"{os.path.dirname(os.path.realpath(__file__))}/tests/test_actions.yml", 'r') as f:
    actions = yaml.safe_load(f)
action = actions[0]
"""

### HELPER FUNCTIONS
def apply_custom_assertion(condition, exception, msg):
    if condition:
        raise exception(msg)


## CORE OBJECTS
class ActionReader:
    def __init__(self, path_to_yaml):
        self.path_to_yaml = path_to_yaml
        self._load_yaml()
        self._validate()

    def _load_yaml(self):
        with open(self.path_to_yaml, 'r') as f:
            try:
                self.action = yaml.safe_load(f)
            except ComposerError as ce:
                logger.error(f"you tried loading multiple actions at single yaml file please check your yaml file")
                raise ce


    def _validate(self):
        assert ActionSchema.validate(self.action)
        logger.debug(f"Action {self.action['name']} schema looks good")
        if type(self.action) == list:
            raise ValueError("Only one action can be retrieved at a time. If you have multiple steps or targets, define at your action.yaml file")
        try:
            assert self.action["steps"]
            assert self.action["targets"]
        except KeyError as ke:
            logger.error("Actions must be a single dictionary with steps,targets instructions, use ActionReader to parse your action.yaml file")
            raise ke


class GenericCrawler:
    def __init__(self, endpoint=None):
        if endpoint == None:
            self.endpoint = settings.service_root_endpoint
        else:
            self.endpoint = endpoint
        logger.debug(f"health checking for service {self.endpoint}")
        health_check_url = f"{self.endpoint}/health/live"
        response = requests.get(health_check_url, verify=False)
        status_code = response.status_code
        ## TEST!! -> burada pod adedini 0'layıp dene garip bir hata alınıyor
        ## o hatayı düzgün handle edebilmelisin
        logger.debug("health check success, service is alive!")
        content = json.loads(response.content.decode('utf-8'))
        if status_code == 200 and content["detail"] == "OK!": self.is_alive = True
        else: raise ConnectionError(f"Failed to connect crawler service - {self.endpoint}")


    def retrieve(self, action):
        self.action = action
        logger.info(f"Requesting from crawl service for action {self.action['name']}, this can take around a minute.")
        response = requests.post(f"{self.endpoint}/crawl", json=self.action, verify=False)
        content = json.loads(response.content.decode('utf-8'))
        logger.info(f"Data retrieval sequence on service completed, should check whether fail or success")
        return content, response


