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
```bash
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
So, If you need to execute a specific blueprint, you have to add its full name after -b and if you don't need to clone the repo, Just use --no-clone parameter.

* Check logs in log.log file.
* The results will be documented in testresults.xml file.

# Blueprint Templates Creation:
To create a new blueprint you have to follow the following sample:

```yaml
g8client__main:
    url: '{environment}'
    login: '{username}'
    password: '{password}'

vdc__{random_vdc}:
    description: '{random}'
    g8client: 'main'
    account: '{account}'
    location: '{location}'
    uservdc:
        - '{username}'

# 'QA SERVICE' (THE TEMPLATE SHOULD HAS THIS LINE)
test_create_cloudspace__{random}:
   vdc: {random_vdc}
   g8client: 'main'

actions:
   - action: 'install'
   - action: 'test_create_cloudspace'
     actor: test_create_cloudspace
```

This sample is following the following rules to identify the instance:
  * {random} : Driver will generate a random string.
  * {random_x} :  Driver will generate a random string and save its value to be set for other {random_x} in the blueprint.
  * {config_parameter} : Driver will replace it with the value of this parameter in the config file.
  * # 'QA SERVICE' (THE TEMPLATE SHOULD HAS THIS LINE) : This line should be set before the testing service consuming line.

# Add Blueprint templates to the repo:
  The driver is looking for the blueprint templates in the /<repo_name>/tests/bp_test_templates directory so you have to craete this path and add your blueprint templates under it.

# Add testing service to the AYS repo:
  You have to add any new test service to the AYS repo and to consume these services you should have a cockpit machine which was installed from this repo.

# Author
* Islam Taha
