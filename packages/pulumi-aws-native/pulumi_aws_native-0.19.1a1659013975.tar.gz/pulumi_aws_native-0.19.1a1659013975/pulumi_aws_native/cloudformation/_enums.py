# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

from enum import Enum

__all__ = [
    'HookTypeConfigConfigurationAlias',
    'HookVersionVisibility',
    'ModuleVersionVisibility',
    'PublicTypeVersionType',
    'PublisherIdentityProvider',
    'PublisherStatus',
    'ResourceVersionProvisioningType',
    'ResourceVersionVisibility',
    'StackSetCallAs',
    'StackSetCapability',
    'StackSetPermissionModel',
    'StackSetRegionConcurrencyType',
    'TypeActivationType',
    'TypeActivationVersionBump',
]


class HookTypeConfigConfigurationAlias(str, Enum):
    """
    An alias by which to refer to this extension configuration data.
    """
    DEFAULT = "default"


class HookVersionVisibility(str, Enum):
    """
    The scope at which the type is visible and usable in CloudFormation operations.

    Valid values include:

    PRIVATE: The type is only visible and usable within the account in which it is registered. Currently, AWS CloudFormation marks any types you register as PRIVATE.

    PUBLIC: The type is publically visible and usable within any Amazon account.
    """
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class ModuleVersionVisibility(str, Enum):
    """
    The scope at which the type is visible and usable in CloudFormation operations.

    The only allowed value at present is:

    PRIVATE: The type is only visible and usable within the account in which it is registered. Currently, AWS CloudFormation marks any types you register as PRIVATE.
    """
    PRIVATE = "PRIVATE"


class PublicTypeVersionType(str, Enum):
    """
    The kind of extension
    """
    RESOURCE = "RESOURCE"
    MODULE = "MODULE"
    HOOK = "HOOK"


class PublisherIdentityProvider(str, Enum):
    """
    The type of account used as the identity provider when registering this publisher with CloudFormation.
    """
    AWS_MARKETPLACE = "AWS_Marketplace"
    GIT_HUB = "GitHub"
    BITBUCKET = "Bitbucket"


class PublisherStatus(str, Enum):
    """
    Whether the publisher is verified.
    """
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class ResourceVersionProvisioningType(str, Enum):
    """
    The provisioning behavior of the type. AWS CloudFormation determines the provisioning type during registration, based on the types of handlers in the schema handler package submitted.
    """
    NON_PROVISIONABLE = "NON_PROVISIONABLE"
    IMMUTABLE = "IMMUTABLE"
    FULLY_MUTABLE = "FULLY_MUTABLE"


class ResourceVersionVisibility(str, Enum):
    """
    The scope at which the type is visible and usable in CloudFormation operations.

    Valid values include:

    PRIVATE: The type is only visible and usable within the account in which it is registered. Currently, AWS CloudFormation marks any types you register as PRIVATE.

    PUBLIC: The type is publically visible and usable within any Amazon account.
    """
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class StackSetCallAs(str, Enum):
    """
    Specifies the AWS account that you are acting from. By default, SELF is specified. For self-managed permissions, specify SELF; for service-managed permissions, if you are signed in to the organization's management account, specify SELF. If you are signed in to a delegated administrator account, specify DELEGATED_ADMIN.
    """
    SELF = "SELF"
    DELEGATED_ADMIN = "DELEGATED_ADMIN"


class StackSetCapability(str, Enum):
    CAPABILITY_IAM = "CAPABILITY_IAM"
    CAPABILITY_NAMED_IAM = "CAPABILITY_NAMED_IAM"
    CAPABILITY_AUTO_EXPAND = "CAPABILITY_AUTO_EXPAND"


class StackSetPermissionModel(str, Enum):
    """
    Describes how the IAM roles required for stack set operations are created. By default, SELF-MANAGED is specified.
    """
    SERVICE_MANAGED = "SERVICE_MANAGED"
    SELF_MANAGED = "SELF_MANAGED"


class StackSetRegionConcurrencyType(str, Enum):
    """
    The concurrency type of deploying StackSets operations in regions, could be in parallel or one region at a time
    """
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"


class TypeActivationType(str, Enum):
    """
    The kind of extension
    """
    RESOURCE = "RESOURCE"
    MODULE = "MODULE"
    HOOK = "HOOK"


class TypeActivationVersionBump(str, Enum):
    """
    Manually updates a previously-enabled type to a new major or minor version, if available. You can also use this parameter to update the value of AutoUpdateEnabled
    """
    MAJOR = "MAJOR"
    MINOR = "MINOR"
