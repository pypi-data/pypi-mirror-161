"""Pyinstaller hook for root module.

Ensures that the shared object libraries packaged with this Py package are
packaged in the PyInstaller package. """

from PyInstaller.utils.hooks import collect_dynamic_libs

binaries = collect_dynamic_libs('py_gs1_barcode_engine')
