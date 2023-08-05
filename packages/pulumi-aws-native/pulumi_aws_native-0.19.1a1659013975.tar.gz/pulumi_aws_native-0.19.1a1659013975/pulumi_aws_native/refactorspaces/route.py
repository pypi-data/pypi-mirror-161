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
from ._enums import *
from ._inputs import *

__all__ = ['RouteArgs', 'Route']

@pulumi.input_type
class RouteArgs:
    def __init__(__self__, *,
                 application_identifier: pulumi.Input[str],
                 environment_identifier: pulumi.Input[str],
                 service_identifier: pulumi.Input[str],
                 route_type: Optional[pulumi.Input['RouteType']] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input['RouteTagArgs']]]] = None,
                 uri_path_route: Optional[pulumi.Input['RouteUriPathRouteInputArgs']] = None):
        """
        The set of arguments for constructing a Route resource.
        :param pulumi.Input[Sequence[pulumi.Input['RouteTagArgs']]] tags: Metadata that you can assign to help organize the frameworks that you create. Each tag is a key-value pair.
        """
        pulumi.set(__self__, "application_identifier", application_identifier)
        pulumi.set(__self__, "environment_identifier", environment_identifier)
        pulumi.set(__self__, "service_identifier", service_identifier)
        if route_type is not None:
            pulumi.set(__self__, "route_type", route_type)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if uri_path_route is not None:
            pulumi.set(__self__, "uri_path_route", uri_path_route)

    @property
    @pulumi.getter(name="applicationIdentifier")
    def application_identifier(self) -> pulumi.Input[str]:
        return pulumi.get(self, "application_identifier")

    @application_identifier.setter
    def application_identifier(self, value: pulumi.Input[str]):
        pulumi.set(self, "application_identifier", value)

    @property
    @pulumi.getter(name="environmentIdentifier")
    def environment_identifier(self) -> pulumi.Input[str]:
        return pulumi.get(self, "environment_identifier")

    @environment_identifier.setter
    def environment_identifier(self, value: pulumi.Input[str]):
        pulumi.set(self, "environment_identifier", value)

    @property
    @pulumi.getter(name="serviceIdentifier")
    def service_identifier(self) -> pulumi.Input[str]:
        return pulumi.get(self, "service_identifier")

    @service_identifier.setter
    def service_identifier(self, value: pulumi.Input[str]):
        pulumi.set(self, "service_identifier", value)

    @property
    @pulumi.getter(name="routeType")
    def route_type(self) -> Optional[pulumi.Input['RouteType']]:
        return pulumi.get(self, "route_type")

    @route_type.setter
    def route_type(self, value: Optional[pulumi.Input['RouteType']]):
        pulumi.set(self, "route_type", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['RouteTagArgs']]]]:
        """
        Metadata that you can assign to help organize the frameworks that you create. Each tag is a key-value pair.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['RouteTagArgs']]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="uriPathRoute")
    def uri_path_route(self) -> Optional[pulumi.Input['RouteUriPathRouteInputArgs']]:
        return pulumi.get(self, "uri_path_route")

    @uri_path_route.setter
    def uri_path_route(self, value: Optional[pulumi.Input['RouteUriPathRouteInputArgs']]):
        pulumi.set(self, "uri_path_route", value)


class Route(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 application_identifier: Optional[pulumi.Input[str]] = None,
                 environment_identifier: Optional[pulumi.Input[str]] = None,
                 route_type: Optional[pulumi.Input['RouteType']] = None,
                 service_identifier: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouteTagArgs']]]]] = None,
                 uri_path_route: Optional[pulumi.Input[pulumi.InputType['RouteUriPathRouteInputArgs']]] = None,
                 __props__=None):
        """
        Definition of AWS::RefactorSpaces::Route Resource Type

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouteTagArgs']]]] tags: Metadata that you can assign to help organize the frameworks that you create. Each tag is a key-value pair.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: RouteArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Definition of AWS::RefactorSpaces::Route Resource Type

        :param str resource_name: The name of the resource.
        :param RouteArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(RouteArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 application_identifier: Optional[pulumi.Input[str]] = None,
                 environment_identifier: Optional[pulumi.Input[str]] = None,
                 route_type: Optional[pulumi.Input['RouteType']] = None,
                 service_identifier: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RouteTagArgs']]]]] = None,
                 uri_path_route: Optional[pulumi.Input[pulumi.InputType['RouteUriPathRouteInputArgs']]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = RouteArgs.__new__(RouteArgs)

            if application_identifier is None and not opts.urn:
                raise TypeError("Missing required property 'application_identifier'")
            __props__.__dict__["application_identifier"] = application_identifier
            if environment_identifier is None and not opts.urn:
                raise TypeError("Missing required property 'environment_identifier'")
            __props__.__dict__["environment_identifier"] = environment_identifier
            __props__.__dict__["route_type"] = route_type
            if service_identifier is None and not opts.urn:
                raise TypeError("Missing required property 'service_identifier'")
            __props__.__dict__["service_identifier"] = service_identifier
            __props__.__dict__["tags"] = tags
            __props__.__dict__["uri_path_route"] = uri_path_route
            __props__.__dict__["arn"] = None
            __props__.__dict__["path_resource_to_id"] = None
            __props__.__dict__["route_identifier"] = None
        super(Route, __self__).__init__(
            'aws-native:refactorspaces:Route',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Route':
        """
        Get an existing Route resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = RouteArgs.__new__(RouteArgs)

        __props__.__dict__["application_identifier"] = None
        __props__.__dict__["arn"] = None
        __props__.__dict__["environment_identifier"] = None
        __props__.__dict__["path_resource_to_id"] = None
        __props__.__dict__["route_identifier"] = None
        __props__.__dict__["route_type"] = None
        __props__.__dict__["service_identifier"] = None
        __props__.__dict__["tags"] = None
        __props__.__dict__["uri_path_route"] = None
        return Route(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="applicationIdentifier")
    def application_identifier(self) -> pulumi.Output[str]:
        return pulumi.get(self, "application_identifier")

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="environmentIdentifier")
    def environment_identifier(self) -> pulumi.Output[str]:
        return pulumi.get(self, "environment_identifier")

    @property
    @pulumi.getter(name="pathResourceToId")
    def path_resource_to_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "path_resource_to_id")

    @property
    @pulumi.getter(name="routeIdentifier")
    def route_identifier(self) -> pulumi.Output[str]:
        return pulumi.get(self, "route_identifier")

    @property
    @pulumi.getter(name="routeType")
    def route_type(self) -> pulumi.Output[Optional['RouteType']]:
        return pulumi.get(self, "route_type")

    @property
    @pulumi.getter(name="serviceIdentifier")
    def service_identifier(self) -> pulumi.Output[str]:
        return pulumi.get(self, "service_identifier")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Sequence['outputs.RouteTag']]]:
        """
        Metadata that you can assign to help organize the frameworks that you create. Each tag is a key-value pair.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="uriPathRoute")
    def uri_path_route(self) -> pulumi.Output[Optional['outputs.RouteUriPathRouteInput']]:
        return pulumi.get(self, "uri_path_route")

