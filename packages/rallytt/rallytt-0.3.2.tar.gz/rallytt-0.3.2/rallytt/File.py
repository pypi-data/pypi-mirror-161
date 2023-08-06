import requests
import urllib.parse

class File:

    def __init__(self,Asset,id=None,label=None):
        self.id = id
        self.Rally = Asset.Rally
        self.Asset = Asset
        self.label = label
        if not label and not id:
            raise TypeError("Please specify either a label or id")
        elif not id:
            try:
                self.id = self.Rally.apiCall("GET","/assets/{}/files?filter=label={}".format(self.Asset.id,urllib.parse.quote_plus(self.label)))["data"][0]["id"]
            except IndexError:
                raise ValueError("Could not find file with label '{}'".format(label)) from None

    def getLabel(self):
        if not self.label:
            self.label = self.Rally.apiCall("GET","/files/{}".format(self.id))["data"]["attributes"]["label"]
        return self.label

    def getAnalyzeInfo(self):
        mediaAttributesLinks = self.Rally.apiCall("GET","/files/{}/mediaAttributes?no-redirect=true".format(self.id))["links"]
        self.analyzeInfo = requests.get(mediaAttributesLinks["mediaAttributes"]).json()
        return self.analyzeInfo