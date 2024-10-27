# Installation

DDLCheck requires Python 3.12 or newer. It's designed to be easy to install and integrate into your existing workflows.

## Using pip

You can install DDLCheck using pip:

```bash
pip install ddlcheck
```

This will install DDLCheck and all its dependencies.

## Using Poetry

If you're using Poetry for dependency management:

```bash
poetry add ddlcheck
```

## From Source

To install from source:

```bash
git clone https://github.com/oliverrice/ddlcheck.git
cd ddlcheck
pip install .
```

Or with Poetry:

```bash
git clone https://github.com/oliverrice/ddlcheck.git
cd ddlcheck
poetry install
```

## Verifying Installation

Once installed, verify the installation by running:

```bash
ddlcheck --version
```

You should see the version number of DDLCheck.

## Dependencies

DDLCheck has the following key dependencies:

- **typer**: For command-line interface
- **pglast**: For PostgreSQL SQL parsing (PostgreSQL 17 syntax)
- **rich**: For colored terminal output

These will be automatically installed when you install DDLCheck. 