from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import  RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel


class SimpleVLANTopo(Topo):
    def build(self):
        # switches (A en B)
        s1 = self.addSwitch('s1')           # Gebouw A
        s2 = self.addSwitch('s2')           # Gebouw B

        # hosts in Gebouw A (1 per VLAN)
        h1 = self.addHost('h1', mac='00:00:00:00:00:01')  # employee A
        h2 = self.addHost('h2', mac='00:00:00:00:00:02')  # guest A
        h3 = self.addHost('h3', mac='00:00:00:00:00:03')  # management A

        # hosts in Gebouw B (1 per VLAN)
        h4 = self.addHost('h4', mac='00:00:00:00:00:11')  # employee B
        h5 = self.addHost('h5', mac='00:00:00:00:00:12')  # guest B
        h6 = self.addHost('h6', mac='00:00:00:00:00:13')  # management B

        # access links (untagged aan hostzijde)
        self.addLink(h1, s1, port2=1)  # A employee
        self.addLink(h2, s1, port2=2)  # A guest
        self.addLink(h3, s1, port2=3)  # A management

        self.addLink(h4, s2, port2=1)  # B employee
        self.addLink(h5, s2, port2=2)  # B guest
        self.addLink(h6, s2, port2=3)  # B management

        # darkfiber trunk tussen centrale patchkasten (s1<->s2)
        # Gebruik poort 10 aan beide kanten voor de
        self.addLink(s1, s2, port1=10, port2=10)  # trunk link

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

topos = {
    'simple_vlan': SimpleVLANTopo
}
