
import time
import random

class Packet:
    def __init__(self, source_ip, dest_ip, size, protocol, timestamp):
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.size = size # in bytes
        self.protocol = protocol
        self.timestamp = timestamp

    def __repr__(self):
        return (f"Packet(src={self.source_ip}, dst={self.dest_ip}, "
                f"size={self.size}B, proto={self.protocol}, time={self.timestamp:.2f})")

class NetworkAnalyzer:
    def __init__(self):
        self.packets = []
        self.analysis_results = {}

    def capture_packets(self, num_packets=10):
        """Simulates capturing network packets."""
        print(f"Capturing {num_packets} packets...")
        for i in range(num_packets):
            src_ip = f"192.168.1.{random.randint(1, 254)}"
            dst_ip = f"10.0.0.{random.randint(1, 254)}"
            size = random.randint(64, 1500)
            protocol = random.choice(["TCP", "UDP", "ICMP", "HTTP"])
            timestamp = time.time() + i * 0.01 # simulate time progression
            self.packets.append(Packet(src_ip, dst_ip, size, protocol, timestamp))
            time.sleep(0.005) # Simulate some delay

        print(f"Captured {len(self.packets)} packets.")

    def analyze_packets(self):
        """Analyzes captured packets to generate statistics."""
        if not self.packets:
            print("No packets to analyze. Please capture packets first.")
            return

        total_size = sum(p.size for p in self.packets)
        protocol_counts = {}
        ip_traffic = {} # (src, dst) -> total size

        for packet in self.packets:
            protocol_counts[packet.protocol] = protocol_counts.get(packet.protocol, 0) + 1
            pair = (packet.source_ip, packet.dest_ip)
            ip_traffic[pair] = ip_traffic.get(pair, 0) + packet.size

        self.analysis_results = {
            "total_packets": len(self.packets),
            "total_data_size_bytes": total_size,
            "protocol_distribution": protocol_counts,
            "top_traffic_pairs": sorted(ip_traffic.items(), key=lambda item: item[1], reverse=True)[:5]
        }
        print("Packet analysis complete.")

    def print_analysis_report(self):
        """Prints a summary of the analysis results."""
        if not self.analysis_results:
            print("No analysis results. Please run analyze_packets first.")
            return

        print("\n--- Network Analysis Report ---")
        print(f"Total Packets: {self.analysis_results['total_packets']}")
        print(f"Total Data Size: {self.analysis_results['total_data_size_bytes']} bytes")
        print("Protocol Distribution:")
        for proto, count in self.analysis_results['protocol_distribution'].items():
            print(f"  - {proto}: {count} packets")
        print("Top 5 Traffic Pairs (Source IP, Destination IP) -> Data Size:")
        for (src, dst), size in self.analysis_results['top_traffic_pairs']:
            print(f"  - {src} -> {dst}: {size} bytes")
        print("-------------------------------\n")

if __name__ == "__main__":
    analyzer = NetworkAnalyzer()
    analyzer.capture_packets(num_packets=50)
    analyzer.analyze_packets()
    analyzer.print_analysis_report()
