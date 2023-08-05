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

__all__ = [
    'DBClusterParameterGroupTag',
    'DBClusterRole',
    'DBClusterScalingConfiguration',
    'DBClusterTag',
    'DBInstanceProcessorFeature',
    'DBInstanceRole',
    'DBInstanceTag',
    'DBParameterGroupTag',
    'DBProxyAuthFormat',
    'DBProxyEndpointTagFormat',
    'DBProxyTagFormat',
    'DBProxyTargetGroupConnectionPoolConfigurationInfoFormat',
    'DBSecurityGroupIngress',
    'DBSecurityGroupTag',
    'DBSubnetGroupTag',
    'EventSubscriptionTag',
    'OptionGroupOptionConfiguration',
    'OptionGroupOptionSetting',
    'OptionGroupTag',
]

@pulumi.output_type
class DBClusterParameterGroupTag(dict):
    """
    A key-value pair to associate with a resource.
    """
    def __init__(__self__, *,
                 key: str,
                 value: str):
        """
        A key-value pair to associate with a resource.
        :param str key: The key name of the tag. You can specify a value that is 1 to 128 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        :param str value: The value for the tag. You can specify a value that is 0 to 256 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        """
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> str:
        """
        The key name of the tag. You can specify a value that is 1 to 128 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        """
        return pulumi.get(self, "key")

    @property
    @pulumi.getter
    def value(self) -> str:
        """
        The value for the tag. You can specify a value that is 0 to 256 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        """
        return pulumi.get(self, "value")


@pulumi.output_type
class DBClusterRole(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "roleArn":
            suggest = "role_arn"
        elif key == "featureName":
            suggest = "feature_name"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in DBClusterRole. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        DBClusterRole.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        DBClusterRole.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 role_arn: str,
                 feature_name: Optional[str] = None):
        pulumi.set(__self__, "role_arn", role_arn)
        if feature_name is not None:
            pulumi.set(__self__, "feature_name", feature_name)

    @property
    @pulumi.getter(name="roleArn")
    def role_arn(self) -> str:
        return pulumi.get(self, "role_arn")

    @property
    @pulumi.getter(name="featureName")
    def feature_name(self) -> Optional[str]:
        return pulumi.get(self, "feature_name")


@pulumi.output_type
class DBClusterScalingConfiguration(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "autoPause":
            suggest = "auto_pause"
        elif key == "maxCapacity":
            suggest = "max_capacity"
        elif key == "minCapacity":
            suggest = "min_capacity"
        elif key == "secondsUntilAutoPause":
            suggest = "seconds_until_auto_pause"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in DBClusterScalingConfiguration. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        DBClusterScalingConfiguration.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        DBClusterScalingConfiguration.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 auto_pause: Optional[bool] = None,
                 max_capacity: Optional[int] = None,
                 min_capacity: Optional[int] = None,
                 seconds_until_auto_pause: Optional[int] = None):
        if auto_pause is not None:
            pulumi.set(__self__, "auto_pause", auto_pause)
        if max_capacity is not None:
            pulumi.set(__self__, "max_capacity", max_capacity)
        if min_capacity is not None:
            pulumi.set(__self__, "min_capacity", min_capacity)
        if seconds_until_auto_pause is not None:
            pulumi.set(__self__, "seconds_until_auto_pause", seconds_until_auto_pause)

    @property
    @pulumi.getter(name="autoPause")
    def auto_pause(self) -> Optional[bool]:
        return pulumi.get(self, "auto_pause")

    @property
    @pulumi.getter(name="maxCapacity")
    def max_capacity(self) -> Optional[int]:
        return pulumi.get(self, "max_capacity")

    @property
    @pulumi.getter(name="minCapacity")
    def min_capacity(self) -> Optional[int]:
        return pulumi.get(self, "min_capacity")

    @property
    @pulumi.getter(name="secondsUntilAutoPause")
    def seconds_until_auto_pause(self) -> Optional[int]:
        return pulumi.get(self, "seconds_until_auto_pause")


@pulumi.output_type
class DBClusterTag(dict):
    def __init__(__self__, *,
                 key: str,
                 value: str):
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> str:
        return pulumi.get(self, "key")

    @property
    @pulumi.getter
    def value(self) -> str:
        return pulumi.get(self, "value")


