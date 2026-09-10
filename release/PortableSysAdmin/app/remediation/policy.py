class RemediationPolicy:
    RISK_SAFE = "SAFE"
    RISK_CONFIRM = "CONFIRMATION_REQUIRED"
    RISK_DANGEROUS = "DANGEROUS"

    @staticmethod
    def can_auto_execute(risk_level: str) -> bool:
        return risk_level == RemediationPolicy.RISK_SAFE

    @staticmethod
    def requires_confirmation(risk_level: str) -> bool:
        return risk_level == RemediationPolicy.RISK_CONFIRM

    @staticmethod
    def is_blocked(risk_level: str) -> bool:
        return risk_level == RemediationPolicy.RISK_DANGEROUS
