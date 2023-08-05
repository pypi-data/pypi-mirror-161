# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

from enum import Enum

__all__ = [
    'ApplicationAlarmSeverity',
    'ApplicationComponentMonitoringSettingComponentConfigurationMode',
    'ApplicationEventLevel',
    'ApplicationGroupingType',
    'ApplicationLogEncoding',
    'ApplicationSubComponentTypeConfigurationSubComponentType',
]


class ApplicationAlarmSeverity(str, Enum):
    """
    Indicates the degree of outage when the alarm goes off.
    """
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ApplicationComponentMonitoringSettingComponentConfigurationMode(str, Enum):
    """
    The component monitoring configuration mode.
    """
    DEFAULT = "DEFAULT"
    DEFAULT_WITH_OVERWRITE = "DEFAULT_WITH_OVERWRITE"
    CUSTOM = "CUSTOM"


class ApplicationEventLevel(str, Enum):
    """
    The level of event to log.
    """
    INFORMATION = "INFORMATION"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    VERBOSE = "VERBOSE"


class ApplicationGroupingType(str, Enum):
    """
    The grouping type of the application
    """
    ACCOUNT_BASED = "ACCOUNT_BASED"


class ApplicationLogEncoding(str, Enum):
    """
    The type of encoding of the logs to be monitored.
    """
    UTF8 = "utf-8"
    UTF16 = "utf-16"
    ASCII = "ascii"


class ApplicationSubComponentTypeConfigurationSubComponentType(str, Enum):
    """
    The sub component type.
    """
    AWSEC2_INSTANCE = "AWS::EC2::Instance"
    AWSEC2_VOLUME = "AWS::EC2::Volume"
