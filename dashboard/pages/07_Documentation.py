"""Page 07: Governance Reports & Audit Documentation Center."""

import sys
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
    "Access, inspect, and download institutional model risk governance reports, "
    "validation audits, model cards, and executive briefs."
    "</p>",
    unsafe_allow_html=True,
)

reports_dir  = root_dir / "reports"
report_files = sorted(reports_dir.glob("*.md")) if reports_dir.is_dir() else []

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
        format_func=lambda p: p.name,
        label_visibility="collapsed",
    )

    if selected and selected.is_file():
        content = selected.read_text(encoding="utf-8")

        col_dl, _ = st.columns([1, 4])
        with col_dl:
            st.download_button(
                label=f"📥  Download {selected.name}",
                data=content.encode("utf-8"),
                file_name=selected.name,
                mime="text/markdown",
            )

        section_divider()
        st.markdown(
            f"""
            <div style="
                background: rgba(15,30,60,0.6);
                border: 1px solid rgba(96,165,250,0.12);
                border-radius: 14px;
                padding: 1.5rem 2rem;
                backdrop-filter: blur(8px);
                color: #94a3b8;
                font-size: 0.88rem;
                line-height: 1.8;
            ">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(content)
        st.markdown("</div>", unsafe_allow_html=True)
