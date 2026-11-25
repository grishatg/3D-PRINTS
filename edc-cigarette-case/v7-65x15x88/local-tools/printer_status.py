#!/usr/bin/env python3
"""READ-ONLY status of a Bambu Lab printer over its local MQTT port. It never sends a print, pause or stop command.

Setup:  pip install paho-mqtt
Usage (the three values come from the printer's own screen / Bambu Studio, never from a file in the repo):
    Windows PowerShell:  $env:BAMBU_IP="192.168.x.x"; $env:BAMBU_SERIAL="..."; $env:BAMBU_CODE="........"; python printer_status.py
    macOS / Linux:       BAMBU_IP=192.168.x.x BAMBU_SERIAL=... BAMBU_CODE=........ python3 printer_status.py
Options:  --watch 60   keep running, print one line every 60 s        --raw   also dump the merged JSON once

How it works (community-documented, not an official Bambu API; it can change with firmware):
  TLS MQTT on <printer ip>:8883, user "bblp", password = the LAN access code, topic device/<SERIAL>/report.
  A1 / P1 printers send only CHANGES, so the script asks once for the full state ("pushall") and then merges updates.
If the connection is refused or nothing arrives in 20 s: the printer may not allow local MQTT in its current mode. Do not change
the printer's network mode to make this work without asking the owner; use the Bambu Studio Device tab instead.
"""
import os, sys, ssl, json, time

def main():
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        print('paho-mqtt is not installed: pip install paho-mqtt'); return 2
    ip, serial, code = (os.environ.get(k) for k in ('BAMBU_IP', 'BAMBU_SERIAL', 'BAMBU_CODE'))
    if not (ip and serial and code):
        print(__doc__); return 2
    watch = int(sys.argv[sys.argv.index('--watch') + 1]) if '--watch' in sys.argv else 0
    state = {}; got = {'n': 0}

    def merge(a, b):
        for k, v in b.items():
            if isinstance(v, dict) and isinstance(a.get(k), dict): merge(a[k], v)
            else: a[k] = v

    def on_connect(client, userdata, *args):
        client.subscribe(f'device/{serial}/report')
        client.publish(f'device/{serial}/request', json.dumps({'pushing': {'sequence_id': '0', 'command': 'pushall'}}))

    def on_message(client, userdata, msg):
        try: merge(state, json.loads(msg.payload.decode('utf-8', 'replace')))
        except Exception: return
        got['n'] += 1

    try: client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)          # paho-mqtt 2.x
    except AttributeError: client = mqtt.Client()                          # paho-mqtt 1.x
    client.username_pw_set('bblp', code)
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE   # the printer's certificate is self-signed
    client.tls_set_context(ctx)
    client.on_connect = on_connect; client.on_message = on_message
    try: client.connect(ip, 8883, keepalive=60)
    except Exception as e:
        print('could not connect to', ip, 'port 8883:', e); return 1
    client.loop_start()
    t0 = time.time()
    while not got['n'] and time.time() - t0 < 20: time.sleep(0.5)
    if not got['n']:
        print('connected, but no status arrived in 20 s (wrong serial, or local MQTT is not allowed in this mode)'); client.loop_stop(); return 1
    time.sleep(2)

    def line():
        p = state.get('print', {})
        ams = p.get('ams', {}).get('ams', [])
        trays = []
        for unit in ams:
            for t in unit.get('tray', []):
                if t.get('tray_type') or t.get('tray_sub_brands'):
                    trays.append(f"slot {int(t.get('id', 0)) + 1}: {t.get('tray_sub_brands') or t.get('tray_type')} #{str(t.get('tray_color', ''))[:6]} {t.get('remain', '?')}%")
        hms = [f"{h.get('attr', 0):08X}_{h.get('code', 0):08X}" for h in p.get('hms', [])]
        return (f"{time.strftime('%H:%M:%S')} state={p.get('gcode_state', '?')} {p.get('mc_percent', '?')}% left={p.get('mc_remaining_time', '?')}min "
                f"layer={p.get('layer_num', '?')}/{p.get('total_layer_num', '?')} nozzle={p.get('nozzle_temper', '?')}/{p.get('nozzle_target_temper', '?')} "
                f"bed={p.get('bed_temper', '?')}/{p.get('bed_target_temper', '?')} job={p.get('subtask_name', '')!r} error={p.get('print_error', 0)} "
                f"hms={hms or 'none'} | AMS: {'; '.join(trays) or 'no data'}")
    print(line())
    if '--raw' in sys.argv: print(json.dumps(state, indent=1)[:6000])
    while watch:
        time.sleep(watch); print(line(), flush=True)
    client.loop_stop(); client.disconnect(); return 0

if __name__ == '__main__':
    sys.exit(main())