@pulumi.output_type
class DBInstanceProcessorFeature(dict):
    def __init__(__self__, *,
                 name: Optional[str] = None,
                 value: Optional[str] = None):
        if name is not None:
            pulumi.set(__self__, "name", name)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[str]:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def value(self) -> Optional[str]:
        return pulumi.get(self, "value")


@pulumi.output_type
class DBInstanceRole(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "featureName":
            suggest = "feature_name"
        elif key == "roleArn":
            suggest = "role_arn"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in DBInstanceRole. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        DBInstanceRole.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        DBInstanceRole.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 feature_name: str,
                 role_arn: str):
        pulumi.set(__self__, "feature_name", feature_name)
        pulumi.set(__self__, "role_arn", role_arn)

    @property
    @pulumi.getter(name="featureName")
    def feature_name(self) -> str:
        return pulumi.get(self, "feature_name")

    @property
    @pulumi.getter(name="roleArn")
    def role_arn(self) -> str:
        return pulumi.get(self, "role_arn")


@pulumi.output_type
class DBInstanceTag(dict):
    def __init__(__self__, *,
                 key: str,
                 value: str):
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> str:
        return pulumi.get(self, "key")

    @property
    @pulumi.getter
    def value(self) -> str:
        return pulumi.get(self, "value")


@pulumi.output_type
class DBParameterGroupTag(dict):
    """
    A key-value pair to associate with a resource.
    """
    def __init__(__self__, *,
                 key: str,
                 value: str):
        """
        A key-value pair to associate with a resource.
        :param str key: The key name of the tag. You can specify a value that is 1 to 128 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        :param str value: The value for the tag. You can specify a value that is 0 to 256 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        """
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> str:
        """
        The key name of the tag. You can specify a value that is 1 to 128 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        """
        return pulumi.get(self, "key")

    @property
    @pulumi.getter
    def value(self) -> str:
        """
        The value for the tag. You can specify a value that is 0 to 256 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        """
        return pulumi.get(self, "value")


