# Introduction 
This project makes it possible to easily interact with the objects in ZEVIT's Asset Integrity Hub.

Project is structured as follows:

```
AIH_SDK
├── AIHClient
├── Assets
│   ├── Equipment
│   ├── MainSystem
│   └── Plant
├── DataProcessing
│   ├── Job
│   ├── JobConfiguration
│   └── JobDefinition
├── DataUpload
│   ├── DataType
│   └── File
├── Designations
│   ├── Design
│   ├── Schema
│   └── Structure
├── Risks
│   ├── Mitigation
│   ├── Risk
│   └── RiskAssessmentResult
├── Maintenance
│   ├── Deviation
│   ├── WorkItem
│   └── Activity
│   └── Input
├── Signals
│   ├── Channel
│   └── Signal
├── Workitems
│   ├── Annotation
│   ├── Assessment
│   ├── AssignedElement
│   ├── Failure
│   ├── Media
│   ├── MediaReference
│   ├── PanoramaImage
│   ├── PanoramicTour
│   └── WorkorderItem
```

# Getting Started
1.	Install by: pip install AIH_SDK
2.	Initialize AIHClient by: AIH_SDK.AIHClient.AIHClient(environment_to_connect_to, client_id, client_secret)
3.	Get objects from APIs. Example of getting a main system: from AIH_SDK.Assets import MainSystem; mainsystem = MainSystem().get(guid)
4.	Objects support CRUD operation in form of post, get, put, and delete.

# Object design
Objects store the information fetched from the APIs in the self.value of the object

self.value can either be a dict containing one instance or be a list containing multiple dicts, representing multiple objects.

All objects contain the following methods:
* get()
* put()
* post()
* delete()
* copy()
* get_value()
* set_value()
* update_values()
* to_dataframe()
* get_keys()
* filter()
* from_dataframe()
* from_dict()
* from_list()
* join()

Methods that modifies the object operate inplace, but also return the object itself to allow chaining of methods.