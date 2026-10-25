"""Execute the A5 notebook in-process when kernel sockets are unavailable.

This is a verification fallback, not a claim that nbconvert kernel execution
passed. It executes the actual five cells in order with IPython and captures
stdout, stderr, and rich display outputs. Run from the repository root:
    uv run --locked python docs/validation/a5_revision_2026-10-24/execute_notebook_inprocess.py
"""
from pathlib import Path
import json
import sys
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output


def main():
    """Run all notebook code cells and save only if every cell succeeds."""
    root=Path(__file__).resolve().parents[3]
    path=root/'notebooks/assignment05_eda.ipynb'
    notebook=nbformat.read(path,as_version=4)
    shell=InteractiveShell.instance()
    executed=0
    for cell in notebook.cells:
        if cell.cell_type!='code':
            continue
        cell.outputs=[]
        with capture_output(stdout=True,stderr=True,display=True) as captured:
            result=shell.run_cell(cell.source,store_history=True)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError(f'Notebook cell {executed+1} failed') from (result.error_before_exec or result.error_in_exec)
        executed+=1
        cell.execution_count=executed
        if captured.stdout:
            cell.outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
        if captured.stderr:
            cell.outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
        for out in captured.outputs:
            cell.outputs.append(nbformat.v4.new_output('display_data',data=out.data,metadata=out.metadata))
    notebook.metadata['language_info']['version']=sys.version.split()[0]
    notebook.metadata['a5_verification']={
        'date':'2026-10-24','method':'IPython in-process execution',
        'code_cells':executed,'errors':0,
        'limitation':'Fresh nbconvert kernel launch unavailable in this runner; independently rerun with a normal Jupyter kernel.'}
    nbformat.validate(notebook)
    nbformat.write(notebook,path)
    print(json.dumps({'status':'pass','execution_method':'IPython in-process','python':sys.version,
                      'code_cells':executed,'errors':0,'output':str(path),
                      'not_standard_kernel_run':True},indent=2))


if __name__=='__main__':
    main()
