import importlib.resources as resources
import xmltodict
import pymavlink
from pymavlink import mavutil

from connectionFunctions import *
# Enter the following code into WSL to start the simulation:
# sim_vehicle.py -v Rover -f motorboat-skid -A "--serial0=tcp:0.0.0.0:5760" --no-mavproxy

# # Device ID to connect to
# DEVICE = "tcp:172.21.103.161:5760"

# # Establish connection to the device
# master_connection = startConnection(DEVICE)

# Define what message types we actually want
desired_message_types = ['SYS_STATUS',
                         'GPS_RAW_INT',
                         'GLOBAL_POSITION_INT',
                         'ATTITUDE',
                         'BATTERY_STATUS',
                         'HEARTBEAT',
                         'VFR_HUD',
                         'MISSION_CURRENT'
                        ]

# There are various sources that define messages and enums for mavlink
# message_paths = ['message_definitions/v1.0/common.xml',
#                 'message_definitions/v1.0/minimal.xml'
#                ]

message_paths = ['dialects/v10/common.xml',
                 'dialects/v10/minimal.xml'
                ]


def read_and_parse_file(message_path):
    # We want to access the .xml that contains our definitions
    common_file = resources.files(pymavlink).joinpath(message_path)
    
    # Open and read the .xml file we've chosen
    with common_file.open("r") as file:
        read_xml = file.read()
        print("We read the file")

    # Use xmltodict to parse and convert 
    # the XML document
    mavlink_dictionary = xmltodict.parse(read_xml)

    return mavlink_dictionary

def ensure_list_of_dicts(item):
    if isinstance(item, list):
        return item
    else:
        return [item]

def prepare_message_dictionary():

    mavlink_common_dictionary = read_and_parse_file(message_paths[0])
    mavlink_minimal_dictionary = read_and_parse_file(message_paths[1])

    # Create a list of available message types
    common_messages_available = mavlink_common_dictionary['mavlink']['messages']['message']
    minimal_messages_available = mavlink_minimal_dictionary['mavlink']['messages']['message']
    combined_messages_available = ensure_list_of_dicts(common_messages_available) + ensure_list_of_dicts(minimal_messages_available)

    ordered_messages = []

    for msg_type in desired_message_types:
        for msg in combined_messages_available:
            if msg.get('@name') == msg_type:
                fields = msg.get('field', [])
                if isinstance(fields, dict):
                    # Single field → wrap in list
                    fields = [fields]
                
                # Extract just the names
                field_names = [f['@name'] for f in fields]
                
                ordered_messages.append({
                    'name': msg_type,
                    'description': msg.get('description', ''),
                    'fields': field_names,
                    'field_values': {}  # prepare dict to store live values
                })
                break
    return ordered_messages

# Change the default set of messages sent by the boat
def set_messages(master_connection, ordered_messages = prepare_message_dictionary()):
    for msg in ordered_messages:
        msg_name = msg['name']
        msg_id = getattr(mavutil.mavlink, f"MAVLINK_MSG_ID_{msg_name}")
        master_connection.mav.command_long_send(
            master_connection.target_system,
            master_connection.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
            0,
            msg_id,
            1000000,
            0,0,0,0,0
        )
        print(f'Added {msg_name} to communications')

def get_desired_messages(master_connection):
    while True:
        if master_connection != None:
            msg = master_connection.recv_match(blocking=False)

            if msg == None:
                break

            msg_type = msg.get_type()
            for type in desired_message_types:
                if type == msg_type:
                    return(msg)
            break
        else:
            break

def get_msg_fields(msg):
    if msg != None:
        fieldnames = msg.get_fieldnames()

        fields = []
        
        for field in fieldnames:
            fields.append(field)
    
        return fields
    
def get_msg_values(msg):
    if msg != None:
        fieldnames = msg.get_fieldnames()

        values = []
        
        for field in fieldnames:
            values.append(getattr(msg, field))
    
        return values
