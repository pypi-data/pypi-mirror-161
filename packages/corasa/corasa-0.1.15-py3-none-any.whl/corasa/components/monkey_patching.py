import logging
import re
from typing import List, Dict, Text, Optional

from rasa.core.nlg import interpolator
from rasa.core.policies.rule_policy import RULES, RulePolicy
from rasa.nlu.components import Component
from rasa.shared.core.generator import TrackerWithCachedStates
from .datetime_util import nlg_formatter

logger = logging.getLogger(__name__)


class MonkeyPatching(Component):
    """Patches a few things to improve the RASA behavior."""
    pass


def interpolate_text(response: Text, values: Dict[Text, Text]) -> Text:
    """Interpolate values into responses with placeholders.

    Transform response tags from "{tag_name}" to "{0[tag_name]}" as described here:
    https://stackoverflow.com/questions/7934620/python-dots-in-the-name-of-variable-in-a-format-string#comment9695339_7934969
    Block characters, making sure not to allow:
    (a) newline in slot name
    (b) { or } in slot name

    Args:
        response: The piece of text that should be interpolated.
        values: A dictionary of keys and the values that those
            keys should be replaced with.

    Returns:
        The piece of text with any replacements made.
    """
    try:
        # print(f"Interpolating {response}.")

        # First, we compute the filters for every value that needs to be interpolated
        matches = re.findall(r"{([^}]+)}\|(\w+)", response)
        filters = {}
        for key, filter_name in matches:
            filters[key] = filter_name

        # Next, we get rid of the filters
        response = re.sub(r"}\|\w+", "}", response)

        # Next, we apply the filters to all keys present in the response
        matches = re.findall(r"{([^}]+)}", response)
        for key in matches:
            key_filters = [filters[key]] if key in filters else []
            obj = values
            while "." in key:
                _start, key = key.split(".", 1)
                obj = values.get(_start, {})

            obj[key] = nlg_formatter(obj.get(key, ""), key_filters)

            # print(f"Adjusted '{key}' to '{obj[key]}'")

        text = re.sub(r"{([^\n{}]+?)}", r"{0[\1]}", response)
        text = text.format(values)
        if "0[" in text:
            # regex replaced tag but format did not replace
            # likely cause would be that tag name was enclosed
            # in double curly and format func simply escaped it.
            # we don't want to return {0[SLOTNAME]} thus
            # restoring original value with { being escaped.
            return response.format({})

        return text
    except KeyError as e:
        logger.exception(
            f"Failed to replace placeholders in response '{response}'. "
            f"Tried to replace '{e.args[0]}' but could not find "
            f"a value for it. There is no slot with this "
            f"name nor did you pass the value explicitly "
            f"when calling the response. Return response "
            f"without filling the response. "
        )
        return response


interpolator.interpolate_text = interpolate_text


def _check_prediction(
        self,
        tracker: TrackerWithCachedStates,
        predicted_action_name: Optional[Text],
        gold_action_name: Text,
        prediction_source: Optional[Text],
) -> List[Text]:
    if not predicted_action_name or predicted_action_name == gold_action_name:
        return []

    # Also, disable checking when the predicted action name is "action_listen".
    # This is because of conflicts caused by implicitly adding "listen" at the end of
    # the stories.
    if gold_action_name == "action_listen":
        return []

    if self._should_delete(prediction_source, tracker, predicted_action_name):
        self.lookup[RULES].pop(prediction_source)
        return []

    tracker_type = "rule" if tracker.is_rule_tracker else "story"
    contradicting_rules = {
        rule_name
        for rule_name, action_name in self._rules_sources[prediction_source]
        if action_name != gold_action_name
    }

    error_message = (
        f"- the prediction of the action '{gold_action_name}' in {tracker_type} "
        f"'{tracker.sender_id}' "
        f"is contradicting with rule(s) '{', '.join(contradicting_rules)}'"
    )
    # outputting predicted action 'action_default_fallback' is confusing
    if predicted_action_name != self._fallback_action_name:
        error_message += f" which predicted action '{predicted_action_name}'"

    return [error_message + "."]


RulePolicy._check_prediction = _check_prediction


print("CoRASA monkey patching applied.")
