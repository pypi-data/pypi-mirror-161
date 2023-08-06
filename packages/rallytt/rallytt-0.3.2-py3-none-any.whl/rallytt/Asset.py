import uuid
import requests
import urllib.parse
from .File import File
from .Preset import Preset
from .SupplyChain import SupplyChain

class Asset:

    def __init__(self,Rally,id=None,name=None,copy=True):
        self.Rally = Rally
        self.id = id
        self.name = name
        if not id and not name:
            self.name = "Temp_Asset_{}".format(str(uuid.uuid4()))
            self.id = Rally.apiCall("POST","/assets",body={"data":{"attributes":{"name":self.name},"type":"assets"}})["data"]["id"]
        elif not copy:
            if not id:
                self.name = name
                try:
                    self.id = Rally.apiCall("GET","/assets?search=name={}".format(urllib.parse.quote_plus(name)))["data"][0]["id"]
                except IndexError:
                    raise ValueError("Could not find asset with name '{}'".format(name)) from None
        else:
            if not id:
                assetName = name
                try:
                    self.id = Rally.apiCall("GET","/assets?search=name={}".format(urllib.parse.quote_plus(name)))["data"][0]["id"]
                except IndexError:
                    raise ValueError("Could not find asset with name '{}'".format(name)) from None
            elif not name:
                assetName = Rally.apiCall("GET","/assets/{}".format(self.id))["data"]["attributes"]["name"]
            self.name = "{}_Temp_Asset_{}".format(assetName,str(uuid.uuid4()))
            payload = Rally.apiCall("GET","/assets/{}".format(self.id))
            payload["data"]["attributes"] = {"name":self.name,"tagList":payload["data"]["attributes"]["tagList"],"status":payload["data"]["attributes"]["status"]}
            newId = Rally.apiCall("POST","/assets",body=payload)["data"]["id"]
            fileData = self.Rally.apiCall("GET","/assets/{}/files".format(self.id),paginate=True)["data"]
            for file in fileData:
                for instance in file["attributes"]["instances"]:
                    if file["attributes"]["instances"][instance]["storageLocationName"] == "Rally Platform Bucket":
                        del file["attributes"]["instances"][instance]
                file["relationships"]["asset"] = {"data":{"id":newId,"type":"assets"}}
                self.Rally.apiCall("POST","/files",body={"data":file})
            oldId = self.id
            self.id = newId
            try:
                metadataPayload = Rally.apiCall("GET","/userMetadata/{}".format(oldId))
                Rally.apiCall("PATCH","/userMetadata/{}".format(self.id),body=metadataPayload)
            except:
                pass
            wfmPresetName = "Add Workflow Metadata"
            try:
                workflowMetadata = Rally.apiCall("GET","/supplyChainMetadata/{}".format(oldId))["data"]["attributes"]["metadata"]
                try:
                    workflowMetadataPresetId = Rally.apiCall("GET","/presets?filter=name={}".format(urllib.parse.quote_plus(wfmPresetName)))["data"][0]["id"]
                    workflowMetadataPreset = Preset(self,id=workflowMetadataPresetId)
                    workflowMetadataPreset.run(dynamicPresetData=workflowMetadata,timeout=10)
                except IndexError:
                    providerTypeId = Rally.apiCall("GET","/providerTypes?filter=name=SdviEvaluate")["data"][0]["id"]
                    workflowMetadataPresetId = Rally.apiCall("POST","/presets",body={"data": {"type": "presets","attributes": {"name": wfmPresetName},"relationships": {"providerType": {"data": {"id": providerTypeId,"type": "providerTypes"}}}}})["data"]["id"]
                    Rally.apiCall("PUT","/presets/{}/providerData".format(workflowMetadataPresetId),body="WORKFLOW_METADATA = {{DYNAMIC_PRESET_DATA}}",fullResponse=True)
                    workflowMetadataPreset = Preset(self,id=workflowMetadataPresetId)
                    workflowMetadataPreset.run(dynamicPresetData=workflowMetadata,timeout=10)
            except:
                pass

    def getName(self):
        if not self.name:
            self.name = self.Rally.apiCall("GET","/assets/{}".format(self.id))["data"]["attributes"]["name"]
        return self.name

    def getMetadata(self):
        self.metadata = self.Rally.apiCall("GET","/movies/{}/metadata/Metadata".format(self.id))["data"]["attributes"]["metadata"]
        return self.metadata

    def getWorkflowMetadata(self):
        self.workflowMetadata = self.Rally.apiCall("GET","/movies/{}/metadata/Workflow".format(self.id))["data"]["attributes"]["metadata"]
        return self.workflowMetadata
    
    def delete(self):
        try:
            self.deleteMocks()
        except:
            pass
        return self.Rally.apiCall("DELETE","/assets/{}".format(self.id),fullResponse=True)

    def deleteMocks(self):
        metadata = self.getMetadata()
        for imposter in metadata.get("mountebankImposters",[]):
            baseUrl = metadata["mountebankImposters"][imposter]
            port = baseUrl.split("/")[-1]
            requests.delete(url="http://rally-mountebank.{}.dcitech.cloud/2525/imposters/{}".format(self.Rally.env.lower(),port))

    def preset(self,id=None,name=None):
        return Preset(self,id=id,name=name)

    def supplychain(self,id=None,name=None):
        return SupplyChain(self,id=id,name=name)

    def listFiles(self):
        fileData = self.Rally.apiCall("GET","/assets/{}/files".format(self.id),paginate=True)["data"]
        return [File(self,id=item["id"],label=item["attributes"]["label"]) for item in fileData]

    def getFile(self,id=None,label=None):
        return File(self,id=id,label=label)

    def revertMovieFile(self):
        originalFileId = self.getFile(label="OriginalSdviMovieFile").id
        currentFileId = self.getFile(label="SdviMovieFile").id
        self.Rally.apiCall("DELETE","/files/{}?mode=forget".format(currentFileId),fullResponse=True)
        originalFile = self.Rally.apiCall("GET","/files/{}".format(originalFileId))
        originalFile["data"]["attributes"]["label"] = "SdviMovieFile"
        self.Rally.apiCall("POST","/files",body=originalFile)
        self.Rally.apiCall("DELETE","/files/{}?mode=forget".format(originalFileId),fullResponse=True)