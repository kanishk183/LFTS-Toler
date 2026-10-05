#!/bin/bash

cd /home/kt_18/lfts-toler
source venv/bin/activate
python -m tests.test_metadata
python -m backup.incremental_backup
python -m reporting.report >> logs/cron_report.log 2>&1