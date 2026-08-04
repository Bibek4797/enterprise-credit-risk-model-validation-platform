"""Page 07: Documentation & Reports Center."""

import sys
from pathlib import Path
import streamlit as st

file_path = Path(__file__).resolve()
dash_dir = file_path.parent.parent if file_path.parent.name == "pages" else file_path.parent
root_dir = dash_dir.parent
for d in [str(root_dir), str(dash_dir), str(root_dir / "src")]:
    if d not in sys.path:
        sys.path.insert(0, d)

st.set_page_config(page_title="Governance Reports", page_icon="📄", layout="wide")

st.title("📄 Governance Reports & Audit Documentation Center")
st.caption("Enterprise Credit Risk Analytics & Model Risk Governance Platform (SR 11-7 / Basel III)")
st.markdown("---")

st.markdown("""
Access, inspect, and download institutional model risk governance reports, validation audits, model cards, and executive briefs.
""")

reports_dir = root_dir / "reports"
report_files = sorted(list(reports_dir.glob("*.md"))) if reports_dir.is_dir() else []

if not report_files:
    st.info("No report files found in `reports/` directory.")
else:
    selected_report_path = st.selectbox(
        "Select Governance Document to View",
        options=report_files,
        format_func=lambda p: p.name
    )

    if selected_report_path and selected_report_path.is_file():
        with open(selected_report_path, "r", encoding="utf-8") as f:
            content = f.read()

        st.download_button(
            label=f"📥 Download {selected_report_path.name}",
            data=content.encode("utf-8"),
            file_name=selected_report_path.name,
            mime="text/markdown",
        )

        st.markdown("---")
        st.markdown(content)
