from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
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
        h7 = self.addHost('h7', mac='00:00:00:00:00:04')  # ISP A
       
        # hosts in Gebouw B (1 per VLAN)
        h4 = self.addHost('h4', mac='00:00:00:00:00:11')  # employee B
        h5 = self.addHost('h5', mac='00:00:00:00:00:12')  # guest B
        h6 = self.addHost('h6', mac='00:00:00:00:00:13')  # management B
        h8 = self.addHost('h8', mac='00:00:00:00:00:14')  # ISP B
        
        # access links Gebouw A
        self.addLink(h1, s1, port2=1)
        self.addLink(h2, s1, port2=2)
        self.addLink(h3, s1, port2=3)
        self.addLink(h7, s1, port2=20)

        # access links Gebouw B
        self.addLink(h4, s2, port2=1)
        self.addLink(h5, s2, port2=2)
        self.addLink(h6, s2, port2=3)
        self.addLink(h8, s2, port2=20)

        # trunk tussen s1 en s2
        self.addLink(s1, s2, port1=10, port2=10)

def run():
    topo = SimpleVLANTopo()
    net = Mininet(topo=topo, controller=RemoteController)
    net.start()

    # Configureer IP’s voor ISP hosts
    h7 = net.get('h7')
    h8 = net.get('h8')

    h7.cmd('ip addr flush dev h7-eth0')
    h8.cmd('ip addr flush dev h8-eth0')
    h7.cmd('ip addr add 203.0.113.2/28 dev h7-eth0')
    h8.cmd('ip addr add 203.0.113.3/28 dev h8-eth0')

    # Start VRRP met keepalived
    h7.cmd('keepalived -n -l -f /tmp/keepalived-h7.conf &')
    h8.cmd('keepalived -n -l -f /tmp/keepalived-h8.conf &')

    # Wacht even zodat VRRP zich kan vestigen
    net.waitConnected(timeout=3)

    print("✅ Network is up and running.")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()

topos = {
    'simple_vlan': SimpleVLANTopo
}
