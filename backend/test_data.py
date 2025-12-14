"""
Test script to generate sample network data for testing the Cyber Attack Detection System
Generates UNSW-NB15 format data matching the training dataset
"""

import requests
import time
import random
import json

API_URL = "http://localhost:5000/api/submit"

# Sample IP addresses
IP_POOL = [
    f"192.168.1.{i}" for i in range(1, 50)
] + [
    f"10.0.0.{i}" for i in range(1, 30)
]

# UNSW-NB15 categorical values
PROTOCOLS = ['tcp', 'udp', 'icmp', 'arp', 'ospf', 'sctp']
SERVICES = ['http', 'ftp', 'smtp', 'ssh', 'dns', 'dhcp', 'snmp', 'ssl', '-', 'irc', 'radius', 'ftp-data']
STATES = ['FIN', 'CON', 'INT', 'REQ', 'RST', 'ACC', 'CLO', 'URN', 'no', 'PAR', 'ECO', 'TST', 'TXD', 'TXT']

ATTACK_TYPES = ['Normal', 'Exploits', 'Reconnaissance', 'Worms', 'DoS', 'Fuzzers']

def generate_sample_data(attack_type=None):
    """Generate sample network traffic data in UNSW-NB15 format
    
    Args:
        attack_type: Specific attack type to generate ('DoS', 'Exploits', 'Reconnaissance', 'Worms', 'Fuzzers', or None for random)
    """
    # Base data structure with IPs
    base_data = {
        "src_ip": random.choice(IP_POOL),
        "dst_ip": random.choice(IP_POOL),
    }
    
    if attack_type or random.random() < 0.3:  # 30% chance of attack
        # Choose attack type if not specified
        if not attack_type:
            attack_type = random.choice(['DoS', 'Exploits', 'Reconnaissance', 'Worms', 'Fuzzers'])
        
        # Generate attack-specific patterns
        if attack_type == 'DoS':
            # DoS: High volume, short duration, many packets
            attack_data = {
                "dur": random.uniform(0.1, 5),
                "proto": random.choice(['tcp', 'udp']),
                "service": random.choice(['http', 'ftp', 'smtp']),
                "state": random.choice(['FIN', 'RST', 'CON']),
                "spkts": random.randint(100, 1000),
                "dpkts": random.randint(0, 100),
                "sbytes": random.randint(50000, 500000),
                "dbytes": random.randint(0, 1000),
                "rate": random.uniform(50.0, 100.0),
                "sload": random.uniform(0.8, 1.0),
                "dload": random.uniform(0.0, 0.2),
                "sloss": random.randint(0, 10),
                "dloss": random.randint(0, 5),
                "sinpkt": random.uniform(0.001, 0.01),
                "dinpkt": random.uniform(0.1, 1.0),
                "sjit": random.uniform(0.0, 0.1),
                "djit": random.uniform(0.0, 0.1),
                "swin": random.randint(0, 65535),
                "stcpb": random.randint(0, 1000000),
                "dtcpb": random.randint(0, 100000),
                "dwin": random.randint(0, 65535),
                "tcprtt": random.uniform(0.0, 0.1),
                "synack": random.uniform(0.0, 0.05),
                "ackdat": random.uniform(0.0, 0.05),
                "smean": random.randint(100, 1000),
                "dmean": random.randint(0, 100),
                "trans_depth": random.randint(0, 5),
                "response_body_len": random.randint(0, 1000),
                "ct_src_dport_ltm": random.randint(0, 50),
                "ct_dst_sport_ltm": random.randint(0, 50),
                "is_ftp_login": 0,
                "ct_ftp_cmd": 0,
                "ct_flw_http_mthd": random.randint(0, 10),
                "is_sm_ips_ports": random.randint(0, 1),
            }
        elif attack_type == 'Exploits':
            # Exploits: Medium duration, various protocols, file operations
            attack_data = {
                "dur": random.uniform(1, 30),
                "proto": random.choice(['tcp', 'udp']),
                "service": random.choice(['http', 'ftp', 'ssh', 'smtp']),
                "state": random.choice(['FIN', 'CON', 'INT']),
                "spkts": random.randint(20, 200),
                "dpkts": random.randint(10, 150),
                "sbytes": random.randint(10000, 100000),
                "dbytes": random.randint(1000, 50000),
                "rate": random.uniform(10.0, 50.0),
                "sload": random.uniform(0.3, 0.7),
                "dload": random.uniform(0.2, 0.6),
                "sloss": random.randint(0, 5),
                "dloss": random.randint(0, 3),
                "sinpkt": random.uniform(0.01, 0.1),
                "dinpkt": random.uniform(0.01, 0.1),
                "sjit": random.uniform(0.0, 0.05),
                "djit": random.uniform(0.0, 0.05),
                "swin": random.randint(1000, 65535),
                "stcpb": random.randint(10000, 500000),
                "dtcpb": random.randint(10000, 300000),
                "dwin": random.randint(1000, 65535),
                "tcprtt": random.uniform(0.01, 0.5),
                "synack": random.uniform(0.01, 0.1),
                "ackdat": random.uniform(0.01, 0.1),
                "smean": random.randint(50, 500),
                "dmean": random.randint(50, 300),
                "trans_depth": random.randint(1, 10),
                "response_body_len": random.randint(100, 5000),
                "ct_src_dport_ltm": random.randint(5, 30),
                "ct_dst_sport_ltm": random.randint(5, 30),
                "is_ftp_login": random.randint(0, 1),
                "ct_ftp_cmd": random.randint(0, 5),
                "ct_flw_http_mthd": random.randint(1, 20),
                "is_sm_ips_ports": random.randint(0, 1),
            }
        elif attack_type == 'Reconnaissance':
            # Reconnaissance: Scanning, multiple services, various states
            attack_data = {
                "dur": random.uniform(5, 60),
                "proto": random.choice(['tcp', 'udp', 'icmp']),
                "service": random.choice(['http', 'ftp', 'ssh', 'dns', 'smtp', '-']),
                "state": random.choice(['FIN', 'CON', 'REQ', 'RST']),
                "spkts": random.randint(10, 100),
                "dpkts": random.randint(0, 50),
                "sbytes": random.randint(1000, 20000),
                "dbytes": random.randint(0, 5000),
                "rate": random.uniform(1.0, 20.0),
                "sload": random.uniform(0.1, 0.5),
                "dload": random.uniform(0.0, 0.3),
                "sloss": random.randint(0, 3),
                "dloss": random.randint(0, 2),
                "sinpkt": random.uniform(0.05, 0.5),
                "dinpkt": random.uniform(0.1, 1.0),
                "sjit": random.uniform(0.0, 0.2),
                "djit": random.uniform(0.0, 0.2),
                "swin": random.randint(0, 65535),
                "stcpb": random.randint(0, 200000),
                "dtcpb": random.randint(0, 100000),
                "dwin": random.randint(0, 65535),
                "tcprtt": random.uniform(0.0, 1.0),
                "synack": random.uniform(0.0, 0.5),
                "ackdat": random.uniform(0.0, 0.5),
                "smean": random.randint(10, 200),
                "dmean": random.randint(0, 100),
                "trans_depth": random.randint(0, 3),
                "response_body_len": random.randint(0, 2000),
                "ct_src_dport_ltm": random.randint(10, 100),
                "ct_dst_sport_ltm": random.randint(10, 100),
                "is_ftp_login": 0,
                "ct_ftp_cmd": 0,
                "ct_flw_http_mthd": random.randint(0, 5),
                "is_sm_ips_ports": random.randint(0, 1),
            }
        elif attack_type == 'Worms':
            # Worms: Rapid spreading, high packet counts
            attack_data = {
                "dur": random.uniform(0.1, 10),
                "proto": random.choice(['tcp', 'udp']),
                "service": random.choice(['http', 'ftp', 'smtp']),
                "state": random.choice(['FIN', 'CON', 'RST']),
                "spkts": random.randint(50, 500),
                "dpkts": random.randint(20, 300),
                "sbytes": random.randint(5000, 50000),
                "dbytes": random.randint(0, 10000),
                "rate": random.uniform(20.0, 80.0),
                "sload": random.uniform(0.6, 0.9),
                "dload": random.uniform(0.1, 0.5),
                "sloss": random.randint(0, 8),
                "dloss": random.randint(0, 4),
                "sinpkt": random.uniform(0.001, 0.05),
                "dinpkt": random.uniform(0.01, 0.2),
                "sjit": random.uniform(0.0, 0.15),
                "djit": random.uniform(0.0, 0.15),
                "swin": random.randint(0, 65535),
                "stcpb": random.randint(0, 800000),
                "dtcpb": random.randint(0, 400000),
                "dwin": random.randint(0, 65535),
                "tcprtt": random.uniform(0.0, 0.2),
                "synack": random.uniform(0.0, 0.1),
                "ackdat": random.uniform(0.0, 0.1),
                "smean": random.randint(50, 800),
                "dmean": random.randint(20, 400),
                "trans_depth": random.randint(0, 8),
                "response_body_len": random.randint(0, 3000),
                "ct_src_dport_ltm": random.randint(20, 150),
                "ct_dst_sport_ltm": random.randint(20, 150),
                "is_ftp_login": random.randint(0, 1),
                "ct_ftp_cmd": random.randint(0, 3),
                "ct_flw_http_mthd": random.randint(0, 15),
                "is_sm_ips_ports": random.randint(0, 1),
            }
        elif attack_type == 'Fuzzers':
            # Fuzzers: Random inputs, various protocols, high error rates
            attack_data = {
                "dur": random.uniform(1, 20),
                "proto": random.choice(['tcp', 'udp', 'icmp']),
                "service": random.choice(['http', 'ftp', 'ssh', 'dns', '-']),
                "state": random.choice(['FIN', 'RST', 'REQ', 'INT']),
                "spkts": random.randint(10, 150),
                "dpkts": random.randint(5, 100),
                "sbytes": random.randint(1000, 50000),
                "dbytes": random.randint(0, 20000),
                "rate": random.uniform(5.0, 40.0),
                "sload": random.uniform(0.4, 0.8),
                "dload": random.uniform(0.1, 0.6),
                "sloss": random.randint(0, 6),
                "dloss": random.randint(0, 3),
                "sinpkt": random.uniform(0.01, 0.3),
                "dinpkt": random.uniform(0.05, 0.5),
                "sjit": random.uniform(0.0, 0.3),
                "djit": random.uniform(0.0, 0.3),
                "swin": random.randint(0, 65535),
                "stcpb": random.randint(0, 600000),
                "dtcpb": random.randint(0, 300000),
                "dwin": random.randint(0, 65535),
                "tcprtt": random.uniform(0.0, 0.8),
                "synack": random.uniform(0.0, 0.4),
                "ackdat": random.uniform(0.0, 0.4),
                "smean": random.randint(20, 600),
                "dmean": random.randint(10, 300),
                "trans_depth": random.randint(0, 5),
                "response_body_len": random.randint(0, 4000),
                "ct_src_dport_ltm": random.randint(5, 80),
                "ct_dst_sport_ltm": random.randint(5, 80),
                "is_ftp_login": random.randint(0, 1),
                "ct_ftp_cmd": random.randint(0, 2),
                "ct_flw_http_mthd": random.randint(0, 10),
                "is_sm_ips_ports": random.randint(0, 1),
            }
        else:
            # Default anomalous pattern
            attack_data = {
                "dur": random.uniform(0.1, 10),
                "proto": random.choice(['tcp', 'udp']),
                "service": random.choice(['http', 'ftp']),
                "state": random.choice(['FIN', 'RST']),
                "spkts": random.randint(50, 200),
                "dpkts": random.randint(0, 100),
                "sbytes": random.randint(10000, 100000),
                "dbytes": random.randint(0, 5000),
                "rate": random.uniform(20.0, 80.0),
                "sload": random.uniform(0.6, 1.0),
                "dload": random.uniform(0.0, 0.4),
                "sloss": random.randint(0, 10),
                "dloss": random.randint(0, 5),
                "sinpkt": random.uniform(0.001, 0.1),
                "dinpkt": random.uniform(0.1, 1.0),
                "sjit": random.uniform(0.0, 0.2),
                "djit": random.uniform(0.0, 0.2),
                "swin": random.randint(0, 65535),
                "stcpb": random.randint(0, 1000000),
                "dtcpb": random.randint(0, 500000),
                "dwin": random.randint(0, 65535),
                "tcprtt": random.uniform(0.0, 0.2),
                "synack": random.uniform(0.0, 0.1),
                "ackdat": random.uniform(0.0, 0.1),
                "smean": random.randint(100, 1000),
                "dmean": random.randint(0, 500),
                "trans_depth": random.randint(0, 5),
                "response_body_len": random.randint(0, 2000),
                "ct_src_dport_ltm": random.randint(10, 100),
                "ct_dst_sport_ltm": random.randint(10, 100),
                "is_ftp_login": random.randint(0, 1),
                "ct_ftp_cmd": random.randint(0, 3),
                "ct_flw_http_mthd": random.randint(0, 10),
                "is_sm_ips_ports": random.randint(0, 1),
            }
        
        return {**base_data, **attack_data}
    else:
        # Generate normal traffic patterns
        normal_data = {
            "dur": random.uniform(10, 600),
            "proto": random.choice(['tcp', 'udp']),
            "service": random.choice(['http', 'ftp', 'ssh', 'dns', 'smtp']),
            "state": random.choice(['FIN', 'CON']),
            "spkts": random.randint(5, 50),
            "dpkts": random.randint(5, 50),
            "sbytes": random.randint(1000, 10000),
            "dbytes": random.randint(1000, 10000),
            "rate": random.uniform(0.5, 10.0),
            "sload": random.uniform(0.0, 0.3),
            "dload": random.uniform(0.0, 0.3),
            "sloss": 0,
            "dloss": 0,
            "sinpkt": random.uniform(0.1, 1.0),
            "dinpkt": random.uniform(0.1, 1.0),
            "sjit": random.uniform(0.0, 0.05),
            "djit": random.uniform(0.0, 0.05),
            "swin": random.randint(10000, 65535),
            "stcpb": random.randint(10000, 200000),
            "dtcpb": random.randint(10000, 200000),
            "dwin": random.randint(10000, 65535),
            "tcprtt": random.uniform(0.01, 0.5),
            "synack": random.uniform(0.01, 0.1),
            "ackdat": random.uniform(0.01, 0.1),
            "smean": random.randint(50, 200),
            "dmean": random.randint(50, 200),
            "trans_depth": random.randint(1, 5),
            "response_body_len": random.randint(100, 5000),
            "ct_src_dport_ltm": random.randint(1, 20),
            "ct_dst_sport_ltm": random.randint(1, 20),
            "is_ftp_login": 0,
            "ct_ftp_cmd": 0,
            "ct_flw_http_mthd": random.randint(1, 5),
            "is_sm_ips_ports": 0,
        }
        return {**base_data, **normal_data}

