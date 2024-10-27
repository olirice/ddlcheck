"""Check implementations for DDLCheck."""

from ddlcheck.checks.add_column import AddColumnCheck
from ddlcheck.checks.alter_column_type import AlterColumnTypeCheck
from ddlcheck.checks.create_index import CreateIndexCheck
from ddlcheck.checks.drop_column import DropColumnCheck
from ddlcheck.checks.drop_table import DropTableCheck
from ddlcheck.checks.rename_column import RenameColumnCheck
from ddlcheck.checks.set_not_null import SetNotNullCheck
from ddlcheck.checks.truncate import TruncateCheck
from ddlcheck.checks.update_without_filter import UpdateWithoutFilterCheck

# List of all available checks
ALL_CHECKS = [
    AddColumnCheck,
    AlterColumnTypeCheck,
    CreateIndexCheck,
    DropColumnCheck,
    DropTableCheck,
    RenameColumnCheck,
    SetNotNullCheck,
    TruncateCheck,
    UpdateWithoutFilterCheck,
]

__all__ = [
    "ALL_CHECKS",
    "AddColumnCheck",
    "AlterColumnTypeCheck",
    "CreateIndexCheck",
    "DropColumnCheck",
    "DropTableCheck",
    "RenameColumnCheck",
    "SetNotNullCheck",
    "TruncateCheck",
    "UpdateWithoutFilterCheck",
]
