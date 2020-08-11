import uuid
import os
import traceback
import flask
import urllib, json
import logging
import jsonschema

class FlaskHelper():
    def __init__(self, port=None):
        self.session = {}
        self.server = flask.Flask(__name__)
        
        self.port = port if port else os.environ["PORT"]

    def route(self, url_rule, **kwargs):
        def wrapper(func):
            def method(*default_args, **default_kwargs):

                message = ""
                status_code = 200
                args = flask.request.get_json()
                args = {} if not args else args
                url_rule = str(flask.request.url_rule)

                with open("settings.json", "r", encoding="utf-8") as fp:
                    settings = json.loads(fp.read())

                schema_item = settings["api_schemas"][url_rule]

                try:
                    if schema_item == None:
                        raise ValueError(
                            "schema is none. url_rule is %s" % (url_rule))
                    try:
                        args = self.get_validated_obj(args, schema_item)
                    except Exception as e:
                        status_code = 400
                        raise ValueError(e)
                    default_kwargs.update({"args": args})
                    message = func(*default_args, **default_kwargs)

                except ValueError as e:
                    status_code = 400
                    exc = traceback.format_exc()
                    logging.warning("process failed. status code is %s. traceback is %s" % (
                        status_code, exc))
                    message = str(e)

                except Exception as e:
                    status_code = 500
                    exc = traceback.format_exc()
                    logging.error("process failed. status code is %s. traceback is %s" % (
                        status_code, exc))
                    message = str(e)

                return flask.jsonify({
                    "message": message
                }), status_code

            if "methods" not in kwargs:
                kwargs["methods"] = ["POST"]

            method.__name__ = func.__name__
            self.server.route(url_rule, **kwargs)(method)

            return method
        return wrapper


    def get_validated_obj(self, obj, schema_item):

        schema = schema_item.get("schema", {})
        properties = schema_item.get("properties", {})

        for name in properties:
            prop = properties[name]

            for key in prop:
                if key == "default":
                    default = prop[key]
                    if name not in obj:
                        obj[name] = default

            for key in prop:
                value = obj[name]
                if key == "change_type":
                    type_name = prop[key]
                    obj[name] = self.set_type(type_name, value)
        try:
            jsonschema.validate(obj, schema)
        except Exception as e:
            raise ValueError(f"validate failed. {e}")

        return obj

    def set_type(self, type_name, value):
        if type_name == "int":
            return int(value)
        elif type_name == "float":
            return float(value)
        elif type_name == "string":
            return str(value)
        elif type_name == "bool":
            if value == "true" or value == "True":
                return True
            elif value == "false" or value == "False":
                return False
            else:
                raise ValueError(f"invalid bool value. value is [{value}]")
        else:
            raise ValueError("invalid set type name %s" % (type_name))

    def listen(self):

        self.server.run("0.0.0.0", self.port)
