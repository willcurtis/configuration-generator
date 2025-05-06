#!/usr/bin/env python3
"""
config_generator_jinja2.py

Generate device configurations in bulk from Jinja2 templates and a CSV,
with friendly error reporting for missing template variables.

Usage:
    python3 config_generator_jinja2.py \
      --template-dir templates \
      --template-file switch_template.j2 \
      --csv variables.csv \
      --output configs/
"""
import os
import csv
import argparse
import ast
from datetime import datetime

from jinja2 import Environment, FileSystemLoader, StrictUndefined, UndefinedError

def main():
    parser = argparse.ArgumentParser(description="Bulk Config Generator with Jinja2")
    parser.add_argument(
        '--template-dir', '-d', required=True,
        help="Directory containing Jinja2 templates"
    )
    parser.add_argument(
        '--template-file', '-t', required=True,
        help="Template filename (within template dir)"
    )
    parser.add_argument(
        '--csv', '-c', required=True,
        help="CSV file with device variables"
    )
    parser.add_argument(
        '--output', '-o', default='output_configs',
        help="Directory to save generated configs"
    )
    args = parser.parse_args()

    # Prepare output directory
    os.makedirs(args.output, exist_ok=True)

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(args.template_dir),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = env.get_template(args.template_file)

    # Read CSV and render configs
    with open(args.csv, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        if 'hostname' not in reader.fieldnames:
            parser.error("CSV must contain 'hostname' column")

        for row in reader:
            hostname = row['hostname']
            # Build context: parse Python literals where possible
            context = {}
            for key, value in row.items():
                if key == 'hostname':
                    context[key] = value
                else:
                    try:
                        context[key] = ast.literal_eval(value)
                    except Exception:
                        context[key] = value

            try:
                config_text = template.render(**context)
            except UndefinedError as e:
                missing = str(e).split("'")[1]
                print(f"[ERROR] Device {hostname}: missing variable '{missing}' in CSV.")
                continue

            out_path = os.path.join(args.output, f"{hostname}.cfg")
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(config_text)
            print(f"Generated config for {hostname}: {out_path}")

if __name__ == '__main__':
    main()
