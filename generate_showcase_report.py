import os
import markdown
from datetime import datetime, timezone

# Ensure docs directory exists
os.makedirs("docs", exist_ok=True)

# Read the cheat sheet
with open("docs/cheat_sheets/ifs_solution_architect_framework.md", "r", encoding="utf-8") as f:
    cheat_sheet_md = f.read()

# Read the execution output from Omarchy compute
execution_log = ""
if os.path.exists("test_run_variance_output.txt"):
    with open("test_run_variance_output.txt", "r", encoding="utf-8") as f:
        execution_log = f.read()
else:
    execution_log = "[INFO] No test_run_variance_output.txt found. Run lakehouse_pipeline and pytest first."

html_body = markdown.markdown(cheat_sheet_md, extensions=['tables', 'fenced_code'])

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CIRCOR IFS Solution Architecture Showcase</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 960px; margin: 40px auto; padding: 0 20px; color: #24292e; background-color: #f6f8fa; }}
  .container {{ background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  h1, h2, h3 {{ color: #111827; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
  th, td {{ border: 1px solid #d1d5db; padding: 12px; text-align: left; }}
  th {{ background-color: #f3f4f6; }}
  pre {{ background: #1f2937; color: #f9fafb; padding: 16px; border-radius: 6px; overflow-x: auto; font-family: "Courier New", Courier, monospace; }}
  .badge {{ display: inline-block; padding: 4px 8px; font-size: 12px; font-weight: bold; background: #0284c7; color: white; border-radius: 4px; margin-bottom: 12px; }}
</style>
</head>
<body>
<div class="container">
  <span class="badge">Architecture Benchmark & Verification Report</span>
  <p><em>Generated from local Omarchy compute node: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</em></p>
  {html_body}
  <hr style="margin: 32px 0;">
  <h2>5. Live Engine Output (Executed on Omarchy Local Node)</h2>
  <pre><code>{execution_log}</code></pre>
</div>
</body>
</html>
"""

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print("Report generated successfully at docs/index.html")
