import threading
import queue
from CreateBluePrint import CreateBluePrint
from RequestCockpitAPI import RequestCockpitAPI
from cockpit_testing.Framework.utils.utils import BaseTest
import time, traceback, sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='use a specific blueprint directory', dest='bpDirectory', default='', action='store')
    parser.add_argument('-b', help='run list of blueprints name', dest='bpName', action='store', default=[], nargs='+')
    parser.add_argument('-a', help='use a specific account', dest='account', default='', action='store')
    parser.add_argument('--clone', help='clone development repo', dest='clone', default=False, action='store_true')
    parser.add_argument('--teardown', help='teardown', dest='teardown', default=False, action='store_true')
    parser.add_argument('--no-backend', help='no backend environment', dest='no_backend', default=False,
                        action='store_true')
    options = parser.parse_args()

    print(' * Driver is running ..... ')
    base_test = BaseTest()
    base_test.check_cockpit_is_exist()

    THREADS_NUMBER = int(base_test.values['threads_number'])
    BLUEPRINT_NAME = options.bpName

    create_blueprint = CreateBluePrint(clone=options.clone, no_backend=options.no_backend, bp_dir=options.bpDirectory)
    if options.account:
        create_blueprint.values['account'] = options.account
    elif not options.no_backend:
        create_blueprint.create_account()

    create_blueprint.create_blueprint()
    role = {}  # {'Thread_name : [ [role_name, service], [role_name, service], .. ]}


    def get_testService_role(blueprint, thread_name):
        global role
        index = []
        blueprint = blueprint.splitlines()
        for line in blueprint:
            if 'test_' == line[:5]:
                index.append(blueprint.index(line))

        if len(index) == 0:
            raise NameError("The blueprint doesn't have any test roles.")

        role[thread_name] = []
        for i in index:
            role_line = blueprint[i]
            role_name = role_line[:role_line.find('__')]
            role_service = role_line[role_line.find('__') + 2:-1]
            role[thread_name].append([role_name, role_service])


    queue = queue.Queue()
    jobs = base_test.get_jobs(BLUEPRINT_NAME)
    for job in jobs:
        queue.put(job)


    def work():
        while not queue.empty():
            testCasesPath = queue.get()
            bpFileName = testCasesPath[testCasesPath.index('/TestCases/') + 11:]
            print((' * Test case : %s' % bpFileName))
            base_test.logging.info('\n')
            base_test.logging.info('* Test case : %s' % bpFileName)

            try:
                blueprint = create_blueprint.load_blueprint(testCasesPath=testCasesPath)
                get_testService_role(blueprint=blueprint, thread_name=threading.current_thread().name)
                request_cockpit_api = RequestCockpitAPI()
                request_cockpit_api.create_new_repository(repository=request_cockpit_api.repo['name'])
                request_cockpit_api.send_blueprint(repository=request_cockpit_api.repo['name'],
                                                   blueprint=blueprint)

                request_cockpit_api.execute_blueprint(repository=request_cockpit_api.repo['name'],
                                                      blueprint=request_cockpit_api.blueprint['name'])
                request_cockpit_api.run_repository(repository=request_cockpit_api.repo['name'])

                testCase_time = request_cockpit_api.get_run_status(repository=request_cockpit_api.repo['name'],
                                                                   run_key=request_cockpit_api.repo['key'],
                                                                   bpFileName=bpFileName)
                if testCase_time:
                    base_test.Testcases_results[bpFileName] = []
                    base_test.Testcases_results[bpFileName].append(['TestCase Time', testCase_time])
                    for role_item in role[threading.current_thread().name]:
                        base_test.Testcases_results[
                            bpFileName].append(request_cockpit_api.get_service_data(
                            repository=request_cockpit_api.repo['name'],
                            role=role_item[0],
                            service=role_item[1]))
                else:
                    request_cockpit_api.testcase_time = '{:0.2f}'.format(time.time() - request_cockpit_api.start_time)
                    error_message = 'ERROR : %s %s' % (
                        request_cockpit_api.blueprint['name'], request_cockpit_api.blueprint['log'])
                    #import ipdb; ipdb.set_trace()
                    base_test.Testcases_results[bpFileName] = [['TestCase Time', request_cockpit_api.testcase_time],
                                                               [error_message, role[threading.current_thread().name][0]]]

                queue.task_done()

            except:
                base_test.logging.error(traceback.format_exc())

                # Add error message to xml result
                error_message = 'ERROR : %s %s' % (traceback.format_exc(), request_cockpit_api.response_error_content)
                base_test.Testcases_results[bpFileName] = [['TestCase Time', 0], [error_message, 'Unknown service']]

                queue.task_done()


    for _ in range(THREADS_NUMBER):
        threading.Thread(target=work).start()

    queue.join()
    base_test.generate_xml_results()
    if options.teardown:
        create_blueprint.teardown()
