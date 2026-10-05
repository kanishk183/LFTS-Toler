CREATE TABLE monitored_paths (
    id INT AUTO_INCREMENT PRIMARY KEY,
    path VARCHAR(1024) NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_monitored_path (path(512))
);

CREATE TABLE files (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    monitored_path_id INT NOT NULL,
    file_path VARCHAR(2048) NOT NULL,
    file_path_hash CHAR(64) NOT NULL UNIQUE,
    file_name VARCHAR(512) NOT NULL,
    file_size BIGINT UNSIGNED NOT NULL DEFAULT 0,
    permissions VARCHAR(20),
    owner_name VARCHAR(255),
    group_name VARCHAR(255),
    created_time DATETIME NULL,
    modified_time DATETIME NULL,
    accessed_time DATETIME NULL,
    current_hash CHAR(64),
    status ENUM('active', 'modified', 'deleted', 'corrupted') NOT NULL DEFAULT 'active',
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (monitored_path_id) REFERENCES monitored_paths(id)
    ON DELETE CASCADE


);

CREATE TABLE file_versions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT NOT NULL,
    version_number INT NOT NULL,
    file_hash CHAR(64) NOT NULL,
    file_size BIGINT UNSIGNED NOT NULL DEFAULT 0,
    backup_path VARCHAR(2048) NOT NULL,
    permissions VARCHAR(20),
    owner_name VARCHAR(255),
    group_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (file_id, version_number),
    FOREIGN KEY (file_id) REFERENCES files(id)
        ON DELETE CASCADE
);

CREATE TABLE backups (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    backup_type ENUM('full', 'incremental') NOT NULL,
    backup_path VARCHAR(2048) NOT NULL,
    started_at DATETIME NOT NULL,
    completed_at DATETIME NULL,
    status ENUM('running', 'completed', 'failed') NOT NULL DEFAULT 'running',
    total_files INT UNSIGNED NOT NULL DEFAULT 0,
    total_size BIGINT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE backup_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    backup_id BIGINT NOT NULL,
    file_id BIGINT NOT NULL,
    source_path VARCHAR(2048) NOT NULL,
    backup_path VARCHAR(2048) NOT NULL,
    file_hash CHAR(64) NOT NULL,
    file_size BIGINT UNSIGNED NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (backup_id, file_id),
    FOREIGN KEY (backup_id) REFERENCES backups(id)
        ON DELETE CASCADE,
    FOREIGN KEY (file_id) REFERENCES files(id)
        ON DELETE CASCADE
);

CREATE TABLE integrity_checks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT NOT NULL,
    expected_hash CHAR(64) NOT NULL,
    actual_hash CHAR(64),
    result ENUM('match', 'mismatch', 'missing') NOT NULL,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id)
        ON DELETE CASCADE
);

CREATE TABLE recovery_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    file_id BIGINT NULL,
    recovery_source VARCHAR(2048),
    destination_path VARCHAR(2048),
    recovery_type ENUM('file', 'directory') NOT NULL,
    status ENUM('started', 'completed', 'failed') NOT NULL,
    message TEXT,
    started_at DATETIME NOT NULL,
    completed_at DATETIME NULL,
    FOREIGN KEY (file_id) REFERENCES files(id)
        ON DELETE SET NULL
);

CREATE TABLE system_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    log_level ENUM('INFO', 'WARNING', 'ERROR') NOT NULL DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);