#!/usr/bin/env python
import os
import sys

sys.path.insert(0, "..")
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "topic_space_service.settings")

    from django.core.management import execute_from_command_line

    import topic_space_app.views # load the data to memory
    
    execute_from_command_line(sys.argv)
