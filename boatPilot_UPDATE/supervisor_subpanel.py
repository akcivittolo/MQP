from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit
)

import datetime

class SupervisorSubpanel(QWidget):
    def __init__(self, the_boat, telem_data):
        super().__init__()

        self.the_boat = the_boat
        self.telem_data = telem_data

        self.last_message = None

        # Connect telem data available signal to UI updater
        the_boat.connection_status_signal.connect(self.handle_connection)
        telem_data.telem_data_update.connect(self.update_UI)

        # Create a layout
        layout = QVBoxLayout(self)

        # Title and message 
        self.title = QLabel("Supervisor Computer")
        self.sup_message = QLabel("Placeholder")
        self.sup_message.setText("No data available")
        self.sup_message.setStyleSheet("background-color: red;")

        # Log View
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)

        # Add content to layout
        layout.addWidget(self.title)
        layout.addWidget(self.sup_message)
        layout.addWidget(self.log_view)
            
    def handle_connection(self, connection_status):
        if connection_status == True:
            self.sup_message.setStyleSheet("background-color: green;")
            self.sup_message.setText("Data available")

            message_to_print = self.addTimeStamp("Connection Initiated")

            self.log_view.appendPlainText(message_to_print)
        else:
            self.sup_message.setText("Disconnected")
            self.sup_message.setText("No data available")
            self.sup_message.setStyleSheet("background-color: red;")

            message_to_print = self.addTimeStamp("Connection Terminated")

            self.log_view.appendPlainText(message_to_print)

            self.last_message = None
    
    def update_UI(self):

        sup_message_text = self.telem_data.telemetry_data["STATUSTEXT"]["text"]
        sup_message_sev = self.telem_data.telemetry_data["STATUSTEXT"]["severity"]

        if sup_message_text != None:

            self.sup_message.setText(str(sup_message_text))
            message_to_print = self.addTimeStamp(sup_message_text)
            self.log_view.appendPlainText(message_to_print)

            self.last_message = str(sup_message_text)
        

    def addTimeStamp(self, text):
        current_time = datetime.datetime.now()
        formated_time = current_time.strftime("%H:%M:%S")
        final_text = (formated_time + ": " + str(text))

        return final_text