def send_data(data):
    """Send data to the API"""
    try:
        response = requests.post(API_URL, json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            node = result.get('node', {})
            print(f"✅ Submitted: {node.get('ip')} | Type: {node.get('attack_type')} | Anomaly: {node.get('is_anomaly')}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Cyber Attack Detection - Test Data Generator")
    print("UNSW-NB15 Format Data")
    print("=" * 60)
    print("\nThis script will send sample network data to the API.")
    print("Press Ctrl+C to stop.\n")
    
    try:
        count = 0
        attack_types_cycle = ['DoS', 'Exploits', 'Reconnaissance', 'Worms', 'Fuzzers', None, None, None]  # More normal than attacks
        while True:
            # Cycle through different attack types to test variety
            attack_type = random.choice(attack_types_cycle)
            data = generate_sample_data(attack_type=attack_type)
            if attack_type:
                print(f"🔴 Sending {attack_type.upper()} attack pattern...")
            send_data(data)
            count += 1
            time.sleep(1.5)  # Send data every 1.5 seconds
            
            if count % 10 == 0:
                print(f"\n📊 Sent {count} data points (varied attack types)...\n")
            
    except KeyboardInterrupt:
        print(f"\n\n✅ Test complete! Sent {count} data points.")
        print("Check your dashboard at http://localhost:3000")

if __name__ == "__main__":
    main()
