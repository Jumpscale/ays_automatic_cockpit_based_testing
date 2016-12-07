'''
    This file should manipulate the bps. It should replace each variable with its correct value.
'''

from cockpit_testing.Framework.utils.utils import BaseTest
import os


class CreateBluePrint(BaseTest):

    def __init__(self):
        super(CreateBluePrint, self).__init__()
        self.setup()
        script_dir = os.path.dirname(__file__)
        self.testCasesTemplateDirectory = os.path.join(script_dir, "../TestCasesTemplate/")
        self.TestCasesTemplatePath = []
        self.TestCasesPath = []
        self.testCasesDirectory = os.path.join(script_dir, "../TestCases/")
        self.get_TestcasesTemplate_files()

        if not os.path.exists(self.testCasesDirectory):
            os.makedirs(self.testCasesDirectory)

    def get_TestcasesTemplate_files(self):

        files = os.listdir(self.testCasesTemplateDirectory)

        for file_name in files:
            if 'yaml' in file_name:
                self.TestCasesTemplatePath.append(os.path.join(self.testCasesTemplateDirectory, file_name))
                self.TestCasesPath.append(os.path.join(self.testCasesDirectory, file_name))

    def create_blueprint(self, name=''):
        if name:
            try:
                index = self.TestCasesTemplatePath.index(name)
            except:
                raise NameError('ERROR : There is no blueprint template with %s name ' % name)
            else:
                testCasesTemplatePath = self.TestCasesTemplatePath[index]
                self.pre_blueprint(index, testCasesTemplatePath)
        else:
            for index, testCasesTemplatePath in enumerate(self.TestCasesTemplatePath):
                self.pre_blueprint(index, testCasesTemplatePath)

    def pre_blueprint(self, index, testCasesTemplatePath):
        blueprintTemplate = open(testCasesTemplatePath, 'r')
        blueprint = self.convert_blueprintTemplate(blueprintTemplate)

        blueprintFile = open(self.TestCasesPath[index], 'w')
        for item in blueprint:
            blueprintFile.write(item)

        self.delete_random_from_values()

    def convert_blueprintTemplate(self, blueprintTemplate):
        blueprint = []
        self.blueprint_values = dict(self.values)
        for line in blueprintTemplate:
            if '{random_' in line:
                key = line[line.index('{') + 1: line.index('}')]
                if key not in self.blueprint_values:
                    generate = self.random_string()
                    self.blueprint_values[key] = generate
                new_line = line.replace('{' + key + '}', self.blueprint_values[key])
            elif '{random}' in line:
                new_line = line.replace('{random}', self.random_string())
            elif '{' in line and '}' in line:
                key = line[line.index('{') + 1: line.index('}')]
                new_line = line.replace('{' + key + '}', self.blueprint_values[key])
            else:
                new_line = line
            blueprint.append(new_line)
        return blueprint

    def load_blueprint(self, testCasesPath):
        blueprint = open(testCasesPath, 'r')
        return blueprint.read()

    def delete_random_from_values(self):
        # This method will delete 'random_' from the self.values' key
        for key in self.values:
            if 'random_' in key:
                new_key = key[key.index('random_') + 7:]
                self.values[new_key] = self.values.pop(key)
