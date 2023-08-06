---
title: |
  ![](docs/logo-1.jpeg){ width=30% } \
  Turkcell
  Generic Crawler SDK
#author: "Mahmut Yılmaz, Mithat Sinan Ergen, Umut Alihan Dikel"
date: 2022
geometry: margin=2cm
---
\pagebreak

# Description
Generic Crawler SDK is a web crawling framework used to extract structured data from world wide web. It can be used for a wide range of purposes, from data mining for intelligent analytics to monitoring competitor pricing.
\vspace{10mm}

# Requirements
* Python 3.8
* Works on Linux, Windows
* Whitelisting to 
    * service endpoint URL 
    * outbound port 443(https) required
\vspace{10mm}

# Installation
This SDK is a Python package. Therefore it can be easily installed via pip:
```
pip install generic-crawler-sdk
```
\pagebreak

# Usage
\vspace{5mm}

## Action Components
Actions are yaml formatted files, where browser interactions are defined and consist of two components; **steps & targets**. 

Action files should include name, url info:
```
name: SAMPLE-ACTION
url: https://www.google.com
```

/break [screenshot of action files here]
\vspace{3mm}

### Steps
Steps point to elements and describe specific actions on those, which are required in order to reach the target element(s).

#### do-nothing \break
Literally does nothing. Because generic crawler always requires minimum a single step to execute, use this action if there is no step required to extract the target.
```
steps:
  - name: just do nothing
    action: do-nothing
```

#### wait-for \break
Waits for given duration.
```
  - name: wait 10 seconds after pageload
    action: wait-for
    duration: 10
```

#### click \break
Mouse click on given element selector
```
  - name: click on login button
    action: click
    type: xpath
    selector: //*[@id="button"]/div/div[1]/div/a
```

