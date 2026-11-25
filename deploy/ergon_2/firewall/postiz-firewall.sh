#!/bin/sh
# Restringe el puerto publicado 4007 (Postiz) al proxy 10.0.0.90. Idempotente.
IF=enp3s0
PROXY=10.0.0.90
PORT=4007
iptables -N DOCKER-USER 2>/dev/null || true
iptables -C DOCKER-USER -s $PROXY/32 -i $IF -p tcp -m conntrack --ctorigdstport $PORT -j RETURN 2>/dev/null \
  || iptables -I DOCKER-USER 1 -s $PROXY/32 -i $IF -p tcp -m conntrack --ctorigdstport $PORT -j RETURN
iptables -C DOCKER-USER -i $IF -p tcp -m conntrack --ctorigdstport $PORT -j DROP 2>/dev/null \
  || iptables -I DOCKER-USER 2 -i $IF -p tcp -m conntrack --ctorigdstport $PORT -j DROP
