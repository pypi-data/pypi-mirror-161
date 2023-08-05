import random
import re

from .default_functions import default_functions
from rasa_sdk import Tracker


class AttributeDict(dict):
    """A simple helper class to allow for dot notation when accessing dict members."""
    def __getattr__(self, attr):
        val = self.get(attr, None)
        if isinstance(val, dict):
            return AttributeDict(val)
        elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
            return [AttributeDict(x) for x in val]
        else:
            return val

    def __setattr__(self, attr, value):
        self[attr] = value


def eval_expr(tracker: Tracker, expr: str) -> any:
    """Evaluates the given expression in the context of the tracker.

    Args:
        tracker: The tracker to evaluate the expression in.
        expr: The expression to evaluate.
    """
    if not expr:
        return None

    # Hacked support for "no" instead of "not", "is" and "is not"
    expr = re.sub(r"(^| )no ", " not ", expr)
    expr = re.sub(r" is ", " == ", expr)
    expr = re.sub(r" is not ", " != ", expr)

    # First, we extract all the variable names and replace $ with "var_.
    var_names = re.findall(r'(?<!")\$([a-zA-Z_][a-zA-Z0-9_]*)', expr)
    updated_expr = re.sub(r'(?<!")\$([a-zA-Z_][a-zA-Z0-9_]*)', r"var_\1", expr)
    expr_locals = {}

    for var_name in var_names:
        # if we've already computed the value, we skip
        if f"var_{var_name}" in expr_locals:
            continue

        val = tracker.slots.get(var_name, None)
        if isinstance(val, dict):
            val = AttributeDict(val)

        expr_locals[f"var_{var_name}"] = val

    # Next, we just evaluate the expression using python.
    try:
        return eval(
            updated_expr, {"random": random, **expr_locals, **default_functions}
        )
    except Exception as ex:
        raise Exception(f"Error evaluating '{expr}' ('{updated_expr}'): {str(ex)}")
