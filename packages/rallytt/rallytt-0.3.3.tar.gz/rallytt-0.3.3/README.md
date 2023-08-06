# rally-test-tools
A set of python classes for running and verifying results for presets/supply chains in SDVI Rally.

## Installation
`pip install rallytt`

## Examples

Running a sandbox preset that returns the dynamic preset data:

    from rallytt import Rally

    RallyInstance = Rally(env="DEV")
    TestAsset = RallyInstance.asset()
    ExamplePreset = TestAsset.preset(name="00 Carson Sandbox rallytt")
    NewJob = ExamplePreset.run(dynamicPresetData={"message":"hello world"})
    print(NewJob.getArtifact("result",parse=True))
    TestAsset.delete()

Output:

    {"message":"hello world"}

---

Using the Test class to display test results:

    from rallytt import Test

    TestGroup = Test()
    expected = 1
    actual = 2
    TestGroup.test(expected == actual,"Basic equality test",expected=expected,actual=actual)
    expected = 1
    actual = 1
    TestGroup.test(expected == actual,"Basic equality test 2",expected=expected,actual=actual)
    TestGroup.print()

Output:

    ---------------
    Name: Basic equality test
    Result: fail
    expected = 1
    actual = 2
    ---------------
    Name: Basic equality test 2
    Result: pass
    expected = 1
    actual = 1
    ---------------

---

Full integration test script example (caption proxy workflow for EMEA assets):

    from rallytt import *

    TEST = Test()
    R = Rally(env="UAT")

    ASSET = R.asset(name="EMEA_ESD_860863E_119863_003_a_1598432456239")

    SUPPLYCHAIN = ASSET.supplychain(name="Caption Workflow Caption Proxy Creation")
    JOBS = SUPPLYCHAIN.run(initData={'sdviMovieLabel': 'SdviMovieFile'},timeout=1500)
    TEST.test(any([job.result != "pass" for job in JOBS]),"All jobs passed")

    captionProxy = ASSET.getFile(label="CaptionProxy608i50")
    analyzeInfo = captionProxy.getAnalyzeInfo()
    TEST.test(analyzeInfo.get("audio"),"Caption proxy was created and has audio")

    TEST.print()

    ASSET.delete()

Output:

    ---------------
    Name: All jobs passed
    Result: pass
    ---------------
    Name: Caption proxy was created and has audio
    Result: pass
    ---------------

---

Sample integration test using a mocked service:

    from rallytt import *

    TEST = Test()
    R = Rally(env="UAT")
    ASSET = R.asset(copy=False)

    ASSET.preset(name="lib/testing/mountebank/mocks/sample_service").run() #Create the mock

    JOB = ASSET.preset(name="unit_test_example").run()

    expected = {"message":"Hello World"}
    actual = JOB.getArtifact("result",parse=True)
    TEST.test(expected == actual,"Test mock response",expected=expected,actual=actual)

    expected = "validated"
    actual = ASSET.getMetadata().get("validationKey")
    TEST.test(expected == actual,"Check if key was added to metadata",expected=expected,actual=actual)

    TEST.print()
    ASSET.delete()

Output:

    ---------------
    Name: Test mock response
    Result: pass
    expected = {'message': 'Hello World'}
    actual = {'message': 'Hello World'}
    ---------------
    Name: Check if key was added to metadata
    Result: pass
    expected = validated
    actual = validated
    ---------------

---

## Classes

### **Test**  

#### *Properties*  

- **Test.tests** *Dictionary of all collected tests.*  

#### *Methods*  

- **Test.__init__()**  

- **Test.test(condition,testName,kwargs)**  
*Any keyword arguments will be displayed in the test results. This is useful for determining why tests might be failing.*  

- **Test.print()**  
*Prints the results of the tests.*  

---

### **Rally** 

#### *Properties*  

- **Rally.env** *Only necessary if using your rally-tools config.*  
- **Rally.apiUrl**  
- **Rally.apiKey**  

#### *Methods*  

- **Rally.__init__(findParams=True,env="UAT",apiUrl=None,apiKey=None)**  
*Leaving findParams set to "True" will use "apiKey" and "apiUrl" environment variables if they exist. If they do not, it will load in API keys from your rally-tools config file, based on the "env" parameter you specified (default is UAT).*  

- **Rally.apiCall(method,endpoint,body={},paginate=False,fullResponse=False,errors=True)**  
*fullResponse determines if the .json() method (part of the requests package) is applied to the response object.*  
*If errors are true, any non 2-- status code will throw an error.*  

- **Rally.asset(id=None,name=None)**  
*Creates an instance of an Asset class which points to a real asset in Rally. If neither id or name are specified, a new asset will be created in Rally.*  

---

### **Asset**  

#### *Properties*  

- **Asset.Rally** *The Rally class instance associated with the asset.*  
- **Asset.name**  
- **Asset.id**  
- **Asset.metadata** *Not defined until the getMetadata() method is used.*  
- **Asset.workflowMetadata** *Not defined until the getWorkflowMetadata() method is used.*  

