import random
import dearpygui.dearpygui as dpg

# Create context
dpg.create_context()

# Create viewport
dpg.create_viewport(title="AVO Instrument Panel", width=500, height=400)


def update_sensors():
    """Simulate updating sensor values based on user inputs."""
    desired_temp = dpg.get_value("desired_temp")
    inlet_pressure = dpg.get_value("inlet_pressure")
    inlet_temp = dpg.get_value("inlet_temp")
    product_flow = dpg.get_value("product_flow")
    fan_speed = dpg.get_value("fan_speed")

    dpg.set_value(
        "out_temp_val", f"{desired_temp + random.uniform(-1, 1):.1f} \u00b0C"
    )
    dpg.set_value(
        "out_pressure_val", f"{inlet_pressure + random.uniform(-5, 5):.1f} Pa"
    )
    dpg.set_value(
        "air_flow_val", f"{product_flow + random.uniform(-10, 10):.1f} m\u00b3/h"
    )
    dpg.set_value(
        "fan_speed_val", f"{fan_speed + random.uniform(-20, 20):.1f} rpm"
    )


# Main window
with dpg.window(label="Main Window", width=500, height=400):
    # Toolbar group at top
    with dpg.group(horizontal=True):
        dpg.add_button(label="Open", callback=lambda: print("Open clicked"))
        dpg.add_button(label="Save", callback=lambda: print("Save clicked"))
        dpg.add_button(label="Cut", callback=lambda: print("Cut clicked"))
        dpg.add_button(label="Copy", callback=lambda: print("Copy clicked"))
        dpg.add_button(label="Paste", callback=lambda: print("Paste clicked"))

    dpg.add_separator()
    dpg.add_text("Input Parameters")
    dpg.add_input_float(
        label="Desired Output Temperature (\u00b0C)", default_value=20.0, tag="desired_temp"
    )
    dpg.add_input_float(
        label="Inlet Pressure (Pa)", default_value=1000.0, tag="inlet_pressure"
    )
    dpg.add_input_float(
        label="Inlet Temperature (\u00b0C)", default_value=25.0, tag="inlet_temp"
    )
    dpg.add_input_float(
        label="Product Flow (m\u00b3/h)", default_value=100.0, tag="product_flow"
    )
    dpg.add_input_float(
        label="Initial Fan Speed (rpm)", default_value=1000.0, tag="fan_speed"
    )

    dpg.add_separator()
    dpg.add_text("Sensor Readings")

    with dpg.table(header_row=True, resizable=True):
        dpg.add_table_column(label="Sensor")
        dpg.add_table_column(label="Value")

        with dpg.table_row():
            dpg.add_text("Output Temperature")
            dpg.add_text("0.0 \u00b0C", tag="out_temp_val")
        with dpg.table_row():
            dpg.add_text("Output Pressure")
            dpg.add_text("0.0 Pa", tag="out_pressure_val")
        with dpg.table_row():
            dpg.add_text("Air Flow")
            dpg.add_text("0.0 m\u00b3/h", tag="air_flow_val")
        with dpg.table_row():
            dpg.add_text("Fan Speed")
            dpg.add_text("0.0 rpm", tag="fan_speed_val")

    dpg.add_button(label="Refresh Sensors", callback=update_sensors)


# Setup and launch
dpg.setup_dearpygui()
dpg.show_viewport()
update_sensors()

# Start event loop
dpg.start_dearpygui()

# Destroy context
dpg.destroy_context()
