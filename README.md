# 0 Agenda :
- 1- Introduction
- 2- The Framework Architecture:
- 3- Cockpit Driver
  - 3.1- Introduction
  - 3.2- The Architecture
  - 3.3- The Flow Description
  - 3.4- The Execution Steps
  - 3.5- The Blueprint Templates Creation
  - 3.6- Add Blueprint Templates To The Repo
  - 3.7- The Service template
  - 3.8- Add Testing Service To The AYS Repo
- 4- Cockpit Installer


# 1 Introduction
This documentation includes the full details of **Cockpit Driver** and **Cockpit Installer**. The goal of **Cockpit Driver** is automating execution of blueprints. It takes a template of blueprints and produces the results in XML file. The goal of **Cockpit Installer** is automating the cockpit installation process in the development mode.

### 2 The Framework Architecture
```bash
├── cockpit_testing
│   ├── Config
│   │   ├── config.ini
│   │   └── generate_config.py
│   ├── Framework
│   │   ├── Driver
│   │   │   ├── CreateBluePrint.py
│   │   │   ├── Driver.py
│   │   │   ├── __init__.py
│   │   │   ├── README.md
│   │   │   └── RequestCockpitAPI.py
│   │   ├── __init__.py
│   │   ├── Installer
│   │   │   ├── ExecuteRemoteCommands.py
│   │   │   ├── __init__.py
│   │   │   ├── Installer.py
│   │   │   ├── README.md
│   │   │   ├── RequestEnvAPI.py
│   │   │   └── UpdateConfig.py
│   │   └── utils
│   │       ├── client.py
│   │       ├── __init__.py
│   │       └── utils.py
│   └── __init__.py
├── README.md
├── requirements.txt
└── results.xml
```

# 3 Cockpit Driver
### 3.1 Introduction:
The cockpit driver is a script to automate the execution of the blueprints and produce the results in XML file. The driver needs a cockpit machine which has the service which will be consumed by these blueprints. The driver will request the execution cockpit API to execute this blueprint and get the result back then it will create a result XML file.


### 3.3 The Flow Description:
The **Cockpit Drive** will parse the config.ini file then it will:
* Connect to a remote environment and create an account (default). You can pass a specific account using **-u** option, or you can ignore accessing an environment at all by using **--no-clone** option.
* Clone a specific repo which has the blueprints templates (make sure that you have access to clone this github repo via ssh).
* Create the blueprints by replacing all random values in these blueprints with the specific values depending on the config.ini file.
* Call the cockpit API to create new repo.
* Call the cockpit API to add a new blueprint to this repo.
* Call the cockpit API to execute this repo get the run key.
* Call the cockpit API to check the running status (NEW, OK and ERROR).
* Get the result values after the execution status switch from 'NEW' to 'OK' or 'ERROR'.
* Generate a result XML file which is compatible with Jenkins.
* Delete the created account.


### 3.4 The Execution Steps:
To use the Driver, follow the following commands:
* Clone the repo
```
git clone git@github.com:Jumpscale/ays_automatic_cockpit_based_testing.git
cd ays_automatic_cockpit_based_testing/cockpit_testing/Config
vim config.ini
```

* Edit the config.ini values:
```
  [main]
  environment = du-conv-2.demo.greenitglobe.com
  username = <username>
  password = <password>
  location = du-conv-2
  cockpit_url = http://192.168.28.63:5000/ays
  client_id =
  client_secret =
  repo = git@github.com:Jumpscale/ays_jumpscale8.git
  branch = 8.1.0
  # number of test cases to run in parallel
  threads_number = 1
```
 - environment : URL Of the environment
 - username : environment username
 - password : environment username password
 - location : One of the enviroment location
 - cockpit_url : URL of the cockpit
 - client_id and client_secret are using to get JWT from itsyou.online for the production cockpit mode.
 - repo : Which has the blueprints templates
 - branch : A specific repo branch
 - threads_number : Number of threads to execute blueprints in parallel


