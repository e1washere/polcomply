"""Path resolver for FA-3 schema files"""

import os
from pathlib import Path


def resolve_fa3_schema() -> Path | None:
    """
    Resolve FA-3 XSD schema file path

    Search order:
    1. Environment variable FA3_SCHEMA_PATH
    2. ./schemas/FA-3.xsd (current directory)
    3. ./backend/schemas/FA-3.xsd (backend directory)
    4. ../backend/schemas/FA-3.xsd (parent/backend)
    5. Package schemas/FA-3.xsd (in polcomply package)

    Returns:
        Path to FA-3.xsd if found, None otherwise
    """

    # 1. Environment variable
    env_path = os.getenv("FA3_SCHEMA_PATH")
    if env_path:
        schema_path = Path(env_path)
        if schema_path.exists() and schema_path.is_file():
            return schema_path

    # Current working directory
    cwd = Path.cwd()

    # 2. ./schemas/FA-3.xsd
    schema_path = cwd / "schemas" / "FA-3.xsd"
    if schema_path.exists():
        return schema_path

    # 3. ./backend/schemas/FA-3.xsd
    schema_path = cwd / "backend" / "schemas" / "FA-3.xsd"
    if schema_path.exists():
        return schema_path

    # 4. ../backend/schemas/FA-3.xsd
    schema_path = cwd.parent / "backend" / "schemas" / "FA-3.xsd"
    if schema_path.exists():
        return schema_path

    # 5. Package schemas (relative to this file)
    package_dir = Path(__file__).parent.parent
    schema_path = package_dir / "schemas" / "FA-3.xsd"
    if schema_path.exists():
        return schema_path

    return None


def get_fa3_schema_or_fail() -> Path:
    """
    Get FA-3 schema path or raise error

    Returns:
        Path to FA-3.xsd

    Raises:
        FileNotFoundError: If schema not found
    """
    schema_path = resolve_fa3_schema()
    if schema_path is None:
        raise FileNotFoundError(
            "FA-3 schema not found. Please:\n"
            "1. Set FA3_SCHEMA_PATH environment variable, or\n"
            "2. Place FA-3.xsd in ./schemas/, ./backend/schemas/, or package schemas/"
        )
    return schema_path
