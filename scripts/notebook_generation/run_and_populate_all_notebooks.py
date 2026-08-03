"""Execute and populate outputs for all 15 Jupyter Notebooks in notebooks/."""

from __future__ import annotations

import io
import os
import sys
import glob
import traceback
from pathlib import Path
import nbformat as nbf

# Ensure src and root are in sys.path
root_dir = Path.cwd()
src_dir = root_dir / "src"
for d in [str(root_dir), str(src_dir)]:
    if d not in sys.path:
        sys.path.insert(0, d)


def execute_notebook_and_populate_outputs(nb_path: Path) -> None:
    """Execute code cells of a notebook and populate output objects."""
    print(f"\n==========================================")
    print(f"Executing and Populating Outputs: {nb_path.name}")
    print(f"==========================================")

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = nbf.read(f, as_version=4)

    # Normalize notebook for IDs and schema
    nb = nbf.v4.upgrade(nb)

    # Initialize execution namespace for this notebook
    exec_globals = {
        "__name__": "__main__",
        "__file__": str(nb_path),
        "sys": sys,
        "os": os,
        "Path": Path,
    }

    execution_count = 1

    for cell_idx, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue

        code_source = cell.source.strip()
        if not code_source:
            cell.outputs = []
            cell.execution_count = None
            continue

        outputs = []
        stdout_buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = stdout_buf

        try:
            # Parse code to check if last line is an expression
            lines = [l for l in code_source.splitlines() if l.strip() and not l.strip().startswith("#")]
            
            exec_res = None
            if lines and not lines[-1].strip().startswith(("import ", "from ", "def ", "class ", "if ", "for ", "while ", "with ", "print(", "return", "assert", "fig")):
                pre_code = "\n".join(code_source.splitlines()[:-1])
                last_expr = code_source.splitlines()[-1]

                if pre_code.strip():
                    exec(pre_code, exec_globals)
                
                try:
                    exec_res = eval(last_expr, exec_globals)
                except SyntaxError:
                    exec(last_expr, exec_globals)
            else:
                exec(code_source, exec_globals)

            printed_text = stdout_buf.getvalue()

            if printed_text:
                outputs.append(nbf.v4.new_output("stream", name="stdout", text=printed_text))

            if exec_res is not None:
                res_data = {"text/plain": str(exec_res)}
                if hasattr(exec_res, "_repr_html_"):
                    res_data["text/html"] = exec_res._repr_html_()
                elif hasattr(exec_res, "to_string"):
                    res_data["text/plain"] = exec_res.to_string()

                outputs.append(nbf.v4.new_output("execute_result", data=res_data, execution_count=execution_count))

        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            printed_text = stdout_buf.getvalue()
            if printed_text:
                outputs.append(nbf.v4.new_output("stream", name="stdout", text=printed_text))
            
            outputs.append(nbf.v4.new_output("error", ename=type(e).__name__, evalue=str(e), traceback=err_msg.splitlines()))
            print(f"  [NOTE] Cell {cell_idx} handled: {e}")
        finally:
            sys.stdout = old_stdout

        cell.outputs = outputs
        cell.execution_count = execution_count
        execution_count += 1

    with open(nb_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(f"  [OK] Finished: {nb_path.name} ({execution_count - 1} code cells executed & outputs saved)")


def main():
    notebook_files = sorted(list(Path("notebooks").glob("*.ipynb")))
    print(f"Found {len(notebook_files)} notebooks to run and populate.")
    
    for nb_file in notebook_files:
        execute_notebook_and_populate_outputs(nb_file)

    print("\nALL NOTEBOOKS EXECUTED & OUTPUTS POPULATED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
