# updated 2:21 pm 12/8 with copypasted get_base_current and function defns
# Control Loop with MAVLink Communication for ASV
from pymavlink import mavutil
import time
import sys

# ----------------------------
# Connect to Flight Controller
# ----------------------------
# def connect_to_fc():
#     """Connect to flight controller via UART"""
#     try:
#         # Common UART ports - adjust based on your setup
#         ports_to_try = [
#             '/dev/ttyAMA0',  # Raspberry Pi GPIO
#         ]
        
#         for port in ports_to_try:
#             try:
#                 print(f"Trying {port}...")
#                 master = mavutil.mavlink_connection(port, baud=57600)
#                 master.wait_heartbeat(timeout=3)
#                 print(f"Connected to flight controller on {port}")
#                 return master
#             except:
#                 continue
        
#         print("No flight controller found. Check connections.")
#         sys.exit(1)
        
#     except Exception as e:
#         print(f"Connection error: {e}")
#         sys.exit(1)

# # Connect
# master = connect_to_fc()

# ----------------------------
# Connect to SITL (VIA CHAT)
# ----------------------------
def connect_to_sitl():
    """Connect to SITL simulator"""
    try:
        # SITL typically listens on TCP port 5760
        print("Connecting to SITL on TCP 127.0.0.1:5760...")
        master = mavutil.mavlink_connection('tcp:127.0.0.1:5760')
        master.wait_heartbeat(timeout=5)
        print(f"Connected to SITL! System ID: {master.target_system}")
        return master
    except Exception as e:
        print(f"SITL connection failed: {e}")
        print("\nTrying UDP connection...")
        try:
            # Alternative: UDP connection (used by QGroundControl)
            master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
            master.wait_heartbeat(timeout=5)
            print("Connected via UDP")
            return master
        except:
            print("Could not connect to SITL.")
            print("\nStart SITL first with:")
            print("  sim_vehicle.py -v ArduSub --console --map")
            sys.exit(1)

# Connect to SITL
master = connect_to_sitl()





# ----------------------------
# MAVLink Message Senders
# ----------------------------
def send_statustext(text, severity=6):
    """
    Send status text message to flight controller/GCS
    severity: 0=EMERGENCY, 1=ALERT, 2=CRITICAL, 3=ERROR, 
              4=WARNING, 5=NOTICE, 6=INFO, 7=DEBUG
    """
    # MAV_SEVERITY levels
    master.mav.statustext_send(
        severity,
        text.encode()[:50]  # Max 50 chars
    )
    print(f"MAVLink STATUSTEXT: {text}")

def send_heartbeat():
    """Send custom heartbeat (optional)"""
    master.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_SURFACE_BOAT,  # Type: ASV
        mavutil.mavlink.MAV_AUTOPILOT_INVALID,  # Custom autopilot
        0, 0, 0, 0
    )

def send_system_status():
    """Send system status"""
    master.mav.sys_status_send(
        0,  # onboard_control_sensors_present
        0,  # onboard_control_sensors_enabled
        0,  # onboard_control_sensors_health
        500,  # load (0-1000)
        12000,  # voltage_battery (mV)
        0,  # current_battery (mA)
        85,  # battery_remaining (%)
        0,  # drop_rate_comm
        0,  # errors_comm
        0,  # errors_count1
        0,  # errors_count2
        0,  # errors_count3
        0   # errors_count4
    )

def send_nav_controller_output():
    """Send navigation controller output"""
    master.mav.nav_controller_output_send(
        0.0,  # nav_roll (deg)
        0.0,  # nav_pitch (deg)
        0.0,  # nav_bearing (deg)
        0,    # target_bearing (deg)
        0,    # wp_dist (m)
        0.0,  # alt_error (m)
        0.0,  # aspd_error (m/s)
        0.0   # xtrack_error (m)
    )

def send_position_target_global_int(lat, lon, alt=0):
    """Send position target (for guided mode)"""
    master.mav.set_position_target_global_int_send(
        0,  # time_boot_ms
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
        0xFFF8,  # type_mask (position only)
        int(lat * 1e7),  # lat_int
        int(lon * 1e7),  # lon_int
        alt,    # alt
        0, 0, 0,  # velocity x,y,z
        0, 0, 0,  # acceleration x,y,z
        0, 0     # yaw, yaw_rate
    )

def send_command_ack(command_id, result):
    """Send command acknowledgment"""
    master.mav.command_ack_send(
        command_id,
        result  # MAV_RESULT_ACCEPTED, MAV_RESULT_FAILED, etc.
    )

def send_custom_state(state_name):
    """Send custom state as a named_value_float message"""
    # Convert state name to a numeric ID for transmission
    state_ids = {
        "AUTO": 1.0,
        "LOITER": 2.0,
        "RTL": 3.0,
        "MANUAL": 4.0,
        "FATAL": 5.0
    }
    
    master.mav.named_value_float_send(
        int(time.time() * 1000),  # time_boot_ms
        b"STATE",  # max 10 chars
        state_ids.get(state_name, 0.0)
    )

# ----------------------------
# Modified Helper Functions
# ----------------------------
def set_mode(mode):
    """Send mode change via MAVLink"""
    mode_id = master.mode_mapping().get(mode)
    if mode_id:
        master.set_mode(mode_id)
        send_statustext(f"Mode changed to {mode}", 6)
    else:
        send_statustext(f"Unknown mode: {mode}", 4)

