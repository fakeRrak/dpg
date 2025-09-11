import random
import math
import os
import platform
import dearpygui.dearpygui as dpg

# Create context
dpg.create_context()

# Load font with Cyrillic support without bundling binary files
font_path = (
    "C:\\Windows\\Fonts\\arial.ttf"
    if platform.system() == "Windows"
    else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
)

with dpg.font_registry():
    if os.path.exists(font_path):
        default_font = dpg.add_font(font_path, 16)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic, parent=default_font)
        dpg.bind_font(default_font)

# Create viewport
dpg.create_viewport(title="Панель приборов AVO", width=500, height=400)



def update_thermometer(temp: float) -> None:
    """Update thermometer level based on temperature."""
    temp = max(0.0, min(temp, 100.0))
    height = 120  # drawable height of tube
    top = 150 - (temp / 100.0) * height
    dpg.configure_item("thermo_level", pmin=(25, top), pmax=(35, 150))


def update_pressure_gauge(pressure: float) -> None:
    """Rotate pressure gauge arrow."""
    pressure = max(0.0, min(pressure, 2000.0))
    angle = math.pi - (pressure / 2000.0) * math.pi
    x = 100 + 70 * math.cos(angle)
    y = 100 - 70 * math.sin(angle)
    dpg.configure_item("pressure_arrow", p1=(100, 100), p2=(x, y))


def update_sensors():
    """Simulate updating sensor values based on user inputs."""
    desired_temp = dpg.get_value("desired_temp")
    inlet_pressure = dpg.get_value("inlet_pressure")
    inlet_temp = dpg.get_value("inlet_temp")
    product_flow = dpg.get_value("product_flow")
    fan_speed = dpg.get_value("fan_speed")

    out_temp = desired_temp + random.uniform(-1, 1)
    out_pressure = inlet_pressure + random.uniform(-5, 5)

    dpg.set_value("out_temp_val", f"{out_temp:.1f} \u00b0C")
    dpg.set_value("out_pressure_val", f"{out_pressure:.1f} Па")
    dpg.set_value(
        "air_flow_val", f"{product_flow + random.uniform(-10, 10):.1f} м\u00b3/ч"
    )
    dpg.set_value(
        "fan_speed_val", f"{fan_speed + random.uniform(-20, 20):.1f} об/мин"
    )

    update_thermometer(out_temp)
    update_pressure_gauge(out_pressure)


def auto_update_sensors() -> None:
    """Automatically refresh sensor readings every second."""
    update_sensors()
    dpg.set_frame_callback(dpg.get_frame_count() + 60, auto_update_sensors)


available_components = ["H2O", "CO2", "O2", "N2"]
component_inputs: dict[str, str] = {}


def update_mix_sum(sender=None, app_data=None, user_data=None) -> None:
    total = sum(dpg.get_value(tag) for tag in component_inputs.values())
    missing = max(0.0, 1.0 - total)
    dpg.set_value(
        "mix_sum_text", f"Сумма долей: {total:.2f}, не хватает: {missing:.2f}"
    )


def add_selected_components() -> None:
    for comp in available_components:
        if dpg.get_value(f"select_{comp}") and comp not in component_inputs:
            tag = f"share_{comp}"
            dpg.add_input_float(
                label=comp,
                default_value=0.0,
                min_value=0.0,
                max_value=1.0,
                width=100,
                parent="mix_group",
                tag=tag,
                callback=update_mix_sum,
            )
            component_inputs[comp] = tag
            dpg.set_value(f"select_{comp}", False)
    dpg.configure_item("component_selector", show=False)
    update_mix_sum()


with dpg.window(label="Выбор компонентов", modal=True, show=False, tag="component_selector"):
    for comp in available_components:
        dpg.add_checkbox(label=comp, tag=f"select_{comp}")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Добавить", callback=add_selected_components)
        dpg.add_button(
            label="Отмена",
            callback=lambda: dpg.configure_item("component_selector", show=False),
        )


# Main window
with dpg.window(label="Главное окно", width=500, height=400):
    dpg.add_text("Входные параметры")
    dpg.add_input_float(
        label="Желаемая температура на выходе (\u00b0C)",
        default_value=20.0,
        tag="desired_temp",
    )
    dpg.add_input_float(
        label="Давление на входе (Па)", default_value=1000.0, tag="inlet_pressure"
    )
    dpg.add_input_float(
        label="Температура на входе (\u00b0C)", default_value=25.0, tag="inlet_temp"
    )
    dpg.add_input_float(
        label="Расход продукта (м\u00b3/ч)", default_value=100.0, tag="product_flow"
    )
    dpg.add_input_float(
        label="Начальная скорость вентилятора (об/мин)",
        default_value=1000.0,
        tag="fan_speed",
    )

    dpg.add_separator()
    dpg.add_text("Состав смеси")
    dpg.add_button(
        label="Выбрать компоненты",
        callback=lambda: dpg.configure_item("component_selector", show=True),
    )
    with dpg.group(tag="mix_group"):
        pass
    dpg.add_text("Сумма долей: 0.00, не хватает: 1.00", tag="mix_sum_text")

    dpg.add_separator()
    dpg.add_text("Показания датчиков")

    with dpg.table(header_row=True, resizable=True):
        dpg.add_table_column(label="Датчик")
        dpg.add_table_column(label="Значение")

        with dpg.table_row():
            dpg.add_text("Температура на выходе")
            dpg.add_text("0.0 \u00b0C", tag="out_temp_val")
        with dpg.table_row():
            dpg.add_text("Давление на выходе")
            dpg.add_text("0.0 Па", tag="out_pressure_val")
        with dpg.table_row():
            dpg.add_text("Расход воздуха")
            dpg.add_text("0.0 м\u00b3/ч", tag="air_flow_val")
        with dpg.table_row():
            dpg.add_text("Скорость вентилятора")
            dpg.add_text("0.0 об/мин", tag="fan_speed_val")

    with dpg.group(horizontal=True):
        with dpg.drawlist(width=60, height=180, tag="thermo_draw"):
            dpg.draw_rectangle((25, 20), (35, 150), color=(255, 255, 255))
            dpg.draw_circle((30, 150), 20, color=(255, 255, 255))
            dpg.draw_rectangle((25, 150), (35, 150), color=(255, 0, 0), fill=(255, 0, 0), tag="thermo_level")
            dpg.draw_circle((30, 150), 20, color=(255, 0, 0), fill=(255, 0, 0), tag="thermo_bulb")
        with dpg.drawlist(width=200, height=120, tag="pressure_draw"):
            arc_points = [
                (100 + 80 * math.cos(theta), 100 - 80 * math.sin(theta))
                for theta in [i * math.pi / 20 for i in range(21)]
            ]
            dpg.draw_polyline(arc_points, color=(255, 255, 255), thickness=2)
            dpg.draw_line((100, 100), (100, 20), color=(255, 0, 0), thickness=3, tag="pressure_arrow")

# Setup and launch
dpg.setup_dearpygui()
dpg.show_viewport()
auto_update_sensors()

# Start event loop
dpg.start_dearpygui()

# Destroy context
dpg.destroy_context()
