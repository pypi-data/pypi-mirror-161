![DASF Logo](https://git.geomar.de/digital-earth/dasf/dasf-messaging-python/-/raw/master/docs/_static/dasf_logo.svg)

[![PyPI version](https://badge.fury.io/py/deprogressapi.svg)](https://badge.fury.io/py/deprogressapi)

## dasf-progress-api

`DASF: Progress API` is part of the Data Analytics Software Framework (DASF, https://git.geomar.de/digital-earth/dasf), 
developed at the GFZ German Research Centre for Geosciences (https://www.gfz-potsdam.de). 
It is funded by the Initiative and Networking Fund of the Helmholtz Association through the Digital Earth project 
(https://www.digitalearth-hgf.de/).

`DASF: Progress API` provides a light-weight tree-based structure to be sent via the DASF RCP messaging protocol. 
It's generic design supports deterministic as well as non-deterministic progress reports. 
While `DASF: Messaging Python` provides the necessary implementation to distribute 
the progress reports from the reporting backend modules, 
`DASF: Web` includes ready to use components to visualize the reported progress.

### Service Desk

For everyone without a Geomar Gitlab account, we setup the Service Desk feature for this repository.
It lets you communicate with the developers via a repository specific eMail address. Each request will be tracked via the Gitlab issuse tracker.

eMail: [gitlab+digital-earth-dasf-dasf-progress-api-2274-issue-@git-issues.geomar.de](mailto:gitlab+digital-earth-dasf-dasf-progress-api-2274-issue-@git-issues.geomar.de)


### Usage

A progress report is stored in a tree structure. So there will be one 'root' report instance containing multiple 'sub-reports'.

The root report will be initialized directly. The contructor demands a `send_handler` argument, so we need to create one first. 
The `dasf-messaging-python` module provides a ready to use implementation for the `send_handler` via the `ProgressSendHandler` class.
In order to instantiate the send handler you need to pass the `PulsarMessageConsumer` that is used to receive the request that is monitored,
as well as the corresponding request message. You might add additional message properties via the `msg_props` dictionary.

```python
from demessaging.progress_send_handler import ProgressSendHandler

send_handler=ProgressSendHandler(pulsar=self.__pulsar,
                                 request_msg=request_msg,
                                 msg_props={'additional': 'some addtional property'})
```

Once we have a `send_handler` we can use it to create the 'root' progress report for the request.
In case we already know how many steps (sub-reports) there are going to be on the next level, we can pass it via the optional `steps` argument.

```python
root_report = ProgressReport(step_message="Label/message of the root report",
                                 send_handler=send_handler,
                                 steps=2)
```

Once we have the root report instance we create new subreports for it via the `create_subreport` method. 
Each created report is published automatically upon creation and completion.

```python
# create a subreport
sub_report = root_report.create_subreport(step_message="Calculating something")

# execute some logic
# ...

# mark the sub-report as compelte
sub_report.complete()
```

All sub-reports are again instances of `ProgressReport`, so you can create more sub-reports for each.

#### error handling
For now there is no distinct error flag in the report. 
But you can update the `step_message` prop before marking it as complete to indicate an error.

```python
# some code that raises an exception
# ...
except Exception as e:
    error = str(e)
    progress_report.step_message = "error '{msg}': {err}".format(msg=progress_report.step_message, err=error)
    progress_report.complete()
```

### Recommended Software Citation

`Eggert, Daniel; Dransch, Doris (2021): DASF: Progress API: A progress reporting structure for the data analytics software framework. V. v0.1.4. GFZ Data Services. https://doi.org/10.5880/GFZ.1.4.2021.007`


### License
```
Copyright 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany / DASF Data Analytics Software Framework

Licensed under the Apache License, Version 2.0 (the "License");
you may not use these files except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

### Contact
Dr.-Ing. Daniel Eggert  
eMail: <daniel.eggert@gfz-potsdam.de>


Helmholtz Centre Potsdam GFZ German Research Centre for Geoscienes  
Section 1.4 Remote Sensing & Geoinformatics  
Telegrafenberg  
14473 Potsdam  
Germany
