# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs

__all__ = [
    'GetNatGatewayResult',
    'AwaitableGetNatGatewayResult',
    'get_nat_gateway',
    'get_nat_gateway_output',
]

@pulumi.output_type
class GetNatGatewayResult:
    def __init__(__self__, nat_gateway_id=None, tags=None):
        if nat_gateway_id and not isinstance(nat_gateway_id, str):
            raise TypeError("Expected argument 'nat_gateway_id' to be a str")
        pulumi.set(__self__, "nat_gateway_id", nat_gateway_id)
        if tags and not isinstance(tags, list):
            raise TypeError("Expected argument 'tags' to be a list")
        pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="natGatewayId")
    def nat_gateway_id(self) -> Optional[str]:
        return pulumi.get(self, "nat_gateway_id")

    @property
    @pulumi.getter
    def tags(self) -> Optional[Sequence['outputs.NatGatewayTag']]:
        return pulumi.get(self, "tags")


class AwaitableGetNatGatewayResult(GetNatGatewayResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetNatGatewayResult(
            nat_gateway_id=self.nat_gateway_id,
            tags=self.tags)


def get_nat_gateway(nat_gateway_id: Optional[str] = None,
                    opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetNatGatewayResult:
    """
    Resource Type definition for AWS::EC2::NatGateway
    """
    __args__ = dict()
    __args__['natGatewayId'] = nat_gateway_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:ec2:getNatGateway', __args__, opts=opts, typ=GetNatGatewayResult).value

    return AwaitableGetNatGatewayResult(
        nat_gateway_id=__ret__.nat_gateway_id,
        tags=__ret__.tags)


@_utilities.lift_output_func(get_nat_gateway)
def get_nat_gateway_output(nat_gateway_id: Optional[pulumi.Input[str]] = None,
                           opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetNatGatewayResult]:
    """
    Resource Type definition for AWS::EC2::NatGateway
    """
    ...
