DROP TABLE evidence_lifecycle;

DROP TABLE evidence;


CREATE TABLE evidence (
    evidence_id TEXT PRIMARY KEY,
    service_id TEXT,
    evidence_type TEXT NOT NULL,
    evidence_status TEXT NOT NULL,
    identity_seed_ids_json TEXT NOT NULL,
    classification_method TEXT NOT NULL,
    classifier_version TEXT NOT NULL,
    reason_codes_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);


CREATE INDEX idx_evidence_service
ON evidence (
    service_id
);


CREATE INDEX idx_evidence_type
ON evidence (
    evidence_type
);


CREATE INDEX idx_evidence_status
ON evidence (
    evidence_status
);


CREATE TABLE evidence_observations (
    evidence_id TEXT NOT NULL,
    observation_id TEXT NOT NULL,

    PRIMARY KEY (
        evidence_id,
        observation_id
    ),

    FOREIGN KEY (
        evidence_id
    )
    REFERENCES evidence (
        evidence_id
    )
    ON DELETE CASCADE,

    FOREIGN KEY (
        observation_id
    )
    REFERENCES observations (
        observation_id
    )
    ON DELETE CASCADE
);


CREATE INDEX idx_evidence_observations_observation
ON evidence_observations (
    observation_id
);


CREATE TABLE evidence_lifecycle (
    lifecycle_event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    evidence_id TEXT NOT NULL,
    previous_status TEXT NOT NULL,
    new_status TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    actor TEXT NOT NULL,
    superseded_by_evidence_id TEXT,
    changed_at TEXT NOT NULL,

    FOREIGN KEY (
        evidence_id
    )
    REFERENCES evidence (
        evidence_id
    )
    ON DELETE CASCADE,

    FOREIGN KEY (
        superseded_by_evidence_id
    )
    REFERENCES evidence (
        evidence_id
    )
    ON DELETE SET NULL
);


CREATE INDEX idx_evidence_lifecycle_evidence
ON evidence_lifecycle (
    evidence_id,
    changed_at
);


UPDATE schema_metadata
SET
    schema_version = 2,
    applied_at = CURRENT_TIMESTAMP
WHERE
    schema_name = 'personal_data_governance';
