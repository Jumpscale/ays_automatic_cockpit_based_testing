# Cockpit Installer
cockpit installer is a script to automate the cockpit installation steps. It executes the following steps:
* create an account.
* Create an cloudspace.
* Create a virtual machine with Ubuntu 16.04.
* Forward port 2222 to 22.
* Create an ssh connection between your local machine and this virtual machine.
* Update this virtual machine.
* Install jumpscale using a specific branch.
* Install cockpit using a specific branch.
* Forward port 80 to 82.
* Forward port 5000 to 5000.

# Getting Started
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
python cockpit_testing/Framework/Installer/Installer.py -b <JS branch> -s <cockpit branch>
```
* Check logs in log.log file.
* After the installation is completed, the cockpit_url variable in the config.ini file will be changed automatically to point the new cockpit.

# Author
* Islam Taha
