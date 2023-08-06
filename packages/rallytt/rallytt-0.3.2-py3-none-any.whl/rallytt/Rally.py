import os
import requests
import json
from .Asset import Asset
import re

class Rally:

    def __init__(self,findParams=True,env="UAT",apiUrl=None,apiKey=None):
        self.apiUrl = apiUrl
        self.apiKey = apiKey
        if findParams:
            if os.environ.get("apiKey") and os.environ.get("apiUrl"):
                self.apiUrl = os.environ.get("apiUrl")
                self.apiKey = os.environ.get("apiKey")
            else:
                configPath = os.path.expanduser('~')+"/.rallyconfig"
                rallyConfig = open(configPath)
                rallyConfigJson = json.load(rallyConfig)
                apiConfig = rallyConfigJson["api"]
                rallyConfig.close()
                self.apiUrl = apiConfig[env]["url"]
                self.apiKey = apiConfig[env]["key"]
        elif not apiUrl or not apiKey:
            raise TypeError("Please specify both apiUrl and apiKey parameters")
        matches = re.findall("discovery.*sdvi", self.apiUrl)
        if len(matches) == 0:
            raise ValueError("Cannot extract environment from api url")
        env = matches[0].replace(".sdvi","").replace("discovery","")
        self.env = "PROD" if env == "" else env.replace("-","").upper()
    
    def apiCall(self,method,endpoint,body={},paginate=False,fullResponse=False,errors=True):
        headers={"Authorization":"Bearer {}".format(self.apiKey),"Content-Type":"application/json" if type(body) is dict else "text/plain"}
        response = requests.request(method,headers=headers,url="{}{}".format(self.apiUrl,endpoint),data=json.dumps(body) if type(body) is dict else body)
        if errors:
            response.raise_for_status()
        if not fullResponse or paginate:
            response = response.json()
        page = 2
        while paginate:
            if "?" in endpoint:
                url = "{}{}&page={}p10".format(self.apiUrl,endpoint,page)
            else:
                url = "{}{}?page={}p10".format(self.apiUrl,endpoint,page)
            results = requests.request(method,headers=headers,url=url,data=json.dumps(body))
            if results.status_code != 404:
                if errors:
                    results.raise_for_status()
                response["data"].extend(results.json()["data"])
                if len(results.json()["data"]) < 10:
                    paginate = False
                page+=1
            else:
                paginate = False
        return response

    def asset(self,id=None,name=None,copy=True):
        return Asset(self,id=id,name=name,copy=copy)