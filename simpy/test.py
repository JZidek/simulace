import simpy, random, statistics, simpy.rt, collections, datetime
import sys, os
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from datetime import timedelta

'''
#--------------------PREPAZKA BANKY-----------------------------------------------
class Zakaznik():
    def __init__(self,env, res, name, arrive):
        self.env = env
        self.res = res
        self.name = name
        self.arrive = arrive
        self.cas_v_bance = 0
        self.cas_ve_fronte = 0
        self.cas_u_prepazky = 0
        self.fronta = 0

        self.proces = env.process(self.vyrizeni())

    def vyrizeni(self):
        yield self.env.timeout(self.arrive)
        prichod = self.env.now
        print("zakaznik c.{0} dorazil do banky v {1}".format(self.name, prichod))
        self.fronta = len(self.res.queue)
        with self.res.request() as request:
            
            yield request
            na_rade = self.env.now
            print("zakaznik c.{0} se dostal na radu v {1}".format(self.name, na_rade))
            yield self.env.timeout(random.randint(4,15))
            odchod = self.env.now
            print("zakaznik c.{0} byl obslouzen a odchazi v {1}".format(self.name, odchod))
        self.cas_v_bance = odchod - prichod
        self.cas_ve_fronte = na_rade - prichod
        self.cas_u_prepazky = odchod - na_rade
        print(self.env.now)

env = simpy.Environment()
res = simpy.Resource(env, capacity=4)
zakaznici = []
x = 0
for i in range(180): 
    z = Zakaznik(env, res, i,x)
    zakaznici.append(z)
    x += random.randint(0,5)

#zakaznici = [Zakaznik(env, res, i,random.randint(1,5)) for i in range(5)]
env.run()
for i in zakaznici:
    print('zakaznik c.{0} - fronta pri prichodu: {1} / cekani ve fronte: {2} / cas u prepazky: {3} / celkovy cas v bance: {4}'.format(i.name, i.fronta, i.cas_ve_fronte, i.cas_u_prepazky, i.cas_v_bance))

#---------------------VYROBNI STROJ------------------------------------------

class Machine():
    def __init__(self, env, res, jmeno, cas_vyroby):
        self.env = env 
        self.res = res
        self.jmeno = jmeno
        self.cas_vyroby = cas_vyroby
        self.soucastky = 0
        self.t = 0.0
        self.porucha = False
        self.pocet_poruch = 0
        self.proces = env.process(self.vyroba(self.res))
        env.process(self.porucha_stroje())

    def vyroba(self, opravar):
        
        while True:
            try:
                yield self.env.timeout(self.cas_vyroby)
                self.soucastky += 1
            except simpy.Interrupt:
                start = self.env.now
                self.porucha = True
                self.pocet_poruch += 1
                with opravar.request() as request:
                    yield request
                    yield self.env.timeout(random.normalvariate(60,20))
                self.porucha = False
                stop = self.env.now
                self.t += stop - start
            

    def porucha_stroje(self):
        while True:
            yield env.timeout(random.expovariate(1/300.0))
            if not self.porucha:
                self.proces.interrupt()
    
env = simpy.Environment()
res = simpy.Resource(env, capacity=2)
machines = [Machine(env, res, 'Mach %d'%i, random.normalvariate(1,0.02))for i in range(5)]

den = 24 * 60
tyden = 5 * den
mesic = 20 * den
env.run(mesic)

for i in machines:
    print(i.jmeno + " : " + str(i.soucastky) + " - error " + ":pocet poruch = " + str(i.pocet_poruch) + " :cas poruch = " + str(round(i.t,0)) + " :prumerny cas v poruse = " + str(round(i.t/i.pocet_poruch,2)))
print('\nprumer na stroj: ' + str(sum(i.soucastky for i in machines)/len(machines))+' ks / '+str(sum(i.pocet_poruch for i in machines)/len(machines)) + ' poruch / ' +str(round(sum(i.t for i in machines)/len(machines),0)) + ' min/stroj v poruse')
print('celkem : ' + str(sum(i.soucastky for i in machines))+' ks / '+str(sum(i.pocet_poruch for i in machines)) + ' poruch / '+str(round(sum(i.t for i in machines),0)) + 'min na poruchach')
print('')

#----------------------PRODEJ LISTKU DO KINA-----------------------------------------------

def divak(env, film, pocet, kino):

    with kino.counter.request() as request:
        result = yield request | kino.vyprodano[film]

        if request not in result:
            kino.zklamani[film] += 1
            return
        if kino.listky[film] < pocet:
            yield env.timeout(0.5)
            return
        kino.listky[film] -= pocet
        if kino.listky[film] < 2:
            kino.vyprodano[film].succeed()
            kino.listky[film] = 0
            print("Listky na film {0} vyprodany v {1}".format(film, env.now))
        yield env.timeout(1)

def prodej(env, kino):
    while True:
       
        yield env.timeout(random.expovariate(1 / 1))
        film = random.choice(filmy)
        pocet = random.randint(1,5)
        if kino.listky[film]:
            
            env.process(divak(env,film, pocet, kino))
          
env = simpy.Environment()
counter = simpy.Resource(env, capacity=1)
pocet_listku = 50
filmy = ["Pulp Fiction", "Terminator I", "Angry Birds 2"]
listky = {film: pocet_listku for film in filmy}
vyprodano = {film: env.event() for film in filmy}
zklamani = {film: 0 for film in filmy}

Kino = collections.namedtuple("Kino", "counter, filmy, listky, vyprodano, zklamani")
kino = Kino(counter, filmy, listky, vyprodano, zklamani)

env.process(prodej(env, kino))
env.run(until=1000)

for film in filmy:
   print(kino.zklamani[film])

'''
#-----------------------SLEVARNA---------------------------------------------
  
