import json

def deep_json_eval(data):
    if isinstance(data, dict):
        return {k: deep_json_eval(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [deep_json_eval(item) for item in data]
    elif isinstance(data, str):
        try:
            parsed = json.loads(data)
            return deep_json_eval(parsed)
        except (json.JSONDecodeError, TypeError):
            return data
    else:
        return data