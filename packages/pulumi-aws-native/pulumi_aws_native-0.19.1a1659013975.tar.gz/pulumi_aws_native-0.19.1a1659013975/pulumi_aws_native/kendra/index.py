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

__all__ = ['IndexArgs', 'Index']

@pulumi.input_type
class IndexArgs:
    def __init__(__self__, *,
                 edition: pulumi.Input['IndexEdition'],
                 role_arn: pulumi.Input[str],
                 capacity_units: Optional[pulumi.Input['IndexCapacityUnitsConfigurationArgs']] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 document_metadata_configurations: Optional[pulumi.Input[Sequence[pulumi.Input['IndexDocumentMetadataConfigurationArgs']]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 server_side_encryption_configuration: Optional[pulumi.Input['IndexServerSideEncryptionConfigurationArgs']] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input['IndexTagArgs']]]] = None,
                 user_context_policy: Optional[pulumi.Input['IndexUserContextPolicy']] = None,
                 user_token_configurations: Optional[pulumi.Input[Sequence[pulumi.Input['IndexUserTokenConfigurationArgs']]]] = None):
        """
        The set of arguments for constructing a Index resource.
        :param pulumi.Input['IndexCapacityUnitsConfigurationArgs'] capacity_units: Capacity units
        :param pulumi.Input[str] description: A description for the index
        :param pulumi.Input[Sequence[pulumi.Input['IndexDocumentMetadataConfigurationArgs']]] document_metadata_configurations: Document metadata configurations
        :param pulumi.Input['IndexServerSideEncryptionConfigurationArgs'] server_side_encryption_configuration: Server side encryption configuration
        :param pulumi.Input[Sequence[pulumi.Input['IndexTagArgs']]] tags: Tags for labeling the index
        """
        pulumi.set(__self__, "edition", edition)
        pulumi.set(__self__, "role_arn", role_arn)
        if capacity_units is not None:
            pulumi.set(__self__, "capacity_units", capacity_units)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if document_metadata_configurations is not None:
            pulumi.set(__self__, "document_metadata_configurations", document_metadata_configurations)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if server_side_encryption_configuration is not None:
            pulumi.set(__self__, "server_side_encryption_configuration", server_side_encryption_configuration)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if user_context_policy is not None:
            pulumi.set(__self__, "user_context_policy", user_context_policy)
        if user_token_configurations is not None:
            pulumi.set(__self__, "user_token_configurations", user_token_configurations)

    @property
    @pulumi.getter
    def edition(self) -> pulumi.Input['IndexEdition']:
        return pulumi.get(self, "edition")

    @edition.setter
    def edition(self, value: pulumi.Input['IndexEdition']):
        pulumi.set(self, "edition", value)

    @property
    @pulumi.getter(name="roleArn")
    def role_arn(self) -> pulumi.Input[str]:
        return pulumi.get(self, "role_arn")

    @role_arn.setter
    def role_arn(self, value: pulumi.Input[str]):
        pulumi.set(self, "role_arn", value)

    @property
    @pulumi.getter(name="capacityUnits")
    def capacity_units(self) -> Optional[pulumi.Input['IndexCapacityUnitsConfigurationArgs']]:
        """
        Capacity units
        """
        return pulumi.get(self, "capacity_units")

    @capacity_units.setter
    def capacity_units(self, value: Optional[pulumi.Input['IndexCapacityUnitsConfigurationArgs']]):
        pulumi.set(self, "capacity_units", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A description for the index
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="documentMetadataConfigurations")
    def document_metadata_configurations(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['IndexDocumentMetadataConfigurationArgs']]]]:
        """
        Document metadata configurations
        """
        return pulumi.get(self, "document_metadata_configurations")

    @document_metadata_configurations.setter
    def document_metadata_configurations(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['IndexDocumentMetadataConfigurationArgs']]]]):
        pulumi.set(self, "document_metadata_configurations", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="serverSideEncryptionConfiguration")
    def server_side_encryption_configuration(self) -> Optional[pulumi.Input['IndexServerSideEncryptionConfigurationArgs']]:
        """
        Server side encryption configuration
        """
        return pulumi.get(self, "server_side_encryption_configuration")

    @server_side_encryption_configuration.setter
    def server_side_encryption_configuration(self, value: Optional[pulumi.Input['IndexServerSideEncryptionConfigurationArgs']]):
        pulumi.set(self, "server_side_encryption_configuration", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['IndexTagArgs']]]]:
        """
        Tags for labeling the index
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['IndexTagArgs']]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="userContextPolicy")
    def user_context_policy(self) -> Optional[pulumi.Input['IndexUserContextPolicy']]:
        return pulumi.get(self, "user_context_policy")

    @user_context_policy.setter
    def user_context_policy(self, value: Optional[pulumi.Input['IndexUserContextPolicy']]):
        pulumi.set(self, "user_context_policy", value)

    @property
    @pulumi.getter(name="userTokenConfigurations")
    def user_token_configurations(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['IndexUserTokenConfigurationArgs']]]]:
        return pulumi.get(self, "user_token_configurations")

    @user_token_configurations.setter
    def user_token_configurations(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['IndexUserTokenConfigurationArgs']]]]):
        pulumi.set(self, "user_token_configurations", value)


class Index(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 capacity_units: Optional[pulumi.Input[pulumi.InputType['IndexCapacityUnitsConfigurationArgs']]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 document_metadata_configurations: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['IndexDocumentMetadataConfigurationArgs']]]]] = None,
                 edition: Optional[pulumi.Input['IndexEdition']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 role_arn: Optional[pulumi.Input[str]] = None,
                 server_side_encryption_configuration: Optional[pulumi.Input[pulumi.InputType['IndexServerSideEncryptionConfigurationArgs']]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['IndexTagArgs']]]]] = None,
                 user_context_policy: Optional[pulumi.Input['IndexUserContextPolicy']] = None,
                 user_token_configurations: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['IndexUserTokenConfigurationArgs']]]]] = None,
                 __props__=None):
        """
        A Kendra index

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['IndexCapacityUnitsConfigurationArgs']] capacity_units: Capacity units
        :param pulumi.Input[str] description: A description for the index
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['IndexDocumentMetadataConfigurationArgs']]]] document_metadata_configurations: Document metadata configurations
        :param pulumi.Input[pulumi.InputType['IndexServerSideEncryptionConfigurationArgs']] server_side_encryption_configuration: Server side encryption configuration
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['IndexTagArgs']]]] tags: Tags for labeling the index
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: IndexArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        A Kendra index

        :param str resource_name: The name of the resource.
        :param IndexArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(IndexArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 capacity_units: Optional[pulumi.Input[pulumi.InputType['IndexCapacityUnitsConfigurationArgs']]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 document_metadata_configurations: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['IndexDocumentMetadataConfigurationArgs']]]]] = None,
                 edition: Optional[pulumi.Input['IndexEdition']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 role_arn: Optional[pulumi.Input[str]] = None,
                 server_side_encryption_configuration: Optional[pulumi.Input[pulumi.InputType['IndexServerSideEncryptionConfigurationArgs']]] = None,
                 tags: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['IndexTagArgs']]]]] = None,
                 user_context_policy: Optional[pulumi.Input['IndexUserContextPolicy']] = None,
                 user_token_configurations: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['IndexUserTokenConfigurationArgs']]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = IndexArgs.__new__(IndexArgs)

            __props__.__dict__["capacity_units"] = capacity_units
            __props__.__dict__["description"] = description
            __props__.__dict__["document_metadata_configurations"] = document_metadata_configurations
            if edition is None and not opts.urn:
                raise TypeError("Missing required property 'edition'")
            __props__.__dict__["edition"] = edition
            __props__.__dict__["name"] = name
            if role_arn is None and not opts.urn:
                raise TypeError("Missing required property 'role_arn'")
            __props__.__dict__["role_arn"] = role_arn
            __props__.__dict__["server_side_encryption_configuration"] = server_side_encryption_configuration
            __props__.__dict__["tags"] = tags
            __props__.__dict__["user_context_policy"] = user_context_policy
            __props__.__dict__["user_token_configurations"] = user_token_configurations
            __props__.__dict__["arn"] = None
        super(Index, __self__).__init__(
            'aws-native:kendra:Index',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Index':
        """
        Get an existing Index resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = IndexArgs.__new__(IndexArgs)

        __props__.__dict__["arn"] = None
        __props__.__dict__["capacity_units"] = None
        __props__.__dict__["description"] = None
        __props__.__dict__["document_metadata_configurations"] = None
        __props__.__dict__["edition"] = None
        __props__.__dict__["name"] = None
        __props__.__dict__["role_arn"] = None
        __props__.__dict__["server_side_encryption_configuration"] = None
        __props__.__dict__["tags"] = None
        __props__.__dict__["user_context_policy"] = None
        __props__.__dict__["user_token_configurations"] = None
        return Index(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="capacityUnits")
    def capacity_units(self) -> pulumi.Output[Optional['outputs.IndexCapacityUnitsConfiguration']]:
        """
        Capacity units
        """
        return pulumi.get(self, "capacity_units")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        A description for the index
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="documentMetadataConfigurations")
    def document_metadata_configurations(self) -> pulumi.Output[Optional[Sequence['outputs.IndexDocumentMetadataConfiguration']]]:
        """
        Document metadata configurations
        """
        return pulumi.get(self, "document_metadata_configurations")

    @property
    @pulumi.getter
    def edition(self) -> pulumi.Output['IndexEdition']:
        return pulumi.get(self, "edition")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="roleArn")
    def role_arn(self) -> pulumi.Output[str]:
        return pulumi.get(self, "role_arn")

    @property
    @pulumi.getter(name="serverSideEncryptionConfiguration")
    def server_side_encryption_configuration(self) -> pulumi.Output[Optional['outputs.IndexServerSideEncryptionConfiguration']]:
        """
        Server side encryption configuration
        """
        return pulumi.get(self, "server_side_encryption_configuration")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Sequence['outputs.IndexTag']]]:
        """
        Tags for labeling the index
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="userContextPolicy")
    def user_context_policy(self) -> pulumi.Output[Optional['IndexUserContextPolicy']]:
        return pulumi.get(self, "user_context_policy")

    @property
    @pulumi.getter(name="userTokenConfigurations")
    def user_token_configurations(self) -> pulumi.Output[Optional[Sequence['outputs.IndexUserTokenConfiguration']]]:
        return pulumi.get(self, "user_token_configurations")

