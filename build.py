#!/usr/bin/env python3
"""
Configuration builder with Jinja2 templating support.
Supports JSON/YAML configs, advanced templating, validation, and more.
"""

import argparse
import json
import os
import sys
import re
from pathlib import Path
from typing import Any, Dict, List

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jsonschema import validate, ValidationError


# Colors for terminal output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def _env_filter(key: str, default: str = None) -> str:
    """Get environment variable with optional default"""
    return os.getenv(key, default or "")


def _default_filter(value: Any, default: Any) -> Any:
    """Return default if value is None or empty"""
    return value if value not in (None, "", []) else default


def _resolve_recursive_variables(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve recursive variable references in configuration.
    Replaces {{ variable }} with corresponding value from config.
    Similar to the old $(variable) resolution but using Jinja2 syntax.
    """

    def get_nested_value(path: str, obj: dict) -> Any:
        """Get nested value from dict using dot notation"""
        keys = path.split(".")
        result = obj
        for key in keys:
            if isinstance(result, dict) and key in result:
                result = result[key]
            else:
                return None
        return result

    def resolve_value(value: Any, context: Dict[str, Any], depth: int = 0) -> Any:
        """Recursively resolve variables in a value"""
        if depth > 10:  # Prevent infinite recursion
            return value

        if isinstance(value, str):
            # Look for {{ variable }} patterns
            def replace_var(match):
                var_path = match.group(1).strip()
                # Handle filter expressions like 'VAR' | env('default')
                if '|' in var_path:
                    # For complex expressions, let Jinja2 handle them later
                    return match.group(0)

                try:
                    resolved = get_nested_value(var_path, context)
                    if resolved is not None:
                        return str(resolved)
                except:
                    pass
                return match.group(0)

            # Continue resolving until no more changes
            resolved = value
            max_iterations = 10
            iteration = 0

            while iteration < max_iterations:
                new_resolved = re.sub(r'\{\{\s*([^}|]+?)\s*\}\}', replace_var, resolved)
                if new_resolved == resolved:
                    break
                resolved = new_resolved
                iteration += 1

            return resolved
        elif isinstance(value, dict):
            return {k: resolve_value(v, context, depth + 1) for k, v in value.items()}
        elif isinstance(value, list):
            return [resolve_value(item, context, depth + 1) for item in value]
        else:
            return value

    return resolve_value(config, config)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON or YAML file and resolve recursive references"""
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_file, 'r', encoding='utf-8') as f:
        if config_file.suffix.lower() in ['.yml', '.yaml']:
            config = yaml.safe_load(f)
        else:
            config = json.load(f)

    # Resolve recursive variable references in config
    return _resolve_recursive_variables(config)


def validate_config(config: Dict[str, Any], schema_path: str = None) -> bool:
    """Validate configuration against JSON schema"""
    if not schema_path:
        return True

    schema_file = Path(schema_path)
    if not schema_file.exists():
        print(f"{Colors.YELLOW}⚠{Colors.END} Schema file not found: {schema_path}")
        return True

    with open(schema_file, 'r') as f:
        schema = json.load(f)

    try:
        validate(instance=config, schema=schema)
        return True
    except ValidationError as e:
        print(f"{Colors.RED}✗{Colors.END} Config validation failed: {e.message}")
        return False


class ConfigBuilder:
    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or Path.cwd())
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.base_dir),
            undefined=StrictUndefined,  # Fail on undefined variables
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        self.jinja_env.filters['env'] = _env_filter
        self.jinja_env.filters['default'] = _default_filter
        self.jinja_env.filters['split'] = lambda s, sep=',': s.split(sep) if s else []
        self.jinja_env.filters['join_path'] = lambda parts: '/'.join(str(p) for p in parts if p)

        # Add custom global functions
        from datetime import datetime
        self.jinja_env.globals['now'] = lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.jinja_env.globals['today'] = lambda: datetime.now().strftime('%Y-%m-%d')

        # Make env available globally as well
        self.jinja_env.globals['env'] = os.environ

    def render_template(self, template_path: str, config: Dict[str, Any]) -> str:
        """Render template with Jinja2"""
        template_file = Path(template_path)

        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        # Read template content directly
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Create template from string
        template = self.jinja_env.from_string(template_content)

        # First render with config
        rendered = template.render(**config, env=os.environ)

        # Second pass: resolve any remaining Jinja2 expressions in the output
        # This handles cases where config values contain Jinja2 expressions
        try:
            final_template = self.jinja_env.from_string(rendered)
            final_rendered = final_template.render(**config, env=os.environ)
            return final_rendered
        except:
            # If second pass fails, return first pass result
            return rendered

    def build_templates(self, config_path: str, template_paths: List[str],
                        output_dir: str = None, schema_path: str = None) -> Dict[str, Any]:
        """Build all templates with given config"""
        # Load and validate config
        config = load_config(config_path)

        if schema_path and not validate_config(config, schema_path):
            return {"success": [], "errors": ["Config validation failed"]}

        success = []
        errors = []

        for template_path in template_paths:
            try:
                # Render template
                rendered_content = self.render_template(template_path, config)

                # Determine output path
                template_file = Path(template_path)

                # Smart output name generation
                output_name = template_file.name
                if output_name.endswith('.j2'):
                    output_name = output_name[:-3]  # Remove .j2
                elif output_name.endswith('.template'):
                    output_name = output_name.replace('.template', '')

                if output_dir:
                    output_file = Path(output_dir) / output_name
                else:
                    output_file = template_file.with_name(output_name)

                # Ensure output directory exists
                output_file.parent.mkdir(parents=True, exist_ok=True)

                # Write rendered content
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(rendered_content)

                success.append(str(output_file))

            except Exception as e:
                errors.append(f"{template_path}: {str(e)}")

        return {"success": success, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description="Build configuration templates with Jinja2")
    parser.add_argument("templates", nargs="*", help="Template files to process")
    parser.add_argument("--config", "-c", required=True,
                        help="Config file path (required, YAML or JSON)")
    parser.add_argument("--output-dir", "-o", help="Output directory for rendered files")
    parser.add_argument("--schema", "-s", help="JSON schema file for validation")
    parser.add_argument("--watch", "-w", action="store_true",
                        help="Watch files for changes and rebuild")

    args = parser.parse_args()

    # Use provided config path
    config_path = args.config

    # Verify config file exists
    if not Path(config_path).exists():
        print(f"{Colors.RED}✗{Colors.END} Config file not found: {config_path}")
        sys.exit(1)

    # Create builder with current working directory as base
    builder = ConfigBuilder(str(Path.cwd()))

    # Build templates
    try:
        result = builder.build_templates(
            config_path=config_path,
            template_paths=args.templates,
            output_dir=args.output_dir,
            schema_path=args.schema
        )

        # Print results
        for success_file in result["success"]:
            print(f"{Colors.GREEN}✔{Colors.END} {success_file}")

        if result["errors"]:
            print(f"\n{Colors.RED}Errors:{Colors.END}")
            for error in result["errors"]:
                print(f"{Colors.RED}✗{Colors.END} {error}")
            print(
                f"\n{Colors.RED}Done with {Colors.BOLD}{len(result['errors'])}{Colors.END}{Colors.RED} error(s){Colors.END}")
            sys.exit(1)
        else:
            print(f"\n{Colors.BOLD}{Colors.GREEN}Done{Colors.END}")

    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
