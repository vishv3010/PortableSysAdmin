import json
import os
import html as html_lib
from datetime import datetime

class ReportGenerator:
    def __init__(self, session_log_dir, project_root, platform_info):
        self.session_log_dir = session_log_dir
        self.project_root = project_root
        self.platform_info = platform_info
        
    def generate(self) -> str:
        # Load diagnostics
        diag_path = os.path.join(self.session_log_dir, "diagnostics.json")
        diagnostics = []
        if os.path.exists(diag_path):
            with open(diag_path, 'r') as f:
                for line in f:
                    if line.strip():
                        diagnostics.append(json.loads(line))
                        
        # Load actions
        audit_path = os.path.join(self.session_log_dir, "actions.json")
        actions = []
        if os.path.exists(audit_path):
            with open(audit_path, 'r') as f:
                for line in f:
                    if line.strip():
                        actions.append(json.loads(line))
                        
        # Determine overall status and counts
        total_tests = len(diagnostics)
        failed_count = sum(1 for d in diagnostics if d.get('status') == "FAIL")
        warning_count = sum(1 for d in diagnostics if d.get('status') == "WARNING")
        passed_count = sum(1 for d in diagnostics if d.get('status') == "PASS")
        
        overall_status = "PASS"
        if failed_count > 0:
            overall_status = "FAIL"
        elif warning_count > 0:
            overall_status = "WARNING"

        hostname = html_lib.escape(self.platform_info.get('hostname', 'Unknown'))
        os_info = html_lib.escape(self.platform_info.get('os', 'Unknown'))
        release = html_lib.escape(self.platform_info.get('release', 'Unknown'))
        gen_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SysAdmin Diagnostic Report</title>
    <style>
        :root {{
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --info: #3b82f6;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 2rem;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid var(--border-color); padding-bottom: 1rem; }}
        .header h1 {{ margin: 0; font-size: 2rem; color: var(--text-main); }}
        .header-meta {{ color: var(--text-muted); font-size: 0.9rem; text-align: right; }}
        
        /* Summary Cards */
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .card {{ background: var(--card-bg); padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid var(--border-color); }}
        .card-title {{ font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 0.5rem; }}
        .card-value {{ font-size: 2rem; font-weight: bold; }}
        
        /* Badges */
        .badge {{ padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }}
        .badge.PASS {{ background-color: #d1fae5; color: #065f46; }}
        .badge.FAIL {{ background-color: #fee2e2; color: #991b1b; }}
        .badge.WARNING {{ background-color: #fef3c7; color: #92400e; }}
        .badge.INFO {{ background-color: #e0f2fe; color: #075985; }}
        
        /* Tables */
        .table-container {{ background: var(--card-bg); border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; margin-bottom: 2rem; border: 1px solid var(--border-color); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 1rem; text-align: left; border-bottom: 1px solid var(--border-color); }}
        th {{ background-color: #f1f5f9; font-weight: 600; color: var(--text-muted); font-size: 0.875rem; text-transform: uppercase; }}
        tr:last-child td {{ border-bottom: none; }}
        
        /* Detailed Findings */
        .finding {{ background: var(--card-bg); border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 1rem; overflow: hidden; }}
        .finding-header {{ padding: 1rem; background-color: #f8fafc; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; gap: 1rem; }}
        .finding-header h3 {{ margin: 0; font-size: 1.1rem; flex-grow: 1; }}
        .finding-body {{ padding: 1rem; }}
        .evidence-block {{ background: #1e293b; color: #f8fafc; padding: 1rem; border-radius: 6px; overflow-x: auto; font-family: monospace; font-size: 0.875rem; margin-top: 1rem; }}
        details summary {{ cursor: pointer; font-weight: 600; color: var(--info); outline: none; }}
        
        @media print {{
            body {{ background-color: #fff; padding: 0; }}
            .card {{ box-shadow: none; }}
            .table-container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Diagnostic Report</h1>
                <p style="margin: 0.5rem 0 0 0; color: var(--text-muted);">Portable SysAdmin Toolkit</p>
            </div>
            <div class="header-meta">
                <div><strong>Machine:</strong> {hostname}</div>
                <div><strong>OS:</strong> {os_info} ({release})</div>
                <div><strong>Generated:</strong> {gen_time}</div>
            </div>
        </div>

        <div class="summary-grid">
            <div class="card">
                <div class="card-title">Overall Health</div>
                <div class="card-value"><span class="badge {overall_status}">{overall_status}</span></div>
            </div>
            <div class="card">
                <div class="card-title">Total Tests</div>
                <div class="card-value">{total_tests}</div>
            </div>
            <div class="card">
                <div class="card-title">Passed</div>
                <div class="card-value" style="color: var(--success);">{passed_count}</div>
            </div>
            <div class="card">
                <div class="card-title">Issues Found</div>
                <div class="card-value" style="color: var(--danger);">{failed_count + warning_count}</div>
            </div>
        </div>

        <h2>Diagnostic Summary</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr><th>Category</th><th>Test Name</th><th>Status</th><th>Severity</th></tr>
                </thead>
                <tbody>
"""
        for d in diagnostics:
            st = html_lib.escape(d.get('status', 'UNKNOWN'))
            cat = html_lib.escape(str(d.get('category', '')))
            test = html_lib.escape(str(d.get('test', '')))
            sev = html_lib.escape(str(d.get('severity', '')))
            html += f"                    <tr><td>{cat}</td><td>{test}</td><td><span class='badge {st}'>{st}</span></td><td><span class='badge {sev}'>{sev}</span></td></tr>\n"

        html += """                </tbody>
            </table>
        </div>

        <h2>Detailed Findings</h2>
"""
        findings_exist = False
        for d in diagnostics:
            if d.get('status') in ['FAIL', 'WARNING']:
                findings_exist = True
                st = html_lib.escape(d.get('status', 'UNKNOWN'))
                sev = html_lib.escape(str(d.get('severity', '')))
                msg = html_lib.escape(str(d.get('message', '')))
                cat = html_lib.escape(str(d.get('category', '')))
                test = html_lib.escape(str(d.get('test', '')))
                evidence_json = html_lib.escape(json.dumps(d.get('evidence', {}), indent=2))
                
                html += f"""        <div class="finding">
            <div class="finding-header">
                <span class="badge {st}">{st}</span>
                <h3>{msg}</h3>
                <span class="badge {sev}">{sev}</span>
            </div>
            <div class="finding-body">
                <p style="margin-top: 0;"><strong>Category:</strong> {cat} | <strong>Test:</strong> {test}</p>
                <details>
                    <summary>View Raw Evidence Logs</summary>
                    <div class="evidence-block">{evidence_json}</div>
                </details>
            </div>
        </div>
"""
        if not findings_exist:
            html += "<p style='color: var(--text-muted);'>No issues were found during the diagnostic checks.</p>"
            
        html += """
        <h2>Remediation Audit Trail</h2>
"""
        if not actions:
            html += "<p style='color: var(--text-muted);'>No remediation actions were executed during this session.</p>"
        else:
            html += """        <div class="table-container">
            <table>
                <thead>
                    <tr><th>Timestamp</th><th>Action Name</th><th>Risk Level</th><th>Status</th><th>Log Message</th></tr>
                </thead>
                <tbody>
"""
            for a in actions:
                st = "PASS" if a.get('success') else "FAIL"
                ts = html_lib.escape(str(a.get('timestamp', ''))[:19])
                name = html_lib.escape(str(a.get('action_name', '')))
                risk = html_lib.escape(str(a.get('risk', '')))
                msg = html_lib.escape(str(a.get('message', '')))
                html += f"                    <tr><td>{ts}</td><td>{name}</td><td><span class='badge {risk}'>{risk}</span></td><td><span class='badge {st}'>{st}</span></td><td>{msg}</td></tr>\n"
            html += """                </tbody>
            </table>
        </div>\n"""

        html += """
        <div style="margin-top: 4rem; text-align: center; color: var(--text-muted); font-size: 0.875rem; border-top: 1px solid var(--border-color); padding-top: 2rem;">
            Generated securely offline by the <strong>Portable SysAdmin Toolkit</strong>
        </div>
    </div>
</body>
</html>
"""
        # Save report
        out_file = os.path.join(self.session_log_dir, "final-report.html")
        with open(out_file, 'w') as f:
            f.write(html)
            
        return out_file
