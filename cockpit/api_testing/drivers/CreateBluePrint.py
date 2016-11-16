'''
    This file should manipulate the bps. It should replace each variable with its correct value.
'''

from cockpit.api_testing.utilz.utilz import BaseTest
import os
import yaml


class CreateBluePrint(BaseTest):
    
    script_dir = os.path.dirname(__file__)
    blueprint_template = "../testcases_template/demo_bp.yaml"
    blueprint = "../testcases/demo_bp.yaml"
    bp_template_file_path = os.path.join(script_dir, blueprint_template)
    bp_file_path = os.path.join(script_dir, blueprint)

    def __init__(self):
        super(CreateBluePrint, self).__init__()
        self.new_blueprint = []

        self.values = {'environment':'be-scale-3.demo.greenitglobe.com',
                       'username':'ramez',
                       'password':'saeedramez1',
                       'account':'Automated QA',
                       'location':'be-scale-3'
                       }

    def create_blueprint(self):
        self.new_blueprint = []
        blueprint = open(self.bp_template_file_path, 'r')
        
        for line in blueprint:
            if '{random_' in line:
                key = line[line.index('{')+1 : line.index('}')]
                if key not in self.values:
                    generate = self.random_string()
                    self.values[key] = generate
                new_line = line.replace('{'+key+'}', self.values[key])
            elif '{random}' in line:
                new_line = line.replace('{random}', self.random_string())
            elif '{' in line and '}' in line:
                key = line[line.index('{')+1 : line.index('}')]
                new_line = line.replace('{'+key+'}', self.values[key])
            else:
                new_line = line
            self.new_blueprint.append(new_line)

        new_blueprint_ = open(self.bp_file_path, 'w')
        for item in self.new_blueprint:
            new_blueprint_.write(item)

    def load_bp(self):
        with open(self.bp_file_path, 'r') as bp:
            return bp.read()
