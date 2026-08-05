"""Root Entry Point for Streamlit Community Cloud & Public Deployment Platforms."""

import sys
from pathlib import Path
import runpy

# Ensure root, dashboard, and src are in Python path
root_dir = Path(__file__).resolve().parent
dash_dir = root_dir / "dashboard"
src_dir = root_dir / "src"

for d in [str(root_dir), str(dash_dir), str(src_dir)]:
    if d not in sys.path:
        sys.path.insert(0, d)

# Execute dashboard/app.py as the primary application
app_path = dash_dir / "app.py"
runpy.run_path(str(app_path), run_name="__main__")
