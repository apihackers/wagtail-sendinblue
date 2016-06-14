# Automatically register extension if django jinja is installed
from django_jinja import library
from ..jinja  import SendinBlueExtension

library.extension(SendinBlueExtension)
