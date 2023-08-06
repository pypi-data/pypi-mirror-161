import os
import signal
import sys
import random
import contextlib

import numpy as np
import torch

#########################################################
### python script containing various context managers ###
#########################################################

class SimulFileHandler:
    """
    A context manager that ensures all the files asscoiated with filenames 
    must coexist. If any one file is missing upon exiting the with block
    (either because of an exception, a SIGTERM, or normal exiting),
    all the files will be deleted.
    """
    def __init__(self, *filenames):
        self.filenames = filenames
        
    def cleanup(self):
        if all([os.path.isfile(filename) for filename in self.filenames]):
            print("All files exist. No cleanup needed.")
            return
        print("Cleaning up...")
        for filename in self.filenames:
            if os.path.isfile(filename):
                os.remove(filename)
        print("Finished cleanup.")
        
    def handler(self, signum, frame):
        print(f"Received signal {signal.strsignal(signum)}.")
        sys.exit(0) # This throws the exception SystemExit, which is then caught by __exit__ and triggers self.cleanup()
    
    def __enter__(self):
        self.old_sigterm = signal.signal(signal.SIGTERM, self.handler)
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"Caught exception {exc_type}: {exc_val}")
        self.cleanup()
        signal.signal(signal.SIGTERM, self.old_sigterm)


class TmpFileHandler:
    """
    A context manager that removes all temporary files with names tmp_filenames
    upon encountering an exception or a termination signal SIGTERM.
    """
    def __init__(self, *tmp_filenames):
        self.tmp_filenames = tmp_filenames
        
    def cleanup(self):
        print("Cleaning up...")
        for tmp_filename in self.tmp_filenames:
            if os.path.isfile(tmp_filename):
                os.remove(tmp_filename)
        print("Finished cleanup.")
        
    def handler(self, signum, frame):
        print(f"Received signal {signal.strsignal(signum)}.")
        sys.exit(0) # This throws the exception SystemExit, which is then caught by __exit__ and triggers self.cleanup()
    
    def __enter__(self):
        self.old_sigterm = signal.signal(signal.SIGTERM, self.handler)
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"Caught exception {exc_type}: {exc_val}")
        self.cleanup()
        signal.signal(signal.SIGTERM, self.old_sigterm)
        
@contextlib.contextmanager
def set_seed(seed):
    python_state = random.getstate()
    np_state = np.random.get_state()
    torch_state = torch.random.get_rng_state()
    random.seed(seed)
    np.random.seed(seed)
    torch.random.manual_seed(seed)
    try:
        yield
    finally:
        random.setstate(python_state)
        np.random.set_state(np_state)
        torch.random.set_rng_state(torch_state)