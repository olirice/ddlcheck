"""Utility functions for DDLCheck."""

from typing import Any, Dict, List, Optional, Union

import pglast


def get_node_type(node: Dict[str, Any]) -> str:
    """Get the type of a parse tree node.

    Args:
        node: A parse tree node

    Returns:
        The type of the node as a string
    """
    # The node type is always the only key in the dict
    return list(node.keys())[0]


def is_alter_table_stmt(node: Dict[str, Any]) -> bool:
    """Check if a node is an ALTER TABLE statement.

    Args:
        node: A parse tree node

    Returns:
        True if the node is an ALTER TABLE statement, False otherwise
    """
    return get_node_type(node) == "AlterTableStmt"


def is_create_index_stmt(node: Dict[str, Any]) -> bool:
    """Check if a node is a CREATE INDEX statement.

    Args:
        node: A parse tree node

    Returns:
        True if the node is a CREATE INDEX statement, False otherwise
    """
    return get_node_type(node) == "IndexStmt"


def is_drop_stmt(node: Dict[str, Any]) -> bool:
    """Check if a node is a DROP statement.

    Args:
        node: A parse tree node

    Returns:
        True if the node is a DROP statement, False otherwise
    """
    return get_node_type(node) == "DropStmt"


def is_update_stmt(node: Dict[str, Any]) -> bool:
    """Check if a node is an UPDATE statement.

    Args:
        node: A parse tree node

    Returns:
        True if the node is an UPDATE statement, False otherwise
    """
    return get_node_type(node) == "UpdateStmt"


def is_truncate_stmt(node: Dict[str, Any]) -> bool:
    """Check if a node is a TRUNCATE statement.

    Args:
        node: A parse tree node

    Returns:
        True if the node is a TRUNCATE statement, False otherwise
    """
    return get_node_type(node) == "TruncateStmt"


def is_rename_stmt(node: Dict[str, Any]) -> bool:
    """Check if a node is a RENAME statement.

    Args:
        node: A parse tree node

    Returns:
        True if the node is a RENAME statement, False otherwise
    """
    return get_node_type(node) == "RenameStmt"


def get_alter_table_commands(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get the commands from an ALTER TABLE statement.

    Args:
        node: An ALTER TABLE statement node

    Returns:
        List of command nodes
    """
    if not is_alter_table_stmt(node):
        return []

    alter_table_stmt = node["AlterTableStmt"]
    cmds = getattr(alter_table_stmt, "cmds", [])

    # Convert each command object to a dict for consistent handling
    return [{"AlterTableCmd": cmd} for cmd in cmds]


def get_alter_command_type(cmd_node: Dict[str, Any]) -> int:
    """Get the type of an ALTER TABLE command.

    Args:
        cmd_node: An ALTER TABLE command node

    Returns:
        The type of the command
    """
    cmd = cmd_node.get("AlterTableCmd")
    return getattr(cmd, "subtype", 0)


def has_where_clause(update_node: Dict[str, Any]) -> bool:
    """Check if an UPDATE statement has a WHERE clause.

    Args:
        update_node: An UPDATE statement node

    Returns:
        True if the statement has a WHERE clause, False otherwise
    """
    if not is_update_stmt(update_node):
        return True  # Not an UPDATE, so return True

    stmt = update_node["UpdateStmt"]
    return hasattr(stmt, "whereClause") and stmt.whereClause is not None


def is_concurrent_index(index_node: Dict[str, Any]) -> bool:
    """Check if a CREATE INDEX statement has the CONCURRENTLY option.

    Args:
        index_node: A CREATE INDEX statement node

    Returns:
        True if the statement has the CONCURRENTLY option, False otherwise
    """
    if not is_create_index_stmt(index_node):
        return True  # Not a CREATE INDEX, so return True

    stmt = index_node["IndexStmt"]
    return getattr(stmt, "concurrent", False)
