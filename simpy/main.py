import simpy, random, statistics

wait_list = []

class Theater(object):
    def __init__(self, env, num_cashiers, num_servers, num_ushers):
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers)
        self.server = simpy.Resource(env, num_servers)
        self.usher = simpy.Resource(env, num_ushers)

    def purchase_ticket(self, moviegoer):
        yield self.env.timeout(random.randint(1,3))

    def check_ticket(self, moviegoer):
        yield self.env.timeout(3/60)

    def sell_food(self, moviegoer):
        yield self.env.timeout(random.randint(1,5))

def go_to_movies(env, moviegoer, theater):
    print("ok")
    arrival_time = env.now
    yield env.timeout(moviegoer)
    print(arrival_time)
    with theater.cashier.request() as request:
        yield request
        yield env.process(theater.purchase_ticket(moviegoer))
    
    with theater.usher.request() as request:
        yield request
        yield env.process(theater.check_ticket(moviegoer))
    
    if random.choice([True, False]):
        with theater.server.request() as request:
            yield request
            yield env.process(theater.sell_food(moviegoer))
    cas = env.now - arrival_time
    print(cas)
    wait_list.append(cas)

def run_theater(num_cashiers, num_servers, num_ushers):
    
    env = simpy.Environment()
    theater = Theater(env, num_cashiers, num_servers, num_ushers)
    
    for moviegoer in range(3):
        print("ok"+str(moviegoer))
        env.process(go_to_movies(env,moviegoer, theater))

    '''
    while True:
        yield env.timeout(0.20)
    
        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theater))
    '''

envr = simpy.Environment()
run_theater(2 , 2 , 2)


    