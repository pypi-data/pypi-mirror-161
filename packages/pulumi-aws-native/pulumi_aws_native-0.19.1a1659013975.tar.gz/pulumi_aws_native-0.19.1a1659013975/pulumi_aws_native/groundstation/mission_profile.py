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

__all__ = ['MissionProfileArgs', 'MissionProfile']

@pulumi.input_type
class MissionProfileArgs:
    def __init__(__self__, *,
                 dataflow_edges: pulumi.Input[Sequence[pulumi.Input['MissionProfileDataflowEdgeArgs']]],
                 minimum_viable_contact_duration_seconds: pulumi.Input[int],
                 tracking_config_arn: pulumi.Input[str],
                 contact_post_pass_duration_seconds: Optional[pulumi.Input[int]] = None,
                 contact_pre_pass_duration_seconds: Optional[pulumi.Input[int]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input['MissionProfileTagArgs']]]] = None):
        """
        The set of arguments for constructing a MissionProfile resource.
        :param pulumi.Input[int] minimum_viable_contact_duration_seconds: Visibilities with shorter duration than the specified minimum viable contact duration will be ignored when searching for available contacts.
        :param pulumi.Input[int] contact_post_pass_duration_seconds: Post-pass time needed after the contact.
        :param pulumi.Input[int] contact_pre_pass_duration_seconds: Pre-pass time needed before the contact.
        :param pulumi.Input[str] name: A name used to identify a mission profile.
        """
        pulumi.set(__self__, "dataflow_edges", dataflow_edges)
        pulumi.set(__self__, "minimum_viable_contact_duration_seconds", minimum_viable_contact_duration_seconds)
        pulumi.set(__self__, "tracking_config_arn", tracking_config_arn)
        if contact_post_pass_duration_seconds is not None:
            pulumi.set(__self__, "contact_post_pass_duration_seconds", contact_post_pass_duration_seconds)
        if contact_pre_pass_duration_seconds is not None:
            pulumi.set(__self__, "contact_pre_pass_duration_seconds", contact_pre_pass_duration_seconds)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="dataflowEdges")
    def dataflow_edges(self) -> pulumi.Input[Sequence[pulumi.Input['MissionProfileDataflowEdgeArgs']]]:
        return pulumi.get(self, "dataflow_edges")

    @dataflow_edges.setter
    def dataflow_edges(self, value: pulumi.Input[Sequence[pulumi.Input['MissionProfileDataflowEdgeArgs']]]):
        pulumi.set(self, "dataflow_edges", value)

    @property
    @pulumi.getter(name="minimumViableContactDurationSeconds")
    def minimum_viable_contact_duration_seconds(self) -> pulumi.Input[int]:
        """
        Visibilities with shorter duration than the specified minimum viable contact duration will be ignored when searching for available contacts.
        """
        return pulumi.get(self, "minimum_viable_contact_duration_seconds")

    @minimum_viable_contact_duration_seconds.setter
    def minimum_viable_contact_duration_seconds(self, value: pulumi.Input[int]):
        pulumi.set(self, "minimum_viable_contact_duration_seconds", value)

    @property
    @pulumi.getter(name="trackingConfigArn")
    def tracking_config_arn(self) -> pulumi.Input[str]:
        return pulumi.get(self, "tracking_config_arn")

    @tracking_config_arn.setter
    def tracking_config_arn(self, value: pulumi.Input[str]):
        pulumi.set(self, "tracking_config_arn", value)

    @property
    @pulumi.getter(name="contactPostPassDurationSeconds")
    def contact_post_pass_duration_seconds(self) -> Optional[pulumi.Input[int]]:
        """
        Post-pass time needed after the contact.
        """
        return pulumi.get(self, "contact_post_pass_duration_seconds")

    @contact_post_pass_duration_seconds.setter
    def contact_post_pass_duration_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "contact_post_pass_duration_seconds", value)

    @property
    @pulumi.getter(name="contactPrePassDurationSeconds")
    def contact_pre_pass_duration_seconds(self) -> Optional[pulumi.Input[int]]:
        """
        Pre-pass time needed before the contact.
        """
        return pulumi.get(self, "contact_pre_pass_duration_seconds")

    @contact_pre_pass_duration_seconds.setter
    def contact_pre_pass_duration_seconds(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "contact_pre_pass_duration_seconds", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        A name used to identify a mission profile.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['MissionProfileTagArgs']]]]:
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['MissionProfileTagArgs']]]]):
        pulumi.set(self, "tags", value)


