import os
import json
from datetime import datetime
from .policy import RemediationPolicy

class RemediationEngine:
    def __init__(self, logger, session_log_dir, is_admin, current_user):
        self.logger = logger
        self.session_log_dir = session_log_dir
        self.is_admin = is_admin
        self.current_user = current_user
        self.audit_log_path = os.path.join(session_log_dir, "actions.json")

    def _log_audit(self, action_id: str, action_name: str, risk: str, dry_run: bool, success: bool, message: str):
        record = {
            "timestamp": datetime.now().isoformat(),
            "user": self.current_user,
            "action_id": action_id,
            "action_name": action_name,
            "risk": risk,
            "dry_run": dry_run,
            "success": success,
            "message": message
        }
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(record) + "\n")
        self.logger.info(f"AUDIT: {record}")

    def run_remediation(self, remediation, dry_run: bool = False, force_auto: bool = False):
        meta = remediation.metadata
        print(f"\n--- PROPOSED ACTION: {meta['name']} ---")
        print(f"Description: {meta['description']}")
        print(f"Risk Level: {meta['risk']}")
        
        if meta['requires_admin'] and not self.is_admin:
            print("[ERROR] Administrator/Root privileges required for this action. Aborting.")
            self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, False, "Privilege check failed.")
            return False

        if RemediationPolicy.is_blocked(meta['risk']):
            print("[ERROR] This action is classified as DANGEROUS and is blocked by policy.")
            self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, False, "Blocked by policy.")
            return False

        if dry_run:
            print("\n[DRY RUN MODE] The following action WOULD be performed.")
            success, msg = remediation.execute(dry_run=True)
            print(f"Dry Run Result: {msg}")
            self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, success, msg)
            return True

        if RemediationPolicy.requires_confirmation(meta['risk']) and not force_auto:
            confirm = input("This action requires confirmation. Execute? [y/N]: ")
            if confirm.lower() != 'y':
                print("Action cancelled by user.")
                self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, False, "User cancelled.")
                return False

        print("\n[INFO] Executing...")
        success, msg = remediation.execute(dry_run=False)
        print(f"Execution Output: {msg}")
        
        if success:
            print("[INFO] Verifying...")
            ver_success, ver_msg = remediation.verify()
            print(f"Verification Output: {ver_msg}")
            final_success = ver_success
            final_msg = f"{msg} | Verification: {ver_msg}"
        else:
            final_success = False
            final_msg = msg

        self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, final_success, final_msg)
        return final_success
