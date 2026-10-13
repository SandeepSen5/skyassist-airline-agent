import re
from datetime import datetime

BOOKINGS = {
    "ABC123": {"passenger": "Priya Sharma", "flight": "AI101", "date": "2026-10-20",
               "seat": "14A", "status": "CONFIRMED", "fare": "ECONOMY"},
    "XYZ789": {"passenger": "John Smith", "flight": "AI202", "date": "2026-10-22",
               "seat": "3C", "status": "CONFIRMED", "fare": "BUSINESS"},
}
FLIGHTS = {
    "AI101": {"from": "DEL", "to": "BOM", "dep": "08:30", "status": "ON TIME", "gate": "B12"},
    "AI202": {"from": "BOM", "to": "BLR", "dep": "14:10", "status": "DELAYED 45 min", "gate": "A3"},
}
BAGGAGE = {"ECONOMY": "1 x 15 kg checked, 7 kg cabin",
           "BUSINESS": "2 x 30 kg checked, 10 kg cabin"}


def get_booking(pnr: str) -> dict:
    """Look up a booking by its 6-character PNR/booking reference."""
    return BOOKINGS.get(pnr.upper(), {"error": f"No booking found for {pnr}"})


def get_flight_status(flight_number: str) -> dict:
    """Get live status, departure time and gate for a flight number like AI101."""
    return FLIGHTS.get(flight_number.upper(), {"error": f"Unknown flight {flight_number}"})


def search_flights(origin: str, destination: str, date: str) -> list:
    """Search flights between IATA airport codes (e.g. DEL, BOM) on a YYYY-MM-DD date."""
    return [{"flight": k, **v, "date": date} for k, v in FLIGHTS.items()
            if v["from"] == origin.upper() and v["to"] == destination.upper()]


def change_seat(pnr: str, new_seat: str) -> dict:
    """Change the seat on an existing booking. new_seat looks like '12C'."""
    b = BOOKINGS.get(pnr.upper())
    if not b:
        return {"error": "Booking not found"}
    if b["status"] == "CANCELLED":
        return {"error": "Booking is cancelled; seat cannot be changed"}
    seat = new_seat.strip().upper()
    if not re.fullmatch(r"([1-9]|[1-3][0-9])[A-F]", seat):
        return {"error": f"Invalid seat '{new_seat}'. Use a row 1-39 and letter A-F, e.g. 12C"}
    if any(o is not b and o["flight"] == b["flight"] and o["date"] == b["date"]
           and o["seat"] == seat and o["status"] != "CANCELLED"
           for o in BOOKINGS.values()):
        return {"error": f"Seat {seat} is already taken"}
    b["seat"] = seat
    return {"success": True, "pnr": pnr.upper(), "new_seat": seat}


def cancel_booking(pnr: str) -> dict:
    """Cancel a booking. Only call after the customer has explicitly confirmed."""
    b = BOOKINGS.get(pnr.upper())
    if not b:
        return {"error": "Booking not found"}
    if b["status"] == "CANCELLED":
        return {"error": "Booking is already cancelled"}
    b["status"] = "CANCELLED"
    return {"success": True, "pnr": pnr.upper(), "cancelled_at": datetime.now().isoformat()}


def get_baggage_allowance(fare_class: str) -> dict:
    """Get baggage allowance for a fare class: ECONOMY or BUSINESS."""
    return {"fare_class": fare_class.upper(),
            "allowance": BAGGAGE.get(fare_class.upper(), "Unknown fare class")}


ALL_TOOLS = [get_booking, get_flight_status, search_flights,
             change_seat, cancel_booking, get_baggage_allowance]