# trida pro vyrobni procesy
class Machine(): 
    # iniciace stroje:  env - prostredi / 
    #                   opravar - zdroj / 
    #                   jmeno - jmeno stroje(str) / 
    #                   cas_vyroby - cas pro vyrobu jednoho dilu(float) / 
    #                   vstup - [kontejner, pozadovane mnozstvi] / 
    #                   vystup - [kontejner, vyrobene mnozstvi] 
    #                   sklad - vstupni kontejner vyrobniho procesu, kam se vraci material pri poruse stroje
    def __init__(self, env, opravar, jmeno, cas_vyroby, vstup, vystup, sklad, write):
        self.jmeno = jmeno
        self.env = env
        self.opravar = opravar
        self.cas_vyroby = cas_vyroby
        self.vstup = vstup
        self.vystup = vystup
        self.sklad = sklad
        self.pocet_kusu = 0
        self.poruchy_cas = []
        self.porucha = False
        self.write = write

        self.proces = env.process(self.vyroba())
        env.process(self.porouchani_stroje())
    # vyrobni / poruchovy cyklus stroje - pri poruse se material vraci do skladu 
    def vyroba(self):
        while True:
            try:
                yield self.vstup[0].get(self.vstup[1])
                #print("stroj {0} zacal vyrobu kusu v case {1}. \n".format(self.jmeno, round(self.env.now,0)))
                text = "stroj {0} zacal vyrobu kusu c.1{1} v case {2}. \n".format(self.jmeno, self.pocet_kusu+1, round(self.env.now,0))
                self.write.write(text)
                yield self.env.timeout(self.cas_vyroby)
                yield self.vystup[0].put(self.vystup[1])
                self.pocet_kusu += 1
            except simpy.Interrupt:
                porucha = []
                porucha_start = round(self.env.now/60,0)
                porucha.append(porucha_start)
                #print("stroj {0} se porouchal v case {1}. \n".format(self.jmeno, round(self.env.now,0)))
                text = "stroj {0} se porouchal v case {1}. \n".format(self.jmeno, round(self.env.now,0))
                self.write.write(text)
                start = self.env.now
                self.porucha = True
                with self.opravar.request() as request:
                    yield request
                    oprava_start = round(self.env.now/60,0)
                    #print("opravar dorazil na poruchu stroje {0} v {1} za {2} min od nahlaseni. \n".format(self.jmeno, porucha_start, round((oprava_start - porucha_start)/60,0)))
                    text = "opravar dorazil na poruchu stroje {0} v {1} za {2} min od nahlaseni. \n".format(self.jmeno, porucha_start, round((oprava_start - porucha_start),0))
                    self.write.write(text)

                    yield self.env.timeout(random.randint(1800,7200))
                    oprava_konec = round(self.env.now/60,0)
                    #print("stroj {0} byl opraven v case {1}, oprava trvala {2} min, stroj stal {3} min. \n".format(self.jmeno, oprava_konec, round((oprava_konec - oprava_start)/60,0), round((oprava_konec - porucha_start)/60,0))
                    text = "stroj {0} byl opraven v case {1}, oprava trvala {2} min, stroj stal {3} min. \n".format(self.jmeno, oprava_konec, round((oprava_konec - oprava_start),0), round((oprava_konec - porucha_start),0))
                    self.write.write(text)
                self.sklad.put(self.vstup[1])
                self.porucha = False
                porucha.append(round((self.env.now - start)/60, 0))
                porucha.append(self.jmeno)
                self.poruchy_cas.append(porucha)
    # generovani poruch stroje
    def porouchani_stroje(self):
        while True:
            yield self.env.timeout(random.expovariate(0.00001))
            if not self.porucha:
                self.proces.interrupt()
