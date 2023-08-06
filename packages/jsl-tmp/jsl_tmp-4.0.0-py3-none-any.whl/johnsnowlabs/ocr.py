from johnsnowlabs.abstract_base.lib_resolver import try_import_lib

if try_import_lib('sparkocr', True) and  try_import_lib('sparknlp', True):
    from sparkocr.transformers import *
    from sparkocr.enums import *
    import sparkocr
else:
    pass
