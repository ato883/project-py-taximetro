import time

HELP = """
Digital Taxi Meter
  i  start a ride (starts STOPPED)
  p  taxi is stopped
  m  taxi is moving
  f  finish the ride and show the total
  a  show this help
  s  exit
"""

STOPPED_RATE = 0.02
MOVING_RATE = 0.05


def get_rate(state):
    if state == "stopped":
        return STOPPED_RATE
    elif state == "moving":
        return MOVING_RATE


def close_segment(trip):
    now = time.monotonic()
    seconds = now - trip["since"]
    rate = get_rate(trip["state"])
    trip["fare"] += seconds * rate
    trip["since"] = now


def main():
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
                trip = {
                    "state": "stopped",
                    "since": time.monotonic(),
                    "fare": 0.0,
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
                    close_segment(trip)
                    trip["state"] = new_state
                    print(
                        f"State: {new_state.upper()}. "
                        f"Fare so far: €{trip['fare']:.2f}"
                    )
        elif command == "f":
            if trip is None:
                print("There is no ride in progress.")
            else:
                close_segment(trip)
                print(f"Ride finished. Total fare: €{trip['fare']:.2f}")
                trip = None                
        elif command == "s":
            print("Goodbye.")
            break

        else:
            print("Unknown command. Type 'a' to see the help.")


if __name__ == "__main__":
    main()