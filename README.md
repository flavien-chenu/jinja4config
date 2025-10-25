# Jinja4Config 🔧

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-available-blue.svg)](https://hub.docker.com)

A powerful and flexible configuration builder using Jinja2 templating engine. Transform your configuration templates into real configurations with YAML/JSON data, environment variables, and advanced templating features.

## 🌟 Features

- **🎯 Jinja2 Templating**: Full power of Jinja2 templates with custom filters and functions
- **📦 Multiple Formats**: Support for JSON and YAML configuration files
- **🔄 Variable Resolution**: Recursive variable resolution within configuration files
- **✅ Schema Validation**: Optional JSON schema validation for configurations
- **🌍 Environment Variables**: Direct access to environment variables in templates
- **🐳 Docker Support**: Ready-to-use Docker image for isolated builds
- **🎨 Beautiful Output**: Colored terminal output with clear success/error indicators
- **🔧 Custom Filters**: Built-in filters for common operations (env, default, split, join_path)
- **📅 Date/Time Functions**: Built-in functions for timestamps (now, today)

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Template Syntax](#template-syntax)
- [Advanced Features](#advanced-features)
- [Docker Usage](#docker-usage)
- [Use Cases](#use-cases)
- [Examples](#examples)
- [Contributing](#contributing)

## 🚀 Installation

### Using pip (Python)

```bash
pip install -r requirements.txt
```

### Using Docker

```bash
docker pull ghcr.io/flavienchenu/jinja4config:latest
```

### From Source

```bash
git clone https://github.com/flavienchenu/jinja4config.git
cd jinja4config
pip install -r requirements.txt
chmod +x build.py
```

## ⚡ Quick Start

1. **Create a configuration file** (`config.yaml`):

```yaml
app:
  name: MyApp
  version: 1.0.0
  environment: production
database:
  host: localhost
  port: 5432
  name: mydb
```

2. **Create a template** (`app-config.json.j2`):

```jinja
{
  "application": "{{ app.name }}",
  "version": "{{ app.version }}",
  "environment": "{{ app.environment }}",
  "database_url": "postgresql://{{ database.host }}:{{ database.port }}/{{ database.name }}"
}
```

3. **Build the configuration**:

```bash
python build.py --config config.yaml app-config.json.j2
```

4. **Result** (`app-config.json`):

```json
{
  "application": "MyApp",
  "version": "1.0.0",
  "environment": "production",
  "database_url": "postgresql://localhost:5432/mydb"
}
```

## 📖 Usage

### Basic Command

```bash
python build.py --config <config-file> <template-files...>
```

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config` | `-c` | **Required**. Path to configuration file (YAML or JSON) |
| `--output-dir` | `-o` | Output directory for generated files (optional) |
| `--schema` | `-s` | JSON schema file for configuration validation (optional) |
| `--watch` | `-w` | Watch files for changes and auto-rebuild (planned feature) |

### Examples

**Single template:**
```bash
python build.py --config config.yaml nginx.conf.j2
```

**Multiple templates:**
```bash
python build.py --config config.yaml app.conf.j2 db.conf.j2 api.conf.j2
```

**With output directory:**
```bash
python build.py --config config.yaml --output-dir ./output app.conf.j2
```

**With schema validation:**
```bash
python build.py --config config.yaml --schema schema.json app.conf.j2
```

## ⚙️ Configuration

### Configuration File Format

Jinja4Config supports both YAML and JSON configuration files.

**YAML Example (`config.yaml`):**
```yaml
environment: production
app:
  name: MyService
  port: 8080
  log_level: INFO
features:
  - authentication
  - logging
  - monitoring
secrets:
  api_key: "{{ 'API_KEY' | env('default-key') }}"
```

**JSON Example (`config.json`):**
```json
{
  "environment": "production",
  "app": {
    "name": "MyService",
    "port": 8080,
    "log_level": "INFO"
  },
  "features": ["authentication", "logging", "monitoring"],
  "secrets": {
    "api_key": "{{ 'API_KEY' | env('default-key') }}"
  }
}
```

### Variable Resolution

Jinja4Config automatically resolves recursive variable references in your configuration:

```yaml
base_url: "https://api.example.com"
api:
  v1_url: "{{ base_url }}/v1"
  v2_url: "{{ base_url }}/v2"
endpoints:
  users: "{{ api.v1_url }}/users"
  products: "{{ api.v2_url }}/products"
```

## 📝 Template Syntax

### Basic Jinja2 Syntax

**Variables:**
```jinja
{{ variable_name }}
{{ nested.variable.path }}
```

**Conditionals:**
```jinja
{% if environment == 'production' %}
production_setting = true
{% else %}
production_setting = false
{% endif %}
```

**Loops:**
```jinja
{% for feature in features %}
- {{ feature }}
{% endfor %}
```

**Comments:**
```jinja
{# This is a comment and won't appear in output #}
```

### Custom Filters

#### `env` - Environment Variables
Get environment variables with optional defaults:
```jinja
{{ 'DATABASE_HOST' | env('localhost') }}
{{ 'API_KEY' | env }}
```

#### `default` - Default Values
Return default if value is empty or None:
```jinja
{{ some_variable | default('default_value') }}
```

#### `split` - String Splitting
Split strings into lists:
```jinja
{% for item in 'a,b,c' | split(',') %}
  - {{ item }}
{% endfor %}
```

#### `join_path` - Path Joining
Join path components:
```jinja
{{ ['usr', 'local', 'bin'] | join_path }}  {# Output: usr/local/bin #}
```

### Global Functions

#### `now()` - Current Timestamp
```jinja
Generated at: {{ now() }}  {# Output: 2025-10-25 14:30:45 #}
```

#### `today()` - Current Date
```jinja
Date: {{ today() }}  {# Output: 2025-10-25 #}
```

#### `env` - Environment Dictionary
Direct access to all environment variables:
```jinja
PATH: {{ env.PATH }}
HOME: {{ env.HOME }}
```

## 🎓 Advanced Features

### 1. Schema Validation

Create a JSON schema to validate your configuration:

**schema.json:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "app": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535}
      },
      "required": ["name", "port"]
    }
  },
  "required": ["app"]
}
```

**Usage:**
```bash
python build.py --config config.yaml --schema schema.json app.conf.j2
```

### 2. Multi-Stage Variable Resolution

Variables are resolved in multiple passes, allowing complex interdependencies:

```yaml
domain: example.com
subdomain: api
full_domain: "{{ subdomain }}.{{ domain }}"  # Resolves to api.example.com
url: "https://{{ full_domain }}"  # Resolves to https://api.example.com
```

### 3. Template Inheritance

Use Jinja2's template inheritance for complex configurations:

**base.conf.j2:**
```jinja
# Base Configuration
server_name {{ app.name }};

{% block locations %}
{% endblock %}
```

**app.conf.j2:**
```jinja
{% extends "base.conf.j2" %}

{% block locations %}
location / {
    proxy_pass {{ backend_url }};
}
{% endblock %}
```

### 4. Environment-Specific Configs

```yaml
environments:
  development:
    debug: true
    db_host: localhost
  production:
    debug: false
    db_host: "{{ 'DB_HOST' | env('prod-db.example.com') }}"

# Select environment
current: "{{ 'ENV' | env('development') }}"
config: "{{ environments[current] }}"
```

## 🐳 Docker Usage

### Pull the Image

```bash
docker pull flavienchenu/jinja4config:latest
```

### Basic Usage

Mount your project directory and run:

```bash
docker run -v $(pwd):/workspace flavienchenu/jinja4config \
  --config config.yaml \
  template.conf.j2
```

### With Environment Variables

```bash
docker run -v $(pwd):/workspace \
  -e DATABASE_HOST=prod-db.example.com \
  -e API_KEY=secret123 \
  ghcr.io/flavienchenu/jinja4config \
  --config config.yaml \
  app.conf.j2
```

### Docker Compose Example

```yaml
version: '3.8'
services:
  config-builder:
    image: flavienchenu/jinja4config:latest
    volumes:
      - ./config:/workspace
    environment:
      - ENV=production
      - DATABASE_HOST=postgres
      - API_KEY=${API_KEY}
    command: --config config.yaml nginx.conf.j2 app.conf.j2
```

## 💡 Use Cases

### 1. Multi-Environment Deployments

Generate different configurations for dev, staging, and production:

```yaml
# environments.yaml
common:
  app_name: MyApp
  log_format: json

development:
  debug: true
  db_host: localhost
  cache_enabled: false

production:
  debug: false
  db_host: "{{ 'DB_HOST' | env }}"
  cache_enabled: true
  cache_ttl: 3600
```

### 2. Microservices Configuration

Manage configurations for multiple services:

```bash
python build.py --config services.yaml \
  api-gateway.conf.j2 \
  auth-service.conf.j2 \
  user-service.conf.j2 \
  notification-service.conf.j2
```

### 3. Infrastructure as Code

Generate Terraform, Kubernetes, or Docker Compose files:

```yaml
# infrastructure.yaml
cluster:
  name: production
  region: us-east-1
  node_count: 3

services:
  - name: web
    replicas: 3
    port: 80
  - name: api
    replicas: 5
    port: 8080
```

### 4. CI/CD Pipeline Configuration

Generate pipeline configs based on project settings:

```yaml
# pipeline.yaml
project: my-app
stages:
  - build
  - test
  - deploy

environments:
  - name: staging
    branch: develop
  - name: production
    branch: main
    requires_approval: true
```

### 5. Application Configuration Management

Centralize application settings:

```yaml
# app-config.yaml
app:
  name: MyApp
  version: 2.1.0

database:
  host: "{{ 'DB_HOST' | env('localhost') }}"
  port: 5432
  name: "{{ 'DB_NAME' | env('myapp') }}"

redis:
  host: "{{ 'REDIS_HOST' | env('localhost') }}"
  port: 6379

api:
  rate_limit: 1000
  timeout: 30
```

## 📚 Examples

### Example 1: Nginx Configuration

**config.yaml:**
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

**nginx.conf.j2:**
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

### Example 2: Docker Compose

**config.yaml:**
```yaml
project_name: myproject
network: mynetwork

services:
  web:
    image: nginx:latest
    port: 80

  app:
    image: myapp:latest
    port: 8080
    env:
      DATABASE_URL: "{{ 'DATABASE_URL' | env }}"

  db:
    image: postgres:14
    port: 5432
    volume: postgres_data
```

**docker-compose.yml.j2:**
```jinja
version: '3.8'

services:
{% for name, service in services.items() %}
  {{ name }}:
    image: {{ service.image }}
    ports:
      - "{{ service.port }}:{{ service.port }}"
    networks:
      - {{ network }}
    {% if service.env is defined %}
    environment:
      {% for key, value in service.env.items() %}
      - {{ key }}={{ value }}
      {% endfor %}
    {% endif %}
    {% if service.volume is defined %}
    volumes:
      - {{ service.volume }}:/var/lib/postgresql/data
    {% endif %}
{% endfor %}

networks:
  {{ network }}:
    driver: bridge

{% if services.db.volume is defined %}
volumes:
  {{ services.db.volume }}:
{% endif %}
```

### Example 3: Kubernetes Deployment

**config.yaml:**
```yaml
app:
  name: myapp
  namespace: production
  replicas: 3
  image: myapp:v1.2.3

container:
  port: 8080
  cpu_request: 100m
  cpu_limit: 500m
  memory_request: 128Mi
  memory_limit: 512Mi

env:
  - name: DATABASE_HOST
    value: "{{ 'DATABASE_HOST' | env }}"
  - name: REDIS_HOST
    value: "{{ 'REDIS_HOST' | env }}"
```

**deployment.yaml.j2:**
```jinja
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ app.name }}
  namespace: {{ app.namespace }}
  labels:
    app: {{ app.name }}
spec:
  replicas: {{ app.replicas }}
  selector:
    matchLabels:
      app: {{ app.name }}
  template:
    metadata:
      labels:
        app: {{ app.name }}
    spec:
      containers:
      - name: {{ app.name }}
        image: {{ app.image }}
        ports:
        - containerPort: {{ container.port }}
        resources:
          requests:
            cpu: {{ container.cpu_request }}
            memory: {{ container.memory_request }}
          limits:
            cpu: {{ container.cpu_limit }}
            memory: {{ container.memory_limit }}
        env:
        {% for env_var in env %}
        - name: {{ env_var.name }}
          value: "{{ env_var.value }}"
        {% endfor %}
---
apiVersion: v1
kind: Service
metadata:
  name: {{ app.name }}-service
  namespace: {{ app.namespace }}
spec:
  selector:
    app: {{ app.name }}
  ports:
  - port: 80
    targetPort: {{ container.port }}
  type: LoadBalancer
```

### Example 4: Application Properties

**config.yaml:**
```yaml
app:
  name: MySpringApp
  profile: production

server:
  port: 8080
  context_path: /api

spring:
  datasource:
    url: "jdbc:postgresql://{{ 'DB_HOST' | env('localhost') }}:5432/mydb"
    username: "{{ 'DB_USER' | env('admin') }}"
    password: "{{ 'DB_PASSWORD' | env }}"

  jpa:
    hibernate:
      ddl_auto: validate
    show_sql: false

logging:
  level:
    root: INFO
    com.myapp: DEBUG
```

**application.properties.j2:**
```jinja
# {{ app.name }} - {{ app.profile }} Configuration
# Generated: {{ now() }}

spring.application.name={{ app.name }}
spring.profiles.active={{ app.profile }}

server.port={{ server.port }}
server.servlet.context-path={{ server.context_path }}

spring.datasource.url={{ spring.datasource.url }}
spring.datasource.username={{ spring.datasource.username }}
spring.datasource.password={{ spring.datasource.password }}

spring.jpa.hibernate.ddl-auto={{ spring.jpa.hibernate.ddl_auto }}
spring.jpa.show-sql={{ spring.jpa.show_sql | lower }}

{% for package, level in logging.level.items() %}
logging.level.{{ package }}={{ level }}
{% endfor %}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Jinja2](https://jinja.palletsprojects.com/) - The powerful templating engine
- [PyYAML](https://pyyaml.org/) - YAML parser and emitter
- [jsonschema](https://python-jsonschema.readthedocs.io/) - JSON Schema validation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/flavienchenu/jinja4config/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flavienchenu/jinja4config/discussions)


**Made with ❤️ by [Flavien Chenu](https://github.com/flavienchenu)**

If you find this tool useful, please consider giving it a ⭐ on GitHub!
