"""HTML report generator for validation results"""

from datetime import datetime
from pathlib import Path

from polcomply.validators.xsd import ValidationError


def generate_html_report(
    errors: list[ValidationError],
    filename: str = "report.html",
    output_path: Path | None = None,
) -> str:
    """
    Generate HTML report from validation errors

    Args:
        errors: List of validation errors
        filename: Name of the file being validated
        output_path: Optional path to save the report

    Returns:
        HTML content as string
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_count = len(errors)
    is_valid = error_count == 0

    status_class = "valid" if is_valid else "invalid"
    status_text = "✅ VALID" if is_valid else f"❌ {error_count} ERRORS FOUND"

    # Build errors table
    if is_valid:
        errors_html = """
            <div class="success-message">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <h3>Document is valid!</h3>
                <p>Your XML document complies with FA-3 schema requirements.</p>
            </div>
        """
    else:
        error_rows = []
        for i, error in enumerate(errors):
            error_rows.append(
                f"""
                <tr>
                    <td>{i+1}</td>
                    <td class="error-location">Line {error.line or 'N/A'}, Col {error.column or 'N/A'}</td>
                    <td><span class="error-code">{error.code or 'VALIDATION_ERROR'}</span></td>
                    <td class="error-message">{error.message}</td>
                </tr>
            """
            )

        errors_html = f"""
            <table class="error-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Location</th>
                        <th>Error Code</th>
                        <th>Message</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(error_rows)}
                </tbody>
            </table>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PolComply - FA-3 Validation Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 0.5rem;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 0.9rem;
        }}
        .status {{
            display: inline-block;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 1rem;
        }}
        .status.valid {{
            background: #10b981;
            color: white;
        }}
        .status.invalid {{
            background: #ef4444;
            color: white;
        }}
        .report-info {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        .report-info h2 {{
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }}
        .info-item {{
            padding: 0.75rem;
            background: #f9fafb;
            border-radius: 8px;
        }}
        .info-item .label {{
            color: #666;
            font-size: 0.85rem;
            margin-bottom: 0.25rem;
        }}
        .info-item .value {{
            color: #333;
            font-weight: 600;
        }}
        .errors-section {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        .errors-section h2 {{
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }}
        .error-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .error-table th {{
            background: #f9fafb;
            padding: 0.75rem;
            text-align: left;
            font-size: 0.85rem;
            color: #666;
            border-bottom: 2px solid #e5e7eb;
        }}
        .error-table td {{
            padding: 0.75rem;
            border-bottom: 1px solid #e5e7eb;
        }}
        .error-table tr:hover {{
            background: #f9fafb;
        }}
        .error-code {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            background: #fee2e2;
            color: #dc2626;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .error-location {{
            color: #666;
            font-size: 0.85rem;
        }}
        .error-message {{
            color: #333;
        }}
        .success-message {{
            text-align: center;
            padding: 3rem;
            color: #10b981;
        }}
        .success-message svg {{
            width: 64px;
            height: 64px;
            margin-bottom: 1rem;
        }}
        .footer {{
            text-align: center;
            margin-top: 2rem;
            color: white;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 PolComply - FA-3 Validation Report</h1>
            <div class="subtitle">Polish e-invoicing compliance validation</div>
            <div class="status {status_class}">
                {status_text}
            </div>
        </div>

        <div class="report-info">
            <h2>Report Information</h2>
            <div class="info-grid">
                <div class="info-item">
                    <div class="label">File Name</div>
                    <div class="value">{filename}</div>
                </div>
                <div class="info-item">
                    <div class="label">Validation Time</div>
                    <div class="value">{timestamp}</div>
                </div>
                <div class="info-item">
                    <div class="label">Schema Version</div>
                    <div class="value">FA-3 (1-0E)</div>
                </div>
                <div class="info-item">
                    <div class="label">Total Errors</div>
                    <div class="value">{error_count}</div>
                </div>
            </div>
        </div>

        <div class="errors-section">
            <h2>Validation Results</h2>
            {errors_html}
        </div>

        <div class="footer">
            <p>Generated by PolComply v0.1.0 | <a href="https://polcomply.pl" style="color: white;">polcomply.pl</a></p>
        </div>
    </div>
</body>
</html>"""

    if output_path:
        output_path.write_text(html_content, encoding="utf-8")

    return html_content
