
import json
from boltons.setutils import IndexedSet
from ..utils.logger import Logger
logger = Logger()


class BomHandler:
    _dynamic_bom = []
    _appName = ''

    @classmethod
    def cache_dynamic_bom(cls, dynamic_bom_entry, appname):
        cls._dynamic_bom.append(dynamic_bom_entry)
        if cls._appName is not None:
            cls._appName = appname

    @classmethod
    def _pre_process_dynamic_bom_entry(cls, dynamic_bom_list, module_names, unique_dynamic_bom_list):
        unique_modules = set()
        for dynamic_bom_entry in dynamic_bom_list:
            if not dynamic_bom_entry.get('name', '') in unique_modules:
                unique_modules.add(dynamic_bom_entry.get('name', ''))
                module_names.append({"moduleName": dynamic_bom_entry.get('name', ''), "modulePath": cls._get_relative_path(
                    dynamic_bom_entry.get('modulePath', ''), cls._appName)})
                unique_dynamic_bom_list.append(dynamic_bom_entry)
        unique_modules.clear()

    @classmethod
    def _process_stack_trace_entry(cls, dynamic_bom_entry, module_names,
                                   stack_frames, master_module_set, master_module_set_to_skip):
        for stack_trace_entry in dynamic_bom_entry.get('stackTrace', []):
            stack_trace_match = False
            for module in module_names:
                relative_file_name = cls._get_relative_path(
                    stack_trace_entry.get('fileName', ''), cls._appName)
                stack_trace_entry['fileName'] = relative_file_name
                if cls._is_include_stack_frame(stack_trace_entry, module.get('moduleName', '')):
                    stack_frames.append(stack_trace_entry)
                    master_module_set.add(json.dumps(module))
                    if dynamic_bom_entry.get('name', '') != module.get('moduleName', ''):
                        master_module_set_to_skip.add(json.dumps(module))
                    stack_trace_match = True
                    break
            if not stack_trace_match:
                stack_frames.append(stack_trace_entry)

    @classmethod
    def _process_modules_to_skip(cls, modules_of_same_length, master_module_set_to_skip, dynamic_bom_modules_to_skip, size_to_modules_to_skip_map):
        if not cls._if_module_exists(modules_of_same_length, master_module_set_to_skip):
            if len(master_module_set_to_skip):
                dynamic_bom_modules_to_skip.append(master_module_set_to_skip)
                modules_to_skip = size_to_modules_to_skip_map.get(
                    len(master_module_set_to_skip), [])
                if len(modules_to_skip) > 0:
                    modules_to_skip.append(master_module_set_to_skip)
                else:
                    filtered_modules_list = []
                    filtered_modules_list.append(master_module_set_to_skip)
                    size_to_modules_to_skip_map[len(
                        master_module_set_to_skip)] = filtered_modules_list

    @classmethod
    def process_dynamic_bom(cls):
        try:
            if len(cls._dynamic_bom) != 0:
                dynamic_bom_list = cls._dynamic_bom.copy()
                cls._dynamic_bom.clear()
                dynamic_bom_modules = []
                dynamic_bom_modules_to_skip = []
                module_names = []
                unique_dynamic_bom_list = []

                cls._pre_process_dynamic_bom_entry(
                    dynamic_bom_list, module_names, unique_dynamic_bom_list)
                size_to_modules_to_skip_map = {}

                for dynamic_bom_entry in unique_dynamic_bom_list:
                    master_module_set = IndexedSet()
                    master_module_set_to_skip = IndexedSet()
                    stack_frames = []

                    cls._process_stack_trace_entry(dynamic_bom_entry, module_names,
                                                   stack_frames, master_module_set, master_module_set_to_skip)

                    if cls._insert_module_required(master_module_set, dynamic_bom_entry):
                        master_module_set = cls._insert_module(
                            master_module_set, dynamic_bom_entry, cls._appName)

                    modules_of_same_length = cls._process_modules_of_same_length_from_map(
                        size_to_modules_to_skip_map, len(master_module_set_to_skip), dynamic_bom_modules_to_skip)

                    cls._process_modules_to_skip(
                        modules_of_same_length, master_module_set_to_skip, dynamic_bom_modules_to_skip, size_to_modules_to_skip_map)

                    dynamic_bom_entry_object = cls._create_dynamic_bom_entry_object(
                        master_module_set, stack_frames)
                    dynamic_bom_modules.append(dynamic_bom_entry_object)

                filtered_dynamic_bom_modules = cls._get_filtered_dynamic_bom_modules(
                    dynamic_bom_modules, dynamic_bom_modules_to_skip)

                cls._filter_dynamic_bom_modules(filtered_dynamic_bom_modules)
                return filtered_dynamic_bom_modules
        except Exception as e:
            logger.error() and logger.write(
                'process_dynamic_bom Failed with error: ' + str(e))
        return []

    @classmethod
    def _get_filtered_dynamic_bom_modules(cls, dynamic_bom_modules, dynamic_bom_modules_to_skip):
        filtered_dynamic_bom_modules = []
        for dynamic_bom_module_entry in dynamic_bom_modules:
            if not cls._if_module_exists(dynamic_bom_modules_to_skip, dynamic_bom_module_entry.get('modules', [])):
                filtered_dynamic_bom_modules.append(dynamic_bom_module_entry)
        return filtered_dynamic_bom_modules

    @classmethod
    def _create_dynamic_bom_entry_object(cls, master_module_set, stack_frames):
        dynamic_bom_entry_object = {}
        dynamic_bom_entry_object['modules'] = list(master_module_set)
        dynamic_bom_entry_object['stackTrace'] = stack_frames
        return dynamic_bom_entry_object

    @classmethod
    def _filter_dynamic_bom_modules(cls, filtered_dynamic_bom_modules):
        for filtered_dynamic_bom_modules_entry in filtered_dynamic_bom_modules:
            stack_trace = filtered_dynamic_bom_modules_entry.get(
                'stackTrace', [])
            mapped_stack_trace = list(map(cls._map_stack_trace, stack_trace))
            filtered_dynamic_bom_modules_entry['stackTrace'] = mapped_stack_trace
            modules = filtered_dynamic_bom_modules_entry.get('modules', [])
            modules_object = list(map(cls._map_modules, modules))
            filtered_dynamic_bom_modules_entry['modules'] = modules_object

    @classmethod
    def _map_stack_trace(cls, entry):
        file_name = entry.get('fileName', '') if entry.get(
            'fileName', '') else ''
        line_number = ":" + str(entry.get('lineNumber', 0)
                                ) if entry.get('lineNumber') else ""
        return file_name + line_number

    @classmethod
    def _process_modules_of_same_length_from_map(cls, size_to_modules_to_skip_map, module_size, modules_to_search):
        modules_of_same_length = []
        if module_size in size_to_modules_to_skip_map:
            modules_of_same_length = size_to_modules_to_skip_map.get(
                module_size, [])
        else:
            filtered_modules = cls._filter_modules(
                modules_to_search, module_size)
            if len(filtered_modules) > 0:
                modules_to_skip = size_to_modules_to_skip_map.get(
                    module_size, [])
                if len(modules_to_skip) > 0:
                    modules_to_skip.append(set(filtered_modules))
                else:
                    filtered_modules_list = []
                    filtered_modules_list.append(set(filtered_modules))
                    size_to_modules_to_skip_map[module_size] = filtered_modules_list
                modules_of_same_length = size_to_modules_to_skip_map.get(
                    module_size)
        return modules_of_same_length

    @classmethod
    def _filter_modules(cls, modules_to_filter, module_size):
        filtered_modules = [
            modules for modules in modules_to_filter if len(modules) == module_size]
        return filtered_modules

    @classmethod
    def _map_modules(cls, module):
        return json.loads(module)

    @classmethod
    def _get_relative_path(cls, file_name, appname):
        appname_index = file_name.find(appname)
        if appname_index != -1:
            substring_index = appname_index + len(appname)
            return file_name[substring_index+1:]
        else:
            return file_name

    @classmethod
    def _insert_module_required(cls, master_module_set, dynamic_bom_entry):
        if not len(master_module_set):
            return True
        for master_module_set_entry in master_module_set:
            master_module_set_entry_obj = json.loads(master_module_set_entry)
            if master_module_set_entry_obj.get('moduleName', '') == dynamic_bom_entry.get('name', ''):
                return False
        return True

    @classmethod
    def _insert_module(cls, master_module_set, dynamic_bom_entry, appname):
        master_module_set_list = list(master_module_set)
        root_module_name = dynamic_bom_entry.get('name', '')
        root_module_path = dynamic_bom_entry.get('modulePath', '')
        root_module = {"moduleName": root_module_name,
                       "modulePath": cls._get_relative_path(root_module_path, appname)}
        master_module_set_list.insert(0, root_module)
        master_module_set = IndexedSet()
        for entry in master_module_set_list:
            if not isinstance(entry, str):
                master_module_set.add(json.dumps(entry))
            else:
                master_module_set.add(entry)
        return master_module_set

    @classmethod
    def _if_module_exists(cls, modules_to_search_in, modules_to_search_for):
        for module_to_search_in in modules_to_search_in:
            master_module_set_exists = True
            module_names = []
            for module_obj in module_to_search_in:
                module_obj_obj = json.loads(module_obj)
                module_names.append(module_obj_obj.get('moduleName', ''))
            for module_to_search in modules_to_search_for:
                module_to_search_obj = json.loads(module_to_search)
                if not module_to_search_obj.get('moduleName', '') in module_names:
                    master_module_set_exists = False
                    break
            if master_module_set_exists:
                return True
        return False

    @classmethod
    def _is_include_stack_frame(cls, stack_trace_entry, module_name):
        try:
            last_index_of = stack_trace_entry.get('fileName', '').rindex("/")
            path_wo_forward_slash = stack_trace_entry.get('fileName', '')[
                0:last_index_of+1]
            return module_name in path_wo_forward_slash
        except ValueError as e:
            pass
