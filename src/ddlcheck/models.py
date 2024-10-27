"""Data models for DDLCheck."""

import enum
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import toml

logger = logging.getLogger(__name__)


class SeverityLevel(enum.Enum):
    """Severity level for issues."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    INFO = "INFO"


@dataclass
class Issue:
    """Issue found by a check."""

    check_id: str
    message: str
    line: int
    severity: SeverityLevel
    suggestion: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def __repr__(self) -> str:
        """Return string representation of Issue."""
        return f"Issue(check_id='{self.check_id}', line={self.line}, severity={self.severity.name})"


@dataclass
class Config:
    """Configuration for DDLCheck."""

    excluded_checks: Set[str] = field(default_factory=set)
    check_config: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    severity_overrides: Dict[str, SeverityLevel] = field(default_factory=dict)

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from a file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Loaded configuration
        """
        # Default config
        config = cls()

        if not config_path:
            # Look for .ddlcheck in current directory
            default_path = Path.cwd() / ".ddlcheck"
            if default_path.exists():
                config_path = default_path

        # If no config file, return default config
        if not config_path or not config_path.exists():
            logger.debug("No config file found, using default configuration")
            return config

        try:
            # Load config from TOML file
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = toml.load(f)

            # Process excluded checks
            if "excluded_checks" in config_data:
                excluded = config_data.pop("excluded_checks")
                if isinstance(excluded, list):
                    config.excluded_checks = set(excluded)
                else:
                    logger.warning(
                        "Invalid format for excluded_checks in config file, expected list"
                    )

            # Process severity overrides
            if "severity" in config_data:
                severity_data = config_data.pop("severity")
                for check_id, level in severity_data.items():
                    try:
                        config.severity_overrides[check_id] = SeverityLevel[level.upper()]
                    except (KeyError, AttributeError):
                        logger.warning(f"Invalid severity level for {check_id}: {level}")

            # Any remaining keys are assumed to be check-specific configs
            for check_id, check_config in config_data.items():
                if isinstance(check_config, dict):
                    config.check_config[check_id] = check_config
                else:
                    logger.warning(f"Invalid config format for check {check_id}, expected dict")

            logger.debug(f"Loaded configuration from {config_path}")
        except Exception as e:
            logger.warning(f"Error loading config file: {e}")

        return config

    def is_check_enabled(self, check_id: str) -> bool:
        """Check if a specific check is enabled.

        Args:
            check_id: ID of the check to check

        Returns:
            True if the check is enabled, False otherwise
        """
        return check_id not in self.excluded_checks

    def get_check_config(self, check_id: str) -> Dict[str, Any]:
        """Get configuration for a specific check.

        Args:
            check_id: ID of the check to get configuration for

        Returns:
            Configuration dict for the check, empty if not found
        """
        return self.check_config.get(check_id, {})

    def get_severity_override(self, check_id: str) -> Optional[SeverityLevel]:
        """Get severity override for a specific check.

        Args:
            check_id: ID of the check to get severity override for

        Returns:
            Severity override for the check, None if not overridden
        """
        return self.severity_overrides.get(check_id)


class CheckResult:
    """Result of running a check on a SQL file."""

    def __init__(self, file_path: Path, issues: Optional[List[Issue]] = None):
        """Initialize a CheckResult.

        Args:
            file_path: Path to the SQL file that was checked
            issues: List of issues found in the file
        """
        self.file_path = file_path
        self.issues = issues or []

    def add_issue(self, issue: Issue) -> None:
        """Add an issue to the result.

        Args:
            issue: Issue to add
        """
        self.issues.append(issue)

    def has_issues(self) -> bool:
        """Check if there are any issues.

        Returns:
            True if there are issues, False otherwise
        """
        return len(self.issues) > 0

    def __repr__(self) -> str:
        """Return string representation of CheckResult."""
        return f"CheckResult(file_path='{self.file_path}', issues={len(self.issues)})"
