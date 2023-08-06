#!/bin/python
import smallpower.smallPower as smallPower
from smallpower import conf
import os
from dorianUtils.comUtils import print_file

log_file = conf.LOG_FOLDER + '/dumper_smallPower.log'

__appdir = os.path.dirname(os.path.realpath(__file__))
PARENTDIR = os.path.dirname(__appdir)
log_file = PARENTDIR+ '/log/dumper_smallPower.log'
print_file(' '*30 + 'START DUMPER SMALLPOWER' + '\n',filename=log_file,mode='w')

dumperSmallPower = smallPower.SmallPower_dumper(log_file_name=log_file)

dumperSmallPower.park_database()
dumperSmallPower.start_dumping()
