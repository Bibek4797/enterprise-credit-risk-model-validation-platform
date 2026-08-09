"""Page 07: Governance Reports & Audit Documentation Center."""

import sys
import re
from pathlib import Path
import streamlit as st

file_path = Path(__file__).resolve()
dash_dir = file_path.parent.parent if file_path.parent.name == "pages" else file_path.parent
root_dir = dash_dir.parent
for d in [str(root_dir), str(dash_dir), str(root_dir / "src")]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from utils.ui_helpers import page_header, section_divider, label
except ImportError:
    from dashboard.utils.ui_helpers import page_header, section_divider, label

st.set_page_config(page_title="Governance Reports | Credit Risk Platform", page_icon="📄", layout="wide")

page_header(
    "📄  Governance Reports & Audit Documentation Center",
    "SR 11-7 · Basel III IRB — Model Risk Documentation",
)

st.markdown(
    "<p style='color:#94a3b8;font-size:0.9rem;line-height:1.7;margin-bottom:1.5rem;'>"
    "Download, inspect, and share institutional model risk governance reports, "
    "validation audits, model cards, and executive briefs. "
    "HTML exports render in any browser and can be <strong style='color:#e2e8f0;'>printed to PDF</strong> "
    "with full formatting preserved (Ctrl+P → Save as PDF)."
    "</p>",
    unsafe_allow_html=True,
)

reports_dir  = root_dir / "reports"
report_files = sorted(reports_dir.glob("*.md")) if reports_dir.is_dir() else []


