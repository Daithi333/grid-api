from sqlalchemy import Enum, String

from enums import ChangeType, FilterType, ConditionOperator, LookupOperator, FilterOperator, ApprovalStatus, Role

UUID_STRING = String(length=22)

ENUM_CHANGE_TYPE = Enum(ChangeType, name='change_type')
ENUM_FILTER_TYPE = Enum(FilterType, name='filter_type')
ENUM_FILTER_OPERATOR = Enum(FilterOperator, name='filter_operator')
ENUM_CONDITION_OPERATOR = Enum(ConditionOperator, name='condition_operator')
ENUM_LOOKUP_OPERATOR = Enum(LookupOperator, name='lookup_operator')
ENUM_APPROVAL_STATUS = Enum(ApprovalStatus, name='approval_status')
ENUM_ROLE = Enum(Role, name='role')