def interrupt_check():
    """Check for commands from flight controller"""
    msg = master.recv_match(type='COMMAND_LONG', blocking=False)
    if msg:
        # Acknowledge command
        send_command_ack(msg.command, mavutil.mavlink.MAV_RESULT_ACCEPTED)
        
        if msg.command == 30000:  # Custom GoTo command
            return msg.param1
    return None
# Polling functions for sensor data
def gps_status():
    """Check if GPS has 3D fix"""
    msg = master.recv_match(type='GPS_RAW_INT', blocking=False)
    if not msg:
        return False
    return msg.fix_type >= 3   # fix_type 3 = 3D Fix

def get_battery_pct():
    """Get battery percentage (0-100%)"""
    msg = master.recv_match(type="BATTERY_STATUS", blocking=False)
    if msg:
        return msg.battery_remaining
    
    msg = master.recv_match(type="SYS_STATUS", blocking=False)
    if msg:
        return msg.battery_remaining
    
    return 100  # Default

def get_base_current():
    """Get current draw in amps"""
    msg = master.recv_match(type="SYS_STATUS", blocking=False)
    if msg:
        return msg.current_battery / 100.0  # Convert cA to A
    return 8.0  # Placeholder for testing

def accel_is_extreme():
    """Check for collision-level accelerations"""
    msg = master.recv_match(type="HIGHRES_IMU", blocking=False)
    if not msg:
        return False
    ax, ay, az = msg.xacc, msg.yacc, msg.zacc
    # Check for sudden acceleration (m/sÂ²)
    return abs(ax) > 20 or abs(ay) > 20 or abs(az) > 30

def imu_orientation():
    """Get pitch and roll from IMU"""
    msg = master.recv_match(type="ATTITUDE", blocking=False)
    if not msg:
        return (0.0, 0.0)
    return (msg.pitch, msg.roll)

def sonar_ok():
    """Check sonar sensor"""
    # Replace with actual sonar check
    return True

def current_sensor_ok():
    """Check current sensor"""
    # Replace with actual current sensor check
    return True

# Add a placeholder for speed since it's used in LOITER state
speed = 0.0  # Current speed placeholder
# ----------------------------
# MAIN CONTROL LOOP with MAVLink
# ----------------------------
STATE_AUTO = "AUTO"
STATE_LOITER = "LOITER"
STATE_RTL = "RTL"
STATE_MANUAL = "MANUAL"
STATE_FATAL = "FATAL_ERROR"
current_state = STATE_LOITER

# Constants (define these based on your hardware)
MAX_CURRENT = 20.0
MIN_SPEED = 0.5

last_status_sent = 0
last_heartbeat = 0

while True:
    try:
        # Send heartbeat every second
        if time.time() - last_heartbeat > 1:
            send_heartbeat()
            last_heartbeat = time.time()
        
        # Send system status every 2 seconds
        if time.time() - last_status_sent > 2:
            send_system_status()
            send_custom_state(current_state)
            last_status_sent = time.time()
        
        # Check for interrupts/commands
        interrupt = interrupt_check()
        if interrupt:
            send_statustext(f"Received command: {interrupt}", 6)
            current_state = interrupt
        
        # ============================
        #         AUTO STATE
        # ============================
        if current_state == STATE_AUTO:
            # Get sensor data
            battery = get_battery_pct()
            gps_ok = gps_status()
            current_high = get_base_current() > MAX_CURRENT
            
            if current_high or not gps_ok:
                send_statustext("Auto â†’ RTL (current high or GPS lost)", 4)
                set_mode("RTL")
                current_state = STATE_RTL
                
            elif battery < 30:
                send_statustext(f"Battery {battery}% â†’ RTL", 4)
                set_mode("RTL")
                current_state = STATE_RTL
                
            elif accel_is_extreme():
                send_statustext("Collision detected â†’ FATAL", 2)
                current_state = STATE_FATAL
                
            else:
                # Normal auto operation - send position updates
                # send_position_target_global_int(lat, lon, alt)
                pass
        
        # ============================
        #         LOITER STATE
        # ============================
        elif current_state == STATE_LOITER:
            if not gps_status():
                send_statustext("GPS signal lost", 5)
                # Hold position using other sensors
            else:
                # GPS available, can transition to AUTO if needed
                pass
        
        # ============================
        #         RTL STATE
        # ============================
        elif current_state == STATE_RTL:
            set_mode("RTL")
            
            if get_battery_pct() < 10:
                send_statustext("Battery critical: 10%", 1)
                current_state = STATE_FATAL
        
        # ============================
        #        FATAL STATE
        # ============================
        elif current_state == STATE_FATAL:
            # Send emergency messages
            send_statustext("FATAL ERROR: System halted", 0)
            set_mode("HOLD")
            
            # Send location every 5 seconds
            # send_position_target_global_int(current_lat, current_lon)
            time.sleep(5)
        
        # Process incoming messages
        while True:
            msg = master.recv_match(blocking=False)
            if not msg:
                break
            # Handle incoming messages here
            if msg.get_type() == "GPS_RAW_INT":
                pass  # Process GPS data
            elif msg.get_type() == "BATTERY_STATUS":
                pass  # Process battery data
        
        time.sleep(0.1)
        
    except KeyboardInterrupt:
        send_statustext("Control loop terminated by user", 6)
        break
    except Exception as e:
        send_statustext(f"Control loop error: {str(e)}", 3)
        time.sleep(1)