# doplnovani skladu vstupniho materialu pri podlimitu
def call_supply(env, sklad):
    while True:
        if sklad.level < 10000:
            yield sklad.put(10000)
            print("doplneno 10t do skladu hliniku v {0}".format(env.now))
        yield env.timeout(10)
    
# trida pro dopravniky vyrobku
class Conveyor():
    # initiation of conveyor - parameters:  env - simpy environment
    #                                       opravar - simpy resource pro opravu porouchane sekce dopravniku
    #                                       pocet_sekci - pocet sekci dopravniku (min 1)
    #                                       kapacita_sekce - kolik vyrobku se vejde na jednu sekci
    #                                       rychlost_presunu - jak dlouho trva projeti vyrobku pres jednu sekci
    #                                       vstup - simpy conveyor na vstupu do dopravniku
    #                                       vystup - simpy conveyor na vystupu z dopravniku
    def __init__(self, env, opravar, pocet_sekci, kapacita_sekce, rychlost_presunu, vstup, vystup, write):
        self.env = env
        self.opravar = opravar
        self.vstup = vstup
        self.rychlost_presunu = rychlost_presunu
        self.vystup = vystup
        self.kapacita_sekce = kapacita_sekce
        self.pocet_sekci = pocet_sekci
        self.write = write
        
        # tvorba kolekce dopravnikovych sekci
        jmena = []
        for i in range(self.pocet_sekci):
            jmena.append(i + 1)
        stores = {j : simpy.Store(self.env) for j in jmena}
        containers = {j : simpy.Container(self.env, 1,0) for j in jmena}
        fronty = {j : 0 for j in jmena}
        poruchy = {j : False for j in jmena}
        poruchy_cas = {j : [] for j in jmena}
        Dopravnik = collections.namedtuple('Dopravnik', 'jmena, stores, containers, fronty, poruchy, poruchy_cas')
    
        self.dopravnik = Dopravnik(jmena, stores, containers, fronty, poruchy, poruchy_cas)
        #vstupni proces dopravniku
        self.procesy = []
        self.procesy.append(env.process(self.startD([self.vstup, 1], self.dopravnik.stores[1], 1)))
        #vyber procesu nasledne sekce / vystupu z dopravniku v zavislosti na poctu sekci
        if self.pocet_sekci > 1:  
            # pripad vice sekci          
            for i in range(1,self.pocet_sekci):
                self.procesy.append(env.process(self.nextD([self.dopravnik.containers[i], 1], self.dopravnik.stores[i], i)))

                self.procesy.append(env.process(self.startD([self.dopravnik.containers[i], 1], self.dopravnik.stores[i+1], i+1)))
            self.procesy.append(env.process(self.nextD([self.vystup, 1], self.dopravnik.stores[i+1], i+1)))
        else: 
            # pripad jedne sekce      
            self.procesy.append(env.process(self.nextD([self.vystup, 1], self.dopravnik.stores[1], 1)))
        self.env.process(self.porouchani_stroje())
        
    # zpracovani prujezdu sekci
    def prujezd(self, dop, prvek):
        yield self.env.timeout(self.rychlost_presunu)
        dop.put(prvek)

    # zpracovani vyjezdu ze sekce
    def put(self, dop, prvek):  
        self.env.process(self.prujezd(dop, prvek))

    # zpracovani vjezdu do sekce
    def get(self, dop):
        return dop.get()

    #zpracovani predani vyrobku ze zasobniku do sekce
    def startD(self, vstupZ, dop, n):
        x = 1
        while True:      
            # omezeni podle kapacity sekce
            if (self.dopravnik.fronty[n] < self.kapacita_sekce) and not (self.dopravnik.poruchy[n]):
                yield vstupZ[0].get(vstupZ[1])
                self.put(dop, vstupZ[1])
                self.dopravnik.fronty[n] += 1
                #print("kolo {0} vjelo na {1} pas v case {2}. \n".format(x, n, round(self.env.now,0)))
                text = "kolo {0} vjelo na {1} pas v case {2}. \n".format(x, n, round(self.env.now,0))
                self.write.write(text)
                # rychlost vstupu vyrobku na dop po sobe
                yield self.env.timeout(2)
                x += 1
            else:
                yield self.env.timeout(1)
          
    # zpracovani predani vyrobku ze sekce do zasobniku   
    def nextD(self, vystupZ, dop, n):
        x = 1
        while True:      
            if ((n == self.pocet_sekci) or (self.dopravnik.fronty[n+1] < self.kapacita_sekce)) and not (self.dopravnik.poruchy[n]):         
                yield self.get(dop)
                yield vystupZ[0].put(vystupZ[1])
                self.dopravnik.fronty[n] -= 1
                #print("kolo {0} vyjelo z {1} pasu v case {2}. \n".format(x, n, round(self.env.now,0)))
                text = "kolo {0} vyjelo z {1} pasu v case {2}. \n".format(x, n, round(self.env.now,0))
                self.write.write(text)
                x += 1
            # pokud nastane porucha sekce, prijem i vydej vyrobku se zastavi
            elif self.dopravnik.poruchy[n]:
                porucha = []
                porucha.append(round(self.env.now/60,0))
                porucha_start = round(self.env.now,0)
                #print("sekce dopravniku {0} se porouchala v case {1}. \n".format(n, porucha_start))
                text = "sekce dopravniku {0} se porouchala v case {1}. \n".format(n, porucha_start)
                self.write.write(text)
                with self.opravar.request() as request:
                    yield request
                    oprava_start = round(self.env.now,0)
                    #print("opravar dorazil na poruchu sekce {0} dopravniku v {1} za {2} min od nahlaseni. \n".format(n , oprava_start, round((oprava_start - porucha_start)/60,0)))
                    text = "opravar dorazil na poruchu sekce {0} dopravniku v {1} za {2} min od nahlaseni. \n".format(n , oprava_start, round((oprava_start - porucha_start)/60,0))
                    self.write.write(text)
                    yield self.env.timeout(random.randint(900,2400))
                    self.dopravnik.poruchy[n] = False
                    oprava_konec = round(self.env.now, 0)
                    #print("sekce dopravniku {0} byla opravena v case {1}, oprava trvala {2} min, sekce stala {3} min. \n".format(n, oprava_konec, round((oprava_konec - oprava_start)/60,0), round((oprava_konec - porucha_start)/60,0) ))
                    text = "sekce dopravniku {0} byla opravena v case {1}, oprava trvala {2} min, sekce stala {3} min. \n".format(n, oprava_konec, round((oprava_konec - oprava_start)/60,0), round((oprava_konec - porucha_start)/60,0) )
                    self.write.write(text)
                    porucha.append(round((oprava_konec - porucha_start)/60,0))
                    porucha.append("dopravnik-sekce {0}".format(n))
                    self.dopravnik.poruchy_cas[n].append(porucha)
            else: 
                yield self.env.timeout(1)

    # generovani poruch na nahodnych sekcich
    def porouchani_stroje(self):
        
        while True:
            yield self.env.timeout(random.expovariate(0.00007))
            stroj = random.choice(self.dopravnik.jmena)
            if not self.dopravnik.poruchy[stroj]:
                self.dopravnik.poruchy[stroj] = True
                
