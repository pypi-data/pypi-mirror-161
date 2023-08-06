"""
Validate userdata in behave command
rules -> {
    '<rule 1>': [<list>, <of>, <valid>, <values>],
    '<rule 2>': [<list>, <of>, <valid>, <values>],
    '<rule 3>': [<list>, <of>, <valid>, <values>]
    }
"""
import json


class __ValidRules:
    def __init__(self):
        self.all_rules_are_valid = True
        self.all_rules_in_userdata = True
        self.broken_rules = []

    def is_ok(self):
        return self.all_rules_are_valid and self.all_rules_in_userdata and len(self.broken_rules) == 0


def validate_command(*, userdata, rules_file_path):
    validation = __ValidRules()

    with open(rules_file_path) as f:
        rules = json.load(f)

    for rule, valid_values in rules.items():
        if rule not in userdata:
            validation.all_rules_in_userdata = False
            validation.broken_rules.append({rule: 'not in userdata'})
            break
        if rule in userdata and userdata[rule] not in valid_values:
            validation.all_rules_are_valid = False
            validation.broken_rules.append({rule: f'"{userdata[rule]}" is an invalid value'})
            break
    else:
        validation.all_rules_in_userdata = True
        validation.all_rules_are_valid = True

    return validation
