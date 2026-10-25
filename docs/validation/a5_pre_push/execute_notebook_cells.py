"""Verify actual notebook cells in-process when this runner blocks kernel sockets.

This is not a fresh-kernel or student-computer run. Use the normal notebook
command in a Jupyter-capable environment. Run this fallback from project root:
    uv run --locked python docs/validation/a5_pre_push/execute_notebook_cells.py
"""
from pathlib import Path
import json
import sys

import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output


def main():
    """Execute every real code cell and serialize outputs only after success."""
    root=Path(__file__).resolve().parents[3]
    path=root/'notebooks/assignment05_eda.ipynb'
    notebook=nbformat.read(path,as_version=4)
    shell=InteractiveShell.instance()
    executed=0
    for cell in notebook.cells:
        if cell.cell_type!='code':
            continue
        with capture_output(stdout=True,stderr=True,display=True) as captured:
            result=shell.run_cell(cell.source,store_history=True)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError(f'Notebook code cell {executed+1} failed') from (result.error_before_exec or result.error_in_exec)
        executed+=1
        cell.execution_count=executed
        cell.outputs=[]
        for stream in ('stdout','stderr'):
            value=getattr(captured,stream)
            if value:
                cell.outputs.append(nbformat.v4.new_output('stream',name=stream,text=value))
        for output in captured.outputs:
            cell.outputs.append(nbformat.v4.new_output('display_data',data=output.data,metadata=output.metadata))
    notebook.metadata['language_info']['version']=sys.version.split()[0]
    notebook.metadata['a5_verification']={
        'method':'OpenAI assistant: IPython in-process execution',
        'code_cells':executed,'errors':0,
        'limitation':'This run did not launch a fresh Jupyter kernel or execute on the student computer. See docs/LOCAL_EXECUTION_EVIDENCE.md for separately attributed checks.'}
    nbformat.validate(notebook)
    nbformat.write(notebook,path)
    print(json.dumps({'status':'pass','method':'IPython in-process',
                      'code_cells':executed,'errors':0,'fresh_kernel_verified':False,
                      'python':sys.version.split()[0]},indent=2))


if __name__=='__main__':
    main()
