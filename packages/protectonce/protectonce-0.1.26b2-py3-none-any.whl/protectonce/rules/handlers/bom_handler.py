import traceback
from ...core_interface import invoke_core_method
from ...utils.logger import Logger
import os
import sys
from ...utils.config import Config
from ...bom.bom_handler import BomHandler
logger = Logger()

def get_module_details_from_stack_trace(data):
    module_details = {}
    if data['result']:
        module_details['version'] = data['result'].__version__
        module_details['name'] = data['result'].__name__
        module_details['modulePath'] = data['result'].__file__
    return module_details

def get_stack_trace():
    stt_obj = sys._getframe().f_back 
    estt_obj = traceback.extract_stack(f=stt_obj) 
    formatted_stack_trace = traceback.format_list(estt_obj) 
    return formatted_stack_trace

def get_module_details(data):
    try:
        module_details = {}
        try:
            if data['result']:
                module_details = get_module_details_from_stack_trace(data)
                library_path = os.path.dirname(os.__file__)
                if library_path in module_details['modulePath']:
                    return
                formatted_stack_trace = get_stack_trace()
                file_name = ''
                line_number = ''
                stack_trace = []
                for stack_frame_entry in formatted_stack_trace:
                    stack_frame_entry_tokenised = stack_frame_entry.split(',')
                    file_details = stack_frame_entry_tokenised[0]
                    file_details_tokens = file_details.split(' ')
                    if len(file_details_tokens) < 4:
                        continue
                    file_name = file_details_tokens[3]
                    lowest_index_double_quotes = file_details_tokens[3].find("\"")
                    highest_index_double_quotes = file_details_tokens[3].rfind("\"")
                    if lowest_index_double_quotes != -1 and highest_index_double_quotes != -1:
                        file_name = file_details_tokens[3][lowest_index_double_quotes+1:highest_index_double_quotes]

                    if ('protectonce' in file_name or 'frozen' in file_name or 'pythonFiles' in file_name):
                        continue
                    line_number_details = stack_frame_entry_tokenised[1]
                    line_number_details_tokenised = line_number_details.split(' ')
                    if len(line_number_details_tokenised) < 3:
                        continue
                    line_number = line_number_details_tokenised[2]
                    stack_trace_object = {'fileName': file_name, 'lineNumber': line_number}
                    stack_trace.append(stack_trace_object)
                module_details['stackTrace'] = stack_trace 
                BomHandler.cache_dynamic_bom(module_details,Config._appName)
        except Exception as e:
            return 
    except Exception as e:
        logger.error() and logger.write('bom_handler.get_module_details failed with error : ' + str(e))

