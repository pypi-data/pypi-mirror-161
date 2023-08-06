
import json

version_json = '''
{"date": "2022-07-31T13:17:42.165147", "dirty": false, "error": null, "full-revisionid": "4b0a7a8370401573d78abfa7d0b0d916d7f46403", "version": "1.0.0rc1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

