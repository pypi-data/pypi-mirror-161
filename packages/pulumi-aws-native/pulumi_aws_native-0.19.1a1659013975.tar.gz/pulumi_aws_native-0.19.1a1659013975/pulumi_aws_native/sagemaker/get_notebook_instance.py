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
    'GetNotebookInstanceResult',
    'AwaitableGetNotebookInstanceResult',
    'get_notebook_instance',
    'get_notebook_instance_output',
]

@pulumi.output_type
class GetNotebookInstanceResult:
    def __init__(__self__, accelerator_types=None, additional_code_repositories=None, default_code_repository=None, id=None, instance_type=None, lifecycle_config_name=None, role_arn=None, root_access=None, tags=None, volume_size_in_gb=None):
        if accelerator_types and not isinstance(accelerator_types, list):
            raise TypeError("Expected argument 'accelerator_types' to be a list")
        pulumi.set(__self__, "accelerator_types", accelerator_types)
        if additional_code_repositories and not isinstance(additional_code_repositories, list):
            raise TypeError("Expected argument 'additional_code_repositories' to be a list")
        pulumi.set(__self__, "additional_code_repositories", additional_code_repositories)
        if default_code_repository and not isinstance(default_code_repository, str):
            raise TypeError("Expected argument 'default_code_repository' to be a str")
        pulumi.set(__self__, "default_code_repository", default_code_repository)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if instance_type and not isinstance(instance_type, str):
            raise TypeError("Expected argument 'instance_type' to be a str")
        pulumi.set(__self__, "instance_type", instance_type)
        if lifecycle_config_name and not isinstance(lifecycle_config_name, str):
            raise TypeError("Expected argument 'lifecycle_config_name' to be a str")
        pulumi.set(__self__, "lifecycle_config_name", lifecycle_config_name)
        if role_arn and not isinstance(role_arn, str):
            raise TypeError("Expected argument 'role_arn' to be a str")
        pulumi.set(__self__, "role_arn", role_arn)
        if root_access and not isinstance(root_access, str):
            raise TypeError("Expected argument 'root_access' to be a str")
        pulumi.set(__self__, "root_access", root_access)
        if tags and not isinstance(tags, list):
            raise TypeError("Expected argument 'tags' to be a list")
        pulumi.set(__self__, "tags", tags)
        if volume_size_in_gb and not isinstance(volume_size_in_gb, int):
            raise TypeError("Expected argument 'volume_size_in_gb' to be a int")
        pulumi.set(__self__, "volume_size_in_gb", volume_size_in_gb)

    @property
    @pulumi.getter(name="acceleratorTypes")
    def accelerator_types(self) -> Optional[Sequence[str]]:
        return pulumi.get(self, "accelerator_types")

    @property
    @pulumi.getter(name="additionalCodeRepositories")
    def additional_code_repositories(self) -> Optional[Sequence[str]]:
        return pulumi.get(self, "additional_code_repositories")

    @property
    @pulumi.getter(name="defaultCodeRepository")
    def default_code_repository(self) -> Optional[str]:
        return pulumi.get(self, "default_code_repository")

    @property
    @pulumi.getter
    def id(self) -> Optional[str]:
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="instanceType")
    def instance_type(self) -> Optional[str]:
        return pulumi.get(self, "instance_type")

    @property
    @pulumi.getter(name="lifecycleConfigName")
    def lifecycle_config_name(self) -> Optional[str]:
        return pulumi.get(self, "lifecycle_config_name")

    @property
    @pulumi.getter(name="roleArn")
    def role_arn(self) -> Optional[str]:
        return pulumi.get(self, "role_arn")

    @property
    @pulumi.getter(name="rootAccess")
    def root_access(self) -> Optional[str]:
        return pulumi.get(self, "root_access")

    @property
    @pulumi.getter
    def tags(self) -> Optional[Sequence['outputs.NotebookInstanceTag']]:
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="volumeSizeInGB")
    def volume_size_in_gb(self) -> Optional[int]:
        return pulumi.get(self, "volume_size_in_gb")


class AwaitableGetNotebookInstanceResult(GetNotebookInstanceResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetNotebookInstanceResult(
            accelerator_types=self.accelerator_types,
            additional_code_repositories=self.additional_code_repositories,
            default_code_repository=self.default_code_repository,
            id=self.id,
            instance_type=self.instance_type,
            lifecycle_config_name=self.lifecycle_config_name,
            role_arn=self.role_arn,
            root_access=self.root_access,
            tags=self.tags,
            volume_size_in_gb=self.volume_size_in_gb)


def get_notebook_instance(id: Optional[str] = None,
                          opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetNotebookInstanceResult:
    """
    Resource Type definition for AWS::SageMaker::NotebookInstance
    """
    __args__ = dict()
    __args__['id'] = id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws-native:sagemaker:getNotebookInstance', __args__, opts=opts, typ=GetNotebookInstanceResult).value

    return AwaitableGetNotebookInstanceResult(
        accelerator_types=__ret__.accelerator_types,
        additional_code_repositories=__ret__.additional_code_repositories,
        default_code_repository=__ret__.default_code_repository,
        id=__ret__.id,
        instance_type=__ret__.instance_type,
        lifecycle_config_name=__ret__.lifecycle_config_name,
        role_arn=__ret__.role_arn,
        root_access=__ret__.root_access,
        tags=__ret__.tags,
        volume_size_in_gb=__ret__.volume_size_in_gb)


@_utilities.lift_output_func(get_notebook_instance)
def get_notebook_instance_output(id: Optional[pulumi.Input[str]] = None,
                                 opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetNotebookInstanceResult]:
    """
    Resource Type definition for AWS::SageMaker::NotebookInstance
    """
    ...
