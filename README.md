# WPilot - Ground Control Station Software

WPilot is a ground control station (GCS) software developed by Nicole Duong, Will Gerlach, and Benjamin Howes for use in the Major Qualifying Project entitled, "Autonomous Surface Vehicle for Shallow Water Bathymetry." Developed with ease of use in mind, this GCS allows the user to easily plan missions, change modes, observe messages from the vehicle's companion computer, and track vital telemetry data. WPilot utilizes pymavlink to communicate via MAVLink to an autopilot running ArduPilot Rover firmware, leverages folium to display map data, and generates a UI using PyQt6. 

## Demo

![WPilot Demo](docs/WPilot_Demo.gif)
WPilot being used to create, send, and monitor a point to point mission. [Software in the Loop](https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html) simulation used to generate data.

## Key Features
- Real-time telemetry data display
- Point and click waypoint planning
- RC override
- Vehicle mode switching
- Companion computer message monitoring
- Interactive map

## System Architecture
**UI Diagram**
```mermaid
    flowchart LR

    subgraph Statusbar and Toolbar
        StatusbarPanel
        ToolbarPanel
    end

    subgraph Main Panels
        TelemetryPanel
        MapPanel
        ControlPanel
    end

    subgraph Telemetry Subpanels
        GPSSubpanel
        BatterySubpanel
        SupervisorSubpanel
        ServoOutputSubpanel
    end

    subgraph Map Subpanels
        MapSubpanel
        WaypointDisplaySubpanel
    end

    subgraph Control Subpanels
        RCOverrideSubpanel
        MissionPlanningSubpanel
    end

    MainWindow --> StatusbarPanel
    MainWindow --> ToolbarPanel
    MainWindow --> TelemetryPanel
    MainWindow --> MapPanel
    MainWindow --> ControlPanel

    TelemetryPanel --> GPSSubpanel
    TelemetryPanel --> BatterySubpanel
    TelemetryPanel --> SupervisorSubpanel
    TelemetryPanel --> ServoOutputSubpanel

    MapPanel --> MapSubpanel
    MapPanel --> WaypointDisplaySubpanel

    ControlPanel --> RCOverrideSubpanel
    ControlPanel --> MissionPlanningSubpanel

```
**Core Logic Diagram**
```mermaid
    flowchart LR

    subgraph Core Logic
        ConnectionData
        TelemetryData
        MissionData
    end

    ConnectionData --> TelemetryData

    ConnectionData --> MissionData

    subgraph Main Panels
        TelemetryPanel
        MapPanel
        ControlPanel
    end

    ConnectionData --> ControlPanel
    MissionData --> ControlPanel
    TelemetryData --> ControlPanel

    ConnectionData --> TelemetryPanel
    TelemetryData --> TelemetryPanel

    MissionData --> MapPanel
    TelemetryData --> MapPanel
```

## Installation and Running
1. Clone the repository into a directory of your choosing:
```bash
git clone https://github.com/wsgerlach/WPIlot-ASV.git
```
2. Create a virtual environment inside the cloned repository:
```bash
python3 -m venv .venv
```
3. Activate the virtual environment:
```bash
source .venv/bin/activate
```
4. Install the necessary dependencies using requirements.txt:
```bash
pip install -r requirements.txt
```
5. Start the program using main.py:
```bash
python3 main.py
```
