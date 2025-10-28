from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

class SimpleVLANTopo(Topo):
    def build(self):
        # Switches
        s1 = self.addSwitch('s1')  # Building A
        s2 = self.addSwitch('s2')  # Building B

        # Hosts in Building A
        h1 = self.addHost('h1',
                          mac='00:00:00:00:00:01',
                          ip='10.0.10.11/24',
                          defaultRoute='via 10.0.10.1')
        h2 = self.addHost('h2',
                          mac='00:00:00:00:00:02',
                          ip='10.0.20.11/24',
                          defaultRoute='via 10.0.20.1')
        h3 = self.addHost('h3',
                          mac='00:00:00:00:00:03',
                          ip='10.0.30.11/24',
                          defaultRoute='via 10.0.30.1')
        h7 = self.addHost('h7',
                          mac='00:00:00:00:00:04',
                          ip='203.0.113.2/28',
                          defaultRoute='via 203.0.113.14')

        # Hosts in Building B
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
                          defaultRoute='via 203.0.113.14')

        # Access links for Building A (s1)
        self.addLink(h1, s1, port2=1)
        self.addLink(h2, s1, port2=2, bw=1)
        self.addLink(h3, s1, port2=3)
        self.addLink(h7, s1, port2=20)

        # Access links for Building B (s2)
        self.addLink(h4, s2, port2=1)
        self.addLink(h5, s2, port2=2, bw=1)
        self.addLink(h6, s2, port2=3)
        self.addLink(h8, s2, port2=20)

        # Trunk link between s1 and s2
        self.addLink(s1, s2, port1=10, port2=10)

def run():
    topo = SimpleVLANTopo()
    net = Mininet(topo=topo, controller=RemoteController, link=TCLink)
    net.start()

    # Dual-stack IPv6 additions for all hosts
    ipv6_config = {
        'h1': '2001:db8:10::11/64', 'h4': '2001:db8:10::12/64',
        'h2': '2001:db8:20::11/64', 'h5': '2001:db8:20::12/64',
        'h3': '2001:db8:30::11/64', 'h6': '2001:db8:30::12/64',
        'h7': '2001:db8:40::2/64',  'h8': '2001:db8:40::3/64'
    }
    routes = {
        'h1': '2001:db8:10::1', 'h4': '2001:db8:10::1',
        'h2': '2001:db8:20::1', 'h5': '2001:db8:20::1',
        'h3': '2001:db8:30::1', 'h6': '2001:db8:30::1',
        'h7': '2001:db8:40::14', 'h8': '2001:db8:40::14'
    }

    for host, ip6 in ipv6_config.items():
        net.get(host).cmd(f'ip -6 addr add {ip6} dev {host}-eth0')
        net.get(host).cmd(f'ip -6 route add default via {routes[host]}')

    net.get('h7').cmd('keepalived -n -l -f /tmp/keepalived-h7.conf &')
    net.get('h8').cmd('keepalived -n -l -f /tmp/keepalived-h8.conf &')

    print("\n[OK] Network is up and running. Starting connectivity tests...")

    def test_and_report():
        tests = [
            ('h1', '10.0.10.12', 'Employee ↔ Employee (IPv4)'),
            ('h4', '10.0.10.11', 'Employee ↔ Employee (IPv4)'),
            ('h2', '203.0.113.2', 'Guest → ISP (IPv4)'),
            ('h2', '203.0.113.3', 'Guest → ISP (IPv4)'),
            ('h3', '10.0.10.11', 'Management → Employee (IPv4)'),
            ('h3', '10.0.20.12', 'Management → Guest (IPv4)'),
            ('h3', '203.0.113.2', 'Management → ISP (IPv4)'),
            ('h5', '10.0.10.11', 'Guest → Employee (IPv4, moet mislukken)'),
            ('h5', '10.0.30.11', 'Guest → Management (IPv4, moet mislukken)'),
            ('h7', '10.0.20.11', 'ISP → Guest (IPv4, moet mislukken)'),
        ]
        print("\n[TESTRESULTATEN - IPv4]")
        for src, dst, desc in tests:
            result = "geslaagd" if "0% packet loss" in net.get(src).cmd(f'ping -c1 -W1 {dst}') else "mislukt"
            print(f"- {desc} ({src} → {dst}): {result}")

        tests6 = [
            ('h1', '2001:db8:10::12', 'Employee ↔ Employee (IPv6)'),
            ('h3', '2001:db8:40::2', 'Management → ISP (IPv6)'),
            ('h2', '2001:db8:40::2', 'Guest → ISP (IPv6)'),
            ('h7', '2001:db8:20::11', 'ISP → Guest (IPv6, moet mislukken)'),
        ]
        print("\n[TESTRESULTATEN - IPv6]")
        for src, dst, desc in tests6:
            result = "geslaagd" if "0% packet loss" in net.get(src).cmd(f'ping6 -c1 -W1 {dst}') else "mislukt"
            print(f"- {desc} ({src} → {dst}): {result}")

    test_and_report()

    print("\n[INFO] Automated tests completed. Entering Mininet CLI for further inspection.\n")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
