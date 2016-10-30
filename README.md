
### TESTING STRATEGY
	we need to use the cockpit and AYS blue prints to drive test in these features.
	@Geert: please provide where we should add the test results as we used to track test results in jenkins but now for
			cockpit we need to have these result added somewhere (Ex.: push test results to github)
	
	## install cockpit
	- We need to install a stable cockpit somewhere to be used for drive test suites (Ex. be-scale-3)
		https://gig.gitbooks.io/cockpit/content/installation/installation.html

	## testing
	- we need to write the test which will be run through blue prints on the cockpit.
	There should be a configurable blue print which points out to the the environment to test.

	## AYS templates
	- For every script that we are running we need to create an AYS template. For the moment we have several AYS templates which can be re-used.

	## using REST APIs
	- this script can be used to call all the system REST APIs in order to check, verify and assert the results will come out from the blue prints:
		https://raw.githubusercontent.com/grimpy/openvcloudash/master/openvcloudash/openvcloud/client.py
		```
		client = Client(url, login, password)
		client.system.health.getOverallStatus()
		client.cloudapi.accounts.list()

		```