#### *Methods*  

- **Asset.__init__(Rally,id=None,name=None,copy=True)**  
*Rally is an instance of a Rally class.*  
*If neither id or name are specified, a new asset will be created in Rally.*  
*Setting 'copy' to True (default) will create a copy of the asset you have specified. Setting it to False will use the asset you have specified.*  

- **Asset.getName()**  
*Return the asset's name and store it in the 'name' property of the asset.*  

- **Asset.getMetadata()**  
*Return the asset's METADATA object and store it in the 'metadata' property of the asset.*  

- **Asset.getWorkflowMetadata()**  
*Return the asset's WORKFLOW_METADATA object and store it in the 'workflowMetadata' property of the asset.*  

- **Asset.delete()**  
*Delete the asset in Rally. Automatically runs the deleteMocks method as well.*  

- **Asset.deleteMocks()**  
*Shuts down any mocks present in the asset's metadata*  

- **Asset.preset(id=None,name=None)**  
*Create a Preset class instance associated with the current Asset instance.*  
*An id or name must be specified.*  

- **Asset.supplychain(id=None,name=None)**  
*Create a SupplyChain class instance associated with the current Asset instance.*  
*An id or name must be specified.*  

- **Asset.listFiles()**  
*Return a list of File class instances belonging to all files in the Asset's inventory.*  

- **Asset.getFile(id=None,label=None)**  
*Create a File class instance from the label or id of the file.*  

- **Asset.revertMovieFile()**  
*Replaces the SdviMovieFile with the OriginalSdviMovieFile, and then removes the OriginalSdviMovieFile.*  

---

### **Preset**  

#### *Properties*  

- **Preset.id**  
- **Preset.name**  
- **Preset.Rally** *The Rally class instance associated with the preset.*  
- **Preset.Asset** *The Asset class instance pointing to the asset that the preset will run on.*  

#### *Methods*  

- **Preset.__init__(Asset,id=None,name=None)**  
*Asset is an instance of an Asset class, and it will be the asset that the preset runs on.*  
*Either an id or name must be specified.*  

- **Preset.getName()**  
*Return the preset's name and store it in the 'name' property of the preset.*  

- **Preset.run(dynamicPresetData=None,timeout=5)**  
*Once the preset has completed (within the timout), an instance of a Job class is returned.*  

- **Preset.job(id=None,attributes=None)**  
*Returns an instance of a Job class based on the id specified.*  
*Attributes are optional, and would be a dicitonary of job attributes based on a response from the Rally API.*  

---

### **SupplyChain**  

#### *Properties*  

- **SupplyChain.id**  
- **SupplyChain.name**  
- **SupplyChain.Rally** *The Rally class instance associated with the supply chain.*  
- **SupplyChain.Asset** *The Asset class instance pointing to the asset that the supply chain will run on.*  

#### *Methods*  

- **SupplyChain.__init__(Asset,id=None,name=None)**  
*Asset is an instance of an Asset class, and it will be the asset that the supply chain runs on.*  
*Either an id or name of a rule must be specified.*  

- **SupplyChain.run(initData={},endingPresetName=None,endingPresetId=None,timeout=15)**  
*Returns a list of Job class instances representing all jobs that were completed in the suppy chain run.*  
*The endingPreset defines the last preset in a supply chain that we care about running. Once it is finished, all subsequent jobs in the supply chain will be cancelled.*  

---

### **Job**  

#### *Properties*  

- **Job.id**  
- **Job.Rally** *The Rally class instance associated with the job.*  
- **Job.Asset** *The Asset class instance pointing to the asset that the job was run on.*  
- **Job.Preset** *The Preset class instance pointing to the preset that created the job.*  
- **Job.presetName** *The name of the preset that created the job.*  
- **Job.result** *The result of the job, could be pass, fail, cancelled, etc.*  
- **Job.dynamicPresetData**  

#### *Methods*  

- **Job.__init__(Preset,id=None,attributes=None)**  
*Asset is an instance of an Preset class, and it is the preset that produced the job.*  
*Attributes are optional, and would be a dicitonary of job attributes based on a response from the Rally API.*  

- **Job.getArtifact(name,parse=False)**  
*The name of the job artifact must be specified. Examples could be "result", "trace", "error", or "preset".*  
*If parse is set to True, the artifact will be parsed into a dictionary. If this is not possible, an error will be thrown.*  

---

### **File**  

#### *Properties*  

- **File.id**  
- **File.label**  
- **File.Rally** *The Rally class instance associated with the file.*  
- **File.Asset** *The Asset class instance pointing to the asset that the file belongs to.*  

#### *Methods*  

- **File.__init__(Asset,id=None,label=None)**  
*Asset is an instance of an Asset class, and it will be the asset that the file belongs to.*  
*An id or label must be specified.*  

- **File.getLabel()**  
*Return the file's label and store it in the 'label' property of the file.*  

- **File.getAnalyzeInfo()**  
*Return the analyze info of the file*  