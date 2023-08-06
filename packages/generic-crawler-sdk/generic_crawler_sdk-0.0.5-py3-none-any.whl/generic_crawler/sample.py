"""
with open(f"{os.path.dirname(os.path.realpath(__file__))}/tests/test_actions.yml", 'r') as f:
    actions = yaml.safe_load(f)
action = actions[0]

#for Tuncel: crawler = GenericCrawler(endpoint=)
"""

from generic_crawler.core import GenericCrawler, ActionReader

#reader = ActionReader(path_to_yaml="/Users/tcudikel/Dev/ace/generic-crawler-sdk/tests/actions/test_get_attribute_value.yml")
reader = ActionReader(path_to_yaml="/Users/tcudikel/Dev/ace/competitor-crawler/actions/azercell_tariffs_archive_urls.yml")
#crawler = GenericCrawler(endpoint="https://generic-crawler-service-ai-sensai.apps.tocpgt01.tcs.turkcell.tgc")
crawler = GenericCrawler(endpoint="http://localhost:33718")

#reader.action["steps"][0]["duration"] = 20

data, _ = crawler.retrieve(reader.action)

print("ok")

