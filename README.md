# Digital Taxi Meter

A command-line taxi meter built in Python for Phase 1 of the TaxiTech project.

## Requirements

- Python 3.10 or newer

## Run the program

Open a terminal in this folder and run:

    python taximetro.py

## Commands

| Command | Action |
|---|---|
| `i` | Start a ride |
| `p` | Set the taxi state to stopped |
| `m` | Set the taxi state to moving |
| `f` | Finish the ride and show the fare |
| `a` | Show help |
| `s` | Exit when no ride is active |

## Fare calculation

The meter charges €0.02 per second while stopped and €0.05 per second while moving. It calculates the cost for each time segment and adds those costs to the ride total.

## Implementation notes

The program uses `time.monotonic()` to measure elapsed time. The fare calculation is split into segments so each segment uses the correct rate for the taxi's state.