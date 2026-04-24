from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPlainTextEdit,
    QGroupBox
)

from PyQt6.QtCore import Qt

import datetime

class SupervisorSubpanel(QGroupBox):
    def __init__(self, the_boat, telem_data):
        super().__init__("Supervisor Computer")

        self.the_boat = the_boat
        self.telem_data = telem_data

        self.last_message = None

        # Connect telem data available signal to UI updater
        the_boat.connection_status_signal.connect(self.handle_connection)
        telem_data.telem_data_update.connect(self.update_UI)

        # Create a layout
        layout = QVBoxLayout(self)

        # Title and message 
        # self.title = QLabel("Supervisor Computer")
        # self.sup_message = QLabel("Placeholder")
        # self.sup_message.setText("No data available")
        # self.sup_message.setStyleSheet("background-color: red;")

        # Log View
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # Add content to layout
        # layout.addWidget(self.title)
        # layout.addWidget(self.sup_message)
        layout.addWidget(self.log_view)
            
    def handle_connection(self, connection_status):
        if connection_status == True:
            # self.sup_message.setStyleSheet("background-color: green;")
            # self.sup_message.setText("Data available")

            message_to_print = self.addTimeStamp("Connection Initiated")

            self.log_view.appendPlainText(message_to_print)
        else:
            # self.sup_message.setText("Disconnected")
            # self.sup_message.setText("No data available")
            # self.sup_message.setStyleSheet("background-color: red;")

            message_to_print = self.addTimeStamp("Connection Terminated")

            self.log_view.appendPlainText(message_to_print)

            self.last_message = None
    
    def update_UI(self):

        sup_message_text = self.telem_data.telemetry_data["STATUSTEXT"]["text"]
        sup_message_sev = self.telem_data.telemetry_data["STATUSTEXT"]["severity"]

        print(f"Updating ui with {sup_message_text}")

        if sup_message_text != None:

            # self.sup_message.setText(str(sup_message_text))
            message_to_print = self.addTimeStamp(sup_message_text)

            if self.last_message != str(sup_message_text):
                self.log_view.appendPlainText(message_to_print)


            self.last_message = str(sup_message_text)

        self.log_view.verticalScrollBar().setValue(self.log_view.verticalScrollBar().maximum())
        

    def addTimeStamp(self, text):
        current_time = datetime.datetime.now()
        formated_time = current_time.strftime("%H:%M:%S")
        if "SUP" in text:
            cleaned_text = text[4:]
            final_text = (formated_time + " SUPERVISOR: " + str(cleaned_text))
        else:
            final_text = (formated_time + " PIXHAWK: " + str(text))

        return final_text



