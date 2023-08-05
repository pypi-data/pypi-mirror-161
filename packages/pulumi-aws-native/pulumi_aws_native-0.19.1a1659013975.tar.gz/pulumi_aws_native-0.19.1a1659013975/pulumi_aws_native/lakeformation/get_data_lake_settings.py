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
    'GetDataLakeSettingsResult',
    'AwaitableGetDataLakeSettingsResult',
    'get_data_lake_settings',
    'get_data_lake_settings_output',
]

@pulumi.output_type
class GetDataLakeSettingsResult:
    def __init__(__self__, admins=None, id=None, trusted_resource_owners=None):
        if admins and not isinstance(admins, dict):
            raise TypeError("Expected argument 'admins' to be a dict")
        pulumi.set(__self__, "admins", admins)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if trusted_resource_owners and not isinstance(trusted_resource_owners, list):
            raise TypeError("Expected argument 'trusted_resource_owners' to be a list")
        pulumi.set(__self__, "trusted_resource_owners", trusted_resource_owners)

    @property
    @pulumi.getter
    def admins(self) -> Optional['outputs.DataLakeSettingsAdmins']:
        return pulumi.get(self, "admins")

    @property
    @pulumi.getter
    def id(self) -> Optional[str]:
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="trustedResourceOwners")
    def trusted_resource_owners(self) -> Optional[Sequence[str]]:
        return pulumi.get(self, "trusted_resource_owners")


class AwaitableGetDataLakeSettingsResult(GetDataLakeSettingsResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetDataLakeSettingsResult(
            admins=self.admins,
            id=self.id,
            trusted_resource_owners=self.trusted_resource_owners)


def get_data_lake_settings(id: Optional[str] = None,
                           opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetDataLakeSettingsResult:
    """
    Resource Type definition for AWS::LakeFormation::DataLakeSettings
    """
    __args__ = dict()
    __args__['id'] = id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:lakeformation:getDataLakeSettings', __args__, opts=opts, typ=GetDataLakeSettingsResult).value

    return AwaitableGetDataLakeSettingsResult(
        admins=__ret__.admins,
        id=__ret__.id,
        trusted_resource_owners=__ret__.trusted_resource_owners)


@_utilities.lift_output_func(get_data_lake_settings)
def get_data_lake_settings_output(id: Optional[pulumi.Input[str]] = None,
                                  opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetDataLakeSettingsResult]:
    """
    Resource Type definition for AWS::LakeFormation::DataLakeSettings
    """
    ...
