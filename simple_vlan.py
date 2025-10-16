from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

class SimpleVLANTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')  # Gebouw A
        s2 = self.addSwitch('s2')  # Gebouw B

        # Gebouw A
        h1 = self.addHost('h1',
                          mac='00:00:00:00:00:01',
                          ip='10.0.10.11/24',
                          defaultRoute='via 10.0.10.1')   # employees
        h2 = self.addHost('h2',
                          mac='00:00:00:00:00:02',
                          ip='10.0.20.11/24',
                          defaultRoute='via 10.0.20.1')   # guests (rate limited)
        h3 = self.addHost('h3',
                          mac='00:00:00:00:00:03',
                          ip='10.0.30.11/24',
                          defaultRoute='via 10.0.30.1')   # management
        h7 = self.addHost('h7',
                          mac='00:00:00:00:00:04',
                          ip='203.0.113.2/28',
                          defaultRoute='via 203.0.113.14')  # ISP A

        # Gebouw B
        h4 = self.addHost('h4',
                          mac='00:00:00:00:00:11',
                          ip='10.0.10.12/24',
                          defaultRoute='via 10.0.10.1')
        h5 = self.addHost('h5',
                          mac='00:00:00:00:00:12',
                          ip='10.0.20.12/24',
                          defaultRoute='via 10.0.20.1')
        h6 = self.addHost('h6',
                          mac='00:00:00:00:00:13',
                          ip='10.0.30.12/24',
                          defaultRoute='via 10.0.30.1')
        h8 = self.addHost('h8',
                          mac='00:00:00:00:00:14',
                          ip='203.0.113.3/28',
                          defaultRoute='via 203.0.113.14')  # ISP B

        # Access links A
        self.addLink(h1, s1, port2=1)
        self.addLink(h2, s1, port2=2, bw=1)   # guest poort (QoS)
        self.addLink(h3, s1, port2=3)
        self.addLink(h7, s1, port2=20)  # ISP A

        # Access links B
        self.addLink(h4, s2, port2=1)
        self.addLink(h5, s2, port2=2, bw=1)
        self.addLink(h6, s2, port2=3)
        self.addLink(h8, s2, port2=20)  # ISP B

        # Trunk tussen s1 en s2
        self.addLink(s1, s2, port1=10, port2=10)


def run():
    topo = SimpleVLANTopo()
    net = Mininet(topo=topo, controller=RemoteController, link=TCLink)
    net.start()


    # Start VRRP met keepalived
    net.get('h7').cmd('keepalived -n -l -f /tmp/keepalived-h7.conf &')
    net.get('h8').cmd('keepalived -n -l -f /tmp/keepalived-h8.conf &')


   
   
    print("[OK] Network is up and running.")
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()

topos = {
    'simple_vlan': SimpleVLANTopo
}