* From your terminal make sure that the current directory is ays_automatic_cockpit_based_testing, then execute the following command:
```bash
export PYTHONPATH='./'
python cockpit_testing/Framework/Driver/Driver.py # This will clone the repo and execute all the blueprints.
```

  **Driver options:**

    The driver --help is:

    ```
    Usage: Driver.py [options]

    Options:
      -h, --help      show this help message and exit
      -b BPNAME       run a specific blueprint name
      -d BPDIRECTORY  use a specific blueprint directory
      -a ACCOUNT      use a specific account
      --no-clone      clone development repo
      --no-backend    no backend environment
      --no-teardown   no teardown
    ```

    - To execute a specific blueprint which should be in the available blueprints directory, use -b option.
    - To execute a specific blueprints in a directory, use -d option.
    - To not clone the repo and use the exist one, use --no-clone option.
    - To use a specific account, use -a option and in this case, Driver won't delete this account.
    - To not use the back end environment, Use --no-backend option.
    - To not delete the created account, use --no-teardown option.


* Check logs in log.log file.
* The results will be documented in testresults.xml file.

### 3.5 The Blueprint Templates Creation:
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

The sample rules are:
  * {random} : Driver will generate a random string.
  * {random_x} :  Driver will generate a random string and save its value to be set for other {random_x} in the blueprint.
  * {config_parameter} : Driver will replace it with the value of this parameter in the config file.
  * #'QA SERVICE' (THE TEMPLATE SHOULD HAS THIS LINE) : This line should be set before the testing service consuming line.

### 3.6 Add Blueprint Templates To The Repo:
  The driver is looking for the blueprint templates in the /< repo_name>/tests/bp_test_templates directory so you have to create this path and add your blueprint templates under it.

### 3.7 The Service template:
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

### 3.8 Add Testing Service To The AYS Repo:
  You have to add any new test service to the AYS repo. To consume these services you should have a cockpit machine which was installed from this AYS repo or you have to update services directory on the cockpit machine.

# 4. Cockpit Installer
### 4.1 Introduction:
The cockpit installer is a script to automate the cockpit installation steps in the development mode.

### 4.2 The Flow Description:

The **Cockpit Installer** will parse the config.ini file then it will:
* Connect to a remote environment and create an account (default). You can pass a specific account using -u option
* Create a new cloudspace.
* Create a new virtual machine with Ubuntu 16.04.
* Forward ports 2222 to 22, 80 to 82 and 5000 to 5000.
* Create an ssh connection between your local machine and this virtual machine.
* Update this virtual machine OS.
* Install jumpscale using the specific branch.
* Install cockpit using the specific branch.
* Update the config.ini file with the new cockpit url.

# 4.3 The Execution Steps:
To use the Installer, follow the following commands:

  * Clone the repo

```bash
git clone git@github.com:Jumpscale/ays_automatic_cockpit_based_testing.git
```

* Edit the config.ini values:

```bash
cd ays_automatic_cockpit_based_testing/cockpit_testing/Config
vim config.ini
```

```
  [main]
  environment = du-conv-2.demo.greenitglobe.com
  username = <username>
  password = <password>
```
 - environment : URL Of the environment
 - username : environment username
 - password : environment username password


* From your terminal make sure that the current directory is ays_automatic_cockpit_based_testing
* Execute the following commands:
```bash
export PYTHONPATH='./'
python cockpit_testing/Framework/Installer/Installer.py
```
**Installer Options:**

   The Installer --help is:
  ```
  Usage: Installer.py [options]

  Options:
    -h, --help            show this help message and exit
    -b BRANCH              * branch, Default : 8.1.0
    -a ACCOUNT, --use-account=ACCOUNT
                          use a specific account
  ```

  - To install from a specific jumpscale branch, add the branch number after -b option.
  - To install from a specific cockpit branch, add the branch number after -s option.
  - To use a specific account, Please set its name after -u option.

* Check logs in log.log file.
* After the installation is completed, the cockpit_url variable in the config.ini file will be changed automatically to point the new cockpit.


# Author
* Islam Taha
