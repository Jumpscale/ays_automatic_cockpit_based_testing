# make sure you are a root user .. don't need password for sudo
# have your ssh keys that have access on all repos
# all tests in all repos should be in /tests/testcasestemplate/
from subprocess import Popen, PIPE
from argparse import ArgumentParser
import re


def run_cmd_via_subprocess(cmd):
    sub = Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)
    out, err = sub.communicate()
    if sub.returncode == 0:
        return out.decode('utf-8')
    else:
        error_output = err.decode('utf-8')
        raise RuntimeError("Failed to execute command.\n\ncommand:\n{}\n\n".format(cmd, error_output))

def main(options):
    repos = options.repos[0].split()
    branches = options.branches[0].split()

    # make directory to clone repos on
    run_cmd_via_subprocess('mkdir removable')

    bps_driver_path = 'cockpit_testing/Framework/TestCasesTemplate'

    for repo, branch in zip(repos, branches):
        match = re.search(r'/(\S+).git', repo)
        repo_name = match.group(1)
        run_cmd_via_subprocess('cd removable; git clone %s' % repo)
        if branch != 'master':
            run_cmd_via_subprocess('cd removable/%s; git checkout %s' % (repo_name, branch))
        run_cmd_via_subprocess('cp -r removable/%s/tests/testcasestemplate/. %s' % (repo_name, bps_driver_path))

    run_cmd_via_subprocess('rm -rf removable')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-r", "--repos", dest="repos", nargs="+",
                        required=True, help="repos that contain the blueprints tests")
    parser.add_argument("-b", "--branches", dest="branches", nargs="+",
                        required=True, help="corresponding branches that contain tests")
    options = parser.parse_args()
    if not options.repos or not options.branches:
        parser.print_usage()
    else:
        main(options)
