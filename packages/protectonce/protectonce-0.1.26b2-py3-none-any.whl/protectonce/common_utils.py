from .utils.logger import Logger
logger = Logger()


def is_action_blocked(data):
    try:
        return data['result'] and isinstance(data['result'], dict) and data['result'].get('action', '') in ['block', 'abort', 'redirect']
    except Exception as e:
        logger.error() and logger.write(
            'common_utils.is_action_blocked failed with error ' + str(e))

    return False


def map_stack_trace(stack_frame):
    return {
        'fileName': stack_frame.filename,
        'functionName': stack_frame.name,
        'lineNumber': stack_frame.lineno
    }
