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

__all__ = ['ListenerArgs', 'Listener']

@pulumi.input_type
class ListenerArgs:
    def __init__(__self__, *,
                 default_actions: pulumi.Input[Sequence[pulumi.Input['ListenerActionArgs']]],
                 load_balancer_arn: pulumi.Input[str],
                 alpn_policy: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 certificates: Optional[pulumi.Input[Sequence[pulumi.Input['ListenerCertificateArgs']]]] = None,
                 port: Optional[pulumi.Input[int]] = None,
                 protocol: Optional[pulumi.Input[str]] = None,
                 ssl_policy: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a Listener resource.
        """
        pulumi.set(__self__, "default_actions", default_actions)
        pulumi.set(__self__, "load_balancer_arn", load_balancer_arn)
        if alpn_policy is not None:
            pulumi.set(__self__, "alpn_policy", alpn_policy)
        if certificates is not None:
            pulumi.set(__self__, "certificates", certificates)
        if port is not None:
            pulumi.set(__self__, "port", port)
        if protocol is not None:
            pulumi.set(__self__, "protocol", protocol)
        if ssl_policy is not None:
            pulumi.set(__self__, "ssl_policy", ssl_policy)

    @property
    @pulumi.getter(name="defaultActions")
    def default_actions(self) -> pulumi.Input[Sequence[pulumi.Input['ListenerActionArgs']]]:
        return pulumi.get(self, "default_actions")

    @default_actions.setter
    def default_actions(self, value: pulumi.Input[Sequence[pulumi.Input['ListenerActionArgs']]]):
        pulumi.set(self, "default_actions", value)

    @property
    @pulumi.getter(name="loadBalancerArn")
    def load_balancer_arn(self) -> pulumi.Input[str]:
        return pulumi.get(self, "load_balancer_arn")

    @load_balancer_arn.setter
    def load_balancer_arn(self, value: pulumi.Input[str]):
        pulumi.set(self, "load_balancer_arn", value)

    @property
    @pulumi.getter(name="alpnPolicy")
    def alpn_policy(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        return pulumi.get(self, "alpn_policy")

    @alpn_policy.setter
    def alpn_policy(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "alpn_policy", value)

    @property
    @pulumi.getter
    def certificates(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ListenerCertificateArgs']]]]:
        return pulumi.get(self, "certificates")

    @certificates.setter
    def certificates(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ListenerCertificateArgs']]]]):
        pulumi.set(self, "certificates", value)

    @property
    @pulumi.getter
    def port(self) -> Optional[pulumi.Input[int]]:
        return pulumi.get(self, "port")

    @port.setter
    def port(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "port", value)

    @property
    @pulumi.getter
    def protocol(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "protocol")

    @protocol.setter
    def protocol(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "protocol", value)

    @property
    @pulumi.getter(name="sslPolicy")
    def ssl_policy(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "ssl_policy")

    @ssl_policy.setter
    def ssl_policy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "ssl_policy", value)


class Listener(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 alpn_policy: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 certificates: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ListenerCertificateArgs']]]]] = None,
                 default_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ListenerActionArgs']]]]] = None,
                 load_balancer_arn: Optional[pulumi.Input[str]] = None,
                 port: Optional[pulumi.Input[int]] = None,
                 protocol: Optional[pulumi.Input[str]] = None,
                 ssl_policy: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Resource Type definition for AWS::ElasticLoadBalancingV2::Listener

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ListenerArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource Type definition for AWS::ElasticLoadBalancingV2::Listener

        :param str resource_name: The name of the resource.
        :param ListenerArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ListenerArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 alpn_policy: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 certificates: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ListenerCertificateArgs']]]]] = None,
                 default_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ListenerActionArgs']]]]] = None,
                 load_balancer_arn: Optional[pulumi.Input[str]] = None,
                 port: Optional[pulumi.Input[int]] = None,
                 protocol: Optional[pulumi.Input[str]] = None,
                 ssl_policy: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ListenerArgs.__new__(ListenerArgs)

            __props__.__dict__["alpn_policy"] = alpn_policy
            __props__.__dict__["certificates"] = certificates
            if default_actions is None and not opts.urn:
                raise TypeError("Missing required property 'default_actions'")
            __props__.__dict__["default_actions"] = default_actions
            if load_balancer_arn is None and not opts.urn:
                raise TypeError("Missing required property 'load_balancer_arn'")
            __props__.__dict__["load_balancer_arn"] = load_balancer_arn
            __props__.__dict__["port"] = port
            __props__.__dict__["protocol"] = protocol
            __props__.__dict__["ssl_policy"] = ssl_policy
            __props__.__dict__["listener_arn"] = None
        super(Listener, __self__).__init__(
            'aws-native:elasticloadbalancingv2:Listener',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Listener':
        """
        Get an existing Listener resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = ListenerArgs.__new__(ListenerArgs)

        __props__.__dict__["alpn_policy"] = None
        __props__.__dict__["certificates"] = None
        __props__.__dict__["default_actions"] = None
        __props__.__dict__["listener_arn"] = None
        __props__.__dict__["load_balancer_arn"] = None
        __props__.__dict__["port"] = None
        __props__.__dict__["protocol"] = None
        __props__.__dict__["ssl_policy"] = None
        return Listener(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="alpnPolicy")
    def alpn_policy(self) -> pulumi.Output[Optional[Sequence[str]]]:
        return pulumi.get(self, "alpn_policy")

    @property
    @pulumi.getter
    def certificates(self) -> pulumi.Output[Optional[Sequence['outputs.ListenerCertificate']]]:
        return pulumi.get(self, "certificates")

    @property
    @pulumi.getter(name="defaultActions")
    def default_actions(self) -> pulumi.Output[Sequence['outputs.ListenerAction']]:
        return pulumi.get(self, "default_actions")

    @property
    @pulumi.getter(name="listenerArn")
    def listener_arn(self) -> pulumi.Output[str]:
        return pulumi.get(self, "listener_arn")

    @property
    @pulumi.getter(name="loadBalancerArn")
    def load_balancer_arn(self) -> pulumi.Output[str]:
        return pulumi.get(self, "load_balancer_arn")

    @property
    @pulumi.getter
    def port(self) -> pulumi.Output[Optional[int]]:
        return pulumi.get(self, "port")

    @property
    @pulumi.getter
    def protocol(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "protocol")

    @property
    @pulumi.getter(name="sslPolicy")
    def ssl_policy(self) -> pulumi.Output[Optional[str]]:
        return pulumi.get(self, "ssl_policy")

