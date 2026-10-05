# LFTS-Toler

## Linux-Based File System Fault Tolerance Framework

LFTS-Toler is a Linux-based file system fault tolerance and recovery framework developed using Python and MySQL. The system monitors files and directories, maintains file metadata and SHA-256 integrity information, creates full and incremental backups, maintains file versions, detects filesystem faults, restores files from trusted recovery points, verifies recovered data, and generates system reports.

The project is designed for a local Linux environment and demonstrates practical concepts from Operating Systems and Database Management Systems.

---

## 1. Project Objectives

The main objectives of LFTS-Toler are:

- Monitor files and directories on a Linux filesystem.
- Collect and maintain file metadata.
- Calculate SHA-256 hashes for file integrity verification.
- Store filesystem information in a relational MySQL database.
- Create full backups of monitored files.
- Create incremental backups when files change.
- Maintain multiple file versions.
- Detect modified, deleted, and corrupted files.
- Restore files from trusted backup versions.
- Restore file permissions and ownership where possible.
- Verify recovered files using SHA-256.
- Maintain recovery and integrity-check history.
- Generate system status reports.
- Automate periodic scanning and incremental backup using Linux cron.

---

## 2. System Architecture

The main workflow of the system is:

Linux File System
        |
        v
Filesystem Scanner
        |
        v
Metadata Collection + SHA-256 Hashing
        |
        v
MySQL Database
        |
        +-------------------+
        |                   |
        v                   v
Backup Manager        Version Manager
        |                   |
        +---------+---------+
                  |
                  v
          Disaster Detection
                  |
                  v
           Recovery Engine
                  |
                  v
        Integrity Verification
                  |
                  v
            System Reports

The implementation follows the overall architecture proposed during Phase-I.

---

## 3. Technology Stack

| Technology | Purpose |
|------------|---------|
| Ubuntu / Linux | Operating system environment |
| Python | Application and system logic |
| MySQL | Metadata, backup, version, recovery and integrity records |
| SHA-256 | File integrity verification |
| Linux Filesystem API | File metadata and filesystem operations |
| Linux Cron | Automated periodic execution |
| VS Code | Development environment |

---

## 4. Project Structure

```text
lfts-toler/
│
├── backup/
│   ├── full_backup.py
│   └── incremental_backup.py
│
├── cli/
│   ├── __init__.py
│   └── main.py
│
├── config/
│   └── config.py
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── init_db.py
│   └── schema.sql
│
├── disaster/
│   └── detector.py
│
├── integrity/
│   ├── __init__.py
│   └── hasher.py
│
├── logs/
│   ├── cron.log
│   └── cron_report.log
│
├── recovery/
│   └── recovery_engine.py
│
├── reporting/
│   ├── __init__.py
│   └── report.py
│
├── scanner/
│   ├── __init__.py
│   ├── metadata.py
│   └── scanner.py
│
├── scheduler/
│   ├── __init__.py
│   └── backup_job.sh
│
├── storage/
│   ├── full/
│   └── incremental/
│
├── tests/
│   ├── __init__.py
│   └── test_metadata.py
│
├── verification/
│   └── integrity_checker.py
│
├── versioning/
│   └── version_manager.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md