s = datetime.datetime.now()

# trida pro chod simulace
class Runtime():
    def __init__(self, vstup_sklad, vystup_sklad, TP, LS, DOP, opravari, chod):
        # parametry vstupniho skladu (vstup do TP)
        self.sklad_vstup_max = vstup_sklad[0]
        self.sklad_vstup_akt = vstup_sklad[1]
        # parametry skladu taveniny (vystup z TP / vstup do LS)

        # parametry vystupniho skladu (vystup z TP)
        self.sklad_vystup_max = vystup_sklad[0]
        self.sklad_vystup_akt = vystup_sklad[1]
        # tvorba prostredi, skladu, zdroju
        self.env = simpy.Environment()
        self.sklad = simpy.Container(self.env, self.sklad_vstup_max, self.sklad_vstup_akt)
        self.tavenina = simpy.Container(self.env, 20000, 5000)
        self.odlitky = simpy.Container(self.env, 100, 0)
        self.vystup = simpy.Container(self.env, self.sklad_vystup_max, self.sklad_vystup_akt)
        self.opravar = simpy.Resource(self.env, opravari)
        self.pocet_doplneni = 0
        self.zacatek = ""
        self.konec = ""
    
        self.tp = []
        self.ls = []

        # vypis pocatecnich hodnot prostredku

        with open('dopravniky.txt', 'w', encoding='utf-8') as dop, open('tp.txt', 'w', encoding='utf-8') as tp, open('ls.txt', 'w', encoding='utf-8') as ls, open('zasobovani.txt', 'w', encoding='utf-8') as z:    
            self.env.process(self.call_supply(z))
            for i in range(TP[0]):
                self.tp.append(Machine(self.env, self.opravar, "TP{0}".format(i), random.normalvariate(TP[2],40), [self.sklad, TP[1]], [self.tavenina, TP[1]], self.sklad, tp))

            for i in range(LS[0]): 
                self.ls.append(Machine(self.env, self.opravar, "ls{0}".format(i), random.normalvariate(LS[2], 10), [self.tavenina, LS[3]], [self.odlitky, LS[4]], self.sklad, ls))
            self.c = Conveyor(self.env, self.opravar, DOP[0], DOP[2], DOP[1], self.odlitky, self.vystup, dop )
        

            print("\n---------POCATECNI STAV--------------")
            print("Sklad : "+ str(self.sklad.level) + "| tavenina : " + str(self.tavenina.level) + "| odlitky : " + str(self.odlitky.level) + "| vystup z dop : " + str(self.vystup.level))
            self.zacatek = "Sklad : "+ str(self.sklad.level) + "| tavenina : " + str(self.tavenina.level) + "| odlitky : " + str(self.odlitky.level) + "| vystup z dop : " + str(self.vystup.level)

            self.env.run(until = chod)
        tp.close()
        ls.close()
        dop.close()
        
        print("\n-----------KONCOVY STAV----------------")
        print("Sklad : "+ str(self.sklad.level) + "| tavenina : " + str(self.tavenina.level) + "| odlitky : " + str(self.odlitky.level) + "| vystup z dop : " + str(self.vystup.level))
        self.konec = "Sklad : "+ str(self.sklad.level) + "| tavenina : " + str(self.tavenina.level) + "| odlitky : " + str(self.odlitky.level) + "| vystup z dop : " + str(self.vystup.level)
        print("\n----------CAS CHODU SIMULACE-----------")
        print("cas programu: {0}".format(datetime.datetime.now() - s))
        print("\n------------PORUCHY--------------------")

        #--------------------PORUCHY----------------------------------------------


        p = []
        for i in self.tp:
            try:
                for j in i.poruchy_cas:
                    p.append(j)
            except:
                pass
        for i in self.ls:
            try:
                for j in i.poruchy_cas:
                    p.append(j)
            except:
                pass    
        for jmeno in self.c.dopravnik.jmena:
            try:
                for j in range(len(self.c.dopravnik.poruchy_cas[jmeno])):
                    #print(self.c.dopravnik.poruchy_cas[jmeno][j])
                    p.append(self.c.dopravnik.poruchy_cas[jmeno][j])
            except:
                pass
        self.poruchy = sorted(p)
        for i in self.poruchy:
            print("porucha na stroji {0} v case {1} trvala {2}min.".format(i[2], i[0], i[1]))
 
        
    def call_supply(self, z):
        while True:
            if self.sklad.level < 10000:
                yield self.sklad.put(10000)
                #print("doplneno 10t do skladu hliniku v {0}. \n".format(round(self.env.now,0)))
                text = "doplneno 10t do skladu hliniku v {0}. \n".format(round(self.env.now,0))
                z.write(text)
                self.pocet_doplneni += 1
            yield self.env.timeout(10)

