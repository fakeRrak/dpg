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



thermo_tick_tags: list[str] = []
pressure_tick_tags: list[str] = []


current_scale = 1.0

# Digital twin state variables
dt_out_temp = 20.0
dt_out_pressure = 1000.0
dt_air_flow = 100.0
dt_fan_speed = 1000.0

def scale_instruments(sender=None, app_data=None, user_data=None) -> None:
    """Scale instrument drawings based on slider value."""
    global current_scale
    new_scale = dpg.get_value("instrument_scale")
    ratio = new_scale / current_scale if current_scale else 1.0
    for node_tag, draw_tag, w, h in [
        ("thermo_node", "thermo_draw", 60, 200),
        ("pressure_node", "pressure_draw", 200, 150),
    ]:
        dpg.apply_transform(node_tag, dpg.create_scale_matrix([ratio, ratio, 1]))
        dpg.configure_item(draw_tag, width=int(w * new_scale), height=int(h * new_scale))
    current_scale = new_scale


def draw_thermometer_scale() -> None:
    """Draw tick marks and labels for the thermometer."""
    for tag in thermo_tick_tags:
        dpg.delete_item(tag)
    thermo_tick_tags.clear()

    max_temp = dpg.get_value("temp_max")
    step = max(1e-5, dpg.get_value("temp_step"))
    height = 120
    base_y = 150

    count = int(max_temp // step) + 1
    last_y = base_y + 20  # ensure first label is drawn
    for i in range(count):
        value = i * step
        y = base_y - (value / max_temp) * height
        tick_tag = f"thermo_tick_{i}"
        dpg.draw_line((35, y), (45, y), color=(255, 255, 255), parent="thermo_node", tag=tick_tag)
        thermo_tick_tags.append(tick_tag)
        # draw text only if it does not overlap previous label
        if last_y - y >= 15 or i == count - 1:
            text_tag = f"thermo_text_{i}"
            dpg.draw_text((48, y - 7), f"{int(value)}", color=(255, 255, 255), size=10, parent="thermo_node", tag=text_tag)
            thermo_tick_tags.append(text_tag)
            last_y = y


def draw_pressure_scale() -> None:
    """Draw tick marks and labels for the pressure gauge."""
    for tag in pressure_tick_tags:
        dpg.delete_item(tag)
    pressure_tick_tags.clear()

    max_pressure = dpg.get_value("pressure_max")
    step = max(1e-5, dpg.get_value("pressure_step"))
    count = int(max_pressure // step) + 1

    last_angle = None
    min_angle_step = 0.2  # radians ~11 degrees
    for i in range(count):
        value = i * step
        angle = math.pi - (value / max_pressure) * math.pi
        x1 = 100 + 70 * math.cos(angle)
        y1 = 100 - 70 * math.sin(angle)
        x2 = 100 + 80 * math.cos(angle)
        y2 = 100 - 80 * math.sin(angle)
        tx = 100 + 90 * math.cos(angle) - 10
        ty = 100 - 90 * math.sin(angle) - 5
        tick_tag = f"pressure_tick_{i}"
        dpg.draw_line((x1, y1), (x2, y2), color=(255, 255, 255), parent="pressure_node", tag=tick_tag)
        pressure_tick_tags.append(tick_tag)
        if (
            last_angle is None
            or abs(last_angle - angle) >= min_angle_step
            or i == 0
            or i == count - 1
        ):
            text_tag = f"pressure_text_{i}"
            dpg.draw_text((tx, ty), f"{int(value)}", color=(255, 255, 255), size=10, parent="pressure_node", tag=text_tag)
            pressure_tick_tags.append(text_tag)
            last_angle = angle


def update_thermo_scale(sender=None, app_data=None, user_data=None) -> None:
    draw_thermometer_scale()
    update_sensors()


def update_pressure_scale(sender=None, app_data=None, user_data=None) -> None:
    draw_pressure_scale()
    update_sensors()


def update_thermometer(temp: float) -> None:
    """Update thermometer level based on temperature."""
    max_temp = dpg.get_value("temp_max")
    temp = max(0.0, min(temp, max_temp))
    height = 120  # drawable height of tube
    top = 150 - (temp / max_temp) * height
    dpg.configure_item("thermo_level", pmin=(25, top), pmax=(35, 150))


def update_pressure_gauge(pressure: float) -> None:
    """Rotate pressure gauge arrow."""
    max_pressure = dpg.get_value("pressure_max")
    pressure = max(0.0, min(pressure, max_pressure))
    angle = math.pi - (pressure / max_pressure) * math.pi
    x = 100 + 70 * math.cos(angle)
    y = 100 - 70 * math.sin(angle)
    dpg.configure_item("pressure_arrow", p1=(100, 100), p2=(x, y))


def adjust_scales(out_temp: float, out_pressure: float) -> None:
    """Auto adjust instrument scales based on current readings."""
    for value, max_tag, step_tag, draw_func in [
        (out_temp, "temp_max", "temp_step", draw_thermometer_scale),
        (out_pressure, "pressure_max", "pressure_step", draw_pressure_scale),
    ]:
        max_val = dpg.get_value(max_tag)
        step = max(1e-5, dpg.get_value(step_tag))
        if value > 0.9 * max_val:
            new_max = math.ceil((value * 1.1) / step) * step
            dpg.set_value(max_tag, new_max)
            draw_func()


def update_sensors():
    """Simulate updating sensor values based on user inputs."""
    global dt_out_temp, dt_out_pressure, dt_air_flow, dt_fan_speed
    desired_temp = dpg.get_value("desired_temp")
    inlet_pressure = dpg.get_value("inlet_pressure")
    inlet_temp = dpg.get_value("inlet_temp")
    product_flow = dpg.get_value("product_flow")
    fan_speed = dpg.get_value("fan_speed")

    # digital twin dynamic predictions
    dt_out_temp += 0.1 * (((desired_temp + inlet_temp) / 2) - dt_out_temp)
    dt_out_pressure += 0.1 * (inlet_pressure - dt_out_pressure) - 0.01 * product_flow
    dt_fan_speed += 0.1 * (fan_speed - dt_fan_speed)
    dt_air_flow += 0.1 * (product_flow - dt_air_flow) + 0.01 * (dt_fan_speed - dt_air_flow)

    # simulated sensor readings around digital twin predictions
    out_temp = dt_out_temp + random.uniform(-1, 1)
    out_pressure = dt_out_pressure + random.uniform(-5, 5)
    air_flow = dt_air_flow + random.uniform(-10, 10)
    fan_speed_out = dt_fan_speed + random.uniform(-20, 20)

    adjust_scales(out_temp, out_pressure)

    dpg.set_value("out_temp_val", f"{out_temp:.1f} \u00b0C")
    dpg.set_value("out_temp_dt", f"{dt_out_temp:.1f} \u00b0C")
    dpg.set_value("out_temp_diff", f"{out_temp - dt_out_temp:+.1f} \u00b0C")

    dpg.set_value("out_pressure_val", f"{out_pressure:.1f} Па")
    dpg.set_value("out_pressure_dt", f"{dt_out_pressure:.1f} Па")
    dpg.set_value(
        "out_pressure_diff", f"{out_pressure - dt_out_pressure:+.1f} Па"
    )

    dpg.set_value("air_flow_val", f"{air_flow:.1f} м\u00b3/ч")
    dpg.set_value("air_flow_dt", f"{dt_air_flow:.1f} м\u00b3/ч")
    dpg.set_value("air_flow_diff", f"{air_flow - dt_air_flow:+.1f} м\u00b3/ч")

    dpg.set_value("fan_speed_val", f"{fan_speed_out:.1f} об/мин")
    dpg.set_value("fan_speed_dt", f"{dt_fan_speed:.1f} об/мин")
    dpg.set_value(
        "fan_speed_diff", f"{fan_speed_out - dt_fan_speed:+.1f} об/мин"
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
        dpg.add_table_column(label="Параметр")
        dpg.add_table_column(label="Сенсор")
        dpg.add_table_column(label="Цифровой двойник")
        dpg.add_table_column(label="Отклонение")

        with dpg.table_row():
            dpg.add_text("Температура на выходе")
            dpg.add_text("0.0 \u00b0C", tag="out_temp_val")
            dpg.add_text("0.0 \u00b0C", tag="out_temp_dt")
            dpg.add_text("+0.0 \u00b0C", tag="out_temp_diff")
        with dpg.table_row():
            dpg.add_text("Давление на выходе")
            dpg.add_text("0.0 Па", tag="out_pressure_val")
            dpg.add_text("0.0 Па", tag="out_pressure_dt")
            dpg.add_text("+0.0 Па", tag="out_pressure_diff")
        with dpg.table_row():
            dpg.add_text("Расход воздуха")
            dpg.add_text("0.0 м\u00b3/ч", tag="air_flow_val")
            dpg.add_text("0.0 м\u00b3/ч", tag="air_flow_dt")
            dpg.add_text("+0.0 м\u00b3/ч", tag="air_flow_diff")
        with dpg.table_row():
            dpg.add_text("Скорость вентилятора")
            dpg.add_text("0.0 об/мин", tag="fan_speed_val")
            dpg.add_text("0.0 об/мин", tag="fan_speed_dt")
            dpg.add_text("+0.0 об/мин", tag="fan_speed_diff")

    dpg.add_separator()
    dpg.add_text("Настройка приборов")
    with dpg.group(horizontal=True):
        dpg.add_input_float(
            label="Макс. термометра",
            default_value=100.0,
            width=120,
            tag="temp_max",
            callback=update_thermo_scale,
        )
        dpg.add_input_float(
            label="Деление термометра",
            default_value=10.0,
            width=120,
            tag="temp_step",
            callback=update_thermo_scale,
        )
        dpg.add_input_float(
            label="Макс. манометра",
            default_value=2000.0,
            width=120,
            tag="pressure_max",
            callback=update_pressure_scale,
        )
        dpg.add_input_float(
            label="Деление манометра",
            default_value=200.0,
            width=120,
            tag="pressure_step",
            callback=update_pressure_scale,
        )

    dpg.add_slider_float(
        label="Масштаб приборов",
        default_value=1.0,
        min_value=0.5,
        max_value=2.0,
        tag="instrument_scale",
        callback=scale_instruments,
    )

    dpg.add_separator()
    with dpg.group(horizontal=True):
        with dpg.group():
            with dpg.drawlist(width=60, height=200, tag="thermo_draw"):
                with dpg.draw_node(tag="thermo_node"):
                    dpg.draw_rectangle((25, 20), (35, 150), color=(255, 255, 255))
                    dpg.draw_circle((30, 150), 20, color=(255, 255, 255))
                    dpg.draw_rectangle((25, 150), (35, 150), color=(255, 0, 0), fill=(255, 0, 0), tag="thermo_level")
                    dpg.draw_circle((30, 150), 20, color=(255, 0, 0), fill=(255, 0, 0), tag="thermo_bulb")
                    dpg.draw_text((18, 180), "Термометр")
        with dpg.group():
            with dpg.drawlist(width=200, height=150, tag="pressure_draw"):
                with dpg.draw_node(tag="pressure_node"):
                    arc_points = [
                        (100 + 80 * math.cos(theta), 100 - 80 * math.sin(theta))
                        for theta in [i * math.pi / 20 for i in range(21)]
                    ]
                    dpg.draw_polyline(arc_points, color=(255, 255, 255), thickness=2)
                    dpg.draw_line((100, 100), (100, 20), color=(255, 0, 0), thickness=3, tag="pressure_arrow")
                    dpg.draw_text((72, 130), "Манометр")

# Setup and launch
dpg.setup_dearpygui()
draw_thermometer_scale()
draw_pressure_scale()
dpg.show_viewport()
auto_update_sensors()

# Start event loop
dpg.start_dearpygui()

# Destroy context
dpg.destroy_context()
