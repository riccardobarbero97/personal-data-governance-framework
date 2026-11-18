ALTER TABLE relationships
ADD COLUMN assessment_method TEXT NOT NULL DEFAULT 'RULE';


UPDATE schema_metadata
SET
    schema_version = 3,
    applied_at = CURRENT_TIMESTAMP
WHERE
    schema_name = 'personal_data_governance';
