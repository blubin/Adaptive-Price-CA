# Copyright (c) 2023 Benjamin Lubin and Sebastien Lahaie.
#
# This file is part of Adaptive-Price-CA
# (see https://github.com/blubin/Adaptive-Price-CA).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Restrict to a specific cpu mask
# SEE: http://stackoverflow.com/questions/15639779/why-does-multiprocessing-use-only-a-single-core-after-i-import-numpy

import os, sys
import multiprocessing

def restrict_to_cpu(cpu, hyperthread_per_core=2):
    ''' If we are on CPLEX, restrict to the given cpu.
        cpu -- which cpu to restrict to, starting from 1
        hyperthread -- how many hyperthreads per core are in the OS
                       we expect max(cpu) * hyperthread_per_core logical cores
    '''
    #Build a hyperthread mask:
    mask = 0

    # This produces adjacent answers:
    #for i in range(0, hyperthread_per_core):
    #    mask += 1 << i
    ## now put the mask where it belongs:
    #mask = mask << (cpu-1)*hyperthread_per_core

    # This produces pairs that are separated by exactly half
    # the total
    cores = multiprocessing.cpu_count()
    mask = 1 << cpu-1
    mask += 1 << cpu-1 + (cores/2)

    # now convert to a string:
    mask = "%x" % mask
    restrict_to_cpu_mask(mask)

def restrict_to_cpu_mask(mask):
    if os.name == 'nt':
        sys.stderr.write("Warning: Can't set CPU affinity for Windows.\n")
    else:
        os.system("taskset -p 0x%s %d" % (mask, os.getpid()))
