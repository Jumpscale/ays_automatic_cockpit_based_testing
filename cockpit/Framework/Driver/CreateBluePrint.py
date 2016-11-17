'''
    This file should manipulate the bps. It should replace each variable with its correct value.
'''

from cockpit.Framework.utils.utils import BaseTest
import os


class CreateBluePrint(BaseTest):
    
    script_dir = os.path.dirname(__file__)
    blueprint_template = "../TestCasesTemplate/demo_bp.yaml"
    blueprint = "../TestCases/demo_bp.yaml"
    bp_template_file_path = os.path.join(script_dir, blueprint_template)
    bp_file_path = os.path.join(script_dir, blueprint)

    def __init__(self):
        super(CreateBluePrint, self).__init__()
        self.new_blueprint = []

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

        self.delete_random_from_values()

    def load_bp(self):
        with open(self.bp_file_path, 'r') as bp:
            return bp.read()

    def delete_random_from_values(self):
        # This method will delete 'random_' from the self.values' key
        for key in self.values:
            if 'random_' in key:
                new_key = key[key.index('random_')+7:]
                self.values[new_key] = self.values.pop(key)
