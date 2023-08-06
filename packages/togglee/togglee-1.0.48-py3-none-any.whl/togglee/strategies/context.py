operations_maps = {
    'eq': lambda first, second: first == second,
    'ne': lambda first, second: first != second,
    'gt': lambda first, second: first > second,
    'ge': lambda first, second: first >= second,
    'lt': lambda first, second: first < second,
    'le': lambda first, second: first <= second,
}


def context_strategy(toggle, context):
    for condition in toggle['conditions']:
        value = context[condition['field']]
        expected_value = condition['value']
        operation = condition['operation']
        if not operations_maps[operation](expected_value, value):
            return False
    return True
