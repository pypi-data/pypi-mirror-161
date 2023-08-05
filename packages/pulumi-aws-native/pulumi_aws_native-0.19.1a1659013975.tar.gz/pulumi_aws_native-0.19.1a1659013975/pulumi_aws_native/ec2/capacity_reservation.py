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

__all__ = ['CapacityReservationArgs', 'CapacityReservation']

@pulumi.input_type
class CapacityReservationArgs:
    def __init__(__self__, *,
                 availability_zone: pulumi.Input[str],
                 instance_count: pulumi.Input[int],
                 instance_platform: pulumi.Input[str],
                 instance_type: pulumi.Input[str],
                 ebs_optimized: Optional[pulumi.Input[bool]] = None,
                 end_date: Optional[pulumi.Input[str]] = None,
                 end_date_type: Optional[pulumi.Input[str]] = None,
                 ephemeral_storage: Optional[pulumi.Input[bool]] = None,
                 instance_match_criteria: Optional[pulumi.Input[str]] = None,
                 out_post_arn: Optional[pulumi.Input[str]] = None,
                 placement_group_arn: Optional[pulumi.Input[str]] = None,
                 tag_specifications: Optional[pulumi.Input[Sequence[pulumi.Input['CapacityReservationTagSpecificationArgs']]]] = None,
                 tenancy: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a CapacityReservation resource.
        """
        pulumi.set(__self__, "availability_zone", availability_zone)
        pulumi.set(__self__, "instance_count", instance_count)
        pulumi.set(__self__, "instance_platform", instance_platform)
        pulumi.set(__self__, "instance_type", instance_type)
        if ebs_optimized is not None:
            pulumi.set(__self__, "ebs_optimized", ebs_optimized)
        if end_date is not None:
            pulumi.set(__self__, "end_date", end_date)
        if end_date_type is not None:
            pulumi.set(__self__, "end_date_type", end_date_type)
        if ephemeral_storage is not None:
            pulumi.set(__self__, "ephemeral_storage", ephemeral_storage)
        if instance_match_criteria is not None:
            pulumi.set(__self__, "instance_match_criteria", instance_match_criteria)
        if out_post_arn is not None:
            pulumi.set(__self__, "out_post_arn", out_post_arn)
        if placement_group_arn is not None:
            pulumi.set(__self__, "placement_group_arn", placement_group_arn)
        if tag_specifications is not None:
            pulumi.set(__self__, "tag_specifications", tag_specifications)
        if tenancy is not None:
            pulumi.set(__self__, "tenancy", tenancy)

    @property
    @pulumi.getter(name="availabilityZone")
    def availability_zone(self) -> pulumi.Input[str]:
        return pulumi.get(self, "availability_zone")

    @availability_zone.setter
    def availability_zone(self, value: pulumi.Input[str]):
        pulumi.set(self, "availability_zone", value)

    @property
    @pulumi.getter(name="instanceCount")
    def instance_count(self) -> pulumi.Input[int]:
        return pulumi.get(self, "instance_count")

    @instance_count.setter
    def instance_count(self, value: pulumi.Input[int]):
        pulumi.set(self, "instance_count", value)

    @property
    @pulumi.getter(name="instancePlatform")
    def instance_platform(self) -> pulumi.Input[str]:
        return pulumi.get(self, "instance_platform")

    @instance_platform.setter
    def instance_platform(self, value: pulumi.Input[str]):
        pulumi.set(self, "instance_platform", value)

    @property
    @pulumi.getter(name="instanceType")
    def instance_type(self) -> pulumi.Input[str]:
        return pulumi.get(self, "instance_type")

    @instance_type.setter
    def instance_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "instance_type", value)

    @property
    @pulumi.getter(name="ebsOptimized")
    def ebs_optimized(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "ebs_optimized")

    @ebs_optimized.setter
    def ebs_optimized(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "ebs_optimized", value)

    @property
    @pulumi.getter(name="endDate")
    def end_date(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "end_date")

    @end_date.setter
    def end_date(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "end_date", value)

    @property
    @pulumi.getter(name="endDateType")
    def end_date_type(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "end_date_type")

    @end_date_type.setter
    def end_date_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "end_date_type", value)

    @property
    @pulumi.getter(name="ephemeralStorage")
    def ephemeral_storage(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "ephemeral_storage")

    @ephemeral_storage.setter
    def ephemeral_storage(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "ephemeral_storage", value)

    @property
    @pulumi.getter(name="instanceMatchCriteria")
    def instance_match_criteria(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "instance_match_criteria")

    @instance_match_criteria.setter
    def instance_match_criteria(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "instance_match_criteria", value)

    @property
    @pulumi.getter(name="outPostArn")
    def out_post_arn(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "out_post_arn")

    @out_post_arn.setter
    def out_post_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "out_post_arn", value)

    @property
    @pulumi.getter(name="placementGroupArn")
    def placement_group_arn(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "placement_group_arn")

    @placement_group_arn.setter
    def placement_group_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "placement_group_arn", value)

    @property
    @pulumi.getter(name="tagSpecifications")
    def tag_specifications(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['CapacityReservationTagSpecificationArgs']]]]:
        return pulumi.get(self, "tag_specifications")

    @tag_specifications.setter
    def tag_specifications(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['CapacityReservationTagSpecificationArgs']]]]):
        pulumi.set(self, "tag_specifications", value)

    @property
    @pulumi.getter
    def tenancy(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "tenancy")

    @tenancy.setter
    def tenancy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "tenancy", value)


warnings.warn("""CapacityReservation is not yet supported by AWS Native, so its creation will currently fail. Please use the classic AWS provider, if possible.""", DeprecationWarning)


class CapacityReservation(pulumi.CustomResource):
    warnings.warn("""CapacityReservation is not yet supported by AWS Native, so its creation will currently fail. Please use the classic AWS provider, if possible.""", DeprecationWarning)

    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 availability_zone: Optional[pulumi.Input[str]] = None,
                 ebs_optimized: Optional[pulumi.Input[bool]] = None,
                 end_date: Optional[pulumi.Input[str]] = None,
                 end_date_type: Optional[pulumi.Input[str]] = None,
                 ephemeral_storage: Optional[pulumi.Input[bool]] = None,
                 instance_count: Optional[pulumi.Input[int]] = None,
                 instance_match_criteria: Optional[pulumi.Input[str]] = None,
                 instance_platform: Optional[pulumi.Input[str]] = None,
                 instance_type: Optional[pulumi.Input[str]] = None,
                 out_post_arn: Optional[pulumi.Input[str]] = None,
                 placement_group_arn: Optional[pulumi.Input[str]] = None,
                 tag_specifications: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['CapacityReservationTagSpecificationArgs']]]]] = None,
                 tenancy: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Resource Type definition for AWS::EC2::CapacityReservation

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: CapacityReservationArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource Type definition for AWS::EC2::CapacityReservation

        :param str resource_name: The name of the resource.
        :param CapacityReservationArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(CapacityReservationArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 availability_zone: Optional[pulumi.Input[str]] = None,
                 ebs_optimized: Optional[pulumi.Input[bool]] = None,
                 end_date: Optional[pulumi.Input[str]] = None,
                 end_date_type: Optional[pulumi.Input[str]] = None,
                 ephemeral_storage: Optional[pulumi.Input[bool]] = None,
                 instance_count: Optional[pulumi.Input[int]] = None,
                 instance_match_criteria: Optional[pulumi.Input[str]] = None,
                 instance_platform: Optional[pulumi.Input[str]] = None,
                 instance_type: Optional[pulumi.Input[str]] = None,
                 out_post_arn: Optional[pulumi.Input[str]] = None,
                 placement_group_arn: Optional[pulumi.Input[str]] = None,
                 tag_specifications: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['CapacityReservationTagSpecificationArgs']]]]] = None,
                 tenancy: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        pulumi.log.warn("""CapacityReservation is deprecated: CapacityReservation is not yet supported by AWS Native, so its creation will currently fail. Please use the classic AWS provider, if possible.""")
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = CapacityReservationArgs.__new__(CapacityReservationArgs)

            if availability_zone is None and not opts.urn:
                raise TypeError("Missing required property 'availability_zone'")
            __props__.__dict__["availability_zone"] = availability_zone
            __props__.__dict__["ebs_optimized"] = ebs_optimized
            __props__.__dict__["end_date"] = end_date
            __props__.__dict__["end_date_type"] = end_date_type
            __props__.__dict__["ephemeral_storage"] = ephemeral_storage
            if instance_count is None and not opts.urn:
                raise TypeError("Missing required property 'instance_count'")
            __props__.__dict__["instance_count"] = instance_count
            __props__.__dict__["instance_match_criteria"] = instance_match_criteria
            if instance_platform is None and not opts.urn:
                raise TypeError("Missing required property 'instance_platform'")
            __props__.__dict__["instance_platform"] = instance_platform
            if instance_type is None and not opts.urn:
                raise TypeError("Missing required property 'instance_type'")
            __props__.__dict__["instance_type"] = instance_type
            __props__.__dict__["out_post_arn"] = out_post_arn
            __props__.__dict__["placement_group_arn"] = placement_group_arn
            __props__.__dict__["tag_specifications"] = tag_specifications
            __props__.__dict__["tenancy"] = tenancy
            __props__.__dict__["available_instance_count"] = None
            __props__.__dict__["total_instance_count"] = None
        super(CapacityReservation, __self__).__init__(
            'aws-native:ec2:CapacityReservation',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'CapacityReservation':
        """
        Get an existing CapacityReservation resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = CapacityReservationArgs.__new__(CapacityReservationArgs)

        __props__.__dict__["availability_zone"] = None
        __props__.__dict__["available_instance_count"] = None
        __props__.__dict__["ebs_optimized"] = None
        __props__.__dict__["end_date"] = None
        __props__.__dict__["end_date_type"] = None
        __props__.__dict__["ephemeral_storage"] = None
        __props__.__dict__["instance_count"] = None
        __props__.__dict__["instance_match_criteria"] = None
        __props__.__dict__["instance_platform"] = None
        __props__.__dict__["instance_type"] = None
        __props__.__dict__["out_post_arn"] = None
        __props__.__dict__["placement_group_arn"] = None
        __props__.__dict__["tag_specifications"] = None
        __props__.__dict__["tenancy"] = None
        __props__.__dict__["total_instance_count"] = None
        return CapacityReservation(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="availabilityZone")
    def availability_zone(self) -> pulumi.Output[str]:
        return pulumi.get(self, "availability_zone")

    @property
    @pulumi.getter(name="availableInstanceCount")
    def available_instance_count(self) -> pulumi.Output[int]:
        return pulumi.get(self, "available_instance_count")

    @property
    @pulumi.getter(name="ebsOptimized")
    def ebs_optimized(self) -> pulumi.Output[Optional[bool]]:
        return pulumi.get(self, "ebs_optimized")

    @property
    @pulumi.getter(name="endDate")
    def end_date(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "end_date")

    @property
    @pulumi.getter(name="endDateType")
    def end_date_type(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "end_date_type")

    @property
    @pulumi.getter(name="ephemeralStorage")
    def ephemeral_storage(self) -> pulumi.Output[Optional[bool]]:
        return pulumi.get(self, "ephemeral_storage")

    @property
    @pulumi.getter(name="instanceCount")
    def instance_count(self) -> pulumi.Output[int]:
        return pulumi.get(self, "instance_count")

    @property
    @pulumi.getter(name="instanceMatchCriteria")
    def instance_match_criteria(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "instance_match_criteria")

    @property
    @pulumi.getter(name="instancePlatform")
    def instance_platform(self) -> pulumi.Output[str]:
        return pulumi.get(self, "instance_platform")

    @property
    @pulumi.getter(name="instanceType")
    def instance_type(self) -> pulumi.Output[str]:
        return pulumi.get(self, "instance_type")

    @property
    @pulumi.getter(name="outPostArn")
    def out_post_arn(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "out_post_arn")

    @property
    @pulumi.getter(name="placementGroupArn")
    def placement_group_arn(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "placement_group_arn")

    @property
    @pulumi.getter(name="tagSpecifications")
    def tag_specifications(self) -> pulumi.Output[Optional[Sequence['outputs.CapacityReservationTagSpecification']]]:
        return pulumi.get(self, "tag_specifications")

    @property
    @pulumi.getter
    def tenancy(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "tenancy")

    @property
    @pulumi.getter(name="totalInstanceCount")
    def total_instance_count(self) -> pulumi.Output[int]:
        return pulumi.get(self, "total_instance_count")

