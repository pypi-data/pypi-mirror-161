
import json

version_json = '''
{"date": "2022-07-31T13:42:18.560652", "dirty": false, "error": null, "full-revisionid": "018fd695ebadad7eed102ec3a00dcfa70cf44e83", "version": "1.0.0rc2"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

