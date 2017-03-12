def init_actions_(service, args):

    """

    this needs to returns an array of actions representing the depencies between actions.

    Looks at ACTION_DEPS in this module for an example of what is expected

    """
    # some default logic for simple actions
    return {

        'test': ['install']

    }



def test(job):
    """
    Tests parsing of a bp with/without default values
    """
    # Tests that parsing args with values set in the bp will override default values
    if job.service.name == 'without_defaultvalue':
        assert job.service.model.data.description == 'another description', "values in blueprint do not override default values"
    # Tests that parsing args with default values works
    elif job.service.name == 'with_defaultvalue':
        assert job.service.model.data.description == 'description', "Parsing blueprint with default values failed"
    # Tests parsing blueprint that has special characters
    elif job.service.name == 'with_special_characters':
        assert job.service.model.data.description == 'Können Sie mir behilflich sein?', "Failed to parse blueprint with special characters"
