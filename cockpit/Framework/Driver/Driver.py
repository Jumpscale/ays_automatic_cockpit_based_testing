from cockpit.Framework.Driver.CreateBluePrint import CreateBluePrint
from cockpit.Framework.Driver.RequestCockpitAPI import RequestCockpitAPI

if __name__ == '__main__':
    create_blueprint = CreateBluePrint()
    request_cockpit_api = RequestCockpitAPI()

    create_blueprint.create_blueprint()
    request_cockpit_api.create_new_repository(repository=request_cockpit_api.repo['name'])
    request_cockpit_api.send_blueprint(repository=request_cockpit_api.repo['name'],
                                       blueprint=create_blueprint.load_bp())

    request_cockpit_api.execute_blueprint(repository=request_cockpit_api.repo['name'],
                                          blueprint=request_cockpit_api.blueprint['name'])
    request_cockpit_api.run_repository(repository=request_cockpit_api.repo['name'])
    request_cockpit_api.get_service_data(repository=request_cockpit_api.repo['name'],
                                         role='vdc_test',
                                         service=create_blueprint.values['vdc_test'])
