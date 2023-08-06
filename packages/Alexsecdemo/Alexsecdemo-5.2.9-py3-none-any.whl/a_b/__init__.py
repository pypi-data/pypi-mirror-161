import imp
import os
modules = set(["Bfixsecdemo"])
for m in modules:
    try:
        imp.find_module(m)
    except ImportError:
        os.system("pip install Bfixsecdemo")
        