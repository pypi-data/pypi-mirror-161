# README #

## Project Scope: ##

### ramshare: ###
Create data structures in shared memory based on a data structure file.
Read and write to data structure tag.
Data structure tags can be accessed system-wide.

### procon: ###
#### producer: ####
Creates a socket server and either connect or create shared data structure. 
Consumers can connect to producer, and all data from data structure will be transferred to connected consumers periodic.

#### consumer: ####
Connects to producer, either creates or connects to shared data structure.
Shared data structure will be overwritten periodic, so shared data structure is read only on consumer site. 


### Data structure .xml file: ###

```xml
<config>
    <connection_status LENGTH="2" TYPE="int" INIT_VALUE="0" DESCRIPTION="connection of status" > </connection_status>
    <tag_1 LENGTH="10" TYPE="int" > </tag_1>
    <timestamp LENGTH="20" TYPE="float" > </timestamp>
    <status LENGTH="100" TYPE="string" ></status>
</config>
```
#### Required tags: ####
For produced / consumed data structures, "connection_status" is required. 

#### Required members: ####
tag_1 = reference name, used to read or write from data structure.

LENGTH = tag length in bytes, minimum value is 2

#### Optional members ####
TYPE = tag type, 
INIT_VALUE = initial tag value

DESCRIPTION = description of tag

### Usage: ###

#### Write to tag: ####
````python
from comram import ramshare

test = ramshare.RamShare("share_name", data_type="/path_to_structure/test_structure.xml")
test.write_to_tag("tag_1", 99)
````

#### Read from tag: ####
````python
from comram import ramshare

test = ramshare.RamShare("share_name", data_type="/path_to_structure/test_structure.xml")
tag_1 = test.read_tag("tag_1")
````

#### Produce data structure: ####
````python
from comram import procon

producer = procon.Produce("share_name", data_type="/path_to_structure/test_structure.xml", ip="127.0.0.1", port=9980, 
                          send_interval=0.01)
producer.start_produce()
````

#### Consume data structure: ####
````python
from comram import procon

consumer = procon.Consume("share_name", "consumer_name", data_type="/path_to_structure/test_structure.xml",
                          ip="127.0.0.1", port=9980)
consumer.start_consume()
````

#### Known issues ####
tag lenght under under 2 byte not possible