
from django.conf import settings 

from chemical.file.models import *

u = UserFile.objects.all().delete()

