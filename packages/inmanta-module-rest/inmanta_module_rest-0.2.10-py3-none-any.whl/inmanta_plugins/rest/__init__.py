"""
    Copyright 2018 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""

import requests
from inmanta.agent import handler
from inmanta.resources import Resource, resource
from jq import jq


@resource("rest::RESTCall", agent="agent", id_attribute="url_id")
class RESTCall(Resource):
    """
    A Call to a rest endpoint
    """

    fields = (
        "url_id",
        "url",
        "method",
        "body",
        "headers",
        "form_encoded",
        "ssl_verify",
        "auth_user",
        "auth_password",
        "return_codes",
        "skip_on_fail",
        "validate_return",
        "agent",
    )


@handler.provider("rest::RESTCall", name="requests")
class RESTHandler(handler.ResourceHandler):
    def list_changes(self, ctx: handler.HandlerContext, resource: RESTCall):
        return {}

    def do_changes(
        self, ctx: handler.HandlerContext, resource: RESTCall, changes: dict
    ):
        return self._call(ctx, resource)

    def _fail(self, resource, message):
        if resource.skip_on_fail:
            raise handler.SkipResource(message)
        raise Exception(message)

    def _call(self, ctx: handler.HandlerContext, resource: RESTCall):
        args = {
            "method": resource.method.upper(),
            "url": resource.url,
            "headers": resource.headers,
            "verify": resource.ssl_verify,
            "auth": (resource.auth_user, resource.auth_password),
        }

        if resource.form_encoded:
            args["data"] = resource.body
        else:
            args["json"] = resource.body

        ctx.debug("Calling REST api", **args)
        result = requests.request(**args)

        json_data = result.json()
        ctx.info("Call returned", status=result.status_code, json=json_data)
        if result.status_code not in resource.return_codes:
            self._fail(resource, "Invalid status code returned %s" % result.status_code)

        if resource.validate_return is not None:
            result = jq(resource.validate_return).transform(json_data)
            ctx.debug(
                "%(query)s validated to %(result)s",
                query=resource.validate_return,
                result=result,
            )

            if not result:
                self._fail(resource, "Returned result not valid.")

        return True
