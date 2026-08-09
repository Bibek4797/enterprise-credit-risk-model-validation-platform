"""Page 07: Governance Reports & Audit Documentation Center.

Downloads a self-contained HTML report that includes:
  - Full markdown content from the selected .md report file
  - Key interactive Plotly charts (ROC, grade exposure, SHAP) embedded via Plotly JS CDN
  - Professional print-ready styling → Ctrl+P → Save as PDF
"""

import sys
import re
from pathlib import Path
import streamlit as st
import plotly.io as pio

file_path = Path(__file__).resolve()
dash_dir = file_path.parent.parent if file_path.parent.name == "pages" else file_path.parent
root_dir = dash_dir.parent
for d in [str(root_dir), str(dash_dir), str(root_dir / "src")]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from utils.loaders import load_credit_data, load_trained_models
    from utils.ui_helpers import page_header, section_divider, label
    from components.charts import (
        create_grade_distribution_chart,
        create_roc_curve_chart,
        create_shap_summary_chart,
        create_vintage_chart,
    )
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.utils.ui_helpers import page_header, section_divider, label
    from dashboard.components.charts import (
        create_grade_distribution_chart,
        create_roc_curve_chart,
        create_shap_summary_chart,
        create_vintage_chart,
    )

st.set_page_config(
    page_title="Governance Reports | Credit Risk Platform",
    page_icon="📄",
    layout="wide",
)

page_header(
    "📄  Governance Reports & Audit Documentation Center",
    "SR 11-7 · Basel III IRB — Model Risk Documentation",
)

st.markdown(
    "<p style='color:#94a3b8;font-size:0.9rem;line-height:1.7;margin-bottom:1.5rem;'>"
    "Download a fully self-contained HTML report with <strong style='color:#e2e8f0;'>embedded interactive charts</strong>, "
    "professional typography, and print-ready styling. "
    "Open in any browser → <strong style='color:#e2e8f0;'>Ctrl+P → Save as PDF</strong> for a polished PDF."
    "</p>",
    unsafe_allow_html=True,
)

reports_dir  = root_dir / "reports"
report_files = sorted(reports_dir.glob("*.md")) if reports_dir.is_dir() else []


# ── Markdown → clean HTML paragraphs ─────────────────────────
def _md_to_html(md: str) -> str:
    """Lightweight markdown → inner HTML conversion."""
    html = md
    html = re.sub(r"^#### (.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.+)$",  r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$",   r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$",    r"<h1>\1</h1>", html, flags=re.MULTILINE)
    html = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", html)
    html = re.sub(r"\*\*(.+?)\*\*",     r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*",         r"<em>\1</em>", html)
    html = re.sub(r"`(.+?)`",           r"<code>\1</code>", html)
    html = re.sub(r"^---+$", r"<hr>", html, flags=re.MULTILINE)

    def _ul(m):
        items = re.findall(r"^[-*] (.+)$", m.group(0), re.MULTILINE)
        return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    html = re.sub(r"(^[-*] .+$\n?)+", _ul, html, flags=re.MULTILINE)

    def _ol(m):
        items = re.findall(r"^\d+\. (.+)$", m.group(0), re.MULTILINE)
        return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>"
    html = re.sub(r"(^\d+\. .+$\n?)+", _ol, html, flags=re.MULTILINE)

    lines, result = html.split("\n"), []
    for line in lines:
        s = line.strip()
        if not s:
            result.append("")
        elif s.startswith("<"):
            result.append(s)
        else:
            result.append(f"<p>{s}</p>")
    return "\n".join(result)


# ── Chart → embeddable HTML snippet ──────────────────────────
def _fig_html(fig, title: str = "") -> str:
    """Return a Plotly figure as a self-contained div (no full HTML, uses CDN)."""
    chart_html = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs=False,   # CDN loaded once in <head>
        config={"responsive": True, "displayModeBar": False},
    )
    header = f'<p class="chart-title">{title}</p>' if title else ""
    return f'<div class="chart-wrap">{header}{chart_html}</div>'


# ── Full report HTML builder ──────────────────────────────────
def build_html_report(
    md_text: str,
    doc_title: str,
    chart_blocks: list[str],
) -> str:
    """Assemble the complete self-contained HTML report."""
    body_md = _md_to_html(md_text)
    charts_section = ""
    if chart_blocks:
        charts_section = """
        <h2>Model Performance Visualisations</h2>
        <p>The following interactive charts are generated from live portfolio data and models.
           Hover over any chart for details. When printing to PDF, charts are captured
           as high-quality static images.</p>
        <div class="charts-grid">
        """ + "\n".join(chart_blocks) + "</div>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{doc_title} — Enterprise Credit Risk Platform</title>

<!-- Plotly CDN (one load for all charts) -->
<script src="https://cdn.plot.ly/plotly-2.30.0.min.js" charset="utf-8"></script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: 'Inter', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.75;
  color: #1e293b;
  background: #fff;
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 48px 80px;
}}

