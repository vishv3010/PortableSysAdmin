import json
import os
from datetime import datetime

from .policy import RemediationPolicy


class RemediationEngine:
    def __init__(self, logger, session_log_dir, is_admin, current_user):
        import tempfile
        self.logger = logger
        # Ensure session_log_dir is valid across Windows and Linux
        if not session_log_dir or (session_log_dir == "/tmp" and os.name == "nt") or not os.path.exists(os.path.dirname(os.path.abspath(session_log_dir))):
            session_log_dir = tempfile.gettempdir()
        self.session_log_dir = session_log_dir
        self.is_admin = is_admin
        self.current_user = current_user
        self.audit_log_path = os.path.join(self.session_log_dir, "actions.json")

    def _log_audit(self, action_id: str, action_name: str, risk: str, dry_run: bool, success: bool, message: str):
        from datetime import timezone
        record = {
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
            "user": self.current_user,
            "action_id": action_id,
            "action_name": action_name,
            "risk": risk,
            "dry_run": dry_run,
            "success": success,
            "message": message
        }
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.audit_log_path)), exist_ok=True)
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Could not append to audit log {self.audit_log_path}: {e}")
        if self.logger:
            self.logger.info(f"AUDIT: {record}")

    def run_remediation(self, remediation, dry_run: bool = False, force_auto: bool = False):
        from ui import UI
        
        meta = remediation.metadata
        UI.info(f"PROPOSED ACTION: {meta['name']}")
        print(f"  Description: {meta['description']}")
        print(f"  Risk Level:  {meta['risk']}")
        
        if meta['requires_admin'] and not self.is_admin:
            UI.error("Administrator/Root privileges required for this action. Aborting.")
            if os.name == "nt":
                print("\n[TIP] To apply this fix, right-click 'START.bat' and select 'Run as administrator'.")
            else:
                print("\n[TIP] To apply this fix, re-run the toolkit with: sudo ./START.sh")
            self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, False, "Privilege check failed.")
            return False

        if RemediationPolicy.is_blocked(meta['risk']):
            UI.error("This action is classified as DANGEROUS and is blocked by policy.")
            self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, False, "Blocked by policy.")
            return False

        # --- PRE-FLIGHT CHECKS ---
        UI.info("Running pre-flight checks...")
        pre_success, pre_msg = remediation.pre_flight()
        if not pre_success:
            UI.error(f"Pre-flight failed: {pre_msg}")
            self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, False, f"Pre-flight failed: {pre_msg}")
            return False
        else:
            print(f"  {pre_msg}")

        # --- DRY RUN MODE ---
        if dry_run:
            UI.info("[DRY RUN MODE] The following action WOULD be performed:")
            success, msg = remediation.execute(dry_run=True)
            print(f"  Result: {msg}")
            self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, success, msg)
            return True

        # --- CONFIRMATION ---
        if RemediationPolicy.requires_confirmation(meta['risk']) and not force_auto:
            confirm = UI.prompt("This action requires confirmation. Execute? [y/N]:")
            if confirm.lower() != 'y':
                UI.warning("Action cancelled by user.")
                self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, False, "User cancelled.")
                return False

        # --- EXECUTION ---
        UI.info("Executing remediation...")
        success, msg = remediation.execute(dry_run=False)
        
        if success:
            UI.success(f"Execution Output: {msg}")
            UI.info("Verifying fix...")
            ver_success, ver_msg = remediation.verify()
            
            if ver_success:
                UI.success(f"Verification Output: {ver_msg}")
                final_success = True
                final_msg = f"{msg} | Verification: {ver_msg}"
            else:
                UI.error(f"Verification Failed: {ver_msg}")
                final_success = False
                final_msg = f"{msg} | Verification Failed: {ver_msg}"
                
                # --- ROLLBACK ORCHESTRATION ---
                if meta.get('rollback_available', False):
                    UI.warning("Automated rollback initiated due to verification failure...")
                    rb_success, rb_msg = remediation.rollback()
                    if rb_success:
                        UI.success(f"Rollback successful: {rb_msg}")
                        final_msg += f" | Rollback: {rb_msg}"
                    else:
                        UI.error(f"Rollback failed: {rb_msg}")
                        final_msg += f" | Rollback Failed: {rb_msg}"
                else:
                    UI.warning("No automated rollback available for this action. Manual intervention may be required.")
        else:
            UI.error(f"Execution Failed: {msg}")
            final_success = False
            final_msg = msg

        self._log_audit(meta['id'], meta['name'], meta['risk'], dry_run, final_success, final_msg)
        return final_success
