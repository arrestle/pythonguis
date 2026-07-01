"""
Diagnostic: send a §3.1.2 Program Dump Request and print every message received.

Usage:
    uv run python test-scripts/scripts/test_dump_request.py
"""
import sys
import time
import mido

OUT_MATCH = "UMC204HD"
IN_MATCH  = "UMC204HD"
TIMEOUT   = 5.0   # seconds to listen after sending request

out_name = next((n for n in mido.get_output_names() if OUT_MATCH in n), None)
in_name  = next((n for n in mido.get_input_names()  if IN_MATCH  in n), None)

if not out_name:
    sys.exit(f"No output port matching {OUT_MATCH!r}. Available: {mido.get_output_names()}")
if not in_name:
    sys.exit(f"No input port matching {IN_MATCH!r}. Available: {mido.get_input_names()}")

print(f"OUT: {out_name}")
print(f"IN:  {in_name}")

with mido.open_output(out_name) as out_port, mido.open_input(in_name) as in_port:
    # Small pause so the input port is fully ready before we send
    time.sleep(0.1)

    # §3.1.2 Program Dump Request — lower keyboard
    req = mido.Message("sysex", data=[0x0F, 0x01, 0x03])
    hex_req = " ".join(f"{b:02X}" for b in req.bytes())
    print(f"\nSending dump request: {hex_req}")
    out_port.send(req)

    print(f"Listening for {TIMEOUT}s ...\n")
    deadline = time.time() + TIMEOUT
    msg_count = 0

    while time.time() < deadline:
        for msg in in_port.iter_pending():
            msg_count += 1
            if msg.type == "sysex":
                data = list(msg.data)
                hex_str = " ".join(f"{b:02X}" for b in msg.bytes())
                print(f"[{msg_count}] sysex  len={len(data)+2}  header={hex_str[:20]}...")
                if len(data) >= 3:
                    print(f"     data[0..2] = {data[0]:02X} {data[1]:02X} {data[2]:02X}")
                    print(f"     nybble payload length = {len(data) - 3}")
            else:
                print(f"[{msg_count}] {msg}")
        time.sleep(0.02)

    print(f"\nDone. {msg_count} message(s) received.")
    if msg_count == 0:
        print("Nothing received — check MIDI cable direction, MASOS boot, and param 91.")