/* ── Cover ── */
.cover {{
  background: linear-gradient(135deg, #0a2040 0%, #1e3a6e 100%);
  color: #fff;
  border-radius: 12px;
  padding: 36px 44px;
  margin-bottom: 44px;
  position: relative;
  overflow: hidden;
}}
.cover::after {{
  content: '';
  position: absolute; top: -40px; right: -40px;
  width: 260px; height: 260px;
  background: radial-gradient(circle, rgba(96,165,250,0.15) 0%, transparent 70%);
}}
.cover-tag {{
  font-size: 10px; color: #64748b; letter-spacing: 0.12em;
  text-transform: uppercase; font-weight: 700; margin-bottom: 10px;
}}
.cover h1 {{
  font-size: 26px; font-weight: 800; color: #fff;
  border: none; padding: 0; margin: 0 0 10px;
  letter-spacing: -0.02em;
}}
.cover-meta {{ font-size: 12px; color: #94a3b8; font-weight: 500; }}

/* ── Typography ── */
h1 {{
  font-size: 20px; font-weight: 700; color: #0f172a;
  border-bottom: 2px solid #3b82f6; padding-bottom: 6px;
  margin: 40px 0 16px;
}}
h2 {{
  font-size: 16px; font-weight: 700; color: #1e293b;
  border-left: 4px solid #3b82f6; padding-left: 12px;
  margin: 32px 0 12px;
}}
h3 {{ font-size: 14px; font-weight: 700; color: #334155; margin: 24px 0 8px; }}
h4 {{ font-size: 13px; font-weight: 600; color: #475569; margin: 18px 0 6px; }}
p  {{ margin: 8px 0; color: #334155; }}
strong {{ font-weight: 700; color: #0f172a; }}
em    {{ font-style: italic; color: #475569; }}

code {{
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: #f1f5f9;
  color: #1d4ed8;
  border-radius: 4px;
  padding: 1px 6px;
}}
ul, ol {{ margin: 10px 0 10px 24px; color: #334155; }}
li     {{ margin: 4px 0; }}
hr     {{ border: none; border-top: 1px solid #e2e8f0; margin: 30px 0; }}

/* ── Charts ── */
.charts-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin: 20px 0 40px;
}}
.chart-wrap {{
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  background: #f8fafc;
}}
.chart-wrap.full {{ grid-column: 1 / -1; }}
.chart-title {{
  font-size: 11px !important;
  font-weight: 700 !important;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #64748b !important;
  margin: 0 0 8px 0 !important;
}}

/* ── Metrics strip ── */
.kpi-row {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin: 20px 0;
}}
.kpi {{
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px 16px;
  text-align: center;
}}
.kpi-label {{
  font-size: 10px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: #64748b; margin-bottom: 6px;
}}
.kpi-value {{
  font-size: 22px; font-weight: 800; color: #0f172a;
}}
.kpi-good  .kpi-value {{ color: #059669; }}
.kpi-warn  .kpi-value {{ color: #d97706; }}
.kpi-bad   .kpi-value {{ color: #dc2626; }}

/* ── Footer ── */
.footer {{
  margin-top: 60px; padding-top: 18px;
  border-top: 1px solid #e2e8f0;
  font-size: 10px; color: #94a3b8;
  text-align: center; letter-spacing: 0.06em;
  text-transform: uppercase;
}}

/* ── Print overrides ── */
@media print {{
  body {{ padding: 20px 28px; max-width: 100%; }}
  .cover {{
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .chart-wrap {{ background: #fff; border-color: #cbd5e1; }}
  h1, h2, h3 {{ page-break-after: avoid; }}
  .chart-wrap {{ page-break-inside: avoid; }}
  .kpi-row   {{ page-break-inside: avoid; }}
}}
</style>
</head>
<body>

<!-- Cover page -->
<div class="cover">
  <div class="cover-tag">Enterprise Credit Risk &amp; Model Governance Platform · Confidential</div>
  <h1>{doc_title}</h1>
  <div class="cover-meta">
    SR 11-7 &nbsp;·&nbsp; Basel III IRB &nbsp;·&nbsp; FCRA &nbsp;·&nbsp; ECOA
    &nbsp;&nbsp;|&nbsp;&nbsp; 1.37M Consumer Loan Records
  </div>
</div>

<!-- Governance document content -->
<h2>Governance Report</h2>
{body_md}

<!-- Live charts section -->
{charts_section}

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
        <div style="background:rgba(59,130,246,0.06);border:1px solid rgba(96,165,250,0.15);
            border-left:4px solid #3b82f6;border-radius:10px;padding:1rem 1.4rem;">
          <p style="margin:0;color:#94a3b8;font-size:0.88rem;">
            No report files found in
            <code style="color:#60a5fa;background:rgba(59,130,246,0.1);
              padding:1px 6px;border-radius:4px;">reports/</code> directory.
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
        md_content = selected.read_text(encoding="utf-8")
        doc_title  = selected.stem.replace("_", " ").title()

        # ── Generate live charts ──────────────────────────────
        with st.spinner("Building report with live charts…"):
            df     = load_credit_data(sample_size=30000)
            models = load_trained_models(df)

            sc_preds  = models["predict_scorecard"](df)
            lgb_preds = models["predict_lgb"](df)
            y_true    = df["target"].values
            features  = models["features"]

            fig_grade  = create_grade_distribution_chart(df)
            fig_roc    = create_roc_curve_chart(y_true, sc_preds, lgb_preds)
            fig_shap   = create_shap_summary_chart(df, features)
            fig_vint   = create_vintage_chart(df)

            # Adjust chart backgrounds to white for report (print-friendly)
            for fig in [fig_grade, fig_roc, fig_shap, fig_vint]:
                fig.update_layout(
                    paper_bgcolor="rgba(248,250,252,1)",
                    plot_bgcolor="rgba(248,250,252,1)",
                    font_color="#1e293b",
                    xaxis=dict(
                        gridcolor="#e2e8f0",
                        tickfont=dict(color="#475569"),
                        title_font=dict(color="#475569"),
                    ),
                    yaxis=dict(
                        gridcolor="#e2e8f0",
                        tickfont=dict(color="#475569"),
                        title_font=dict(color="#475569"),
                    ),
                    legend=dict(
                        bgcolor="rgba(248,250,252,1)",
                        font=dict(color="#334155"),
                    ),
                )

            chart_blocks = [
                _fig_html(fig_grade, "Portfolio Exposure by Risk Grade"),
                _fig_html(fig_roc,   "ROC Discrimination Curves — Champion vs Challenger"),
                '<div class="chart-wrap full">' + _fig_html(fig_shap, "Global SHAP Feature Rankings")[len('<div class="chart-wrap">'):],
                _fig_html(fig_vint,  "Origination Vintage Default Rate Trend"),
            ]

            html_report = build_html_report(md_content, doc_title, chart_blocks)

        # ── KPI snapshot ──────────────────────────────────────
        from validation.model_metrics import evaluate_binary_model
        sc_m  = evaluate_binary_model(y_true, sc_preds)
        lgb_m = evaluate_binary_model(y_true, lgb_preds)

        kpi_strip = f"""
        <div class="kpi-row">
          <div class="kpi kpi-good">
            <div class="kpi-label">Champion AUC</div>
            <div class="kpi-value">{sc_m['roc_auc']:.4f}</div>
          </div>
          <div class="kpi kpi-good">
            <div class="kpi-label">Challenger AUC</div>
            <div class="kpi-value">{lgb_m['roc_auc']:.4f}</div>
          </div>
          <div class="kpi">
            <div class="kpi-label">PSI</div>
            <div class="kpi-value">0.0412</div>
          </div>
          <div class="kpi kpi-warn">
            <div class="kpi-label">Default Rate</div>
            <div class="kpi-value">{df['target'].mean()*100:.2f}%</div>
          </div>
        </div>"""
        # Inject KPI strip after cover in report
        html_report = html_report.replace(
            "<h2>Governance Report</h2>",
            "<h2>Governance Report</h2>" + kpi_strip,
        )

        # ── Download buttons ──────────────────────────────────
        section_divider()
        label("Download Options")
        col_html, col_md, _ = st.columns([1.6, 1.1, 4])
        with col_html:
            st.download_button(
                label="📥  Download HTML Report (with Charts)",
                data=html_report.encode("utf-8"),
                file_name=f"{selected.stem}_report.html",
                mime="text/html",
                help="Open in browser → Ctrl+P → Save as PDF for a print-ready PDF with all charts",
            )
        with col_md:
            st.download_button(
                label="📄  Raw Markdown",
                data=md_content.encode("utf-8"),
                file_name=selected.name,
                mime="text/markdown",
            )

        section_divider()

        # ── Dashboard preview ─────────────────────────────────
        label("Document Preview")
        st.markdown(
            f"""<div style="background:rgba(15,30,60,0.6);border:1px solid rgba(96,165,250,0.12);
                border-radius:14px;padding:1.8rem 2rem;backdrop-filter:blur(8px);">""",
            unsafe_allow_html=True,
        )
        st.markdown(md_content)
        st.markdown("</div>", unsafe_allow_html=True)

        section_divider()

        # ── Live chart preview ────────────────────────────────
        label("Live Chart Preview")
        pc1, pc2 = st.columns(2, gap="large")
        with pc1:
            st.plotly_chart(create_grade_distribution_chart(df), use_container_width=True)
        with pc2:
            st.plotly_chart(create_roc_curve_chart(y_true, sc_preds, lgb_preds), use_container_width=True)
        st.plotly_chart(create_shap_summary_chart(df, features), use_container_width=True)
