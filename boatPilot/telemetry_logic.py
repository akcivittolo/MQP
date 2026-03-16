from pymavlink import mavutil
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class TelemetryData(QObject):
    def __init__(self, the_boat):
        super().__init__()
        self.telemetry_data = {
            "BATTERY_STATUS": {
                "battery_remaining": None
            },
            "ATTITUDE": {
                "roll": None,
                "pitch": None,
                "yaw": None
            },
            "GLOBAL_POSITION_INT": {
                "lat": None,
                "lon": None,
                "alt": None,
                "hdg": None
            },
            "GPS_RAW_INT": {
                "vel": None
            },
            "HEARTBEAT": {
                "base_mode": None
            }
            # "STATUSTEXT": {
            #     "severity": None,
            #     "text": None
            # }
        }

        # Used for telemetry data updates
        self.message_types = list(self.telemetry_data.keys())
        self.message_type_index = 0

        self.the_boat = the_boat

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_telemetry_data)
        self.timer.timeout.connect(self.the_boat.get_arm_status)

        # Connect connection status signal
        self.the_boat.connection_status_signal.connect(self.request_messages)

    def request_messages(self, connection_status):
        if connection_status == True:
            for message_type in self.telemetry_data:
                # Peforme getattr() for a numerical value
                msg_name= "MAVLINK_MSG_ID_" + message_type
                msg_id = getattr(mavutil.mavlink, msg_name)

                self.the_boat.master_connection.mav.command_long_send(
                    self.the_boat.master_connection.target_system,
                    self.the_boat.master_connection.target_component,
                    mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
                    0,
                    msg_id,
                    1000000,
                    0,0,0,0,0
                )

                print(f"Added {msg_name} to comms")

            # Begin updating telemetry data
            self.timer.start()
        else:

            # Stop updating telemetry data
            self.timer.stop()
            pass

    def update_telemetry_data(self):
        message_type_wanted = self.message_types[self.message_type_index]
        msg = self.the_boat.master_connection.recv_match(type = message_type_wanted, blocking=False)
        
        if msg != None:

            for field in self.telemetry_data[message_type_wanted]:
                new_value = getattr(msg, field)
                self.telemetry_data[message_type_wanted][field] = new_value

            self.message_type_index += 1
            if self.message_type_index >= len(self.message_types):
                self.message_type_index = 0

            



    





        


