# McAfee Active Response Tracing

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This is an example how to consume McAfee Active Response trace data locally. Normally the trace data will be send to the McAfee Cloud and be analyzed. 

However due to some restriction customers might have issues in sending the trace data to the McAfee Cloud (e.g. Air-Gapped Networks). The following guide will demonstrate how the trace data can be redirected to a local datastore. In this example Elasticsearch and Kibana is used as datastore and for visualization.

## Process

The trace data will be redirected to a local python webserver. The received trace data will be uncompressed, decoded and ingested into a Elasticsearch datastore.

## Configuration

Download the latest release and install the required libraries.
```sh
$ pip install elasticsearch
```

After the install change the line 15 to 20 in the python script.

<img width="330" alt="Screenshot 2019-09-18 at 18 09 32" src="https://user-images.githubusercontent.com/25227268/65165645-7dcea400-da3f-11e9-935c-696a0d9c1f9e.png">

Execute the python script:
```sh
$ python3.7 mar_tracing_web.py
```

In order to redirect the trace data the McAfee ePO Cloud Databus URL needs to be changed and pointed to the local python webserver. Go to the EPO server settings and change the Cloud Databus URL. The python webserver is listenting on port 8080 (can be changed).

<img width="1440" alt="Screenshot 2019-09-18 at 18 11 54" src="https://user-images.githubusercontent.com/25227268/65165833-d3a34c00-da3f-11e9-90c0-7279f7418df5.png">

The trace data will redirected to the configured Elasticsearch datastore. Here an example Dashboard to visualize the trace data.

<img width="1440" alt="Screenshot 2019-09-18 at 18 16 02" src="https://user-images.githubusercontent.com/25227268/65166134-69d77200-da40-11e9-9551-8bfd37f06514.png">

Here an example of the raw trace data.

```sh
{
  "traceId": "6a276e41-da2e-11e9-9284-aaaaaaaaaaaa",
  "ruleId": 10011,
  "ruleVersion": 206,
  "parentTraceId": "6950d75a-da2e-11e9-9279-aaaaaaaaaaaa",
  "rootTraceId": "68cdb304-da2e-11e9-9278-aaaaaaaaaaaa",
  "pid": 8960,
  "time": "2019-09-18T16:07:29.584Z",
  "attrBitMask": "0x5",
  "eventType": "File Deleted",
  "maGuid": "A53CB87C-37F4-11E8-3671-00505697327C",
  "behaviorBucketOfEvent": "0x0",
  "rootSha2": "2ac2f54c9c2ad354e506a9e1b0b66d1f13707ca0f476d34d2c39dfa96c93e2bd",
  "severity": "s0",
  "fileAttributes": {
    "name": "XNKDZJAK.QZV.PS1",
    "path": "C:\\USERS\\WARROOM\\APPDATA\\LOCAL\\TEMP\\XNKDZJAK.QZV.PS1",
    "md5": "c4ca4238a0b923820dcc509a6f75849b",
    "sha1": "356a192b7913b04c54574d18c28d46e6395428ab",
    "sha256": "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
    "size": 1,
    "onSystemCreationDate": "2019-09-18T16:07:29.317Z",
    "lastModificationDate": "2019-09-18T16:07:29.348Z"
  },
  "maName": "VICTIM",
  "maIpName": "victim.domain.com",
  "maIp": "12.26.161.22"
},
{
  "traceId": "6a2e9583-da2e-11e9-9284-aaaaaaaaaaaa",
  "ruleId": 10011,
  "ruleVersion": 206,
  "parentTraceId": "6950d75a-da2e-11e9-9279-aaaaaaaaaaaa",
  "rootTraceId": "68cdb304-da2e-11e9-9278-aaaaaaaaaaaa",
  "pid": 8960,
  "time": "2019-09-18T16:07:29.642Z",
  "attrBitMask": "0x5",
  "eventType": "File Deleted",
  "maGuid": "A53CB87C-37F4-11E8-3671-00505697327C",
  "behaviorBucketOfEvent": "0x0",
  "rootSha2": "2ac2f54c9c2ad354e506a9e1b0b66d1f13707ca0f476d34d2c39dfa96c93e2bd",
  "severity": "s0",
  "fileAttributes": {
    "name": "1FRPVAYE.40W.PSM1",
    "path": "C:\\USERS\\WARROOM\\APPDATA\\LOCAL\\TEMP\\1FRPVAYE.40W.PSM1",
    "md5": "c4ca4238a0b923820dcc509a6f75849b",
    "sha1": "356a192b7913b04c54574d18c28d46e6395428ab",
    "sha256": "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
    "size": 1,
    "onSystemCreationDate": "2019-09-18T16:07:29.504Z",
    "lastModificationDate": "2019-09-18T16:07:29.536Z"
  },
  "maName": "VICTIM",
  "maIpName": "victim.domain.com",
  "maIp": "12.26.161.22"
}
```
