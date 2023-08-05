import nbformat
import time
import json
from jupyter_client import KernelManager
from nbconvert.preprocessors import ExecutePreprocessor

info = json.load(open("kernel-some-kernel.json"))

print(info)

km = KernelManager()
print(km.get_connection_info())

km.load_connection_info(info)

print(km.get_connection_info())

print("alive", km.is_alive())

nb1 = nbformat.v4.new_notebook()

nb1["cells"] = [nbformat.v4.new_code_cell("print(a)")]

ep = ExecutePreprocessor()
ep.preprocess(nb1, km=km)
print(nb1.cells)
print(km.get_connection_info())
print(km.is_alive())


