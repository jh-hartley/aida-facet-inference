from src.db.connection import db_session
from src.raw_csv_ingestion.records import RawBQBatch16QACompleteRecord
from src.raw_csv_ingestion.repositories import RawBQBatch16QACompleteRepository


def create_bq_batch16_qa_complete(
    product_reference: str,
    attribute_reference: str,
    attribute_name: str,
    recommendation: str,
    unit: str,
    override: str,
    alternative_override: str,
    action: str,
    link_to_site: str,
    comment: str,
) -> RawBQBatch16QACompleteRecord:
    """Create a new B&Q QA Complete record"""
    with db_session().begin() as session:
        repo = RawBQBatch16QACompleteRepository(session)
        record = RawBQBatch16QACompleteRecord(
            product_reference=product_reference,
            attribute_reference=attribute_reference,
            attribute_name=attribute_name,
            recommendation=recommendation,
            unit=unit,
            override=override,
            alternative_override=alternative_override,
            action=action,
            link_to_site=link_to_site,
            comment=comment,
        )
        return repo.create(record)
