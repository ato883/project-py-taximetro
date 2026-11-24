import time
import json
import logging
import csv
from datetime import datetime
from pathlib import Path

HELP = """
Digital Taxi Meter
  i  start a ride (starts STOPPED)
  p  taxi is stopped
  m  taxi is moving
  f  finish the ride and show the total
  h  show today's ride history
  a  show this help
  s  exit
"""

PROJECT_DIR = Path(__file__).parent
CONFIG_FILE = PROJECT_DIR / "config.json"
LOG_FILE = PROJECT_DIR / "taximetro.log"
HISTORY_FILE = PROJECT_DIR / "historial.csv"

DEFAULT_RATES = {
    "tarifa_parado": 0.02,
    "tarifa_movimiento": 0.05,
}

log = logging.getLogger("taximeter")

def configure_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        encoding="utf-8",
        format="%(asctime)s %(levelname)s %(message)s",
    )
    
def save_trip(started_at, duration, fare, path=HISTORY_FILE):
    path = Path(path)
    is_new_file = not path.exists()

    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if is_new_file:
            writer.writerow(["fecha", "hora", "duracion_s", "importe"])

        writer.writerow([
            started_at.strftime("%Y-%m-%d"),
            started_at.strftime("%H:%M:%S"),
            round(duration),
            f"{fare:.2f}",
        ])



def load_rates(path=CONFIG_FILE):
    try:
        values = json.loads(Path(path).read_text(encoding="utf-8"))
        rates = {
            "tarifa_parado": float(values["tarifa_parado"]),
            "tarifa_movimiento": float(values["tarifa_movimiento"]),
        }
    except (OSError, KeyError, TypeError, ValueError) as error:
        log.warning(
            "Could not load rates from %s (%s); using default rates",
            path,
            error,
        )
        return DEFAULT_RATES.copy()

    log.info("Rates loaded from %s: %s", path, rates)
    return rates

def get_rate(state, rates):
    if state == "stopped":
        return rates["tarifa_parado"]
    elif state == "moving":
        return rates["tarifa_movimiento"]
    raise ValueError(f"Unknown taxi state: {state}")

def calculate_segment_fare(seconds, state, rates):
    if seconds < 0:
        raise ValueError("Seconds cannot be negative")

    rate = get_rate(state, rates)
    return seconds * rate


def importe_tramo(segundos, estado, tarifas):
    # Compatibility with the function name and state names in the course guide.
    english_state = {
        "parado": "stopped",
        "movimiento": "moving",
    }.get(estado, estado)

    if segundos < 0:
        raise ValueError("Los segundos no pueden ser negativos")

    return calculate_segment_fare(segundos, english_state, tarifas)

def close_segment(trip, rates):
    now = time.monotonic()
    seconds = now - trip["since"]
    trip["fare"] += calculate_segment_fare(
    seconds,
    trip["state"],
    rates,
)
    trip["since"] = now

def trips_today(path=HISTORY_FILE):
    path = Path(path)

    if not path.exists():
        return []

    today = datetime.now().strftime("%Y-%m-%d")

    with path.open("r", newline="", encoding="utf-8") as file:
        return [
            ride
            for ride in csv.DictReader(file)
            if ride["fecha"] == today
        ]
        
def main():
    configure_logging()
    log.info("Taxi meter started")
    rates = load_rates()
    trip = None
    print(HELP)

    while True:
        command = input("> ").strip().lower()

        if command == "a":
            print(HELP)

        elif command == "i":
            if trip is not None:
                print("A ride is already in progress. Finish it with 'f'.")
            else:
                log.info("Ride started")
                trip = {
                    "state": "stopped",
                    "since": time.monotonic(),
                    "fare": 0.0,
                    "started_at": datetime.now(),
                    "start_monotonic": time.monotonic(),
                }
                print("Ride started. The taxi is STOPPED.")

        elif command in ("p", "m"):
            if trip is None:
                print("Start a ride first with 'i'.")
            else:
                new_state = "stopped" if command == "p" else "moving"

                if trip["state"] == new_state:
                    print(f"The taxi is already {new_state}.")
                else:
                    close_segment(trip, rates)
                    log.info("State changed to %s (€%.2f accrued)", new_state, trip["fare"])
                    trip["state"] = new_state
                    print(
                        f"State: {new_state.upper()}. "
                        f"Fare so far: €{trip['fare']:.2f}"
                    )
        elif command == "f":
            if trip is None:
                print("There is no ride in progress.")
            else:
                close_segment(trip, rates)

                duration = time.monotonic() - trip["start_monotonic"]
                save_trip(trip["started_at"], duration, trip["fare"])

                print(f"Ride finished. Total fare: €{trip['fare']:.2f}")
                trip = None
        elif command == "h":
            rides = trips_today()

            if not rides:
                print("No rides recorded today.")
            else:
                total = 0.0

                for ride in rides:
                    duration = int(ride["duracion_s"])
                    fare = float(ride["importe"])
                    total += fare
                    print(
                        f"  {ride['hora']}  {duration:>5} s  "
                        f"{fare:>8.2f} €"
                    )

                print(f"  Today's total: {total:.2f} €")                        
        elif command == "s":
            log.info("Taxi meter closed")
            print("Goodbye.")
            break

        else:
            log.warning("Unknown command: %r", command)
            print("Unknown command. Type 'a' to see the help.")


if __name__ == "__main__":
    main()