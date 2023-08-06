#!/bin/bash

python3 -m cProfile -o /tmp/pmp_profile.cprof ./pms/main.py
pyprof2calltree -k -i /tmp/pmp_profile.cprof
