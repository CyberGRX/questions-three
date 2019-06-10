import sys

from .junit2jenkins_status import junit2jenkins_status

argv = sys.argv
if len(argv) < 2:
    print('Please specify a path which contains JUnit XML reports')
    exit(1)
print(junit2jenkins_status(path=sys.argv[1]))
