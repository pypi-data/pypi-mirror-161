#  Copyright (c) 2017-2022 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.

import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watchdog(FileSystemEventHandler):

    def __init__(self,queue,path='.') -> None:
        self._queue=queue
        super().__init__()
        self._observer=Observer()
        self._observer.schedule(self, path,recursive=True)

    def process(self,path):
        self._queue.put(path)

    def on_created(self, event):
        logging.info('%s moved' %event.src_path)
        self.process(event.src_path)

    def on_moved(self, event):
        logging.info('%s created' %event.dest_path)
        self.process(event.dest_path)
    
#    def on_modified(self, event):
#        self.process(event)
        
    def start(self):
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()
