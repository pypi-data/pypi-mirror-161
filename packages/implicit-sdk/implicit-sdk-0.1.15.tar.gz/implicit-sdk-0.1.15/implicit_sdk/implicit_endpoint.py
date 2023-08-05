from docstring_parser import parse
from inspect import getfullargspec
from flask import request, make_response
from django.http import HttpResponse
from typing import Optional, TypedDict, Callable
from typing import Optional, TypedDict
from django.views.decorators.csrf import csrf_exempt
import os
import json
import traceback


class FunctionIdentifier(TypedDict):
    name: Optional[str]
    type_name: Optional[str]
    summary: Optional[str]
    default: Optional[str]


class FunctionDocumentation(TypedDict):
    summary: Optional[str]
    params: list[FunctionIdentifier]
    returns: Optional[FunctionIdentifier]


class FunctionStructure(TypedDict):
    name: str
    params: list[str]
    DocComment: Optional[FunctionDocumentation]


class EndpointFunction(TypedDict):
    name: str
    params: list[str]
    DocComment: Optional[FunctionDocumentation]
    ref: Callable


class ImplicitEndpoint:
    JSType = {
        "str": "string",
        "int": "number",
        "float": "number",
        "complex": "number",
        "tuple": "object",
        "list": "object",
        "dict": "object",
        "bool": "boolean",
        "None": "null"
    }

    def __init__(self, url: str):
        base_attrs: dict = {}
        self._location: str = url
        for attr in dir(ImplicitEndpoint):
            base_attrs[attr] = type(getattr(ImplicitEndpoint, attr))
        obj_attrs: list[str] = dir(self)
        self._functions: dict[str, EndpointFunction] = {}
        for attr in obj_attrs:
            obj = getattr(self, attr)
            if type(obj).__name__ == 'method' and attr not in base_attrs:
                self._functions[attr] = self.__analize_function(obj)
                self._functions[attr]['ref'] = obj

    @classmethod
    def __Python_Type_To_JSType(cls, pythonType: str | None) -> str:
        if pythonType is None:
            return ''
        return cls.__use_template(pythonType, cls.JSType)

    @classmethod
    def __JSDoc(cls, func_doc: FunctionDocumentation) -> str:
        """This function takes a FunctionDocumentation Dict object
        and compiles it into a JavaScript JSDoc documentation block
        string describing the function.

        Args:
            func_doc (FunctionDocumentation): Function details to
            be compiled to JavaScript JSDoc comment

        Returns:
            str: A string representing a JSDoc for the provided details
            or an empty string otherwise.
        """
        ret = "/**\n"

        def commentBlock(blockStr):
            return "\n".join(
                map(
                    lambda l: f" * {l}",
                    blockStr.split("\n")
                )
            )
        if 'summary' in func_doc:
            ret += f"{commentBlock(func_doc.get('summary'))}\n"
        if "params" in func_doc:
            params = func_doc.get("params")
            if params:
                for param in params:
                    JSType = cls.__Python_Type_To_JSType(param.get("type_name"))
                    paramStr = f"@param {{{JSType}}} {param.get('name')} {param.get('summary')}"
                    ret += commentBlock(paramStr) + "\n"
        if "returns" in func_doc:
            returns = func_doc["returns"]
            ret_type = cls.__Python_Type_To_JSType(returns["type_name"])
            returnStr = "@return"
            if ret_type:
                returnStr += f" {{{ret_type}}}"
            if returns.get("name"):
                returnStr += f" {returns['name']}"
            if returns.get("summary"):
                returnStr += f" {returns['summary']}"
            ret += commentBlock(returnStr) + "\n"
        ret += " */"
        return ret

    @classmethod
    def __HTMLDoc(cls, func_doc: FunctionDocumentation) -> str:
        """This function takes a FunctionDocumentation Dict object
        and compiles it into an html documentation describing the function 

        Args:
            func_doc (FunctionDocumentation): Function details to
            be compiled to JavaScript JSDoc comment

        Returns:
            str: A string representing HTML documentation for the provided
            details
        """
        ret = ""
        if func_doc.get("summary"):
            ret = "<p class='indented'>" + \
                func_doc["summary"].replace("\n", "<br />") + "</p>"
        ret += "<h4>Parameters: </h4>"
        if len(func_doc["params"]):
            ret += "<ul>"
            for param in func_doc["params"]:
                type_name = param.get("type_name") if param.get(
                    "type_name") else ''
                name = f" {param.get('name')}" if param.get('name') else ''
                arg_desc = f"<p class='indented'>{param.get('summary')} </p>" \
                    if param.get('summary') else ''
                paramStr = f"<li><b><i>{type_name}</i>{name}</b>{arg_desc}</li>"
                ret += paramStr.replace("\n", "<br />")
            ret += "</ul>"
        else:
            ret += "<p>No parameters</p>"
        ret += "<h4>Return Value: </h4>"

        if "returns" in func_doc:
            retStr = "<ul><li>"
            if "type_name" in func_doc["returns"]:
                retStr += "<b><i>" + \
                    func_doc["returns"]["type_name"] + \
                    "</i></b>"
            if "summary" in func_doc["returns"]:
                retStr += "<p>" + \
                    func_doc["returns"]["summary"] + \
                    "</p>"
            retStr += "</li></ul>"
            ret += retStr.replace("\n", "<br />")
        else:
            ret += "<p>No Return value</p>"
        return ret

    @classmethod
    def __parse_DocComment(cls, comment: str) -> FunctionDocumentation:
        doc = parse(comment)
        ret = {}
        summary = None
        if doc.short_description:
            summary = doc.short_description
        if doc.long_description:
            if not summary:
                summary = ''
            summary += "\n\n" + doc.long_description
        if summary:
            ret["summary"] = summary
        ret["params"] = list(map(
            lambda param: {
                "type_name": param.type_name,
                "name": param.arg_name,
                "summary": param.description
            },
            doc.params
        ))
        if doc.returns:
            ret["returns"] = {
                "type_name": doc.returns.type_name,
                "name": doc.returns.return_name,
                "summary": doc.returns.description
            }
        return ret

    @classmethod
    def __analize_function(cls, func: Callable) -> FunctionStructure:
        doc_comment: str = func.__doc__
        name: str = func.__name__
        params: list[str] = getfullargspec(func).args
        params.pop(0)  # Remove 'self' from args
        return {
            "name": name,
            "DocComment": cls.__parse_DocComment(doc_comment),
            "params": params,
        }

    @staticmethod
    def __get_template(file_name: str) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(dir_path, file_name)
        return open(template_path).read()

    @classmethod
    def __get_html_function_template(cls) -> str:
        return cls.__get_template("function-template.html")

    def __get_js_function_template(cls) -> str:
        return cls.__get_template("function-template.js")

    @classmethod
    def __get_html_doc_template(cls) -> str:
        return cls.__get_template("doc-templete.html")

    @classmethod
    def __get_module_template(cls) -> str:
        return cls.__get_template("module-header.js")

    @staticmethod
    def __use_template(template: str, params: dict[str, str]) -> str:
        for param in params:
            template = template.replace(param, params[param])
        return template

    def reflectJS(self):
        output = self.__use_template(self.__get_module_template(), {
            "pathToEndpoint": self._location + "?type=api"
        })

        for function_name in self._functions:
            ServerFunction = self._functions[function_name]
            output += self.__JSDoc(ServerFunction["DocComment"]) + "\n"
            argList = ", ".join(ServerFunction["params"])
            output += self.__use_template(self.__get_js_function_template(), {
                "functionName": ServerFunction["name"],
                "argList": argList
            })
            output += f"\nexport {{{ServerFunction['name']}}};\n\n"
        return output

    def reflectHTML(self):
        content = ""
        for function_name in self._functions:
            ServerFunction = self._functions[function_name]
            definition = f"<b>{ServerFunction['name']}</b>("
            params = ServerFunction["params"]
            definition += f"<i>{', '.join(params)}</i>"
            definition += ")"
            description = self.__HTMLDoc(ServerFunction["DocComment"])
            content += self.__use_template(self.__get_html_function_template(), {
                "[[Function-Name]]": ServerFunction["name"],
                "[[Function-Definition]]": definition,
                "[[Function-Description]]": description
            })
        return self.__use_template(self.__get_html_doc_template(), {
            "[[Endpoint-Name]]": self.__class__.__name__,
            "[[Functions-List]]": content,
            "[[Module-Link]]": self._location + '?type=js'
        })

    def flask_view(self):
        view_type = request.args.get('type')
        if not view_type:
            view_type = 'html'
        view_type = view_type.upper()
        if view_type == 'API' and request.method == 'POST':
            data = request.get_json()
            response = []
            for call in data:
                if "name" in call and call['name'] in self._functions:
                    try:
                        ret = self._functions[call['name']]['ref'](*call['params'])
                    except Exception as e:
                        response.append({"exception": e})
                    else:
                        response.append({"returned": ret})
                else:
                    response.append(None)
            response_obj = make_response(json.dumps(response))
            response_obj.headers["Content-Type"] = "application/json"
            return response_obj
        elif view_type == 'JS':
            response = make_response(self.reflectJS())
            response.headers["Content-Type"] = "text/javascript"
            return response
        else:
            return self.reflectHTML()

    @csrf_exempt
    def django_view(self, request):
        view_type = request.GET.get('type')
        self.request = request
        if not view_type:
            view_type = 'html'
        view_type = view_type.upper()
        if view_type == 'API' and request.method == 'POST':
            data = json.loads(request.body.decode('utf-8'))
            response = []
            for call in data:
                if "name" in call and call['name'] in self._functions:
                    try:
                        ret = self._functions[call['name']]['ref'](*call['params'])
                    except Exception:
                        response.append({"exception": traceback.format_exc()})
                    else:
                        response.append({"returned": ret})
                else:
                    response.append(None)
            return HttpResponse(
                json.dumps(response),
                content_type='application/json; charset=utf8'
            )
        elif view_type == 'JS':
            return HttpResponse(self.reflectJS(), content_type="text/javascript")
        else:
            return HttpResponse(self.reflectHTML())
