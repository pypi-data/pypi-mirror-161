import re
import importlib


def __call_function_based_on_re(**kwargs) -> bool:
    """
        Requires: context, expression, tag
        Args:
            **kwargs:
        Returns:
            bool
    """

    if any([key not in kwargs for key in ['context', 'expression', 'tag']]):
        return False

    tag_match = re.search(kwargs['expression'], kwargs['tag'])

    if tag_match:
        # look through the re to get required info
        mod_name = tag_match.groupdict()['mod_name']
        function_name = tag_match.groupdict()['function_name']
        module = importlib.import_module(f'trigger.{mod_name}')

        # if valid info call the function
        if hasattr(module, function_name):
            getattr(module, function_name)(kwargs['context'])
            return True
    return False


def tag_trigger(context, tag) -> bool:
    return __call_function_based_on_re(
        context=context,
        expression=r'trigger\.(?P<mod_name>before|after)\.(?P<function_name>.*)',
        tag=tag
    )