class MissionProfile(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 contact_post_pass_duration_seconds: Optional[pulumi.Input[int]] = None,
                 contact_pre_pass_duration_seconds: Optional[pulumi.Input[int]] = None,
                 dataflow_edges: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['MissionProfileDataflowEdgeArgs']]]]] = None,
                 minimum_viable_contact_duration_seconds: Optional[pulumi.Input[int]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['MissionProfileTagArgs']]]]] = None,
                 tracking_config_arn: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        AWS Ground Station Mission Profile resource type for CloudFormation.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[int] contact_post_pass_duration_seconds: Post-pass time needed after the contact.
        :param pulumi.Input[int] contact_pre_pass_duration_seconds: Pre-pass time needed before the contact.
        :param pulumi.Input[int] minimum_viable_contact_duration_seconds: Visibilities with shorter duration than the specified minimum viable contact duration will be ignored when searching for available contacts.
        :param pulumi.Input[str] name: A name used to identify a mission profile.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: MissionProfileArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        AWS Ground Station Mission Profile resource type for CloudFormation.

        :param str resource_name: The name of the resource.
        :param MissionProfileArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(MissionProfileArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 contact_post_pass_duration_seconds: Optional[pulumi.Input[int]] = None,
                 contact_pre_pass_duration_seconds: Optional[pulumi.Input[int]] = None,
                 dataflow_edges: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['MissionProfileDataflowEdgeArgs']]]]] = None,
                 minimum_viable_contact_duration_seconds: Optional[pulumi.Input[int]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['MissionProfileTagArgs']]]]] = None,
                 tracking_config_arn: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = MissionProfileArgs.__new__(MissionProfileArgs)

            __props__.__dict__["contact_post_pass_duration_seconds"] = contact_post_pass_duration_seconds
            __props__.__dict__["contact_pre_pass_duration_seconds"] = contact_pre_pass_duration_seconds
            if dataflow_edges is None and not opts.urn:
                raise TypeError("Missing required property 'dataflow_edges'")
            __props__.__dict__["dataflow_edges"] = dataflow_edges
            if minimum_viable_contact_duration_seconds is None and not opts.urn:
                raise TypeError("Missing required property 'minimum_viable_contact_duration_seconds'")
            __props__.__dict__["minimum_viable_contact_duration_seconds"] = minimum_viable_contact_duration_seconds
            __props__.__dict__["name"] = name
            __props__.__dict__["tags"] = tags
            if tracking_config_arn is None and not opts.urn:
                raise TypeError("Missing required property 'tracking_config_arn'")
            __props__.__dict__["tracking_config_arn"] = tracking_config_arn
            __props__.__dict__["arn"] = None
            __props__.__dict__["region"] = None
        super(MissionProfile, __self__).__init__(
            'aws-native:groundstation:MissionProfile',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'MissionProfile':
        """
        Get an existing MissionProfile resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = MissionProfileArgs.__new__(MissionProfileArgs)

        __props__.__dict__["arn"] = None
        __props__.__dict__["contact_post_pass_duration_seconds"] = None
        __props__.__dict__["contact_pre_pass_duration_seconds"] = None
        __props__.__dict__["dataflow_edges"] = None
        __props__.__dict__["minimum_viable_contact_duration_seconds"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["region"] = None
        __props__.__dict__["tags"] = None
        __props__.__dict__["tracking_config_arn"] = None
        return MissionProfile(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="contactPostPassDurationSeconds")
    def contact_post_pass_duration_seconds(self) -> pulumi.Output[Optional[int]]:
        """
        Post-pass time needed after the contact.
        """
        return pulumi.get(self, "contact_post_pass_duration_seconds")

    @property
    @pulumi.getter(name="contactPrePassDurationSeconds")
    def contact_pre_pass_duration_seconds(self) -> pulumi.Output[Optional[int]]:
        """
        Pre-pass time needed before the contact.
        """
        return pulumi.get(self, "contact_pre_pass_duration_seconds")

    @property
    @pulumi.getter(name="dataflowEdges")
    def dataflow_edges(self) -> pulumi.Output[Sequence['outputs.MissionProfileDataflowEdge']]:
        return pulumi.get(self, "dataflow_edges")

    @property
    @pulumi.getter(name="minimumViableContactDurationSeconds")
    def minimum_viable_contact_duration_seconds(self) -> pulumi.Output[int]:
        """
        Visibilities with shorter duration than the specified minimum viable contact duration will be ignored when searching for available contacts.
        """
        return pulumi.get(self, "minimum_viable_contact_duration_seconds")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        A name used to identify a mission profile.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def region(self) -> pulumi.Output[str]:
        return pulumi.get(self, "region")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Sequence['outputs.MissionProfileTag']]]:
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="trackingConfigArn")
    def tracking_config_arn(self) -> pulumi.Output[str]:
        return pulumi.get(self, "tracking_config_arn")

