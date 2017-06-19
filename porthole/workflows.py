

class SimpleWorkflow():
    """
    :functions: A list of functions to be executed:
        {'function': function_object, 'args': {'arg_name': arg_value}}

    Use to execute a sequence of functions. Assumes that each function
    returns boolean. Execution will continue, in order,
    unless/until False is returned, at which point execution will cease.

    Future implementation - option to stop on error vs. continue on error.
    """
    def __init__(self, functions):
        self.functions = functions
        self.completed = None
        self.failed_on = None

    def run(self):
        while self.functions:
            # pop FIRST function from list
            function = self.functions.pop(0)
            try:
                # execute function by unpacking dictionary
                success = function['function'](**function['args'])
            except:
                success = False
            if not success:
                self.completed = False
                self.failed_on = function
                break
        else: # only execute if loop finishes without breaking
            self.completed = True


if __name__ == '__main__':
    pass
