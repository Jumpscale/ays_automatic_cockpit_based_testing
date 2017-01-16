import threading
import Queue
from CreateBluePrint import CreateBluePrint
from RequestCockpitAPI import RequestCockpitAPI
from cockpit_testing.Framework.utils.utils import BaseTest
import time, traceback, sys
from optparse import OptionParser

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', help='run a specific blueprint name', dest='bpName', default='', action='store')
    parser.add_option('-u', help='use a specific account', dest='account', default='', action='store')
    parser.add_option('-s', help='use a specific blueprint directory', dest='bpDirectory', default='', action='store')
    parser.add_option('--no-clone', help='clone development repo', dest='clone', default=True, action='store_false')
    parser.add_option('--no-backend', help='no backend environment', dest='no_backend', default=False, action='store_true')
    (options, args) = parser.parse_args()

    print ' * Driver is running ..... '
    base_test = BaseTest()
    base_test.log()

    THREADS_NUMBER = int(base_test.values['threads_number'])
    BLUEPRINT_NAME = options.bpName

    create_blueprint = CreateBluePrint(clone=options.clone, no_backend=options.no_backend, bp_dir=options.bpDirectory)
    if options.account:
        create_blueprint.values['account'] = options.account
    elif not options.no_backend:
        create_blueprint.create_account()

    create_blueprint.create_blueprint()
    role = {}

    import ipdb; ipdb.set_trace()
    def get_testService_role(blueprint, thread_name):
        global role
        blueprint = blueprint.splitlines()
        for line in blueprint:
            if 'QA SERVICE' in line:
                index = blueprint.index(line) + 1
                break
        else:
            raise NameError("The blueprint doesn't have 'QA SERVICE' indicator line")
        role_line = blueprint[index]
        role[thread_name] = [role_line[:role_line.find('__')], role_line[role_line.find('__') + 2:-1]]


    queue = Queue.Queue()
    jobs = base_test.get_jobs(specific_blueprint=BLUEPRINT_NAME)
    for job in jobs:
        queue.put(job)


    def work():
        while not queue.empty():
            testCasesPath = queue.get()
            bpFileName = testCasesPath[testCasesPath.index('/TestCases/') + 11:]
            print ' * Test case : %s' % bpFileName
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

                if request_cockpit_api.get_run_status(repository=request_cockpit_api.repo['name'],
                                                      run_key=request_cockpit_api.repo['key']):
                    base_test.Testcases_results[
                        bpFileName] = request_cockpit_api.get_service_data(
                        repository=request_cockpit_api.repo['name'],
                        role=role[threading.current_thread().name][0],
                        service=role[threading.current_thread().name][1])
                else:
                    request_cockpit_api.testcase_time = '{:0.2f}'.format(time.time() - request_cockpit_api.start_time)
                    error_message = 'ERROR : %s %s' % (
                        request_cockpit_api.blueprint['name'], request_cockpit_api.blueprint['log'])

                    base_test.Testcases_results[bpFileName] = [error_message,
                                                               request_cockpit_api.testcase_time]

                queue.task_done()

            except:
                base_test.logging.error(traceback.format_exc())

                # Add error message to xml result
                error_message = 'ERROR : %s %s' % (request_cockpit_api.response_error_content, traceback.format_exc())
                base_test.Testcases_results[bpFileName] = [error_message, 0]

                queue.task_done()


    for _ in range(THREADS_NUMBER):
        threading.Thread(target=work).start()

    queue.join()
    base_test.generate_xml_results()
    if not options.account:
        create_blueprint.teardown()
