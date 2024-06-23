import io
import os
import sys
from contextlib import redirect_stdout

from settings import CIR_AVAILABLE_RESPONSE_TYPES

sys.setdlopenflags(os.RTLD_GLOBAL|os.RTLD_NOW)

from pycactvs import Ens, Prop

print('hallo')



response_types = CIR_AVAILABLE_RESPONSE_TYPES

response_type = list(filter(lambda r: r.get('name') == "ficus", CIR_AVAILABLE_RESPONSE_TYPES))
print(response_type)