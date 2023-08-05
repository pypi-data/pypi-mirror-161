# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GetModelResult',
    'AwaitableGetModelResult',
    'get_model',
    'get_model_output',
]

@pulumi.output_type
class GetModelResult:
    def __init__(__self__, content_type=None, description=None, id=None, name=None, schema=None):
        if content_type and not isinstance(content_type, str):
            raise TypeError("Expected argument 'content_type' to be a str")
        pulumi.set(__self__, "content_type", content_type)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if schema and not isinstance(schema, dict):
            raise TypeError("Expected argument 'schema' to be a dict")
        pulumi.set(__self__, "schema", schema)

    @property
    @pulumi.getter(name="contentType")
    def content_type(self) -> Optional[str]:
        return pulumi.get(self, "content_type")

    @property
    @pulumi.getter
    def description(self) -> Optional[str]:
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def id(self) -> Optional[str]:
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def name(self) -> Optional[str]:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def schema(self) -> Optional[Any]:
        return pulumi.get(self, "schema")


class AwaitableGetModelResult(GetModelResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetModelResult(
            content_type=self.content_type,
            description=self.description,
            id=self.id,
            name=self.name,
            schema=self.schema)


def get_model(id: Optional[str] = None,
              opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetModelResult:
    """
    Resource Type definition for AWS::ApiGatewayV2::Model
    """
    __args__ = dict()
    __args__['id'] = id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:apigatewayv2:getModel', __args__, opts=opts, typ=GetModelResult).value

    return AwaitableGetModelResult(
        content_type=__ret__.content_type,
        description=__ret__.description,
        id=__ret__.id,
        name=__ret__.name,
        schema=__ret__.schema)


@_utilities.lift_output_func(get_model)
def get_model_output(id: Optional[pulumi.Input[str]] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetModelResult]:
    """
    Resource Type definition for AWS::ApiGatewayV2::Model
    """
    ...
