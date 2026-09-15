#!/usr/bin/env python3
"""
NIGHTWIRE Stage 5 - PCAP Builder
Generates a sample PCAP with DNS-tunnelled TXT queries.

Note: This is a development reference script.
The final production PCAP must be generated with the controlled lab build script.
"""

import os
from pathlib import Path

try:
    from scapy.all import (
        IP, UDP, DNS, DNSQR, DNSRR, Ether,
        wrpcap
    )
except ImportError:
    print("[!] scapy is required: pip install scapy")
    raise SystemExit(1)


OUTPUT = "artifacts/exfil_capture.pcapng"
FLAG = "NIGHTWIRE{packet_trail_complete}"

# Simulated DNS tunnel: base64 chunks as subdomain labels
CHUNKS = [
    "TklHSFRXSVJFe3BhY2tldF90cmFpbF9jb21wbGV0ZX0",
    "aWFtbmlnaHR3aXJl",
    "c3RhZ2U1",
]


def build_dns_tunnel_pcap():
    packets = []
    src_ip = "10.20.0.50"
    dst_ip = "8.8.8.8"

    for i, chunk in enumerate(CHUNKS):
        pkt = (
            Ether()
            / IP(src=src_ip, dst=dst_ip)
            / UDP(sport=53000 + i, dport=53)
            / DNS(
                id=0x1234 + i,
                qr=0,
                qdcount=1,
                qd=DNSQR(qname=f"{chunk}.exfil.nightwire.local", qtype="TXT"),
            )
        )
        packets.append(pkt)

    # Also add a TXT response for realism
    for i, chunk in enumerate(CHUNKS):
        pkt = (
            Ether()
            / IP(src=dst_ip, dst=src_ip)
            / UDP(sport=53, dport=53000 + i)
            / DNS(
                id=0x1234 + i,
                qr=1,
                qdcount=1,
                ancount=1,
                qd=DNSQR(qname=f"{chunk}.exfil.nightwire.local", qtype="TXT"),
                an=DNSRR(
                    rrname=f"{chunk}.exfil.nightwire.local",
                    type="TXT",
                    ttl=300,
                    rdata=chunk,
                ),
            )
        )
        packets.append(pkt)

    Path("artifacts").mkdir(exist_ok=True)
    wrpcap(OUTPUT, packets)
    print(f"[+] Wrote {len(packets)} packets to {OUTPUT}")


if __name__ == "__main__":
    build_dns_tunnel_pcap()
