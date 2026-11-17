PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS schema_metadata (
    schema_name TEXT PRIMARY KEY,
    schema_version INTEGER NOT NULL,
    applied_at TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS connected_sources (
    connected_source_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    provider_id TEXT NOT NULL,
    provider_display_name TEXT NOT NULL,
    connector_id TEXT NOT NULL,
    display_name TEXT NOT NULL,
    external_account_reference TEXT,
    connection_state TEXT NOT NULL,
    authorization_state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);


CREATE INDEX IF NOT EXISTS idx_connected_sources_user
ON connected_sources (
    user_id
);


CREATE INDEX IF NOT EXISTS idx_connected_sources_provider
ON connected_sources (
    provider_id,
    source_type
);


CREATE TABLE IF NOT EXISTS observations (
    observation_id TEXT PRIMARY KEY,
    connected_source_id TEXT NOT NULL,
    observation_type TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    source_reference_value TEXT,
    observed_at_timestamp TEXT,
    observed_at_semantics TEXT,
    collected_at TEXT NOT NULL,
    payload_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,

    FOREIGN KEY (
        connected_source_id
    )
    REFERENCES connected_sources (
        connected_source_id
    )
    ON DELETE CASCADE,

    UNIQUE (
        connected_source_id,
        source_reference_value
    )
);


CREATE INDEX IF NOT EXISTS idx_observations_connected_source
ON observations (
    connected_source_id
);


CREATE INDEX IF NOT EXISTS idx_observations_type
ON observations (
    observation_type
);


CREATE INDEX IF NOT EXISTS idx_observations_observed_at
ON observations (
    observed_at_timestamp
);


CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    observation_id TEXT NOT NULL,
    service_id TEXT,
    evidence_type TEXT NOT NULL,
    evidence_status TEXT NOT NULL,
    confidence TEXT,
    identity_seed_ids_json TEXT NOT NULL,
    reason_codes_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (
        observation_id
    )
    REFERENCES observations (
        observation_id
    )
    ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_evidence_observation
ON evidence (
    observation_id
);


CREATE INDEX IF NOT EXISTS idx_evidence_service
ON evidence (
    service_id
);


CREATE INDEX IF NOT EXISTS idx_evidence_type
ON evidence (
    evidence_type
);


CREATE INDEX IF NOT EXISTS idx_evidence_status
ON evidence (
    evidence_status
);


CREATE TABLE IF NOT EXISTS evidence_lifecycle (
    lifecycle_event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    evidence_id TEXT NOT NULL,
    previous_status TEXT NOT NULL,
    new_status TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    replacement_evidence_id TEXT,
    changed_at TEXT NOT NULL,

    FOREIGN KEY (
        evidence_id
    )
    REFERENCES evidence (
        evidence_id
    )
    ON DELETE CASCADE,

    FOREIGN KEY (
        replacement_evidence_id
    )
    REFERENCES evidence (
        evidence_id
    )
    ON DELETE SET NULL
);


CREATE INDEX IF NOT EXISTS idx_evidence_lifecycle_evidence
ON evidence_lifecycle (
    evidence_id,
    changed_at
);


CREATE TABLE IF NOT EXISTS relationships (
    relationship_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    service_id TEXT NOT NULL,
    relationship_status TEXT NOT NULL,
    temporal_status TEXT NOT NULL,
    identity_seed_ids_json TEXT NOT NULL,
    evidence_ids_json TEXT NOT NULL,
    reason_codes_json TEXT NOT NULL,
    warnings_json TEXT NOT NULL,
    assessor_version TEXT NOT NULL,
    assessment_policy_version TEXT NOT NULL,
    assessed_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    UNIQUE (
        user_id,
        service_id
    )
);


CREATE INDEX IF NOT EXISTS idx_relationships_user
ON relationships (
    user_id
);


CREATE INDEX IF NOT EXISTS idx_relationships_service
ON relationships (
    service_id
);


CREATE INDEX IF NOT EXISTS idx_relationships_status
ON relationships (
    relationship_status,
    temporal_status
);


INSERT INTO schema_metadata (
    schema_name,
    schema_version,
    applied_at
)
VALUES (
    'personal_data_governance',
    1,
    CURRENT_TIMESTAMP
)
ON CONFLICT (
    schema_name
)
DO UPDATE SET
    schema_version = excluded.schema_version;
