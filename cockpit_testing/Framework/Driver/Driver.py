import threading
import Queue
from CreateBluePrint import CreateBluePrint
from RequestCockpitAPI import RequestCockpitAPI
from cockpit_testing.Framework.utils.utils import BaseTest
import time, traceback, sys

if __name__ == '__main__':

    base_test = BaseTest()
    THREADS_NUMBER = int(base_test.values['threads_number'])
    cmdargs = sys.argv
    if len(cmdargs) > 1:
        BLUEPRINT_NAME = cmdargs[1]
    else:
        BLUEPRINT_NAME = None
    create_blueprint = CreateBluePrint()
    create_blueprint.create_blueprint()
    role = {}


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
            try:
                testCasesPath = queue.get()
                print 'Test case path is : %s' % testCasesPath
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
                    request_cockpit_api.Testcases_results[
                        request_cockpit_api.blueprint['name']] = request_cockpit_api.get_service_data(
                        repository=request_cockpit_api.repo['name'],
                        role=role[threading.current_thread().name][0],
                        service=role[threading.current_thread().name][1])
                else:
                    request_cockpit_api.testcase_time = '{:0.2f}'.format(time.time() - request_cockpit_api.start_time)
                    error_message = 'ERROR : %s %s' % (
                        request_cockpit_api.blueprint['name'], request_cockpit_api.blueprint['log'])

                    request_cockpit_api.Testcases_results[request_cockpit_api.blueprint['name']] = [error_message,
                                                                                                    request_cockpit_api.testcase_time]

                request_cockpit_api.generate_xml_results()
                queue.task_done()
            except:
                queue.task_done()
                print traceback.format_exc()

    for _ in range(THREADS_NUMBER):
        threading.Thread(target=work).start()


    queue.join()
    create_blueprint.teardown()
