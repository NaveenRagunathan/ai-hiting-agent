from typing import Dict

REQUIRED_FIELDS = ["intent"]

class Validator:
    @staticmethod
    def validate(parsed: Dict) -> Dict:
        # Ensure required fields are present
        for field in REQUIRED_FIELDS:
            if field not in parsed or not parsed[field]:
                parsed[field] = None
        # Optionally, add more checks here
        return parsed 