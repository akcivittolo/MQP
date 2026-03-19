boatPilot Ground Control Software

Project Goals:
1. Connect and communicate with a Mavlink source
2. Display information recovered from the Mavlink source
3. Present data and controls on a GUI

connection.py
- This offers connection and disconnection functions to the Mavlink address
- Uses the mavutil from pymavlink

telemetry.py
- Contains a list of all the messages we'd like to receive
- Configures the flight controller to send those desired messages
- Offers a function to update a list of the fields we have




