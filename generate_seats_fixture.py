import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

def generate_seater_seats(bus_id: int, start_pk: int, rows=10, cols=4):
    """
    Generates seat numbers like: A1..A4, B1..B4 ... for 10 rows x 4 cols = 40 seats
    """
    data = []
    pk = start_pk
    for r in range(1, rows + 1):
        row_letter = chr(64 + r)  # A, B, C...
        for c in range(1, cols + 1):
            data.append({
                "model": "buses.seat",
                "pk": pk,
                "fields": {
                    "bus": bus_id,
                    "seat_number": f"{row_letter}{c}",
                    "seat_type": "SEATER",
                    "deck": "LOWER",
                    "row": r,
                    "col": c
                }
            })
            pk += 1
    return data

fixtures = []
fixtures += generate_seater_seats(bus_id=1, start_pk=1, rows=10, cols=4)     # 40 seats
fixtures += generate_seater_seats(bus_id=2, start_pk=1001, rows=10, cols=4)  # 40 seats (pk gap avoids clashes)

out_path = BASE / "apps" / "buses" / "fixtures" / "buses_seat.json"
out_path.parent.mkdir(parents=True, exist_ok=True)

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(fixtures, f, indent=2)

print(f"✅ Generated: {out_path}")
print(f"Total seats: {len(fixtures)}")