# DataBeaver - Data Model Orchestration
DataBeaver is a tool that allows teams to easily realize, test, version, and share their data models. 

## Overview
The aim of data beaver is to create a deterministic process for realizing a given data model.
Data beaver can be used as easily a command line utility or integrated into your application via the DataBeaver class. 
 
## Installing DataBeaver
To install Data Beaver you can run the command below.
```bash
pip install databeaver
```

## Using Data Beaver
### What Can I Do With Data Beaver
* Build your data model - Traditionally creating your data was a labor intensive process. First you would write some sql
then you would run the manually one by one. With Data Beaver a simple `beaver build` command will generate all the models
in their correct order, respecting dependencies. 
* (Not Yet) Visualize Model Dependencies - In a large model it can be tricky to keep track on what tables depend on what
other tables. Instead of trying to keep track of that yourself, let DataBeaver extract it directly from the sql and generate
and image file for you all with the simple `beaver visualize` command
  
### Using DataBeaver as a command line application 
#### Step 1 - Create a New Project
Before we start we need to create the basic directory structure needed and a configuration file that can be edited.  

*Command* 
```bash
beaver create-project --name=<projectName>
```


### Execute a model 
Data Beaver can be used as either a command line application or as a module for a more direct integration. 
#### Module Usage
```python
from databeaver import DataModel
model = DataModel()
model.build()
```



## Major Releases
| Version | Goal |Status|
|---------|----------------------------------------------------------|------|
|0.1.0    | Add the command line utility 'beaver' and 'DataBeaver' class |In Progress|
|0.2.0    | Build a Model against in Postgres                        ||
|0.3.0    | Build database models in MySQL                           ||

## Minor Releases 
| Version | Purpose                                                                       |
|---------|-------------------------------------------------------------------------------|
|0.0.37   | DataBeaver.build() now returns info on the models and files that were processed |

## Additional Documentation
[Classes](./docs/classes.md)<br>
[Configuration](./docs/configuration.md)