#r = Runtime([80000,40000],[150000,20000],4)


class MainW(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainW, self).__init__(*args, **kwargs)
        uic.loadUi("simulace_okno.ui", self)

        self.startBut.clicked.connect(self.run)
        self.doplneniBut.clicked.connect(self.dop)
        self.tpBut.clicked.connect(self.tpklik)
        self.lsBut.clicked.connect(self.lsklik)
        self.dopravnikyBut.clicked.connect(self.dopravnikyklik)
        self.initParam()
        
        self.show()
    def run(self):
        self.TP = [int(self.TPpocet.text()), int(self.TPvstup.text()), int(self.TPchod.text()), int(self.TPcasPorucha.text()), int(self.TPporuchaCas.text())]
        self.LS = [int(self.LSpocet.text()), int(self.LSvstup.text()), int(self.LSchod.text()), int(self.LSmatStart.text()), int(self.LSmatEnd.text()), int(self.LScasPorucha.text()), int(self.LSporuchaCas.text())]
        self.DOP = [int(self.DOPpocet.text()), int(self.DOPcas.text()), int(self.DOPkap.text()), int(self.DOPcasPorucha.text()), int(self.DOPporuchaCas.text())]
        try:
            cas = (24*60*60*self.startTime.dateTime().daysTo(self.stopTime.dateTime())+self.startTime.time().msecsTo(self.stopTime.time())/1000)
            r = Runtime([int(self.vstupMax.text()), int(self.vstupAct.text())],[int(self.vystupMax.text()), int(self.vystupAct.text())],self.TP, self.LS, self.DOP, int(self.Opravari.text()),cas)
            self.startInfo.addItem("start: "+r.zacatek)
            self.startInfo.addItem("stop: "+r.konec)
            self.startInfo.addItem("---------------------------")
            for i in r.poruchy:
                self.stopInfo.addItem("porucha na stroji {0} v case {1} trvala {2}min.".format(i[2], i[0], i[1]))
            self.stopInfo.addItem("----------------------------")

        except:
            print("zadejte spravne udaje!")
    
    def dop(self):
        os.startfile("zasobovani.txt")
    def lsklik(self):
        os.startfile("ls.txt")
    def tpklik(self):
        os.startfile("tp.txt")
    def dopravnikyklik(self):
        os.startfile("dopravniky.txt")

    def initParam(self):
        # vstupni sklad
        self.vstupMax.setText("100000")
        self.vstupAct.setText("10000")
        # TP
        self.TPpocet.setText("6")
        self.TPvstup.setText("800")
        self.TPchod.setText("900")
        self.TPcasPorucha.setText("0")
        self.TPporuchaCas.setText("0")
        # LS
        self.LSpocet.setText("40")
        self.LSvstup.setText("500")
        self.LSmatStart.setText("25")
        self.LSmatEnd.setText("1")
        self.LSchod.setText("300")
        self.LScasPorucha.setText("0")
        self.LSporuchaCas.setText("0")
        # dopravniky
        self.DOPpocet.setText("3")
        self.DOPcas.setText("60")
        self.DOPkap.setText("20")
        self.DOPcasPorucha.setText("0")
        self.DOPporuchaCas.setText("0")
        # runtime
        self.Opravari.setText("4")
        start = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        konec = (datetime.datetime.now() + timedelta(hours=24)).strftime("%d.%m.%Y %H:%M")
        self.startTime.setDateTime(QtCore.QDateTime.fromString(start, 'dd.MM.yyyy hh:mm'))
        self.stopTime.setDateTime(QtCore.QDateTime.fromString(konec, 'dd.MM.yyyy hh:mm'))
        # vystupni sklad
        self.vystupMax.setText("100000")
        self.vystupAct.setText("0")
'''
class MainW(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainW, self).__init__(*args, **kwargs)
        uic.loadUi("test.ui", self)

        self.show()
'''
class App(QtWidgets.QApplication):
    def __init__(self):
        super(App, self).__init__(sys.argv)
    
    def build(self):
        
        self.mainWin = MainW()
        sys.exit(self.exec_())


app = App()
app.build()
'''
for _ in range(10):
    print(random.normalvariate(300,10))

for _ in range(10):
    print((random.expovariate(0.000001))/3600)
    #print(random.gauss(100,10))
'''