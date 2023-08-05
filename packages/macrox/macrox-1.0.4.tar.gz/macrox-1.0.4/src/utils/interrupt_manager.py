class InterruptManager():
    def __init__(self):
        self.interrupts = []

    def add(self, int_obj):
        self.interrupts.append(int_obj)

    def kill_all(self):
        for obj in self.interrupts:
            obj.kill = True
    
    def pause_all(self):
        for obj in self.interrupts:
            obj.pause()
    
    def resume_all(self):
        for obj in self.interrupts:
            obj.resume()