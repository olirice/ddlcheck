#!/usr/bin/env python3

import sys
from pathlib import Path

import pglast
from pglast.enums import AlterTableType

def print_obj_details(obj, indent=0):
    """Print details about an object recursively."""
    prefix = " " * indent
    
    print(f"{prefix}Type: {type(obj)}")
    
    if hasattr(obj, "__dict__"):
        attrs = vars(obj)
        for attr_name, attr_value in attrs.items():
            if attr_name.startswith("_"):
                continue
                
            print(f"{prefix}{attr_name}: ", end="")
            
            if isinstance(attr_value, (str, int, bool)) or attr_value is None:
                print(attr_value)
            elif isinstance(attr_value, (list, tuple)):
                print(f"[List/Tuple with {len(attr_value)} items]")
                if len(attr_value) > 0:
                    print_obj_details(attr_value[0], indent + 2)
            else:
                print("")
                print_obj_details(attr_value, indent + 2)
    elif isinstance(obj, (list, tuple)):
        print(f"{prefix}[List/Tuple with {len(obj)} items]")
        if len(obj) > 0:
            print_obj_details(obj[0], indent + 2)
    else:
        print(f"{prefix}Value: {obj}")

def main():
    """Print parse tree for a SQL file."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <sql_file>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r") as f:
        sql = f.read()

    # Parse the SQL
    parsed = pglast.parse_sql(sql)
    print(f"Number of statements: {len(parsed)}")
    
    # Print available AlterTableType values
    print("\nAlterTableType values:")
    for name in dir(AlterTableType):
        if not name.startswith("_"):
            value = getattr(AlterTableType, name)
            print(f"  {name}: {value}")
    
    # Print the first statement in detail
    first_stmt = parsed[0]
    print("\nFirst statement:")
    print_obj_details(first_stmt)
    
    # Print the actual statement in the first RawStmt
    print("\nActual statement in first RawStmt:")
    print_obj_details(first_stmt.stmt)

if __name__ == "__main__":
    main() 