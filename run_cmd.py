from __future__ import print_function
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue, Empty
import os
import atexit

io_q = Queue()
procs = []

@atexit.register
def kill_subprocesses():
    for proc in procs:
      proc.kill()

def stream_watcher( identifier, stream ):

  for line in stream:
    io_q.put((identifier, line))

  if not stream.closed:
    stream.close()

def wait_for_process(proc, bequiet ):

  while True:
    try:
      item = io_q.get( True, 1 )
    except Empty:
      # no output in either stream for a second. Done?
      if proc.poll() is not None:
        break
    else:
      if bequiet:
        pass
      else:
        identifier, line = item
        print( identifier + ':' + str( line ) )

def run_cmd( command_text, command_arguments=None, bequiet=True ):

  command_list = []
  command_list.append( command_text )

  if command_arguments is not None:
    [command_list.append( listitem ) for listitem in command_arguments]
    print( *command_list, sep=',' )
    print( '   => current directory: ' + os.getcwd() )
    proc = Popen( command_list, stdout=PIPE, stderr=PIPE )
  else:
    print( *command_list, sep=',' )
    print( '   => current directory: ' + os.getcwd() )
    proc = Popen( command_list, stdout=PIPE, stderr=PIPE )

  Thread( target=stream_watcher, name='stdout-watcher', args=('STDOUT', proc.stdout)).start()
  Thread( target=stream_watcher, name='stderr-watcher', args=('STDERR', proc.stderr)).start()
  Thread( target=wait_for_process(proc, bequiet), name='proc_wait').start()
  #proc.communicate()
  return proc.returncode
