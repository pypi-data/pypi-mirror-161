import ast
import json

class Job:

    def __init__(self,Preset,id=None,attributes=None):
        if not id:
            raise TypeError("Please specify the job id")
        self.id = id
        self.Rally = Preset.Asset.Rally
        self.Asset = Preset.Asset
        self.Preset = Preset
        self.presetName = Preset.name
        if not attributes:
            attributes = self.Rally.apiCall("GET","/jobs/{}".format(self.id))["data"]["attributes"]
        self.result = attributes["result"]
        self.dynamicPresetData = attributes["dynamicPresetData"]
        
    def getArtifact(self,name,parse=False):
        artifact = self.Rally.apiCall("GET","/artifacts/{}_{}/content".format(self.id,name),fullResponse=True).text
        if parse:
            oneLine = artifact.replace("'\n '","").replace("\n('","").replace("')\n","").replace('"\n "','').replace('"\n("','').replace('")\n','').replace("\n","")
            if "[" not in oneLine or (oneLine.find("{") < oneLine.find("[") and "{" in oneLine):
                curlyParse = oneLine[oneLine.find("{"):oneLine.rfind("}")+1]
                try:
                    return json.loads(curlyParse)
                except:
                    try:
                        return ast.literal_eval(curlyParse)
                    except:
                        raise ValueError("Could not parse output to a dictionary")
            else:
                squareParse = oneLine[oneLine.find("["):oneLine.rfind("]")+1]
                try:
                    return json.loads(squareParse)
                except:
                    try:
                        return ast.literal_eval(squareParse)
                    except:
                        raise ValueError("Could not parse output to a dictionary")
        return artifact