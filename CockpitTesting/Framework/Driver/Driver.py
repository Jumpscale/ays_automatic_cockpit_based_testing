import threading
import Queue
from CreateBluePrint import CreateBluePrint
from RequestCockpitAPI import RequestCockpitAPI
from CockpitTesting.Framework.utils.utils import BaseTest


if __name__ == '__main__':
    THREADS_NUMBER = 2

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
        role[thread_name] = [role_line[:role_line.find('__')], role_line[role_line.find('__')+2:-1]]

    queue = Queue.Queue()
    base_test = BaseTest()
    jobs = base_test.get_jobs()
    for job in jobs:
        queue.put(job)

    def work():
        while not queue.empty():
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

            request_cockpit_api.Testcases_results[
                request_cockpit_api.blueprint['name']] = request_cockpit_api.get_service_data(
                repository=request_cockpit_api.repo['name'],
                role=role[threading.current_thread().name][0],
                service=role[threading.current_thread().name][1])

            request_cockpit_api.generate_xml_results()
            queue.task_done()

    for _ in range(THREADS_NUMBER):
        threading.Thread(target=work).start()