@pulumi.output_type
class DBProxyAuthFormat(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "authScheme":
            suggest = "auth_scheme"
        elif key == "iAMAuth":
            suggest = "i_am_auth"
        elif key == "secretArn":
            suggest = "secret_arn"
        elif key == "userName":
            suggest = "user_name"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in DBProxyAuthFormat. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        DBProxyAuthFormat.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        DBProxyAuthFormat.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 auth_scheme: Optional['DBProxyAuthFormatAuthScheme'] = None,
                 description: Optional[str] = None,
                 i_am_auth: Optional['DBProxyAuthFormatIAMAuth'] = None,
                 secret_arn: Optional[str] = None,
                 user_name: Optional[str] = None):
        """
        :param 'DBProxyAuthFormatAuthScheme' auth_scheme: The type of authentication that the proxy uses for connections from the proxy to the underlying database. 
        :param str description: A user-specified description about the authentication used by a proxy to log in as a specific database user. 
        :param 'DBProxyAuthFormatIAMAuth' i_am_auth: Whether to require or disallow AWS Identity and Access Management (IAM) authentication for connections to the proxy. 
        :param str secret_arn: The Amazon Resource Name (ARN) representing the secret that the proxy uses to authenticate to the RDS DB instance or Aurora DB cluster. These secrets are stored within Amazon Secrets Manager. 
        :param str user_name: The name of the database user to which the proxy connects.
        """
        if auth_scheme is not None:
            pulumi.set(__self__, "auth_scheme", auth_scheme)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if i_am_auth is not None:
            pulumi.set(__self__, "i_am_auth", i_am_auth)
        if secret_arn is not None:
            pulumi.set(__self__, "secret_arn", secret_arn)
        if user_name is not None:
            pulumi.set(__self__, "user_name", user_name)

    @property
    @pulumi.getter(name="authScheme")
    def auth_scheme(self) -> Optional['DBProxyAuthFormatAuthScheme']:
        """
        The type of authentication that the proxy uses for connections from the proxy to the underlying database. 
        """
        return pulumi.get(self, "auth_scheme")

    @property
    @pulumi.getter
    def description(self) -> Optional[str]:
        """
        A user-specified description about the authentication used by a proxy to log in as a specific database user. 
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="iAMAuth")
    def i_am_auth(self) -> Optional['DBProxyAuthFormatIAMAuth']:
        """
        Whether to require or disallow AWS Identity and Access Management (IAM) authentication for connections to the proxy. 
        """
        return pulumi.get(self, "i_am_auth")

    @property
    @pulumi.getter(name="secretArn")
    def secret_arn(self) -> Optional[str]:
        """
        The Amazon Resource Name (ARN) representing the secret that the proxy uses to authenticate to the RDS DB instance or Aurora DB cluster. These secrets are stored within Amazon Secrets Manager. 
        """
        return pulumi.get(self, "secret_arn")

    @property
    @pulumi.getter(name="userName")
    def user_name(self) -> Optional[str]:
        """
        The name of the database user to which the proxy connects.
        """
        return pulumi.get(self, "user_name")


@pulumi.output_type
class DBProxyEndpointTagFormat(dict):
    def __init__(__self__, *,
                 key: Optional[str] = None,
                 value: Optional[str] = None):
        if key is not None:
            pulumi.set(__self__, "key", key)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[str]:
        return pulumi.get(self, "key")

    @property
    @pulumi.getter
    def value(self) -> Optional[str]:
        return pulumi.get(self, "value")


@pulumi.output_type
class DBProxyTagFormat(dict):
    def __init__(__self__, *,
                 key: Optional[str] = None,
                 value: Optional[str] = None):
        if key is not None:
            pulumi.set(__self__, "key", key)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> Optional[str]:
        return pulumi.get(self, "key")

    @property
    @pulumi.getter
    def value(self) -> Optional[str]:
        return pulumi.get(self, "value")


@pulumi.output_type
class DBProxyTargetGroupConnectionPoolConfigurationInfoFormat(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "connectionBorrowTimeout":
            suggest = "connection_borrow_timeout"
        elif key == "initQuery":
            suggest = "init_query"
        elif key == "maxConnectionsPercent":
            suggest = "max_connections_percent"
        elif key == "maxIdleConnectionsPercent":
            suggest = "max_idle_connections_percent"
        elif key == "sessionPinningFilters":
            suggest = "session_pinning_filters"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in DBProxyTargetGroupConnectionPoolConfigurationInfoFormat. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        DBProxyTargetGroupConnectionPoolConfigurationInfoFormat.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        DBProxyTargetGroupConnectionPoolConfigurationInfoFormat.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 connection_borrow_timeout: Optional[int] = None,
                 init_query: Optional[str] = None,
                 max_connections_percent: Optional[int] = None,
                 max_idle_connections_percent: Optional[int] = None,
                 session_pinning_filters: Optional[Sequence[str]] = None):
        """
        :param int connection_borrow_timeout: The number of seconds for a proxy to wait for a connection to become available in the connection pool.
        :param str init_query: One or more SQL statements for the proxy to run when opening each new database connection.
        :param int max_connections_percent: The maximum size of the connection pool for each target in a target group.
        :param int max_idle_connections_percent: Controls how actively the proxy closes idle database connections in the connection pool.
        :param Sequence[str] session_pinning_filters: Each item in the list represents a class of SQL operations that normally cause all later statements in a session using a proxy to be pinned to the same underlying database connection.
        """
        if connection_borrow_timeout is not None:
            pulumi.set(__self__, "connection_borrow_timeout", connection_borrow_timeout)
        if init_query is not None:
            pulumi.set(__self__, "init_query", init_query)
        if max_connections_percent is not None:
            pulumi.set(__self__, "max_connections_percent", max_connections_percent)
        if max_idle_connections_percent is not None:
            pulumi.set(__self__, "max_idle_connections_percent", max_idle_connections_percent)
        if session_pinning_filters is not None:
            pulumi.set(__self__, "session_pinning_filters", session_pinning_filters)

    @property
    @pulumi.getter(name="connectionBorrowTimeout")
    def connection_borrow_timeout(self) -> Optional[int]:
        """
        The number of seconds for a proxy to wait for a connection to become available in the connection pool.
        """
        return pulumi.get(self, "connection_borrow_timeout")

    @property
    @pulumi.getter(name="initQuery")
    def init_query(self) -> Optional[str]:
        """
        One or more SQL statements for the proxy to run when opening each new database connection.
        """
        return pulumi.get(self, "init_query")

    @property
    @pulumi.getter(name="maxConnectionsPercent")
    def max_connections_percent(self) -> Optional[int]:
        """
        The maximum size of the connection pool for each target in a target group.
        """
        return pulumi.get(self, "max_connections_percent")

    @property
    @pulumi.getter(name="maxIdleConnectionsPercent")
    def max_idle_connections_percent(self) -> Optional[int]:
        """
        Controls how actively the proxy closes idle database connections in the connection pool.
        """
        return pulumi.get(self, "max_idle_connections_percent")

    @property
    @pulumi.getter(name="sessionPinningFilters")
    def session_pinning_filters(self) -> Optional[Sequence[str]]:
        """
        Each item in the list represents a class of SQL operations that normally cause all later statements in a session using a proxy to be pinned to the same underlying database connection.
        """
        return pulumi.get(self, "session_pinning_filters")


@pulumi.output_type
class DBSecurityGroupIngress(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "cIDRIP":
            suggest = "c_idrip"
        elif key == "eC2SecurityGroupId":
            suggest = "e_c2_security_group_id"
        elif key == "eC2SecurityGroupName":
            suggest = "e_c2_security_group_name"
        elif key == "eC2SecurityGroupOwnerId":
            suggest = "e_c2_security_group_owner_id"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in DBSecurityGroupIngress. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        DBSecurityGroupIngress.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        DBSecurityGroupIngress.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 c_idrip: Optional[str] = None,
                 e_c2_security_group_id: Optional[str] = None,
                 e_c2_security_group_name: Optional[str] = None,
                 e_c2_security_group_owner_id: Optional[str] = None):
        if c_idrip is not None:
            pulumi.set(__self__, "c_idrip", c_idrip)
        if e_c2_security_group_id is not None:
            pulumi.set(__self__, "e_c2_security_group_id", e_c2_security_group_id)
        if e_c2_security_group_name is not None:
            pulumi.set(__self__, "e_c2_security_group_name", e_c2_security_group_name)
        if e_c2_security_group_owner_id is not None:
            pulumi.set(__self__, "e_c2_security_group_owner_id", e_c2_security_group_owner_id)

    @property
    @pulumi.getter(name="cIDRIP")
    def c_idrip(self) -> Optional[str]:
        return pulumi.get(self, "c_idrip")

    @property
    @pulumi.getter(name="eC2SecurityGroupId")
    def e_c2_security_group_id(self) -> Optional[str]:
        return pulumi.get(self, "e_c2_security_group_id")

    @property
    @pulumi.getter(name="eC2SecurityGroupName")
    def e_c2_security_group_name(self) -> Optional[str]:
        return pulumi.get(self, "e_c2_security_group_name")

    @property
    @pulumi.getter(name="eC2SecurityGroupOwnerId")
    def e_c2_security_group_owner_id(self) -> Optional[str]:
        return pulumi.get(self, "e_c2_security_group_owner_id")


@pulumi.output_type
class DBSecurityGroupTag(dict):
    def __init__(__self__, *,
                 key: str,
                 value: str):
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> str:
        return pulumi.get(self, "key")

    @property
    @pulumi.getter
    def value(self) -> str:
        return pulumi.get(self, "value")


@pulumi.output_type
class DBSubnetGroupTag(dict):
    """
    A key-value pair to associate with a resource.
    """
    def __init__(__self__, *,
                 key: str,
                 value: str):
        """
        A key-value pair to associate with a resource.
        :param str key: The key name of the tag. You can specify a value that is 1 to 128 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -. 
        :param str value: The value for the tag. You can specify a value that is 0 to 256 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -. 
        """
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> str:
        """
        The key name of the tag. You can specify a value that is 1 to 128 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -. 
        """
        return pulumi.get(self, "key")

    @property
    @pulumi.getter
    def value(self) -> str:
        """
        The value for the tag. You can specify a value that is 0 to 256 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -. 
        """
        return pulumi.get(self, "value")


@pulumi.output_type
class EventSubscriptionTag(dict):
    """
    A key-value pair to associate with a resource.
    """
    def __init__(__self__, *,
                 key: str,
                 value: str):
        """
        A key-value pair to associate with a resource.
        :param str key: The key name of the tag. You can specify a value that is 1 to 128 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        :param str value: The value for the tag. You can specify a value that is 0 to 256 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        """
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> str:
        """
        The key name of the tag. You can specify a value that is 1 to 128 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        """
        return pulumi.get(self, "key")

    @property
    @pulumi.getter
    def value(self) -> str:
        """
        The value for the tag. You can specify a value that is 0 to 256 Unicode characters in length and cannot be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.
        """
        return pulumi.get(self, "value")


@pulumi.output_type
class OptionGroupOptionConfiguration(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "optionName":
            suggest = "option_name"
        elif key == "dBSecurityGroupMemberships":
            suggest = "d_b_security_group_memberships"
        elif key == "optionSettings":
            suggest = "option_settings"
        elif key == "optionVersion":
            suggest = "option_version"
        elif key == "vpcSecurityGroupMemberships":
            suggest = "vpc_security_group_memberships"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in OptionGroupOptionConfiguration. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        OptionGroupOptionConfiguration.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        OptionGroupOptionConfiguration.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 option_name: str,
                 d_b_security_group_memberships: Optional[Sequence[str]] = None,
                 option_settings: Optional[Sequence['outputs.OptionGroupOptionSetting']] = None,
                 option_version: Optional[str] = None,
                 port: Optional[int] = None,
                 vpc_security_group_memberships: Optional[Sequence[str]] = None):
        pulumi.set(__self__, "option_name", option_name)
        if d_b_security_group_memberships is not None:
            pulumi.set(__self__, "d_b_security_group_memberships", d_b_security_group_memberships)
        if option_settings is not None:
            pulumi.set(__self__, "option_settings", option_settings)
        if option_version is not None:
            pulumi.set(__self__, "option_version", option_version)
        if port is not None:
            pulumi.set(__self__, "port", port)
        if vpc_security_group_memberships is not None:
            pulumi.set(__self__, "vpc_security_group_memberships", vpc_security_group_memberships)

    @property
    @pulumi.getter(name="optionName")
    def option_name(self) -> str:
        return pulumi.get(self, "option_name")

    @property
    @pulumi.getter(name="dBSecurityGroupMemberships")
    def d_b_security_group_memberships(self) -> Optional[Sequence[str]]:
        return pulumi.get(self, "d_b_security_group_memberships")

    @property
    @pulumi.getter(name="optionSettings")
    def option_settings(self) -> Optional[Sequence['outputs.OptionGroupOptionSetting']]:
        return pulumi.get(self, "option_settings")

    @property
    @pulumi.getter(name="optionVersion")
    def option_version(self) -> Optional[str]:
        return pulumi.get(self, "option_version")

    @property
    @pulumi.getter
    def port(self) -> Optional[int]:
        return pulumi.get(self, "port")

    @property
    @pulumi.getter(name="vpcSecurityGroupMemberships")
    def vpc_security_group_memberships(self) -> Optional[Sequence[str]]:
        return pulumi.get(self, "vpc_security_group_memberships")


@pulumi.output_type
class OptionGroupOptionSetting(dict):
    def __init__(__self__, *,
                 name: Optional[str] = None,
                 value: Optional[str] = None):
        if name is not None:
            pulumi.set(__self__, "name", name)
        if value is not None:
            pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[str]:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def value(self) -> Optional[str]:
        return pulumi.get(self, "value")


@pulumi.output_type
class OptionGroupTag(dict):
    def __init__(__self__, *,
                 key: str,
                 value: str):
        pulumi.set(__self__, "key", key)
        pulumi.set(__self__, "value", value)

    @property
    @pulumi.getter
    def key(self) -> str:
        return pulumi.get(self, "key")

    @property
    @pulumi.getter
    def value(self) -> str:
        return pulumi.get(self, "value")


