import simpy, random, statistics


class Machine(object):
    def __init__(self, env, name, repairman, time):
        self.env = env
        self.name = name
        self.parts = 0
        self.broken = False
        self.time = time
        self.cas_poruchy = 0
        self.process = env.process(self.working(repairman))
        env.process(self.break_machine())

    def working(self, repairman):
        while True:
            time_done = self.time
            
            while time_done:
                try:
                    start = self.env.now
                    yield self.env.timeout(time_done)
                    time_done = 0
                except simpy.Interrupt:
                    self.broken = True
                    time_done -= self.env.now - start

                    with repairman.request() as request:
                        yield request
                        cas_poruchy = random.uniform(80.0, 200.0)
                        self.cas_poruchy += cas_poruchy
                        yield self.env.timeout(cas_poruchy)                 
                    self.broken = False       
            self.parts += 1
     
    def break_machine(self):
        while True:
            yield self.env.timeout(random.expovariate(0.001))
            if not self.broken:
                self.process.interrupt()







