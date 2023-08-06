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
    <connection_status LENGTH="20" TYPE="string" INIT_VALUE="no connection"  DESCRIPTION="status of connection" > </connection_status>
    <tag_1 LENGTH="10" TYPE="int" > </tag_1>
    <timestamp LENGTH="20" TYPE="float" > </timestamp>
    <status LENGTH="100" TYPE="string" ></status>
</config>
```
#### Required tags: ####
For produced / consumed data structures, "connection_status" is required. 

#### Required members: ####
tag_1 = reference name, used to read or write from data structure.

LENGTH = tag length in bytes

#### Optional members ####
TYPE = tag type, 
INIT_VALUE = initial tag value

DESCRIPTION = description of tag

#### Known issues ####
tag lenght under under 2 byte not possible