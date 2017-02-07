# 1 Cockpit Driver
The cockpit driver is a script to automate testing of the cockpit solution. It drivers the blueprints and generate a result XML file. It executes the following steps:
* Clone a specific repo which has the blueprints templates.
* Create an account (default). You can pass a specific account using -u option, or you can ignore accessing an environment at all by using --no-clone option.
* Create the blueprints by replacing all random values in these bleuprints with the specific values depending on the config.ini file.
* Call the cockpit API to create new repo.
* Call the cockpit API to add a new blueprint to this repo.
* Call the cockpit API to execute this repo get the run key.
* Call the cockpit API to check the running status (NEW, OK and ERROR).
* Get the result values after the execution status switch from 'NEW' to 'OK' or 'ERROR'.
* Generate a result XML file which is compatible with Jenkins.
* Delete the created account.


# 1.1 Getting Started
To use the Driver, follow the following commands:
* Clone the repo
```
git clone git@github.com:Jumpscale/ays_automatic_cockpit_based_testing.git
```
* Enter Username, Password, Environment, Location, cockpit_url, client_id, client_secret, repo and the branch values in the config.ini file.

 Hint : client_id and client_secret are using to get JWT from itsyou.online for the production cockpit mode. Repo and the branch which are having the blueprints will be executed.

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
  -h, --help      show this help message and exit
  -b BPNAME       run a specific blueprint name
  -a ACCOUNT      use a specific account
  -d BPDIRECTORY  use a specific blueprint directory
  --no-clone      clone development repo
  --no-backend    no backend environment
  --no-teardown   no teardown

```
If you need to execute a specific blueprint, you have to add its full name after -b option.
If you don't need to clone the repo, Just use --no-clone option.
If you need to use a specific account add its name after -u  and in this case, Driver won't delete this account.
If you don't need to use the back end environment, Use --no-backend option.
If you need to run a specific blueprints under a specific directory under bp_test_templates, set the directory name after -s option.
If you don't wanna delete the created account, please use --no-teardown option.

* Check logs in log.log file.
* The results will be documented in testresults.xml file.

# 1.2 Blueprint Templates Creation:
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

# Add Blueprint Templates To The Repo:
  The driver is looking for the blueprint templates in the /<repo_name>/tests/bp_test_templates directory so you have to craete this path and add your blueprint templates under it.

# 1.3 Service template:
To create a new testing service, You have to follow this sample:
```python
def init_actions_(service, args):
    return {

        'test': ['install']

    }


def test(job):
    RESULT_OK = 'OK : %s'
    RESULT_FAILED = 'FAILED : %s'
    RESULT_ERROR = 'ERROR : %s %%s' % job.service.name
    try:
        # write your test service body here.

        if 'OK_condition':
             service.model.data.result = RESULT_OK % ('Reason')
        else 'FAILED_condition':
            model.data.result = RESULT_FAILED % ('Trace back')
    except:
        model.data.result = RESULT_ERROR % ('Trace back')
    finally:
        job.service.save()
```

# Add Testing Service To The AYS Repo:
  You have to add any new test service to the AYS repo and to consume these services you should have a cockpit machine which was installed from this repo.

# 2. Cockpit Installer
The cockpit installer is a script to automate the cockpit installation steps in the development mode. It executes the following steps:
* Create a new account (default). You can pass a specific account using -u option.
* Create a new cloudspace.
* Create a new virtual machine with Ubuntu 16.04.
* Forward ports 2222 to 22, 80 to 82 and 5000 to 5000.
* Create an ssh connection between your local machine and this virtual machine.
* Update this virtual machine OS.
* Install jumpscale using a specific branch.
* Install cockpit using a specific branch.
* Update the config.ini file with the new cockpit url.

# 2.1 Getting Started
Follow the following commands:
* Clone the repo
```
git clone git@github.com:Jumpscale/ays_automatic_cockpit_based_testing.git
```
* Enter Username, Password and the Environment values in the config.ini file.
* From your terminal make sure that the current directory is ays_automatic_cockpit_based_testing
* Execute the following commands:
```
export PYTHONPATH='./'
python cockpit_testing/Framework/Installer/Installer.py
```
Hint: The Installer --help is:
```
Usage: Installer.py [options]

Options:
  -h, --help            show this help message and exit
  -b BRANCH              * branch, Default : 8.1.0
  -a ACCOUNT, --use-account=ACCOUNT
                        use a specific account

```
If you need to install from a specific jumpscale branch, add the branch number after -b option.
If you need to install from a specific cockpit branch, add the branch number after -s option.
If you need to use a specific account, Please set its name after -u option.

* Check logs in log.log file.
* After the installation is completed, the cockpit_url variable in the config.ini file will be changed automatically to point the new cockpit.


# Author
* Islam Taha
