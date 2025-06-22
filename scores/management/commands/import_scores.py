# from __future__ import annotations

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings

from ...models import StudentScore


class Command(BaseCommand):
    help = "Import THPT 2024 student scores from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            nargs="?",
            default=str(Path(__file__).resolve().parent.parent / "data" / "diem_thi_thpt_2024.csv"),
            help="Path to CSV file (default: built-in data directory)",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete all existing StudentScore rows before importing.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=5000,  # Increased default for bulk operations
            help="Batch size for bulk operations (default: 5000)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without actually saving to database",
        )

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"]).expanduser().resolve()
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        # Debug database connection
        self.stdout.write(f"Database engine: {settings.DATABASES['default']['ENGINE']}")
        self.stdout.write(f"Database name: {settings.DATABASES['default']['NAME']}")

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No data will be saved"))

        if options["truncate"] and not options["dry_run"]:
            self.stdout.write("Truncating existing StudentScore data …")
            deleted_count = StudentScore.objects.all().delete()[0]
            self.stdout.write(f"Deleted {deleted_count} existing records")

        self.stdout.write(f"Importing scores from {csv_path} …")

        # Read and validate CSV first
        try:
            with csv_path.open(newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                headers = reader.fieldnames
                self.stdout.write(f"CSV headers: {headers}")

                if not headers or 'sbd' not in headers:
                    raise CommandError("CSV must contain 'sbd' column")

                # Process in batches
                self._process_csv_data(csv_path, options)

        except UnicodeDecodeError:
            self.stdout.write(self.style.ERROR("Trying different encoding..."))
            try:
                with csv_path.open(newline="", encoding="utf-8-sig") as fh:
                    self._process_csv_data(csv_path, options)
            except Exception as e:
                raise CommandError(f"Failed to read CSV with UTF-8-BOM: {e}")
        except Exception as e:
            raise CommandError(f"Error reading CSV: {e}")

    def _process_csv_data(self, csv_path, options):
        created = 0
        updated = 0
        errors = 0
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]

        with csv_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)

            # Process in batches without nested transactions
            batch_records = []

            for idx, row in enumerate(reader, start=1):
                try:
                    sbd = row.pop("sbd", "").strip()
                    if not sbd:
                        self.stdout.write(self.style.ERROR(f"Row {idx}: Missing sbd, skipping"))
                        errors += 1
                        continue

                    # Clean and validate data
                    cleaned_data = self._clean_row_data(row)

                    if dry_run:
                        self.stdout.write(f"Row {idx}: Would process sbd={sbd}")
                        created += 1
                    else:
                        batch_records.append((sbd, cleaned_data))

                        # Process batch when it reaches batch_size
                        if len(batch_records) >= batch_size:
                            batch_created, batch_updated, batch_errors = self._process_batch(
                                batch_records, options
                            )
                            created += batch_created
                            updated += batch_updated
                            errors += batch_errors
                            batch_records = []

                        if idx % 100 == 0:  # More frequent updates for debugging
                            self.stdout.write(f"Processed {idx} records... (Created: {created}, Updated: {updated})")

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Row {idx}: Error processing row: {e}"))
                    errors += 1
                    continue

            # Process remaining records in the last batch
            if batch_records and not dry_run:
                batch_created, batch_updated, batch_errors = self._process_batch(
                    batch_records, options
                )
                created += batch_created
                updated += batch_updated
                errors += batch_errors

        # Final summary
        self.stdout.write("")
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"DRY RUN: Would import {created} records"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Import completed: {created} created, {updated} updated, {errors} errors"))

            # Verify data was actually saved
            total_count = StudentScore.objects.count()
            self.stdout.write(f"Total records in database: {total_count}")

    def _clean_row_data(self, row):
        """Clean and validate row data before saving"""
        cleaned = {}

        # CSV column to model field mapping
        field_mapping = {
            'toan': 'math',
            'ngu_van': 'literature',
            'ngoai_ngu': 'foreign_lang',
            'vat_li': 'physics',
            'hoa_hoc': 'chemistry',
            'sinh_hoc': 'biology',
            'lich_su': 'history',
            'dia_li': 'geography',
            'gdcd': 'civic_education',
            'ma_ngoai_ngu': 'foreign_lang_code'
        }

        for csv_col, model_field in field_mapping.items():
            if csv_col in row:
                v = row[csv_col]

                if model_field == "foreign_lang_code":
                    # Keep as string, empty string if no value
                    cleaned[model_field] = (v or "").strip()
                else:
                    # Numeric fields - convert empty strings to None
                    if v and str(v).strip():
                        try:
                            cleaned[model_field] = float(str(v).strip())
                        except (ValueError, TypeError):
                            # If conversion fails, store as None
                            cleaned[model_field] = None
                    else:
                        cleaned[model_field] = None

        return cleaned

    def _process_batch(self, batch_records, options):
        """Process a batch of records using bulk operations for speed"""
        created = 0
        updated = 0
        errors = 0

        try:
            with transaction.atomic():
                # Extract SBDs for this batch
                batch_sbds = [sbd for sbd, _ in batch_records]

                # Get existing records in one query (using r_number as primary key)
                existing_records = {
                    record.r_number: record
                    for record in StudentScore.objects.filter(r_number__in=batch_sbds)
                }

                # Separate records into create and update lists
                records_to_create = []
                records_to_update = []

                for sbd, cleaned_data in batch_records:
                    try:
                        if sbd in existing_records:
                            # Update existing record
                            existing_record = existing_records[sbd]
                            for key, value in cleaned_data.items():
                                setattr(existing_record, key, value)
                            records_to_update.append(existing_record)
                        else:
                            # Create new record (r_number is the primary key)
                            records_to_create.append(
                                StudentScore(r_number=sbd, **cleaned_data)
                            )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error preparing sbd={sbd}: {e}"))
                        errors += 1
                        continue

                # Bulk create new records
                if records_to_create:
                    try:
                        StudentScore.objects.bulk_create(
                            records_to_create,
                            batch_size=1000,
                            ignore_conflicts=True  # Skip duplicates instead of failing
                        )
                        created += len(records_to_create)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Bulk create failed: {e}"))
                        errors += len(records_to_create)

                # Bulk update existing records
                if records_to_update:
                    try:
                        # Get all field names except 'r_number' for bulk_update
                        update_fields = [
                            field.name for field in StudentScore._meta.fields
                            if field.name != 'r_number'
                        ]

                        StudentScore.objects.bulk_update(
                            records_to_update,
                            update_fields,
                            batch_size=1000
                        )
                        updated += len(records_to_update)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Bulk update failed: {e}"))
                        errors += len(records_to_update)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Batch transaction failed: {e}"))
            errors += len(batch_records)

        return created, updated, errors