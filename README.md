# Fixed Value Untrue Precise Time Server

## Requirements
Python 3.7+

## Algorithm
Client and Server built on utilization of NTP Packets.
In trivia, client sends request packet that contains it's current time (origin).
Then server responds with packet that contains origin, client packet receive time (receive)
and time that new packet will be sent (transmit).
Then client receives packet and saves the time it arrived (arrive).
Using these four values clock time delta (pretending to and 
from packet traversal times are equal) evaluated by formulae:
`Delta = (Receive – Originate + (Transmit - Arrive)`.
This value is then added to local time to get precise value

To create time offset server changes it's receive and transmit time for given value

## Usage
Both server and client are started as python-executable file:
```bash
python server.py
python client.py
```

To configure server time offset open `config.json` file and change value at `time_offset`