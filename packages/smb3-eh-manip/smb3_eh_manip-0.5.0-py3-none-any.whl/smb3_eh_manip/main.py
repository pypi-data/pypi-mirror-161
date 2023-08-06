from signal import signal, SIGINT

from smb3_eh_manip.logging import initialize_logging
from smb3_eh_manip.settings import config
from smb3_eh_manip.computers import EhComputer, CalibrationComputer, TwoOneComputer


def handler(_signum, _frame):
    global computer
    print("SIGINT or CTRL-C detected. Exiting gracefully")
    computer.terminate()
    computer = None


def main():
    global computer
    initialize_logging()
    if config.get("app", "computer") == "eh":
        computer = EhComputer()
    elif config.get("app", "computer") == "twoone":
        computer = TwoOneComputer()
    else:
        computer = CalibrationComputer()
    while computer is not None:
        computer.tick()


if __name__ == "__main__":
    signal(SIGINT, handler)
    main()