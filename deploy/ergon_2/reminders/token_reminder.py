#!/usr/bin/env python3
"""Avisa por correo cuando un canal de Postiz está por vencer (10 y 3 días) o ya requiere reconexión.
Uso: token_reminder.py [--dry-run] [--test]
Lee SMTP de /opt/postiz/.env. Destinatario: REMINDER_TO (si no existe, EMAIL_FROM_ADDRESS)."""
import json, os, smtplib, ssl, subprocess, sys
from datetime import datetime, timezone
from email.message import EmailMessage

BASE = "/opt/postiz"
STATE = f"{BASE}/reminders/state.json"
THRESHOLDS = (10, 3)
# Proveedores cuyo token tiene una fecha de vencimiento real que obliga a reconectar.
# YouTube/TikTok renuevan el access token solos: solo se avisa si quedan con refreshNeeded.
DATED = {"instagram", "instagram-standalone", "facebook", "linkedin", "linkedin-page", "threads"}
DRY = "--dry-run" in sys.argv
TEST = "--test" in sys.argv

def load_env():
    env = {}
    for line in open(f"{BASE}/.env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v.strip().strip('"').strip("'")
    return env

def query():
    sql = ("select json_agg(t) from (select i.id, i.name, i.\"providerIdentifier\" prov, o.name org, "
           "i.\"tokenExpiration\" exp, i.\"refreshNeeded\" rn from \"Integration\" i "
           "join \"Organization\" o on o.id=i.\"organizationId\" "
           "where i.\"deletedAt\" is null and i.disabled=false) t")
    out = subprocess.run(["docker", "exec", "postiz-postgres", "psql", "-U", "postiz", "-d", "postiz", "-tAc", sql],
                         capture_output=True, text=True, check=True).stdout.strip()
    return json.loads(out) if out and out != "" else []

def send(env, subject, body):
    to = env.get("REMINDER_TO") or env.get("EMAIL_FROM_ADDRESS")
    msg = EmailMessage()
    msg["Subject"], msg["To"] = subject, to
    msg["From"] = f'{env.get("EMAIL_FROM_NAME","Postiz")} <{env["EMAIL_FROM_ADDRESS"]}>'
    msg.set_content(body)
    if DRY:
        print(f"[dry-run] -> {to}\n{subject}\n{body}\n"); return
    with smtplib.SMTP_SSL(env["EMAIL_HOST"], int(env["EMAIL_PORT"]), context=ssl.create_default_context()) as s:
        s.login(env["EMAIL_USER"], env["EMAIL_PASS"]); s.send_message(msg)

def main():
    env = load_env()
    if TEST:
        send(env, "[Postiz] Prueba de recordatorios", "Si lees esto, el aviso de vencimiento de canales funciona."); return
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    now = datetime.now(timezone.utc)
    alerts, new_state = [], {}
    for it in query() or []:
        key, label = it["id"], f'{it["org"]} · {it["prov"]} · {it["name"]}'
        if it["rn"]:
            k = f"{key}:rn"; new_state[k] = True
            if k not in state: alerts.append((0, f"YA REQUIERE RECONEXIÓN: {label}"))
            continue
        if it["prov"] in DATED and it["exp"]:
            exp = datetime.fromisoformat(it["exp"].replace(" ", "T"))
            if exp.tzinfo is None: exp = exp.replace(tzinfo=timezone.utc)
            days = (exp - now).days
            for t in THRESHOLDS:
                k = f"{key}:{t}"
                if days <= t:
                    new_state[k] = True
                    if k not in state:
                        alerts.append((days, f"Vence en {max(days,0)} día(s) ({exp:%d-%m-%Y}): {label}"))
                    break
    if alerts:
        alerts.sort()
        body = ("Estos canales de Postiz necesitan reconexión:\n\n" + "\n".join(f"- {a[1]}" for a in alerts) +
                "\n\nCómo reconectar: entra a https://postiz.semigod.cl/launches, abre el canal "
                "(el que tiene el aviso) y vuelve a autorizarlo.\n")
        send(env, f"[Postiz] {len(alerts)} canal(es) por vencer o desconectados", body)
    if not DRY:
        json.dump(new_state, open(STATE, "w"))
    print(f"{now:%F %T} revisados; alertas nuevas: {len(alerts)}")

main()
