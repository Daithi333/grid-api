import enum


class FilterType(enum.Enum):
    NUMBER = 'number'
    TEXT = 'text'
    DATE = 'date'


class FilterOperator(enum.Enum):
    AND = 'AND'
    OR = 'OR'


class ConditionOperator(enum.Enum):
    EQUALS = 'equals'
    NOT_EQUAL = 'notEqual'
    CONTAINS = 'contains'
    NOT_CONTAINS = 'notContains'
    STARTS_WITH = 'startsWith'
    ENDS_WITH = 'endsWith'
    LESS_THAN = 'lessThan'
    LESS_THAN_OR_EQUAL = 'lessThanOrEqual'
    GREATER_THAN = 'greaterThan'
    GREATER_THAN_OR_EQUAL = 'greaterThanOrEqual'
    IN_RANGE = 'inRange'
    BLANK = 'blank'
    NOT_BLANK = 'notBlank'
    EMPTY = 'empty'


class LookupOperator(enum.Enum):
    EQUALS = 'equals'
    CONTAINS = 'contains'


class ChangeType(enum.Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'


class ApprovalStatus(enum.Enum):
    PENDING = enum.auto()
    APPROVED = enum.auto()
    AUTO_APPROVED = enum.auto()
    CHANGES_REQUESTED = enum.auto()
    REJECTED = enum.auto()
