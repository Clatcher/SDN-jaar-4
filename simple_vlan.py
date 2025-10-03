from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import  RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel


class SimpleVLANTopo(Topo):
    def build(self):
        #switches
        s1 = self.addSwitch('s1')


        #hosts (employees, guests, management)
        h1 = self.addHost('h1', mac='00:00:00:00:00:01') # employee
        h2 = self.addHost('h2', mac='00:00:00:00:00:02') # guest
        h3 = self.addHost('h3', mac='00:00:00:00:00:03') # management

        #switch koppellen
        self.addLink(h1, s1, port2=1) # employee
        self.addLink(h2, s1, port2=2) # guest
        self.addLink(h3, s1, port2=3) # management

def run():
    topo = SimpleVLANTopo()
    net = Mininet(topo=topo, controller=RemoteController)
    net.start()
    print("Network is up and running.")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()



#runt nu in python 3, kunnen errors van komen bij latere fase. zorg ervoor dat je het kan aanroepen met mininet zelf.
#als je het nu runt zit het in python 3 omgeving en niet in mininet omgeving.