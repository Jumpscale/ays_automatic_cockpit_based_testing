# Cockpit Driver
The cockpit driver is a script to automate testing of the cockpit solution. It drivers the blueprints and generate a result XML file. It executes the following steps:
* Clone a specific repo which has the blueprints templates.
* Create an account.
* Modify these bleuprints templates with a new random values.
* Call the creation a new repo API.
* Call the creation a new blueprint API and send the blueprint.
* Call the execution repo API and get the run key.
* Call the checking running status API.
* Get the result values after the execution status switch from 'NEW' to 'OK'.
* Generate a result XML file which is compatible with Jenkins.


# Getting Started
To use the Driver, follow the following commands:
* Clone the repo
```
git clone git@github.com:Jumpscale/ays_automatic_cockpit_based_testing.git
```
* Enter Username, Password, Environment, Location, cockpit_url, client_id, client_secret, repo and the branch values in the config.ini file.
 Hint : client_id and client_secret are using to get JWT from itsyou.online for the production cockpit mode. Repo and the branch which are having the blueprints and services which will be executed.

* From your terminal make sure that the current directory is ays_automatic_cockpit_based_testing
* Execute the following commands:
```
export PYTHONPATH='./'
python cockpit_testing/Framework/Driver/Driver.py # This will clone the repo and execute all the blueprints.
```
Hint: The driver --help is:
```
Usage: Driver.py [options]

Options:
  -h, --help            show this help message and exit
  -b BPNAME, --bpname=BPNAME
                        blueprint name
  --no-clone            clone development repo

```
* Check logs in log.log file.
* The results will be documented in testresults.xml file.

# Author
* Islam Taha