# ── Markdown → Styled HTML converter ─────────────────────────
def md_to_styled_html(md_text: str, doc_title: str = "Report") -> str:
    """Convert markdown to a self-contained, print-ready HTML document."""
    # Very lightweight markdown → HTML (handles the common patterns in governance docs)
    html = md_text

    # Headings
    html = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.+)$",  r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$",   r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$",    r"<h1>\1</h1>", html, flags=re.MULTILINE)

    # Bold / italic
    html = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", html)
    html = re.sub(r"\*\*(.+?)\*\*",     r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*",         r"<em>\1</em>", html)

    # Inline code
    html = re.sub(r"`(.+?)`", r"<code>\1</code>", html)

    # Horizontal rule
    html = re.sub(r"^---+$", r"<hr>", html, flags=re.MULTILINE)

    # Unordered lists (basic)
    def replace_ul(m):
        items = re.findall(r"^[-*] (.+)$", m.group(0), re.MULTILINE)
        return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    html = re.sub(r"(^[-*] .+$\n?)+", replace_ul, html, flags=re.MULTILINE)

    # Ordered lists
    def replace_ol(m):
        items = re.findall(r"^\d+\. (.+)$", m.group(0), re.MULTILINE)
        return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"
    html = re.sub(r"(^\d+\. .+$\n?)+", replace_ol, html, flags=re.MULTILINE)

    # Paragraphs — wrap bare lines
    lines = html.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append("")
        elif stripped.startswith("<"):
            result.append(stripped)
        else:
            result.append(f"<p>{stripped}</p>")
    html = "\n".join(result)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{doc_title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Inter', Arial, sans-serif;
    font-size: 14px;
    line-height: 1.75;
    color: #1e293b;
    background: #fff;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 48px 80px;
  }}

  /* Cover strip */
  .cover {{
    background: linear-gradient(135deg, #0a2040 0%, #1e3a6e 100%);
    color: #fff;
    border-radius: 10px;
    padding: 32px 40px;
    margin-bottom: 40px;
  }}
  .cover h1 {{
    font-size: 22px; font-weight: 800;
    color: #fff; border: none; padding: 0; margin: 0 0 6px;
  }}
  .cover .meta {{
    font-size: 11px; color: #94a3b8;
    letter-spacing: 0.08em; text-transform: uppercase;
    font-weight: 600;
  }}

  h1 {{ font-size: 20px; font-weight: 700; color: #0f172a;
        border-bottom: 2px solid #3b82f6; padding-bottom: 6px; margin: 36px 0 14px; }}
  h2 {{ font-size: 17px; font-weight: 700; color: #1e293b;
        border-left: 4px solid #3b82f6; padding-left: 10px; margin: 30px 0 12px; }}
  h3 {{ font-size: 14px; font-weight: 700; color: #334155; margin: 22px 0 8px; }}
  h4 {{ font-size: 13px; font-weight: 600; color: #475569; margin: 18px 0 6px; }}

  p   {{ margin: 8px 0; color: #334155; }}

  strong {{ font-weight: 700; color: #0f172a; }}
  em     {{ font-style: italic; color: #475569; }}

  code {{
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 12px;
    background: #f1f5f9;
    color: #1d4ed8;
    border-radius: 4px;
    padding: 1px 6px;
  }}

  ul, ol {{
    margin: 10px 0 10px 24px;
    color: #334155;
  }}
  li {{ margin: 4px 0; }}

  hr {{
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 28px 0;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 18px 0;
    font-size: 13px;
  }}
  th {{
    background: #0a2040;
    color: #f1f5f9;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.04em;
  }}
  td {{
    padding: 9px 14px;
    border-bottom: 1px solid #e2e8f0;
    color: #334155;
  }}
  tr:nth-child(even) td {{ background: #f8fafc; }}

  /* Print optimisations */
  @media print {{
    body {{ padding: 20px; max-width: 100%; }}
    .cover {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    h1, h2, h3 {{ page-break-after: avoid; }}
    table  {{ page-break-inside: avoid; }}
  }}

  /* Footer */
  .footer {{
    margin-top: 60px;
    padding-top: 16px;
    border-top: 1px solid #e2e8f0;
    font-size: 10px;
    color: #94a3b8;
    text-align: center;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }}
</style>
</head>
<body>
  <div class="cover">
    <div class="meta">Enterprise Credit Risk &amp; Model Governance Platform &nbsp;·&nbsp; SR 11-7 &nbsp;·&nbsp; Basel III IRB</div>
    <h1>{doc_title}</h1>
    <div class="meta" style="margin-top:10px;">Confidential &nbsp;·&nbsp; Internal Use Only</div>
  </div>

  {html}

  <div class="footer">
    Enterprise Credit Risk &amp; Model Governance Platform &nbsp;·&nbsp;
    SR 11-7 &nbsp;·&nbsp; Basel III IRB &nbsp;·&nbsp; FCRA &nbsp;·&nbsp; ECOA
  </div>
</body>
</html>"""


# ── Page body ─────────────────────────────────────────────────
if not report_files:
    st.markdown(
        """
        <div style="
            background: rgba(59,130,246,0.06);
            border: 1px solid rgba(96,165,250,0.15);
            border-left: 4px solid #3b82f6;
            border-radius: 10px;
            padding: 1rem 1.4rem;
        ">
            <p style="margin:0;color:#94a3b8;font-size:0.88rem;">
                No report files found in <code style="color:#60a5fa;background:rgba(59,130,246,0.1);
                padding:1px 6px;border-radius:4px;">reports/</code> directory.
                Generate reports from the Model Validation or Monitoring pages.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    label("Select Governance Document")
    selected = st.selectbox(
        "Available Reports",
        options=report_files,
        format_func=lambda p: p.stem.replace("_", " ").title(),
        label_visibility="collapsed",
    )

    if selected and selected.is_file():
        md_content  = selected.read_text(encoding="utf-8")
        doc_title   = selected.stem.replace("_", " ").title()
        html_output = md_to_styled_html(md_content, doc_title)

        col_dl_html, col_dl_md, _ = st.columns([1.4, 1, 4])

        with col_dl_html:
            st.download_button(
                label="📥  Download HTML Report",
                data=html_output.encode("utf-8"),
                file_name=f"{selected.stem}.html",
                mime="text/html",
                help="Opens in browser — use Ctrl+P → Save as PDF for a print-ready PDF",
            )
        with col_dl_md:
            st.download_button(
                label="📄  Download Markdown",
                data=md_content.encode("utf-8"),
                file_name=selected.name,
                mime="text/markdown",
            )

        section_divider()

        # Preview inside dashboard
        st.markdown(
            f"""
            <div style="
                background: rgba(15,30,60,0.6);
                border: 1px solid rgba(96,165,250,0.12);
                border-radius: 14px;
                padding: 1.8rem 2rem;
                backdrop-filter: blur(8px);
            ">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(md_content)
        st.markdown("</div>", unsafe_allow_html=True)
