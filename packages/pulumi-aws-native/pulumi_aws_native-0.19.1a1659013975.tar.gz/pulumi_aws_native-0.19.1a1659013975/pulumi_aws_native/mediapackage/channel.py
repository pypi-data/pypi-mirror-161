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
from ._inputs import *

__all__ = ['ChannelArgs', 'Channel']

@pulumi.input_type
class ChannelArgs:
    def __init__(__self__, *,
                 description: Optional[pulumi.Input[str]] = None,
                 egress_access_logs: Optional[pulumi.Input['ChannelLogConfigurationArgs']] = None,
                 ingress_access_logs: Optional[pulumi.Input['ChannelLogConfigurationArgs']] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input['ChannelTagArgs']]]] = None):
        """
        The set of arguments for constructing a Channel resource.
        :param pulumi.Input[str] description: A short text description of the Channel.
        :param pulumi.Input['ChannelLogConfigurationArgs'] egress_access_logs: The configuration parameters for egress access logging.
        :param pulumi.Input['ChannelLogConfigurationArgs'] ingress_access_logs: The configuration parameters for egress access logging.
        :param pulumi.Input[Sequence[pulumi.Input['ChannelTagArgs']]] tags: A collection of tags associated with a resource
        """
        if description is not None:
            pulumi.set(__self__, "description", description)
        if egress_access_logs is not None:
            pulumi.set(__self__, "egress_access_logs", egress_access_logs)
        if ingress_access_logs is not None:
            pulumi.set(__self__, "ingress_access_logs", ingress_access_logs)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A short text description of the Channel.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="egressAccessLogs")
    def egress_access_logs(self) -> Optional[pulumi.Input['ChannelLogConfigurationArgs']]:
        """
        The configuration parameters for egress access logging.
        """
        return pulumi.get(self, "egress_access_logs")

    @egress_access_logs.setter
    def egress_access_logs(self, value: Optional[pulumi.Input['ChannelLogConfigurationArgs']]):
        pulumi.set(self, "egress_access_logs", value)

    @property
    @pulumi.getter(name="ingressAccessLogs")
    def ingress_access_logs(self) -> Optional[pulumi.Input['ChannelLogConfigurationArgs']]:
        """
        The configuration parameters for egress access logging.
        """
        return pulumi.get(self, "ingress_access_logs")

    @ingress_access_logs.setter
    def ingress_access_logs(self, value: Optional[pulumi.Input['ChannelLogConfigurationArgs']]):
        pulumi.set(self, "ingress_access_logs", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ChannelTagArgs']]]]:
        """
        A collection of tags associated with a resource
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ChannelTagArgs']]]]):
        pulumi.set(self, "tags", value)


class Channel(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 egress_access_logs: Optional[pulumi.Input[pulumi.InputType['ChannelLogConfigurationArgs']]] = None,
                 ingress_access_logs: Optional[pulumi.Input[pulumi.InputType['ChannelLogConfigurationArgs']]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ChannelTagArgs']]]]] = None,
                 __props__=None):
        """
        Resource schema for AWS::MediaPackage::Channel

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: A short text description of the Channel.
        :param pulumi.Input[pulumi.InputType['ChannelLogConfigurationArgs']] egress_access_logs: The configuration parameters for egress access logging.
        :param pulumi.Input[pulumi.InputType['ChannelLogConfigurationArgs']] ingress_access_logs: The configuration parameters for egress access logging.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ChannelTagArgs']]]] tags: A collection of tags associated with a resource
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[ChannelArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource schema for AWS::MediaPackage::Channel

        :param str resource_name: The name of the resource.
        :param ChannelArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ChannelArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 egress_access_logs: Optional[pulumi.Input[pulumi.InputType['ChannelLogConfigurationArgs']]] = None,
                 ingress_access_logs: Optional[pulumi.Input[pulumi.InputType['ChannelLogConfigurationArgs']]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ChannelTagArgs']]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ChannelArgs.__new__(ChannelArgs)

            __props__.__dict__["description"] = description
            __props__.__dict__["egress_access_logs"] = egress_access_logs
            __props__.__dict__["ingress_access_logs"] = ingress_access_logs
            __props__.__dict__["tags"] = tags
            __props__.__dict__["arn"] = None
            __props__.__dict__["hls_ingest"] = None
        super(Channel, __self__).__init__(
            'aws-native:mediapackage:Channel',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Channel':
        """
        Get an existing Channel resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = ChannelArgs.__new__(ChannelArgs)

        __props__.__dict__["arn"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["egress_access_logs"] = None
        __props__.__dict__["hls_ingest"] = None
        __props__.__dict__["ingress_access_logs"] = None
        __props__.__dict__["tags"] = None
        return Channel(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) assigned to the Channel.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        A short text description of the Channel.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="egressAccessLogs")
    def egress_access_logs(self) -> pulumi.Output[Optional['outputs.ChannelLogConfiguration']]:
        """
        The configuration parameters for egress access logging.
        """
        return pulumi.get(self, "egress_access_logs")

    @property
    @pulumi.getter(name="hlsIngest")
    def hls_ingest(self) -> pulumi.Output['outputs.ChannelHlsIngest']:
        """
        A short text description of the Channel.
        """
        return pulumi.get(self, "hls_ingest")

    @property
    @pulumi.getter(name="ingressAccessLogs")
    def ingress_access_logs(self) -> pulumi.Output[Optional['outputs.ChannelLogConfiguration']]:
        """
        The configuration parameters for egress access logging.
        """
        return pulumi.get(self, "ingress_access_logs")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Sequence['outputs.ChannelTag']]]:
        """
        A collection of tags associated with a resource
        """
        return pulumi.get(self, "tags")

