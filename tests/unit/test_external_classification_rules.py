import json
from datetime import datetime, timezone
from pathlib import Path

from personal_data_governance.config.loaders import (
    load_classification_rules,
)
from personal_data_governance.discovery.evidence_classification.deterministic import (
    DeterministicEmailEvidenceClassifier,
)
from personal_data_governance.discovery.evidence_classification.protocol import (
    ClassificationContext,
)
from personal_data_governance.domain.entities.observation import (
    Observation,
)
from personal_data_governance.domain.enums.evidence import (
    EvidenceType,
)
from personal_data_governance.domain.enums.observation import (
    ObservationType,
)
from personal_data_governance.domain.enums.processing import (
    ClassificationStatus,
)
from personal_data_governance.domain.values.email_message_metadata import (
    EmailMessageMetadataV1,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    ObservationId,
)
from personal_data_governance.domain.values.references import (
    SchemaVersion,
    SourceReference,
)


def test_rule_can_be_added_without_changing_classifier_code(
    tmp_path: Path,
) -> None:
    rule_file = (
        tmp_path
        / "rules.json"
    )

    rule_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "rule_set_version": "custom-1",
                "rules": [
                    {
                        "rule_id": "ITALIAN_VERIFICATION",
                        "evidence_type": (
                            "ACCOUNT_VERIFICATION"
                        ),
                        "priority": 10,
                        "patterns": [
                            (
                                "\\bverifica il tuo "
                                "indirizzo email\\b"
                            )
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    loaded = load_classification_rules(
        rule_file
    )

    classifier = (
        DeterministicEmailEvidenceClassifier(
            rules=loaded.rules
        )
    )

    observation = Observation(
        id=ObservationId(
            "observation_001"
        ),
        connected_source_id=ConnectedSourceId(
            "source_gmail"
        ),
        observation_type=(
            ObservationType.EMAIL_MESSAGE_METADATA
        ),
        schema_version=SchemaVersion(1),
        source_reference=SourceReference(
            "message_001"
        ),
        observed_at=None,
        collected_at=datetime.now(
            timezone.utc
        ),
        payload=EmailMessageMetadataV1(
            sender="no-reply@example.com",
            recipients=(
                "user@example.com",
            ),
            subject=(
                "Verifica il tuo indirizzo email"
            ),
            thread_reference=None,
            labels=(),
        ),
    )

    result = classifier.classify(
        observation=observation,
        context=ClassificationContext(
            classifier_version=(
                loaded.rule_set_version
            ),
        ),
    )

    assert (
        result.classification_status
        == ClassificationStatus.CLASSIFIED
    )

    assert (
        result.evidence_candidates[0]
        .evidence_type
        == EvidenceType.ACCOUNT_VERIFICATION
    )

    assert (
        result.evidence_candidates[0]
        .reason_codes
        == (
            "ITALIAN_VERIFICATION",
        )
    )
