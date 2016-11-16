from cockpit.api_testing.drivers.CreateBluePrint import CreateBluePrint
from cockpit.api_testing.drivers.RequestCockpitAPI import RequestCockpitAPI

if __name__ == '__main__':
    '''
    call_create_repo()
    call_create_bp()
    send_bp(load_yaml_bp())
    ays_blueprint()
    ays_run()
    '''
    create_blueprint = CreateBluePrint()
    request_cockpit_api = RequestCockpitAPI()

    create_blueprint.create_blueprint()
    request_cockpit_api.create_new_repo()
    request_cockpit_api.send_blueprint(create_blueprint.load_bp())

    request_cockpit_api.execute_blueprint()
    request_cockpit_api.run_repo()
