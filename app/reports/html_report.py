import html as html_lib
import json
import os
from datetime import datetime


class ReportGenerator:
    def __init__(self, session_log_dir, project_root, platform_info):
        self.session_log_dir = session_log_dir
        self.project_root = project_root
        self.platform_info = platform_info

    def generate_ai_prompt(self, diagnostics, actions) -> str:
        hostname = self.platform_info.get('hostname', 'Unknown')
        os_info = self.platform_info.get('os', 'Unknown')
        release = self.platform_info.get('release', 'Unknown')
        arch = self.platform_info.get('arch', 'Unknown')
        from datetime import timezone
        gen_time = datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')

        failed = [d for d in diagnostics if d.get('status') == "FAIL"]
        warnings = [d for d in diagnostics if d.get('status') == "WARNING"]
        passed = [d for d in diagnostics if d.get('status') == "PASS"]

        prompt = f"""# System Administration Diagnostic Brief
You are an expert Senior Systems Administrator and IT Troubleshooting Specialist.
I ran an automated system health diagnostic scan on this machine using the Portable SysAdmin Toolkit.
Please analyze the diagnostics below, identify root causes, provide exact copy-pasteable terminal commands to fix each issue, and guide me through resolution.

## 💻 Machine Profile
- Hostname: {hostname}
- Operating System: {os_info} ({release})
- Architecture: {arch}
- Scan Time: {gen_time}

## 📊 Executive Summary
- Total Checks: {len(diagnostics)}
- Critical Failures: {len(failed)}
- Warnings: {len(warnings)}
- Passed Checks: {len(passed)}

"""
        if failed or warnings:
            prompt += "## 🚨 Issues Requiring Remediation\n\n"
            issue_num = 1
            for d in failed:
                cat = str(d.get('category', 'general')).upper()
                test = str(d.get('test', 'unknown'))
                msg = str(d.get('message', ''))
                sev = str(d.get('severity', 'HIGH')).upper()
                prompt += f"### Issue #{issue_num}: [FAIL - {sev}] {cat}: {test}\n"
                prompt += f"- **Description**: {msg}\n"
                evidence = d.get('evidence')
                if evidence:
                    prompt += f"- **Telemetry / Error Log**:\n```json\n{json.dumps(evidence, indent=2)}\n```\n\n"
                else:
                    prompt += "\n"
                issue_num += 1

            for d in warnings:
                cat = str(d.get('category', 'general')).upper()
                test = str(d.get('test', 'unknown'))
                msg = str(d.get('message', ''))
                sev = str(d.get('severity', 'MEDIUM')).upper()
                prompt += f"### Issue #{issue_num}: [WARNING - {sev}] {cat}: {test}\n"
                prompt += f"- **Description**: {msg}\n"
                evidence = d.get('evidence')
                if evidence:
                    prompt += f"- **Telemetry / Error Log**:\n```json\n{json.dumps(evidence, indent=2)}\n```\n\n"
                else:
                    prompt += "\n"
                issue_num += 1
        else:
            prompt += "## 🚨 Issues Requiring Remediation\nNo failures or warnings detected. All tests passed.\n\n"

        if passed:
            prompt += "## ✅ Verified Healthy Components\n"
            for d in passed:
                prompt += f"- [{d.get('category', 'general')}] {d.get('test')}: {d.get('message', 'OK')}\n"
            prompt += "\n"

        if actions:
            prompt += "## 🛠️ Prior Remediation Actions Executed\n"
            for a in actions:
                st = "SUCCESS" if a.get('success') else "FAILED"
                prompt += f"- {a.get('action_name')}: {st} - {a.get('message')}\n"
            prompt += "\n"

        prompt += f"""## 🎯 Instructions for the AI Assistant:
Based strictly on this machine's operating system ({os_info}), please provide:
1. **Root Cause Analysis**: For each failure/warning, explain what happened and why it occurred in plain English.
2. **Step-by-Step Fix Commands**: Give the EXACT terminal/shell commands to fix the issues. Format them as copy-pasteable blocks with brief explanations.
3. **Verification Command**: The specific command to run to confirm the issue is fixed.
4. **Interactive Support**: I will run your instructions and reply with any terminal output or errors. Be ready to continue troubleshooting with me.
"""
        return prompt

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
                        
        # Generate and save Online AI Diagnostic Prompt
        ai_prompt_text = self.generate_ai_prompt(diagnostics, actions)
        prompt_out_file = os.path.join(self.session_log_dir, "ai_prompt.txt")
        try:
            with open(prompt_out_file, 'w') as f:
                f.write(ai_prompt_text)
        except Exception:
            pass
        escaped_ai_prompt = html_lib.escape(ai_prompt_text)

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
        from datetime import timezone
        gen_time = datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M:%S')

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

        /* AI Interactive Section */
        .ai-section {{
            background: linear-gradient(135deg, #1e1b4b 0%, #1e293b 100%);
            border: 2px solid #4f46e5;
            border-radius: 12px;
            padding: 1.75rem;
            margin-bottom: 2.5rem;
            color: #f8fafc;
            box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.25);
        }}
        .ai-header {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem; }}
        .ai-icon {{ font-size: 2.2rem; }}
        .ai-title {{ margin: 0; font-size: 1.35rem; color: #c7d2fe; font-weight: 700; }}
        .ai-subtitle {{ margin: 0.25rem 0 0 0; color: #cbd5e1; font-size: 0.95rem; }}
        .ai-actions {{ display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1.25rem; align-items: center; }}
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s ease;
            border: none;
        }}
        .btn-copy {{
            background-color: #4f46e5;
            color: #ffffff;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
        }}
        .btn-copy:hover {{ background-color: #4338ca; transform: translateY(-1px); }}
        .btn-link {{
            background-color: #334155;
            color: #f8fafc;
            border: 1px solid #475569;
        }}
        .btn-link:hover {{ background-color: #475569; color: #ffffff; }}
        .toast-msg {{
            display: none;
            margin-top: 0.75rem;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            background-color: #064e3b;
            color: #6ee7b7;
            border: 1px solid #059669;
            font-size: 0.9rem;
            font-weight: 500;
        }}
        .prompt-details {{ margin-top: 1.25rem; }}
        .prompt-details summary {{ cursor: pointer; color: #a5b4fc; font-weight: 600; font-size: 0.9rem; outline: none; }}
        .prompt-pre {{
            background: #0f172a;
            color: #e2e8f0;
            padding: 1.25rem;
            border-radius: 8px;
            border: 1px solid #312e81;
            overflow-x: auto;
            font-family: monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
            max-height: 320px;
            overflow-y: auto;
            margin-top: 0.75rem;
        }}

        @media print {{
            body {{ background-color: #fff; padding: 0; }}
            .card {{ box-shadow: none; }}
            .table-container {{ box-shadow: none; }}
            .ai-section {{ display: none; }}
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

        <!-- ONLINE AI ASSISTANT CARD -->
        <div class="ai-section">
            <div class="ai-header">
                <div class="ai-icon">🤖</div>
                <div>
                    <h2 class="ai-title">Troubleshoot with Online AI (ChatGPT / Claude)</h2>
                    <p class="ai-subtitle">
                        Avoid 100% CPU usage on this laptop. One-click copy this entire diagnostic brief into ChatGPT or Claude to get root-cause analysis, exact fix commands, and interactive guidance.
                    </p>
                </div>
            </div>
            <div class="ai-actions">
                <button id="copy-btn" class="btn btn-copy" onclick="copyAIPrompt()">
                    📋 Copy Prompt for ChatGPT
                </button>
                <a href="https://chatgpt.com" target="_blank" rel="noopener noreferrer" class="btn btn-link">
                    🚀 Open ChatGPT
                </a>
                <a href="https://claude.ai" target="_blank" rel="noopener noreferrer" class="btn btn-link">
                    🟣 Open Claude
                </a>
            </div>
            <div id="toast-msg" class="toast-msg">
                ✅ Diagnostic prompt copied to clipboard! Paste it into ChatGPT (Ctrl+V) to get instant solutions.
            </div>
            <details class="prompt-details">
                <summary>👁️ Preview the AI Prompt that will be copied</summary>
                <pre id="ai-prompt-content" class="prompt-pre">{escaped_ai_prompt}</pre>
            </details>
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

    <script>
    function copyAIPrompt() {
        const text = document.getElementById('ai-prompt-content').innerText;
        const btn = document.getElementById('copy-btn');
        const toast = document.getElementById('toast-msg');

        function showSuccess() {
            btn.innerHTML = '✅ Copied to Clipboard!';
            btn.style.backgroundColor = '#10b981';
            toast.style.display = 'block';
            setTimeout(() => {
                btn.innerHTML = '📋 Copy Prompt for ChatGPT';
                btn.style.backgroundColor = '';
            }, 3500);
        }

        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(showSuccess).catch(fallback);
        } else {
            fallback();
        }

        function fallback() {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.opacity = '0';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                showSuccess();
            } catch (err) {
                alert('Could not auto-copy. Please select and copy the text from the preview box below.');
            }
            document.body.removeChild(textArea);
        }
    }
    </script>
</body>
</html>
"""
        # Save report
        out_file = os.path.join(self.session_log_dir, "final-report.html")
        with open(out_file, 'w') as f:
            f.write(html)
            
        return out_file
