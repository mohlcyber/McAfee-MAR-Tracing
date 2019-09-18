# McAfee Active Response Tracing

This is an example how to consume McAfee Active Response trace data locally. Normally the trace data will be send to the McAfee Cloud and be analyzed. 

However due to some restriction customers might have issues in sending the trace data to the McAfee Cloud (e.g. Air-Gapped Networks). The following guide will demonstrate how the trace data can be redirected to a local datastore. In this example Elasticsearch and Kibana is used as datastore and for visualization.

## Process

The trace data will be redirected to a local python webserver. The received trace data will be uncompressed, decoded and ingested into a Elasticsearch datastore.

## Configuration

Download the latest release and install the required libraries.
```sh
$ pip install -r requirements.txt
```

After the install change the line 15 to 20 in the python script.

<img width="330" alt="Screenshot 2019-09-18 at 18 09 32" src="https://user-images.githubusercontent.com/25227268/65165645-7dcea400-da3f-11e9-935c-696a0d9c1f9e.png">

Execute the python script:
```sh
$ python3.7 mar_tracing_web.py
```

In order to redirect the trace data the McAfee ePO Cloud Databus URL needs to be changed and pointed to the local python webserver. Go to the EPO server settings and change the Cloud Databus URL. The python webserver is listenting on port 8080 and can be changed.

<img width="1440" alt="Screenshot 2019-09-18 at 18 11 54" src="https://user-images.githubusercontent.com/25227268/65165833-d3a34c00-da3f-11e9-90c0-7279f7418df5.png">



