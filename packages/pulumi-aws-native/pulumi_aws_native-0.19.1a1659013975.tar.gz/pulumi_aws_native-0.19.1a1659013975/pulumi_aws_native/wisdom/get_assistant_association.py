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
    'GetAssistantAssociationResult',
    'AwaitableGetAssistantAssociationResult',
    'get_assistant_association',
    'get_assistant_association_output',
]

@pulumi.output_type
class GetAssistantAssociationResult:
    def __init__(__self__, assistant_arn=None, assistant_association_arn=None, assistant_association_id=None):
        if assistant_arn and not isinstance(assistant_arn, str):
            raise TypeError("Expected argument 'assistant_arn' to be a str")
        pulumi.set(__self__, "assistant_arn", assistant_arn)
        if assistant_association_arn and not isinstance(assistant_association_arn, str):
            raise TypeError("Expected argument 'assistant_association_arn' to be a str")
        pulumi.set(__self__, "assistant_association_arn", assistant_association_arn)
        if assistant_association_id and not isinstance(assistant_association_id, str):
            raise TypeError("Expected argument 'assistant_association_id' to be a str")
        pulumi.set(__self__, "assistant_association_id", assistant_association_id)

    @property
    @pulumi.getter(name="assistantArn")
    def assistant_arn(self) -> Optional[str]:
        return pulumi.get(self, "assistant_arn")

    @property
    @pulumi.getter(name="assistantAssociationArn")
    def assistant_association_arn(self) -> Optional[str]:
        return pulumi.get(self, "assistant_association_arn")

    @property
    @pulumi.getter(name="assistantAssociationId")
    def assistant_association_id(self) -> Optional[str]:
        return pulumi.get(self, "assistant_association_id")


class AwaitableGetAssistantAssociationResult(GetAssistantAssociationResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetAssistantAssociationResult(
            assistant_arn=self.assistant_arn,
            assistant_association_arn=self.assistant_association_arn,
            assistant_association_id=self.assistant_association_id)


def get_assistant_association(assistant_association_id: Optional[str] = None,
                              assistant_id: Optional[str] = None,
                              opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetAssistantAssociationResult:
    """
    Definition of AWS::Wisdom::AssistantAssociation Resource Type
    """
    __args__ = dict()
    __args__['assistantAssociationId'] = assistant_association_id
    __args__['assistantId'] = assistant_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:wisdom:getAssistantAssociation', __args__, opts=opts, typ=GetAssistantAssociationResult).value

    return AwaitableGetAssistantAssociationResult(
        assistant_arn=__ret__.assistant_arn,
        assistant_association_arn=__ret__.assistant_association_arn,
        assistant_association_id=__ret__.assistant_association_id)


@_utilities.lift_output_func(get_assistant_association)
def get_assistant_association_output(assistant_association_id: Optional[pulumi.Input[str]] = None,
                                     assistant_id: Optional[pulumi.Input[str]] = None,
                                     opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetAssistantAssociationResult]:
    """
    Definition of AWS::Wisdom::AssistantAssociation Resource Type
    """
    ...
