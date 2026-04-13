# Jinja4Config

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Generate configuration files from Jinja2 templates and YAML/JSON data files.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Template Syntax](#template-syntax)
- [Config File Features](#config-file-features)
- [Docker Usage](#docker-usage)
- [Example: Nginx Config](#example-nginx-config)

## Installation

**From source:**
```bash
git clone https://github.com/flavien-chenu/jinja4config.git
cd jinja4config
pip install -r requirements.txt
```

**Docker:**
```bash
docker pull ghcr.io/flavien-chenu/jinja4config:latest
```

## Quick Start

**`config.yaml`:**
```yaml
app:
  name: MyApp
  version: 1.0.0
database:
  host: localhost
  port: 5432
  name: mydb
```

**`app-config.json.j2`:**
```jinja
{
  "application": "{{ app.name }}",
  "version": "{{ app.version }}",
  "database_url": "postgresql://{{ database.host }}:{{ database.port }}/{{ database.name }}"
}
```

**Run:**
```bash
python build.py --config config.yaml app-config.json.j2
```

**Output (`app-config.json`):**
```json
{
  "application": "MyApp",
  "version": "1.0.0",
  "database_url": "postgresql://localhost:5432/mydb"
}
```

The output filename is the template name with `.j2` removed.

## Usage

```bash
python build.py --config <config-file> <template-files...>
```

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | Path to config file (YAML or JSON) — **required** |
| `--output-dir` | `-o` | Output directory for generated files |
| `--schema` | `-s` | JSON schema file for config validation |

**Examples:**
```bash
# Single template
python build.py --config config.yaml nginx.conf.j2

# Multiple templates
python build.py --config config.yaml app.conf.j2 db.conf.j2

# With output directory
python build.py --config config.yaml --output-dir ./output app.conf.j2

# With schema validation
python build.py --config config.yaml --schema schema.json app.conf.j2
```

## Template Syntax

Standard Jinja2 syntax — variables, conditionals, loops, and comments all work as expected.

### Custom Filters

#### `env` — Read environment variables
```jinja
{{ 'DATABASE_HOST' | env('localhost') }}  {# with default #}
{{ 'API_KEY' | env }}                     {# returns "" if not set #}
```

#### `default` — Fallback for empty/None values
```jinja
{{ some_variable | default('fallback') }}
```

#### `split` — Split a string into a list
```jinja
{% for item in 'a,b,c' | split(',') %}{{ item }}{% endfor %}
```

#### `join_path` — Join path components
```jinja
{{ ['usr', 'local', 'bin'] | join_path }}  {# Output: usr/local/bin #}
```

### Global Functions and Variables

```jinja
{{ now() }}    {# Current datetime: 2025-10-25 14:30:45 #}
{{ today() }}  {# Current date: 2025-10-25 #}
{{ env.PATH }} {# Direct access to environment variables #}
```

## Config File Features

### Variable Resolution

Config values can reference other config values using `{{ }}` syntax:

```yaml
base_url: "https://api.example.com"
api:
  v1_url: "{{ base_url }}/v1"
  v2_url: "{{ base_url }}/v2"
endpoints:
  users: "{{ api.v1_url }}/users"
  products: "{{ api.v2_url }}/products"
```

Only simple dot-notation references are resolved (e.g. `{{ api.v1_url }}`). Filter expressions like `{{ 'VAR' | env('default') }}` are left for Jinja2 to handle at render time.

### Schema Validation

Validate your config against a JSON schema before rendering:

**`schema.json`:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["app"],
  "properties": {
    "app": {
      "type": "object",
      "required": ["name", "port"],
      "properties": {
        "name": {"type": "string"},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535}
      }
    }
  }
}
```

```bash
python build.py --config config.yaml --schema schema.json app.conf.j2
```

## Docker Usage

```bash
# Basic usage — mount your project to /workspace
docker run -v $(pwd):/workspace ghcr.io/flavien-chenu/jinja4config \
  --config config.yaml template.conf.j2

# With environment variables
docker run -v $(pwd):/workspace \
  -e DATABASE_HOST=prod-db.example.com \
  -e API_KEY=secret123 \
  ghcr.io/flavien-chenu/jinja4config \
  --config config.yaml app.conf.j2
```

## Example: Nginx Config

**`config.yaml`:**
```yaml
server:
  name: example.com
  port: 80
  root: /var/www/html
upstream:
  backend: 127.0.0.1:8080
ssl:
  enabled: true
  cert: /etc/ssl/certs/example.com.crt
  key: /etc/ssl/private/example.com.key
```

**`nginx.conf.j2`:**
```jinja
server {
    listen {{ server.port }};
    server_name {{ server.name }};
    root {{ server.root }};

    {% if ssl.enabled %}
    listen 443 ssl;
    ssl_certificate {{ ssl.cert }};
    ssl_certificate_key {{ ssl.key }};
    {% endif %}

    location / {
        proxy_pass http://{{ upstream.backend }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## License

MIT — see [LICENSE](LICENSE).
