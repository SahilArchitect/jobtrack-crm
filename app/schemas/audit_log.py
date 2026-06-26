from app.schemas.common import Timestamped


class AuditLogRead(Timestamped):
    tenant_id: str
    actor_user_id: str | None
    entity_type: str
    entity_id: str
    action: str
    before: dict | None
    after: dict | None
