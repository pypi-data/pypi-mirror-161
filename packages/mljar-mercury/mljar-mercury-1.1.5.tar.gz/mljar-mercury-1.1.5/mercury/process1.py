import nbformat
import json
import joblib
from jupyter_client import MultiKernelManager
from nbconvert.preprocessors import ExecutePreprocessor

mkm = MultiKernelManager()
mkm.start_kernel(kernel_name="python3", kernel_id="some-kernel")
km = mkm.get_kernel("some-kernel") # the kernel connection file is not created

print(km.get_connection_info())

nb1 = nbformat.v4.new_notebook()

nb1["cells"] = [nbformat.v4.new_code_cell("a = 13")]

ep = ExecutePreprocessor()
ep.preprocess(nb1, km=km)

print(nb1.cells)

print(km.provisioner.process.pid)


