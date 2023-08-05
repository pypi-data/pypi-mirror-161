from typing import Dict, Text, Any
from typing import List

import rasa.shared.utils.io
from rasa.nlu.extractors.duckling_entity_extractor import DucklingEntityExtractor as RASADucklingEntityExtractor
from rasa.shared.constants import DOCS_URL_COMPONENTS
from rasa.shared.nlu.constants import ENTITIES, TEXT
from rasa.shared.nlu.training_data.message import Message
from .datetime_util import parse_duckling_datetime


def extract_value(match: Dict[Text, Any]) -> Dict[Text, Any]:
    if match["value"].get("type") == "interval":
        value = {
            "to": match["value"].get("to", {}).get("value"),
            "from": match["value"].get("from", {}).get("value"),
        }
    else:
        value = match["value"].get("value")

    return value


def convert_duckling_format_to_rasa(
    matches: List[Dict[Text, Any]]
) -> List[Dict[Text, Any]]:
    extracted = []

    for match in matches:
        if match["dim"] == "time":
            entity = "datetime"
            value = parse_duckling_datetime(match)
        else:
            entity = match["dim"]
            value = extract_value(match)

        entity = {
            "start": match["start"],
            "end": match["end"],
            "text": match.get("body", match.get("text", None)),
            "value": value,
            "confidence": 1.0,
            "additional_info": match["value"],
            "entity": entity,
        }

        extracted.append(entity)

    return extracted


class DucklingEntityExtractor(RASADucklingEntityExtractor):
    """Wrapper on top of the original RASA entity extractor."""

    def process(self, message: Message, **kwargs: Any) -> None:

        if self._url() is not None:
            reference_time = self._reference_time_from_message(message)
            matches = self._duckling_parse(message.get(TEXT), reference_time)
            all_extracted = convert_duckling_format_to_rasa(matches)
            dimensions = self.component_config["dimensions"]
            extracted = DucklingEntityExtractor.filter_irrelevant_entities(
                all_extracted, dimensions
            )
        else:
            extracted = []
            rasa.shared.utils.io.raise_warning(
                "Duckling HTTP component in pipeline, but no "
                "`url` configuration in the config "
                "file nor is `RASA_DUCKLING_HTTP_URL` "
                "set as an environment variable. No entities will be extracted!",
                docs=DOCS_URL_COMPONENTS + "#DucklingEntityExtractor",
            )

        extracted = self.add_extractor_name(extracted)
        message.set(ENTITIES, message.get(ENTITIES, []) + extracted, add_to_output=True)
