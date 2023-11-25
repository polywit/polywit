import yaml
import inspect
from abc import ABC, abstractmethod
from collections import defaultdict 
  

# class StepType(Enum):
#     CHOICE = 'Choice',
#     ENGINE = 'Engine',
#     RESULT = 'Result'

class WorkflowParser:

    def __init__(self):
        pass
    
    def parse_workflow(self, file):
        step_map = defaultdict() 
        workflow_dict = self._read_workflow(file)
        description = self._get_required_node(workflow_dict, 'Description')
        start_step = self._get_required_node(workflow_dict, 'StartAt')
        language = self._get_required_node(workflow_dict, 'Language')
        steps = self._get_required_node(workflow_dict, 'Steps')
        
        for step_name, step_config in steps.items():
            step_map[step_name] = self._parse_step(step_config)

        return Workflow(description, language, step_map, start_step)
    
    def _parse_step(self, step_config):
        step_type = self._get_required_node(step_config, 'Type')
        if step_type == 'Choice':
            return self._parse_choice_step(step_config)
        if step_type == 'Engine':
            return self._parse_engine_step(step_config)
        if step_type == 'Result':
            return self._parse_result_step(step_config)
        raise ValueError('TODO: Exception with unknown step')
    
    def _parse_choice_step(self, choice_step_config): 
        choices = self._get_required_node(choice_step_config, 'Choices')
        for choice in choices:
            self._get_required_node(choice, 'Variable')
            self._get_required_node(choice, 'Value')
            self._get_required_node(choice, 'Next')
        return ChoiceStep(choices)

    def _parse_result_step(self, result_step_config):
        result = self._get_required_node(result_step_config, 'Result')
        return ResultStep(result)

    def _parse_engine_step(self, engine_step_config):
        validation_method = self._get_required_node(engine_step_config, 'Method')
        result_variable = self._get_required_node(engine_step_config, 'ResultVariable')
        next_step = self._get_required_node(engine_step_config, 'Next')
        parameters = self._get_required_node(engine_step_config, 'Parameters')
        # Construct the engine based on the validation method and parameters
        engine = None
        return EngineStep(engine, result_variable, next_step)

    @staticmethod
    def _read_workflow(file):
        with open(file, 'r') as file:
            try:
                yaml_content = yaml.safe_load(file)
                return yaml_content
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file: {e}")
                return None 
    
    @staticmethod
    def _get_optional_node(node_dict, node_name):
        return node_dict.get(node_name, None)

    @staticmethod
    def _get_required_node(node_dict, node_name):
        if not node_name in node_dict:
            raise ValueError(f'TODO: Workflow does not contain required node: {node_name} with dict: {node_dict}')
        return node_dict[node_name]
    
class Workflow:

    def __init__(self, description, language, step_map, start_step_name):
        self._description = description
        self._language = language
        self._step_map = step_map
        self._start_step_name = start_step_name

    def execute(self, start_state):
        state = start_state
        next_step_name = self._start_step_name
        step = None
        while next_step_name is not None:
            step = self._step_map.get(next_step_name)
            state = step.step_action(state)
            next_step_name = step.next_step()
        return step.result
        


class Step(ABC):
    '''
    TODO: Description
    TODO: wrapper of intrenal workflow state
    '''

    @abstractmethod
    def step_action(self, state):
        pass

    @abstractmethod
    def next_step(self, state):
        pass

class ChoiceStep(Step):
    '''
    TODO:
    '''

    def __init__(self, choices):
        self.choice_conditions = [
            self._construct_choice_lambda(
                choice['Variable'], 
                choice['Value'], 
                choice['Next']) for choice in choices ]
        self._next_step = None

        
    @staticmethod
    def _construct_choice_lambda(variable_name, matching_value, next_step):
        return lambda state: state.get(variable_name, "") == matching_value, next_step


    def step_action(self, state):
        next_steps = self._evaluate_next_steps(state)
        if len(next_steps) != 1:
            raise ValueError('TODO: Expected a single next step at the evaluated choice block, got ...')
        self._next_step = next_steps[0]
        return state

    def next_step(self):
        return self._next_step

    def _evaluate_next_steps(self, state):
        next_steps = []
        for condition, next_step in self.choice_conditions:
            if condition(state):
                next_steps.append(next_step)
        return next_steps

class ResultStep(Step):
    def __init__(self, result):
        self._next_step = None
        self.result = result

    def step_action(self, state):
        return state

    def next_step(self):
        return self._next_step

class EngineStep(Step):

    def __init__(self, engine, result_variable, next_step):
        self._engine = engine
        self._result_variable = result_variable
        self._next_step = next_step

    def step_action(self, state):
        # self._engine_execute
        state[self._result_variable] = 'VALID' #TODO: Can be different result
        return state

    def next_step(self):
        return self._next_step
    

def read_and_parse_yaml():
    with open('workflow.yaml', 'r') as file:
        try:
            yaml_content = yaml.safe_load(file)
            return yaml_content
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return None

yaml_dict = read_and_parse_yaml()#['Workflow']next_step
state = {'WitnessType': 'VIOLATION'}
workflow = WorkflowParser().parse_workflow('workflow.yaml')
print(workflow.execute(state))

 