try:
    import deveba
except ImportError:
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
    import deveba
