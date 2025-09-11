import random
import dearpygui.dearpygui as dpg

# Create context
dpg.create_context()

# Create viewport
dpg.create_viewport(title="Панель приборов AVO", width=500, height=400)

# Theme for toolbar buttons
with dpg.theme(tag="toolbar_theme"):
    with dpg.theme_component(dpg.mvButton):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (52, 152, 219))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (41, 128, 185))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (31, 97, 141))
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 5)


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
        "out_pressure_val", f"{inlet_pressure + random.uniform(-5, 5):.1f} Па"
    )
    dpg.set_value(
        "air_flow_val", f"{product_flow + random.uniform(-10, 10):.1f} м\u00b3/ч"
    )
    dpg.set_value(
        "fan_speed_val", f"{fan_speed + random.uniform(-20, 20):.1f} об/мин"
    )


# Main window
with dpg.window(label="Главное окно", width=500, height=400):
    # Toolbar group at top
    with dpg.group(horizontal=True):
        btn_refresh = dpg.add_button(label="Обновить датчики", callback=update_sensors)
        btn_settings = dpg.add_button(
            label="Настройки", callback=lambda: print("Открыты настройки")
        )
        btn_exit = dpg.add_button(
            label="Выход", callback=lambda: dpg.stop_dearpygui()
        )

        for btn in (btn_refresh, btn_settings, btn_exit):
            dpg.bind_item_theme(btn, "toolbar_theme")

    dpg.add_separator()
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


# Setup and launch
dpg.setup_dearpygui()
dpg.show_viewport()
update_sensors()

# Start event loop
dpg.start_dearpygui()

# Destroy context
dpg.destroy_context()
