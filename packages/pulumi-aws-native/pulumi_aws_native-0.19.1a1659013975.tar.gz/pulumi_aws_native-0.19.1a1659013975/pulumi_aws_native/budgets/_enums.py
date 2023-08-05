# coding=utf-8
# *** WARNING: this file was generated by the Pulumi SDK Generator. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

from enum import Enum

__all__ = [
    'BudgetsActionActionThresholdType',
    'BudgetsActionActionType',
    'BudgetsActionApprovalModel',
    'BudgetsActionNotificationType',
    'BudgetsActionSsmActionDefinitionSubtype',
    'BudgetsActionSubscriberType',
]


class BudgetsActionActionThresholdType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    ABSOLUTE_VALUE = "ABSOLUTE_VALUE"


class BudgetsActionActionType(str, Enum):
    APPLY_IAM_POLICY = "APPLY_IAM_POLICY"
    APPLY_SCP_POLICY = "APPLY_SCP_POLICY"
    RUN_SSM_DOCUMENTS = "RUN_SSM_DOCUMENTS"


class BudgetsActionApprovalModel(str, Enum):
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"


class BudgetsActionNotificationType(str, Enum):
    ACTUAL = "ACTUAL"
    FORECASTED = "FORECASTED"


class BudgetsActionSsmActionDefinitionSubtype(str, Enum):
    STOP_EC2_INSTANCES = "STOP_EC2_INSTANCES"
    STOP_RDS_INSTANCES = "STOP_RDS_INSTANCES"


class BudgetsActionSubscriberType(str, Enum):
    SNS = "SNS"
    EMAIL = "EMAIL"
