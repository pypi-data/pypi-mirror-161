from .types.class_rule import ClassRule
from .types.virtual_module_rule import VirtualModuleRule


def create_rule(rule):
    intercept = rule.get('intercept', {})
    module = intercept.get('module', '')
    if VirtualModuleRule.is_virtual_module(module):
        return VirtualModuleRule(rule)

    return ClassRule(rule)


class RulesManager:
    def __init__(self, rules) -> None:
        self._rules = rules.get('hooks',[])
        self._features = rules.get('features',{})
        self._generate_rule_set()
        pass

    def apply_rules(self):
        for rule in self._rule_set:
            if rule._rule.get('type', "") == 'feature.sbom':
                if self._features.get('bom', {}).get('enabled', True):
                    rule.add_instrumentation()
            else:
                rule.add_instrumentation()
        pass

    def _generate_rule_set(self):
        self._rule_set = []
        for rule in self._rules:
            _rule = create_rule(rule)
            if _rule:
                self._rule_set.append(_rule)
