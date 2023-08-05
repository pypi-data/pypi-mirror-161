# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from ._enums import *

__all__ = [
    'ComponentVersionComponentPlatformArgs',
    'ComponentVersionLambdaContainerParamsArgs',
    'ComponentVersionLambdaDeviceMountArgs',
    'ComponentVersionLambdaEventSourceArgs',
    'ComponentVersionLambdaExecutionParametersArgs',
    'ComponentVersionLambdaFunctionRecipeSourceArgs',
    'ComponentVersionLambdaLinuxProcessParamsArgs',
    'ComponentVersionLambdaVolumeMountArgs',
]

@pulumi.input_type
class ComponentVersionComponentPlatformArgs:
    def __init__(__self__, *,
                 attributes: Optional[Any] = None,
                 name: Optional[pulumi.Input[str]] = None):
        if attributes is not None:
            pulumi.set(__self__, "attributes", attributes)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter
    def attributes(self) -> Optional[Any]:
        return pulumi.get(self, "attributes")

    @attributes.setter
    def attributes(self, value: Optional[Any]):
        pulumi.set(self, "attributes", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


@pulumi.input_type
class ComponentVersionLambdaContainerParamsArgs:
    def __init__(__self__, *,
                 devices: Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionLambdaDeviceMountArgs']]]] = None,
                 memory_size_in_kb: Optional[pulumi.Input[int]] = None,
                 mount_ro_sysfs: Optional[pulumi.Input[bool]] = None,
                 volumes: Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionLambdaVolumeMountArgs']]]] = None):
        if devices is not None:
            pulumi.set(__self__, "devices", devices)
        if memory_size_in_kb is not None:
            pulumi.set(__self__, "memory_size_in_kb", memory_size_in_kb)
        if mount_ro_sysfs is not None:
            pulumi.set(__self__, "mount_ro_sysfs", mount_ro_sysfs)
        if volumes is not None:
            pulumi.set(__self__, "volumes", volumes)

    @property
    @pulumi.getter
    def devices(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionLambdaDeviceMountArgs']]]]:
        return pulumi.get(self, "devices")

    @devices.setter
    def devices(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionLambdaDeviceMountArgs']]]]):
        pulumi.set(self, "devices", value)

    @property
    @pulumi.getter(name="memorySizeInKB")
    def memory_size_in_kb(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "memory_size_in_kb")

    @memory_size_in_kb.setter
    def memory_size_in_kb(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "memory_size_in_kb", value)

    @property
    @pulumi.getter(name="mountROSysfs")
    def mount_ro_sysfs(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "mount_ro_sysfs")

    @mount_ro_sysfs.setter
    def mount_ro_sysfs(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "mount_ro_sysfs", value)

    @property
    @pulumi.getter
    def volumes(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionLambdaVolumeMountArgs']]]]:
        return pulumi.get(self, "volumes")

    @volumes.setter
    def volumes(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionLambdaVolumeMountArgs']]]]):
        pulumi.set(self, "volumes", value)


@pulumi.input_type
class ComponentVersionLambdaDeviceMountArgs:
    def __init__(__self__, *,
                 add_group_owner: Optional[pulumi.Input[bool]] = None,
                 path: Optional[pulumi.Input[str]] = None,
                 permission: Optional[pulumi.Input['ComponentVersionLambdaFilesystemPermission']] = None):
        if add_group_owner is not None:
            pulumi.set(__self__, "add_group_owner", add_group_owner)
        if path is not None:
            pulumi.set(__self__, "path", path)
        if permission is not None:
            pulumi.set(__self__, "permission", permission)

    @property
    @pulumi.getter(name="addGroupOwner")
    def add_group_owner(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "add_group_owner")

    @add_group_owner.setter
    def add_group_owner(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "add_group_owner", value)

    @property
    @pulumi.getter
    def path(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "path")

    @path.setter
    def path(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "path", value)

    @property
    @pulumi.getter
    def permission(self) -> Optional[pulumi.Input['ComponentVersionLambdaFilesystemPermission']]:
        return pulumi.get(self, "permission")

    @permission.setter
    def permission(self, value: Optional[pulumi.Input['ComponentVersionLambdaFilesystemPermission']]):
        pulumi.set(self, "permission", value)


@pulumi.input_type
class ComponentVersionLambdaEventSourceArgs:
    def __init__(__self__, *,
                 topic: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input['ComponentVersionLambdaEventSourceType']] = None):
        if topic is not None:
            pulumi.set(__self__, "topic", topic)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter
    def topic(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "topic")

    @topic.setter
    def topic(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "topic", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input['ComponentVersionLambdaEventSourceType']]:
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input['ComponentVersionLambdaEventSourceType']]):
        pulumi.set(self, "type", value)


@pulumi.input_type
class ComponentVersionLambdaExecutionParametersArgs:
    def __init__(__self__, *,
                 environment_variables: Optional[Any] = None,
                 event_sources: Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionLambdaEventSourceArgs']]]] = None,
                 exec_args: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 input_payload_encoding_type: Optional[pulumi.Input['ComponentVersionLambdaExecutionParametersInputPayloadEncodingType']] = None,
                 linux_process_params: Optional[pulumi.Input['ComponentVersionLambdaLinuxProcessParamsArgs']] = None,
                 max_idle_time_in_seconds: Optional[pulumi.Input[int]] = None,
                 max_instances_count: Optional[pulumi.Input[int]] = None,
                 max_queue_size: Optional[pulumi.Input[int]] = None,
                 pinned: Optional[pulumi.Input[bool]] = None,
                 status_timeout_in_seconds: Optional[pulumi.Input[int]] = None,
                 timeout_in_seconds: Optional[pulumi.Input[int]] = None):
        if environment_variables is not None:
            pulumi.set(__self__, "environment_variables", environment_variables)
        if event_sources is not None:
            pulumi.set(__self__, "event_sources", event_sources)
        if exec_args is not None:
            pulumi.set(__self__, "exec_args", exec_args)
        if input_payload_encoding_type is not None:
            pulumi.set(__self__, "input_payload_encoding_type", input_payload_encoding_type)
        if linux_process_params is not None:
            pulumi.set(__self__, "linux_process_params", linux_process_params)
        if max_idle_time_in_seconds is not None:
            pulumi.set(__self__, "max_idle_time_in_seconds", max_idle_time_in_seconds)
        if max_instances_count is not None:
            pulumi.set(__self__, "max_instances_count", max_instances_count)
        if max_queue_size is not None:
            pulumi.set(__self__, "max_queue_size", max_queue_size)
        if pinned is not None:
            pulumi.set(__self__, "pinned", pinned)
        if status_timeout_in_seconds is not None:
            pulumi.set(__self__, "status_timeout_in_seconds", status_timeout_in_seconds)
        if timeout_in_seconds is not None:
            pulumi.set(__self__, "timeout_in_seconds", timeout_in_seconds)

    @property
    @pulumi.getter(name="environmentVariables")
    def environment_variables(self) -> Optional[Any]:
        return pulumi.get(self, "environment_variables")

    @environment_variables.setter
    def environment_variables(self, value: Optional[Any]):
        pulumi.set(self, "environment_variables", value)

    @property
    @pulumi.getter(name="eventSources")
    def event_sources(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionLambdaEventSourceArgs']]]]:
        return pulumi.get(self, "event_sources")

    @event_sources.setter
    def event_sources(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionLambdaEventSourceArgs']]]]):
        pulumi.set(self, "event_sources", value)

    @property
    @pulumi.getter(name="execArgs")
    def exec_args(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "exec_args")

    @exec_args.setter
    def exec_args(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "exec_args", value)

    @property
    @pulumi.getter(name="inputPayloadEncodingType")
    def input_payload_encoding_type(self) -> Optional[pulumi.Input['ComponentVersionLambdaExecutionParametersInputPayloadEncodingType']]:
        return pulumi.get(self, "input_payload_encoding_type")

    @input_payload_encoding_type.setter
    def input_payload_encoding_type(self, value: Optional[pulumi.Input['ComponentVersionLambdaExecutionParametersInputPayloadEncodingType']]):
        pulumi.set(self, "input_payload_encoding_type", value)

    @property
    @pulumi.getter(name="linuxProcessParams")
    def linux_process_params(self) -> Optional[pulumi.Input['ComponentVersionLambdaLinuxProcessParamsArgs']]:
        return pulumi.get(self, "linux_process_params")

    @linux_process_params.setter
    def linux_process_params(self, value: Optional[pulumi.Input['ComponentVersionLambdaLinuxProcessParamsArgs']]):
        pulumi.set(self, "linux_process_params", value)

    @property
    @pulumi.getter(name="maxIdleTimeInSeconds")
    def max_idle_time_in_seconds(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "max_idle_time_in_seconds")

    @max_idle_time_in_seconds.setter
    def max_idle_time_in_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "max_idle_time_in_seconds", value)

    @property
    @pulumi.getter(name="maxInstancesCount")
    def max_instances_count(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "max_instances_count")

    @max_instances_count.setter
    def max_instances_count(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "max_instances_count", value)

    @property
    @pulumi.getter(name="maxQueueSize")
    def max_queue_size(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "max_queue_size")

    @max_queue_size.setter
    def max_queue_size(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "max_queue_size", value)

    @property
    @pulumi.getter
    def pinned(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "pinned")

    @pinned.setter
    def pinned(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "pinned", value)

    @property
    @pulumi.getter(name="statusTimeoutInSeconds")
    def status_timeout_in_seconds(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "status_timeout_in_seconds")

    @status_timeout_in_seconds.setter
    def status_timeout_in_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "status_timeout_in_seconds", value)

    @property
    @pulumi.getter(name="timeoutInSeconds")
    def timeout_in_seconds(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "timeout_in_seconds")

    @timeout_in_seconds.setter
    def timeout_in_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "timeout_in_seconds", value)


@pulumi.input_type
class ComponentVersionLambdaFunctionRecipeSourceArgs:
    def __init__(__self__, *,
                 component_dependencies: Optional[Any] = None,
                 component_lambda_parameters: Optional[pulumi.Input['ComponentVersionLambdaExecutionParametersArgs']] = None,
                 component_name: Optional[pulumi.Input[str]] = None,
                 component_platforms: Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionComponentPlatformArgs']]]] = None,
                 component_version: Optional[pulumi.Input[str]] = None,
                 lambda_arn: Optional[pulumi.Input[str]] = None):
        if component_dependencies is not None:
            pulumi.set(__self__, "component_dependencies", component_dependencies)
        if component_lambda_parameters is not None:
            pulumi.set(__self__, "component_lambda_parameters", component_lambda_parameters)
        if component_name is not None:
            pulumi.set(__self__, "component_name", component_name)
        if component_platforms is not None:
            pulumi.set(__self__, "component_platforms", component_platforms)
        if component_version is not None:
            pulumi.set(__self__, "component_version", component_version)
        if lambda_arn is not None:
            pulumi.set(__self__, "lambda_arn", lambda_arn)

    @property
    @pulumi.getter(name="componentDependencies")
    def component_dependencies(self) -> Optional[Any]:
        return pulumi.get(self, "component_dependencies")

    @component_dependencies.setter
    def component_dependencies(self, value: Optional[Any]):
        pulumi.set(self, "component_dependencies", value)

    @property
    @pulumi.getter(name="componentLambdaParameters")
    def component_lambda_parameters(self) -> Optional[pulumi.Input['ComponentVersionLambdaExecutionParametersArgs']]:
        return pulumi.get(self, "component_lambda_parameters")

    @component_lambda_parameters.setter
    def component_lambda_parameters(self, value: Optional[pulumi.Input['ComponentVersionLambdaExecutionParametersArgs']]):
        pulumi.set(self, "component_lambda_parameters", value)

    @property
    @pulumi.getter(name="componentName")
    def component_name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "component_name")

    @component_name.setter
    def component_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "component_name", value)

    @property
    @pulumi.getter(name="componentPlatforms")
    def component_platforms(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionComponentPlatformArgs']]]]:
        return pulumi.get(self, "component_platforms")

    @component_platforms.setter
    def component_platforms(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ComponentVersionComponentPlatformArgs']]]]):
        pulumi.set(self, "component_platforms", value)

    @property
    @pulumi.getter(name="componentVersion")
    def component_version(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "component_version")

    @component_version.setter
    def component_version(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "component_version", value)

    @property
    @pulumi.getter(name="lambdaArn")
    def lambda_arn(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "lambda_arn")

    @lambda_arn.setter
    def lambda_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "lambda_arn", value)


@pulumi.input_type
class ComponentVersionLambdaLinuxProcessParamsArgs:
    def __init__(__self__, *,
                 container_params: Optional[pulumi.Input['ComponentVersionLambdaContainerParamsArgs']] = None,
                 isolation_mode: Optional[pulumi.Input['ComponentVersionLambdaLinuxProcessParamsIsolationMode']] = None):
        if container_params is not None:
            pulumi.set(__self__, "container_params", container_params)
        if isolation_mode is not None:
            pulumi.set(__self__, "isolation_mode", isolation_mode)

    @property
    @pulumi.getter(name="containerParams")
    def container_params(self) -> Optional[pulumi.Input['ComponentVersionLambdaContainerParamsArgs']]:
        return pulumi.get(self, "container_params")

    @container_params.setter
    def container_params(self, value: Optional[pulumi.Input['ComponentVersionLambdaContainerParamsArgs']]):
        pulumi.set(self, "container_params", value)

    @property
    @pulumi.getter(name="isolationMode")
    def isolation_mode(self) -> Optional[pulumi.Input['ComponentVersionLambdaLinuxProcessParamsIsolationMode']]:
        return pulumi.get(self, "isolation_mode")

    @isolation_mode.setter
    def isolation_mode(self, value: Optional[pulumi.Input['ComponentVersionLambdaLinuxProcessParamsIsolationMode']]):
        pulumi.set(self, "isolation_mode", value)


@pulumi.input_type
class ComponentVersionLambdaVolumeMountArgs:
    def __init__(__self__, *,
                 add_group_owner: Optional[pulumi.Input[bool]] = None,
                 destination_path: Optional[pulumi.Input[str]] = None,
                 permission: Optional[pulumi.Input['ComponentVersionLambdaFilesystemPermission']] = None,
                 source_path: Optional[pulumi.Input[str]] = None):
        if add_group_owner is not None:
            pulumi.set(__self__, "add_group_owner", add_group_owner)
        if destination_path is not None:
            pulumi.set(__self__, "destination_path", destination_path)
        if permission is not None:
            pulumi.set(__self__, "permission", permission)
        if source_path is not None:
            pulumi.set(__self__, "source_path", source_path)

    @property
    @pulumi.getter(name="addGroupOwner")
    def add_group_owner(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "add_group_owner")

    @add_group_owner.setter
    def add_group_owner(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "add_group_owner", value)

    @property
    @pulumi.getter(name="destinationPath")
    def destination_path(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "destination_path")

    @destination_path.setter
    def destination_path(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "destination_path", value)

    @property
    @pulumi.getter
    def permission(self) -> Optional[pulumi.Input['ComponentVersionLambdaFilesystemPermission']]:
        return pulumi.get(self, "permission")

    @permission.setter
    def permission(self, value: Optional[pulumi.Input['ComponentVersionLambdaFilesystemPermission']]):
        pulumi.set(self, "permission", value)

    @property
    @pulumi.getter(name="sourcePath")
    def source_path(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "source_path")

    @source_path.setter
    def source_path(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "source_path", value)


