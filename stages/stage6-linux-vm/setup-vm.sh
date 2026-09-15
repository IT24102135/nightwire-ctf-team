#!/bin/bash
# NIGHTWIRE Stage 6 - VM Configuration Script
# Run inside the nightwire-final Ubuntu 20.04 VM as root.

set -e

echo "[*] Creating svc_backup user..."
adduser --disabled-password --gecos "" svc_backup

echo "[*] Setting up writable cron job..."
mkdir -p /opt/maint
cat > /opt/maint/cleanup.sh << 'EOF'
#!/bin/bash
echo "Nightwire maintenance completed"
EOF
chmod +x /opt/maint/cleanup.sh
chmod 777 /opt/maint/cleanup.sh

echo "[*] Adding root cron job..."
(crontab -l 2>/dev/null; echo "* * * * * /opt/maint/cleanup.sh") | crontab -

echo "[*] Configuring sudo find misconfiguration..."
echo "svc_backup ALL=(ALL) NOPASSWD: /usr/bin/find" > /etc/sudoers.d/nightwire
chmod 440 /etc/sudoers.d/nightwire
visudo -c

echo "[*] Creating flag file..."
echo "NIGHTWIRE{r00t_0f_n1ghtw1r3_c4pst0n3}" > /root/flag.txt
chmod 600 /root/flag.txt

echo "[*] Setting up SSH..."
apt install -y openssh-server
systemctl enable --now ssh

echo "[+] Stage 6 setup complete."
