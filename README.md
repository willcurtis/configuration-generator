# Bulk Config Generator (Jinja2)

This tool generates device configurations in bulk using Jinja2 templates and a CSV file.

## Prerequisites

```bash
pip3 install jinja2
```

## Directory Structure

```
config_generator.py
template_dir/
  └── router.j2
devices.csv
output_configs/
```

- **template_dir/**: Contains your Jinja2 `.j2` templates.
- **router.j2**: Example template file with Jinja2 syntax.
- **devices.csv**: CSV file with a header row. Must include `hostname` column and other variables.
- **output_configs/**: Generated configuration files.

## Template Syntax

- Use Jinja2 tags: `{{ variable }}` for substitutions, `{% ... %}` for logic.
- **Variables**: Correspond to CSV headers.
- **Lists/Dicts**: Represent complex data (e.g., `interfaces` column can be a JSON-like list of dicts).

### Example router.j2

```jinja
hostname {{ hostname }}

{% for iface in interfaces %}
interface {{ iface.name }}
  ip address {{ iface.ip }}/{{ iface.mask }}
{% endfor %}

router bgp {{ bgp_asn }}
  neighbor {{ bgp_peer }} remote-as {{ bgp_asn }}
```

## Usage

Run the generator in one line:

```bash
python3 config_generator.py --template-dir template_dir --template-file router.j2 --csv devices.csv --output output_configs/
```

## Modifying Templates

- **Add variables**: Update CSV headers and reference them via `{{ variable }}` in the `.j2` file.
- **Control Logic**: Use Jinja2 tags:
  - `{% if condition %} ... {% endif %}`
  - `{% for item in list %} ... {% endfor %}`
- **Filters**: Use built-in filters (e.g., `{{ var|upper }}`) or define custom filters in the Python script:
  ```python
  env.filters['myfilter'] = lambda x: ...
  ```

## Troubleshooting

- **Undefined variable**: The tool uses `StrictUndefined`, so missing variables will raise errors.
- **Parsing issues**: Ensure JSON-like columns in CSV are valid Python literals for `ast.literal_eval`.
