# TCP by UDP
Use User Datagram Protocol (UDP) to simulate reliable data transmission and
congestion control that are provided in Transmission Control Protocol (TCP).

## Specification
`spec/CN2018_hw2_spec.pdf`

## File Descriptions
- `Sender.py`: Establish a socket that is responsible for sending packets to `Agent.py` and receive acknowledgements from `Agent.py`.
- `Agent.py`: Establish a socket that will randomly drop packets from `Sender.py` and forward other packets.
- `Receiver.py`: Establish a socket that will receive packets from `Agent.py`
  and send acknowledgements to `Agent.py`.
- `utils.py`: Define some shared functions and arguments.

## Requirement
- Python3

## Usage
Type `python3 Agent.py`, `python3 Receiver.py`, and python3 Sender.py` one by
one and in the same order.

Default arguments are defined in the `parse_args' function in file `utils.py`.
