from ...core_interface import invoke_core_method
import traceback
from ...utils.logger import Logger
from ... import common_utils
logger = Logger()


def set_property_to_instance(data):
    setattr(data['instance'], data['config']['property'], data['result'])


def get_stack_trace(data):
    try:
        result = data.get('result', {})
        events = result.get('events', None)
        if isinstance(events, list):
            if result.get('shouldCollectStacktrace', None):
                stack_trace = traceback.extract_stack().copy()
                filtered_stack_trace = list(filter(
                    lambda stack_frame: 'protectonce' not in stack_frame.filename, stack_trace))
                mapped_stack_trace = list(
                    map(common_utils.map_stack_trace, filtered_stack_trace))
                for event in events:
                    event['stackTrace'] = mapped_stack_trace
            return events
    except Exception as e:
        logger.info() and logger.write(
            'basic.get_stack_trace failed with error : ' + str(e))
    return []
