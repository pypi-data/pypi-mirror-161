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
    'GetIPAMAllocationResult',
    'AwaitableGetIPAMAllocationResult',
    'get_ipam_allocation',
    'get_ipam_allocation_output',
]

@pulumi.output_type
class GetIPAMAllocationResult:
    def __init__(__self__, ipam_pool_allocation_id=None):
        if ipam_pool_allocation_id and not isinstance(ipam_pool_allocation_id, str):
            raise TypeError("Expected argument 'ipam_pool_allocation_id' to be a str")
        pulumi.set(__self__, "ipam_pool_allocation_id", ipam_pool_allocation_id)

    @property
    @pulumi.getter(name="ipamPoolAllocationId")
    def ipam_pool_allocation_id(self) -> Optional[str]:
        """
        Id of the allocation.
        """
        return pulumi.get(self, "ipam_pool_allocation_id")


class AwaitableGetIPAMAllocationResult(GetIPAMAllocationResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetIPAMAllocationResult(
            ipam_pool_allocation_id=self.ipam_pool_allocation_id)


def get_ipam_allocation(cidr: Optional[str] = None,
                        ipam_pool_allocation_id: Optional[str] = None,
                        ipam_pool_id: Optional[str] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetIPAMAllocationResult:
    """
    Resource Schema of AWS::EC2::IPAMAllocation Type


    :param str ipam_pool_allocation_id: Id of the allocation.
    :param str ipam_pool_id: Id of the IPAM Pool.
    """
    __args__ = dict()
    __args__['cidr'] = cidr
    __args__['ipamPoolAllocationId'] = ipam_pool_allocation_id
    __args__['ipamPoolId'] = ipam_pool_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:ec2:getIPAMAllocation', __args__, opts=opts, typ=GetIPAMAllocationResult).value

    return AwaitableGetIPAMAllocationResult(
        ipam_pool_allocation_id=__ret__.ipam_pool_allocation_id)


@_utilities.lift_output_func(get_ipam_allocation)
def get_ipam_allocation_output(cidr: Optional[pulumi.Input[str]] = None,
                               ipam_pool_allocation_id: Optional[pulumi.Input[str]] = None,
                               ipam_pool_id: Optional[pulumi.Input[str]] = None,
                               opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetIPAMAllocationResult]:
    """
    Resource Schema of AWS::EC2::IPAMAllocation Type


    :param str ipam_pool_allocation_id: Id of the allocation.
    :param str ipam_pool_id: Id of the IPAM Pool.
    """
    ...
