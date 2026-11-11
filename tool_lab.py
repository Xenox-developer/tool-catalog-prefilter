"""Implementation target for fixed INVARIANT acceptance."""
import json
import math
import re


STOPWORDS=frozenset('a an the and or to of in on for with our by from at as is it this that use search find look up exact text return most results preserve quoted verbatim'.split())


def select_tools(request, tools, k=4):
    def terms(text):
        return set(re.findall(r'[a-z0-9]+', text.lower())) - STOPWORDS

    request_terms = terms(request)

    def rank(tool):
        function = tool['function']
        overlap = request_terms & terms(function['name'] + ' ' + function['description'])
        return -len(overlap), function['name']

    return sorted(tools, key=rank)[:max(0, k)]


def score(response, expected, available_names=None):
    result = dict.fromkeys((
        'valid_single_call', 'name_correct', 'arguments_correct',
        'tool_available', 'exact',
    ), False)
    if not isinstance(response, dict):
        return result
    message = response.get('message')
    if not isinstance(message, dict):
        return result
    calls = message.get('tool_calls')
    if not isinstance(calls, list) or len(calls) != 1:
        return result
    call = calls[0]
    if not isinstance(call, dict):
        return result
    function = call.get('function')
    if not isinstance(function, dict):
        return result
    name = function.get('name')
    if not isinstance(name, str) or not name:
        return result

    result['valid_single_call'] = True
    if available_names is None:
        result['tool_available'] = True
    else:
        try:
            result['tool_available'] = name in available_names
        except TypeError:
            pass

    if not isinstance(expected, dict):
        return result
    result['name_correct'] = name == expected.get('name')
    arguments = function.get('arguments')
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except (ValueError, RecursionError):
            arguments = None
    expected_arguments = expected.get('arguments')
    if (isinstance(arguments, dict)
            and set(arguments) == {'query', 'limit'}
            and isinstance(expected_arguments, dict)):
        query = arguments['query']
        limit = arguments['limit']
        valid_limit = (
            isinstance(limit, (int, float))
            and not isinstance(limit, bool)
            and 1 <= limit <= 20
            and (isinstance(limit, int)
                 or (math.isfinite(limit) and limit.is_integer()))
        )
        result['arguments_correct'] = bool(
            isinstance(query, str)
            and query == expected_arguments.get('query')
            and valid_limit
            and limit == expected_arguments.get('limit')
        )
    result['exact'] = response.get('done') is True and all(
        result[key] for key in (
            'valid_single_call', 'name_correct',
            'arguments_correct', 'tool_available',
        )
    )
    return result
