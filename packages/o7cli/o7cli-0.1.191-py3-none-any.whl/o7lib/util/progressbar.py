from time import sleep
import sys


class ProgressBar:
    def __init__(self, size=25, total=100):
        self.size = size
        self.progress = -1
        self.total = total
        self.current=0
        self.step=self.total / self.size
        self.form="[%-" + str(self.size) + "s] %i of %i"
        
        
    def Kick(self, inc=1):
        self.current += inc
        p = int(self.current / self.step)
        #print("p->", p, " self.current->", self.current)
        if p == self.progress:
            return
        
        self.progress = p
        sys.stdout.write('\r')
        sys.stdout.write(self.form % ('='*self.progress, self.current, self.total))
        sys.stdout.flush()