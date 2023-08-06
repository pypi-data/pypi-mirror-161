import inspect

swagger_json_project = []

swagger_json_class = []
python_column_type_dict = {
    "list": "array",
    "str": "string",
    "int": "integer",
    "dict": "object",
    "bool": "boolean",
    "float": "multipleOf"
}
definitions = {}


def parser_swagger(func, desc):
    if type(func).__name__ == "type":
        swagger_json_project.append(
            {
                "desc": desc,
                "route": func.__route_name__,
                "method_list": swagger_json_class.copy()
            }
        )
        swagger_json_class.clear()

    elif type(func).__name__ == "function":
        param_list = [{
            "name": "Authorization",
            "in": "header",
            "required": False,
            "type": "string"
        }]
        args = get_args(func)
        if func.__http_method__ == "get":
            param_list.extend(args)
            swagger_json_class.append({
                "route": func.__route_name__,
                "summary": "Place an order for a pet",

                "operationId": "placeOrder",
                "consumes": ["application/json"],
                "produces": ["application/json", "application/xml"],
                "parameters": param_list,
                "description": desc,
                "http_method": func.__http_method__
            })
        elif func.__http_method__ == "post":
            schema = {
                "type": "object",
                "properties": {
                }
            }
            for param in args:
                param_type = param.get("type")
                if param_type in ["integer", "string"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": param_type,
                        "enum": [param.get("default", "string")]
                    }
                elif param_type in ["array"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": "array",
                        "xml": {"wrapped": True},
                        "items": {"type": "string"},
                        "enum": [param.get("default", "string")]
                    }
                elif param_type in ["object"]:
                    schema["properties"][param.get("name", "")] = {
                        "required": param.get("required", ""),
                        "type": "object",
                        "properties": {

                        }
                    }
            param_list.append({
                "required": True,
                "name": "body",
                "in": "body",
                "schema": schema
            })
            swagger_json_class.append({
                "route": func.__route_name__,
                "parameters": param_list,
                "description": desc,
                "http_method": func.__http_method__
            })
        else:
            pass


def get_args(func):
    params_list = []
    signature = inspect.signature(func)
    for parameter_name, parameter in signature.parameters.items():
        if parameter_name == 'self':
            continue
        else:
            parameter_type = parameter.annotation
            if parameter_type is inspect.Parameter.empty:
                parameter_type = type(parameter.default)
            parameter_default = None
            if parameter.default is not inspect.Parameter.empty:
                parameter_default = parameter.default
            parameter_type_str = "string"
            if not isinstance(parameter_type, type):
                if isinstance(parameter_type, int):
                    parameter_type_str = "integer"
                elif isinstance(parameter_type, str):
                    parameter_type_str = "string"
                elif isinstance(parameter_type, list) or isinstance(parameter_type, tuple):
                    parameter_type_str = "array"
                elif isinstance(parameter_type, dict):
                    parameter_type_str = "object"
                elif issubclass(parameter_type, object):
                    parameter_type_str = "object"
                elif issubclass(parameter_type, bool):
                    parameter_type_str = "boolean"
            params = {
                "required": False if parameter.default is not inspect.Parameter.empty else True,
                "name": parameter_name,
                "in": "query",
                "type": parameter_type_str,
                "default": parameter_default
            }
            params_list.append(params)
    return params_list