#### write \break
Write specific string on given element selector. When "wait" is true, the step waits for elements visibility & presence before executing (see step [wait](#wait)).
```
  - name: write account username 
    action: write
    value: my_test_user
    type: xpath
    wait: true

```

#### mouse-hover \break
Move mouse (virtually) over the given selector. 
```
  - name: move mouse to green ok button
    action: mouse-hover
    type: xpath
    selector: //*[@id="buttongreen"]
```

#### scroll \break
Scrolls page given direction; up/down. Repetition enables multiple times of scrolling for pages having infinite scroll.
```
  - name: scrolling down
    action: scroll
    scroll_to:
      direction: down
      repeat: 3
```

#### hit-enter \break
Sends keyboard event 'enter' to page.
```
  - name: start search query
    action: hit-enter
    type: xpath
    selector: //*[@id="search_form_input_homepage"]
    wait: false
```

#### iterate-until \break
Retrieves the given parent element and starts iterating over its child elements. Iteration continues until given condition applies. The condition is a string search and its match. Once the looked up child element is found, it executes custom action (e.g.: click, write, etc).
```
  - name: iterate until given shop name is found on search bar
    action: iterate-until
    iteration_on:
      type: xpath
      selector: //*[@id="auto-complete-app"]/div/div[1]/div/a
      look_for: shop_name_string
      when_found: click
```

#### retrieve-sitemap \break
Some pages provide their entire sitemap in xml format without any GUI component. This action enables sitemap data crawling. Depth attribute defines how further crawling should progress recursively.
```
  - name: get urls of product pages from sitemap
    action: retrieve-sitemap
    depth:
      level: 2
```

#### popup-check \break
Waits for popups after page-load and dismisses if given popup window exists.
```
  - name: dismiss popup if any thrown
    action: popup-check
    type: xpath
    selector: //*[@id="gender-popup-modal"]/div/div/div[1]
```
\vspace{5mm}

### Targets
Targets are defined as pointers to elements using xpath/css selectors, which contain data to be extracted from pages. A crawl action can have multiple targets. Currently available target types are text, nontext, url and values of custom attributes.

#### text \break
Extracts text from element, which user sees on the page.
```
targets:
  - name: product name
    type: xpath
    selector: //*[@id="seller-store"]/div/div[1]/div[1]/div[2]/div[2]/div[1]/h1
```

#### nontext \break
Extracts non-text attribute from element. Currently "image_url" is supported and available. 
```
  - name: product image
    type: xpath
    selector: //*[@id="center_column"]/ul/li/div/div/div[1]/div/a[1]/img
    nontext: image_url
```

#### extract-urls \break
Extracts urls from href attribute of given element selector. Used with a boolean value.
```
  - name: get product search result urls
    extract-urls: true
    type: xpath
    selector: //*[@id="resultList"]
```

#### attribute \break
Extracts value of any given attribute from element selector. This target type returns dynamically based on value of extracted attribute. If attribute has multiple values, it returns a list of values, otherwise single string of value is retruend. 
```
  - name: get product tags
    attribute: class
    type: xpath
    selector: /html/body/div/div[3]/div/p
```
\vspace{10mm}

## Action Reader
ActionReader is an object. Its main function is to read, load Action files and validates for structural correctness of the format. In a case where user has written an action which includes an unimplemented attribute or missing one, it will throw Exception.
```
>>> from generic_crawler.core import ActionReader

>>> reader = ActionReader(path_to_yaml="/path/to/file/sample_action.yml")
```
```
2022-07-27 11:56:46.258 | DEBUG    | generic_crawler.core:_validate:47 - Action TEST-WAIT-DURATION schema looks good
reader.action
```

ActionReader object has one attribute: **action**. \break
Loaded valid action file is converted into Dict and assigned to this attribute.
```
>>> print(reader.action)

{
   "name":"TEST-WAIT-DURATION",
   "url":"https://testpages.herokuapp.com/styled/calculator",
   "steps":[
      {
         "name":"wait N seconds after pageload",
         "action":"wait-for",
         "duration":10
      }
   ],
   "targets":[
      {
         "name":"test target",
         "type":"xpath",
         "selector":"/html/body/div/h1"
      }
   ]
}
```
\vspace{5mm}

## Generic Crawler
The main function of GenericCrawler object is to send requests to remote crawler service with payload including actions loaded by ActionReader. During instantiation GenericCrawler object checks the health status of remote endpoint of crawler service. If only service is up and ready, object is created. 
```
>>> crawler = GenericCrawler(endpoint=endpoint_url_string)

2022-07-27 12:18:39.932 | DEBUG    | generic_crawler.core:__init__:64 - health checking for service https://generic-crawler-service-ai-sensai.apps.tocpgt01.tcs.turkcell.tgc
2022-07-27 12:18:40.434 | DEBUG    | generic_crawler.core:__init__:70 - health check success, service is alive!
```

Instantiated crawler onject has two attributes: endpoint & is_alive.
```
>>> crawler.endpoint
"endpoint_url_string"

>>> crawler.is_alive
True

```
It has single method, retrieve(). Retrieve method is called with argument of action method of ActionReader. Once it is called, the request is sent to crawler service and waited for a response.
```
>>> data, _ = crawler.retrieve(reader.action)

2022-07-27 12:24:52.455 | INFO     | generic_crawler.core:retrieve:78 - Requesting from crawl service for action TEST-WAIT-DURATION, this can take around a minute.
```
Crawler service executes actions defined by the users action.yaml file and returns the extracted data from targets or exception detail if there is an error during crawling.
```
2022-07-27 12:25:08.489 | INFO     | generic_crawler.core:retrieve:81 - Data retrieval sequence on service completed, should check whether fail or success
```
Retrieve method of GenericCrawler object returns parsed extracted data and response object. Response object is returned only for debugging purposes. Therefore it can be ignored. Extracted data is converted into Python Dictionary.
```
>>> print(type(data))
<class 'dict'>

>>> print(data)
{'dummy target': 'Simple Calculator'}
```
Keys in dictionary are named based on targets of users action.yaml file.
```
targets:
  - name: dummy target
    type: xpath
    selector: /html/body/div/h1
```

Succesfully crawled data can be further processed & stored by user.

\vspace{10mm}

# Examples of use
We provide some use case examples. Those are heavily commented, so that reader has a grasp on how to implement crawler bots using this SDK. 

\vspace{5mm}

## Example (1) - Crawling the seller info from an ecommerce marketplace site
For each use case where this SDK is used, we write a crawler python script file and as many distinct action files in yml format as required. In this use case which we need to crawl and extract sellers information from a ecommerce marketplace site, the files are as below:

- **crawl_seller_page.py** ; crawler logic
- **actions_seller_page.yml** ; defined interactions as shown in above sections [steps & targets](#steps) described above. 

\vspace{3mm}

``` 
############
filename: 
actions_seller_page.yml:
############

# for ease of readability each action has a name
name: TRENDYOL-MAGAZA

# url is required to connect given web site
url: https://www.trendyol.com/

# steps section are required 
# here are all required to reach the target data
# (note to reader: if target data is reachable without any step, should use single do-nothing step)
steps:

  # site opens a popup 2-3 seconds after pageload
  - name: check for popup and dismiss if exist
  
    # popup-check action is used to detect and dismiss the popup
    action: popup-check

    # should give type of selector (xpath or css)
    type: xpath

    # catched selector of popup element  
    selector: //*[@id="gender-popup-modal"]/div/div/div[1]

    # next step after dismissing popup
  - name: write seller name into search bar
  
    # we use the 'write' action
    action: write
    
    # execution should wait until search bar is available 
    wait: true
    
    # define what to write on search bar
    value: dorcia home
    
    # selector type of search bar
    type: xpath
    
    # selector of search bar
    selector: //*[@id="auto-complete-app"]/div/div/input
    
    # Search bar shows alternative results in realtime
    # We should catch this element and iterate over it until lookup seller name is found
  - name: mağaza ismi bulana kadar sonuçları tara ve tıkla
  
    # for this 'iterate-until' action is used
    action: iterate-until
    
    # here we define the details for element to iterate on and value to look for  
    iteration_on:
    
      # selector type of the element 
      type: xpath
      
      # selector info to iterate on
      selector: //*[@id="auto-complete-app"]/div/div[1]/div/a
      
      # this string value is search in the iterated elements
      look_for: Mağaza
      
      # should define a second action to execute once the looked up element is found 
      when_found: click
      
# We define the targets in order to point the crawler which data to extract once the steps above is completed
targets:

  # names are defined for ease of readability from user and
  # Key name of returned dictionary by crawler service is assigned with this name.  
  # (e.g.: {"seller name": "dorcia home"})
  - name: seller name

    # for every target we define the type of selector
    type: xpath
    
    # and define the selector info
    selector: //*[@id="seller-store"]/div/div[1]/div[1]/div[2]/div[2]/div[1]/h1

  # similar to above target we can define multiple targets in a single action file
  # crawler will return the result dictionary with items defined here 
  # second target:
  - name: seller evaluation point
    type: xpath
    selector: //*[@id="seller-store"]/div/div[1]/div[1]/div[2]/div[2]/div[1]/div
  
  # third target:
  - name: seller follower count
    type: xpath
    selector: //*[@id="seller-store"]/div/div[1]/div[1]/div[3]/div[1]
```

\vspace{3mm}

``` 
############
filename: crawl_seller_page.py
############

# import generic-crawler-sdk objects first
from generic_crawler.core import GenericCrawler, ActionReader


# instantiate ActionReader with action file we defined above
# since if the action.yaml validation fails, this object throws an exception
# therefore this line can be further wrapped in a try-exception block to catch thrown exceptions and handle it
reader = ActionReader(path_to_yaml="actions_seller_page.yml")

# instantiate GenericCrawler with the endpoint url, which points to the remote service
# (note to reader: "endpoint" argument can be deprecated in further versions)
crawler = GenericCrawler(endpoint="endpoint_connection_url_string")


# this part is specific to the current use case
# only generic part is to usage of GenericCrawler and ActionReader objects from SDK
# developers should be writing their own custom logic for each case  

# define a list of sellers for their data to be extracted 
sellers = ["dorcia home", "19 mayıs cam ayna", "akım tekstil"]

# empty dict to append extracted seller info 
tmp = {}

# iterate on seller list to crawl for each seller 
for seller in sellers:

    # modify loaded action for this specific seller
    # 1. element of steps is "write" action
    # we update "value" of "write" action so that crawler writes this sellers name in search bar 
    reader.action["steps"][1]["value"] = seller

    # exception handling can be customized
    # here we implement the most simple one 
    try:
        # we send our updated action to crawler service to exrtract data
        data, _ = crawler.retrieve(reader.action)
    except: 
        # on any exception we assume the looked up seller is not found
        # therefore assigning an empty string as crawled seller's info 
        data = ""
        print("failed")

    # finally we update the dictionary with seller's name as key and extracted seller info as value 
    tmp[firma] = data
```
