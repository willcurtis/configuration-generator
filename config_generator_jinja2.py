#!/usr/bin/env python3
"""
config_generator_jinja2.py

Bulk-generate network device configurations from Jinja2 templates and a CSV.

Example:
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


def parse_args():
    usage = (
        "%(prog)s -d TEMPLATE_DIR -t TEMPLATE_FILE -c CSV_FILE -o OUTPUT_DIR"
    )
    description = (
        "Generate device configs in bulk using a Jinja2 template and CSV variables.\n"
        "Each row in the CSV defines a device. 'hostname' column is required.\n"
    )
    epilog = (
        "Template directory: folder with .j2 files\n"
        "CSV: header row with 'hostname' plus any template variables.\n"
        "Example CSV variables column format: lists or dicts in Python literal syntax.\n"
        "Output: one .cfg file per hostname.\n"
    )
    parser = argparse.ArgumentParser(
        usage=usage,
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--template-dir', '-d',
        required=True,
        help='Directory containing Jinja2 templates'
    )
    parser.add_argument(
        '--template-file', '-t',
        required=True,
        help='Name of the template file (inside template-dir)'
    )
    parser.add_argument(
        '--csv', '-c',
        required=True,
        help="Path to CSV with device variables (must include 'hostname')"
    )
    parser.add_argument(
        '--output', '-o',
        default='output_configs',
        help='Directory to save generated config files'
    )
    return parser.parse_args()


def load_template(env, template_file):
    try:
        return env.get_template(template_file)
    except Exception as e:
        raise RuntimeError(f"Template load error: {e}")


def build_context(row):
    context = {}
    for key, value in row.items():
        if key == 'hostname':
            context[key] = value
        else:
            try:
                context[key] = ast.literal_eval(value)
            except Exception:
                context[key] = value
    return context


def main():
    args = parse_args()

    # Prepare output directory
    os.makedirs(args.output, exist_ok=True)

    # Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(args.template_dir),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True
    )
    template = load_template(env, args.template_file)

    # Read CSV
    with open(args.csv, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        if 'hostname' not in reader.fieldnames:
            print("ERROR: CSV must contain 'hostname' column.")
            return

        for row in reader:
            hostname = row['hostname']
            context = build_context(row)
            try:
                config_text = template.render(**context)
            except UndefinedError as ue:
                missing = str(ue).split("'")[1]
                print(f"[ERROR] {hostname}: missing variable '{missing}' in CSV.")
                continue
            except Exception as e:
                print(f"[ERROR] {hostname}: rendering failed: {e}")
                continue

            out_file = os.path.join(args.output, f"{hostname}.cfg")
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(config_text)
            print(f"Generated config: {out_file}")

if __name__ == '__main__':
    main()
