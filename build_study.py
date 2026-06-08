#!/usr/bin/env python3
# Run ON HA against /config/esphome/study-printer-dashboard.yaml (a fresh copy of
# the bedroom config). Sets study identity + creds, inserts a mockup-styled LVGL
# printer overview page as the home screen + printer sensors, removes the
# full-screen album-art overlay, and repoints "home" nav to printer_page.
import io, re, os

F = "/config/esphome/study-printer-dashboard.yaml"
with io.open(F, "r", encoding="utf-8") as fh:
    txt = fh.read()

API_KEY = os.environ.get("STUDY_API_KEY", "")
OTA_PW  = os.environ.get("STUDY_OTA_PW", "")

# (idk, label, entity_prefix, power_entity)
printers = [
    ("hd2", "HD2",       "hd2",        "input_boolean.hd2"),
    ("hd1", "H2D",       "hd1",        "input_boolean.hd1"),
    ("x1",  "X1 Carbon", "x1_carbon",  "input_boolean.x1_carbon"),
]

# ---------- identity ----------
assert "name: bedroom-voice-assistant" in txt
txt = txt.replace("name: bedroom-voice-assistant", "name: study-printer-dashboard", 1)
txt = txt.replace('friendly_name: "Bedroom Voice Assistant"',
                  'friendly_name: "Study Printer Dashboard"', 1)
if API_KEY:
    txt = re.sub(r'(\n  encryption:\n    key: )[^\n]+', r'\g<1>"' + API_KEY + '"', txt, count=1)
if OTA_PW:
    txt = re.sub(r'(\nota:\n  - platform: esphome\n    password: )[^\n]+',
                 r'\g<1>"' + OTA_PW + '"', txt, count=1)

# ---------- printer_page (mockup-styled) ----------
def card(idk, label, ent):
    return f"""              - obj:
                  scrollable: false
                  width: 684
                  height: 150
                  bg_color: 0x073642
                  bg_opa: COVER
                  radius: 18
                  border_width: 1
                  border_color: 0x2a4048
                  pad_all: 0
                  widgets:
                    - obj:
                        id: p_{idk}_accent
                        align: LEFT_MID
                        x: 0
                        width: 7
                        height: 150
                        radius: 0
                        bg_color: 0x586e75
                        border_width: 0
                        scrollable: false
                    - label:
                        id: p_{idk}_name
                        align: TOP_LEFT
                        x: 22
                        y: 12
                        text: "{label}"
                        text_color: 0xeee8d5
                        text_font: figtree_32
                    - label:
                        id: p_{idk}_status
                        align: TOP_LEFT
                        x: 170
                        y: 20
                        text: "--"
                        text_color: 0x586e75
                        text_font: figtree_20
                        bg_color: 0x002b36
                        bg_opa: COVER
                        radius: 10
                        pad_top: 3
                        pad_bottom: 3
                        pad_left: 10
                        pad_right: 10
                    - label:
                        id: p_{idk}_sub
                        align: TOP_LEFT
                        x: 22
                        y: 48
                        text: ""
                        text_color: 0x839496
                        text_font: figtree_20
                    - bar:
                        id: p_{idk}_bar
                        align: TOP_LEFT
                        x: 22
                        y: 82
                        width: 360
                        height: 14
                        min_value: 0
                        max_value: 100
                        value: 0
                        bg_color: 0x002b36
                        bg_opa: COVER
                        indicator:
                          bg_color: 0x2aa198
                          bg_opa: COVER
                    - label:
                        id: p_{idk}_pct
                        align: TOP_LEFT
                        x: 398
                        y: 76
                        text: "--"
                        text_color: 0xfdf6e3
                        text_font: figtree_32
                    - switch:
                        id: p_{idk}_sw
                        align: RIGHT_MID
                        x: -28
                        y: -10
                        on_change:
                          - if:
                              condition:
                                lambda: 'return x != id(ps_{idk}_pwr).state;'
                              then:
                                - homeassistant.service:
                                    service: input_boolean.toggle
                                    data:
                                      entity_id: {ent}
                    - label:
                        align: RIGHT_MID
                        x: -38
                        y: 26
                        text: "Power"
                        text_color: 0x586e75
                        text_font: figtree_20
                    - obj:
                        align: BOTTOM_LEFT
                        x: 18
                        y: -10
                        width: 560
                        height: 38
                        bg_opa: TRANSP
                        border_width: 0
                        pad_all: 0
                        scrollable: false
                        layout:
                          type: FLEX
                          flex_flow: ROW
                          flex_align_main: START
                          flex_align_cross: CENTER
                          pad_column: 8
                        widgets:
                          - label:
                              id: p_{idk}_chip_rem
                              text: "--"
                              text_color: 0x93a1a1
                              text_font: figtree_20
                              bg_color: 0x002b36
                              bg_opa: COVER
                              radius: 11
                              pad_top: 5
                              pad_bottom: 5
                              pad_left: 11
                              pad_right: 11
                          - label:
                              id: p_{idk}_chip_temp
                              text: "--"
                              text_color: 0x93a1a1
                              text_font: figtree_20
                              bg_color: 0x002b36
                              bg_opa: COVER
                              radius: 11
                              pad_top: 5
                              pad_bottom: 5
                              pad_left: 11
                              pad_right: 11
                          - label:
                              id: p_{idk}_chip_fil
                              text: "--"
                              text_color: 0x93a1a1
                              text_font: figtree_20
                              bg_color: 0x002b36
                              bg_opa: COVER
                              radius: 11
                              pad_top: 5
                              pad_bottom: 5
                              pad_left: 11
                              pad_right: 11
"""

cards = "".join(card(idk, label, pwr) for (idk, label, pf, pwr) in printers)
printer_page = f"""    - id: printer_page
      widgets:
        - obj:
            scrollable: false
            width: 720
            height: 720
            bg_color: 0x002b36
            bg_opa: COVER
            pad_top: 16
            pad_bottom: 10
            pad_left: 18
            pad_right: 18
            border_width: 0
            radius: 0
            layout:
              type: FLEX
              flex_flow: COLUMN
              flex_align_main: START
              flex_align_cross: CENTER
              pad_row: 12
            widgets:
              - obj:
                  width: 684
                  height: 46
                  bg_opa: TRANSP
                  border_width: 0
                  pad_all: 0
                  scrollable: false
                  layout:
                    type: FLEX
                    flex_flow: ROW
                    flex_align_main: SPACE_BETWEEN
                    flex_align_cross: CENTER
                  widgets:
                    - label:
                        recolor: true
                        text: "Study  #cb4b16 Printers#"
                        text_color: 0xfdf6e3
                        text_font: figtree_32
                    - obj:
                        width: 230
                        height: 44
                        bg_opa: TRANSP
                        border_width: 0
                        pad_all: 0
                        scrollable: false
                        layout:
                          type: FLEX
                          flex_flow: ROW
                          flex_align_main: END
                          flex_align_cross: CENTER
                          pad_column: 12
                        widgets:
                          - label:
                              text: "Hey BMO"
                              text_color: 0x859900
                              text_font: figtree_20
                              bg_color: 0x18280a
                              bg_opa: COVER
                              radius: 14
                              pad_top: 5
                              pad_bottom: 5
                              pad_left: 12
                              pad_right: 12
                          - label:
                              id: p_clock
                              text: "--:--"
                              text_color: 0x93a1a1
                              text_font: figtree_32
{cards}"""

# ---------- numeric sensors ----------
sensors = ""
for (idk, label, pf, pwr) in printers:
    sensors += f"""  - platform: homeassistant
    id: ps_{idk}_noz
    entity_id: sensor.{pf}_nozzle_temperature
  - platform: homeassistant
    id: ps_{idk}_prog
    entity_id: sensor.{pf}_print_progress
    on_value:
      then:
        - lvgl.bar.update:
            id: p_{idk}_bar
            value: !lambda 'return isnan(x) ? 0 : (int)x;'
        - lvgl.label.update:
            id: p_{idk}_pct
            text: !lambda |-
              if (isnan(x)) return std::string("--");
              char b[8]; snprintf(b, sizeof(b), "%d%%", (int)x); return std::string(b);
  - platform: homeassistant
    id: ps_{idk}_bed
    entity_id: sensor.{pf}_bed_temperature
    on_value:
      then:
        - lvgl.label.update:
            id: p_{idk}_chip_temp
            text: !lambda |-
              if (isnan(x) || isnan(id(ps_{idk}_noz).state)) return std::string("-- temps");
              char b[40]; snprintf(b, sizeof(b), "Bed %d°  Noz %d°", (int)x, (int)id(ps_{idk}_noz).state); return std::string(b);
"""

# ---------- text sensors (stage -> status text + colour + accent; tray, remaining -> chips) ----------
tsensors = ""
for (idk, label, pf, pwr) in printers:
    tsensors += f"""  - platform: homeassistant
    id: pt_{idk}_stage
    entity_id: sensor.{pf}_current_stage
    on_value:
      then:
        - lvgl.label.update:
            id: p_{idk}_status
            text: !lambda |-
              std::string s = x; for (auto &c : s) c = toupper(c); return s;
        - if:
            condition:
              lambda: 'return x == std::string("printing");'
            then:
              - lvgl.label.update: {{ id: p_{idk}_status, text_color: 0x859900 }}
              - lvgl.widget.update: {{ id: p_{idk}_accent, bg_color: 0x859900 }}
            else:
              - if:
                  condition:
                    lambda: 'return x == std::string("idle");'
                  then:
                    - lvgl.label.update: {{ id: p_{idk}_status, text_color: 0xb58900 }}
                    - lvgl.widget.update: {{ id: p_{idk}_accent, bg_color: 0xb58900 }}
                  else:
                    - lvgl.label.update: {{ id: p_{idk}_status, text_color: 0x586e75 }}
                    - lvgl.widget.update: {{ id: p_{idk}_accent, bg_color: 0x586e75 }}
  - platform: homeassistant
    id: pt_{idk}_fil
    entity_id: sensor.{pf}_active_tray
    on_value:
      then:
        - lvgl.label.update:
            id: p_{idk}_chip_fil
            text: !lambda 'return x.empty() ? std::string("--") : x;'
  - platform: homeassistant
    id: pt_{idk}_rem
    entity_id: sensor.{pf}_remaining
    on_value:
      then:
        - lvgl.label.update:
            id: p_{idk}_chip_rem
            text: !lambda 'return x.empty() ? std::string("--") : (x + std::string(" left"));'
"""

# ---------- power binary sensors (input_boolean state -> switch) ----------
bsensors = ""
for (idk, label, pf, pwr) in printers:
    bsensors += f"""  - platform: homeassistant
    id: ps_{idk}_pwr
    entity_id: {pwr}
    on_value:
      then:
        - lvgl.widget.update:
            id: p_{idk}_sw
            state:
              checked: !lambda 'return x;'
"""

# ---------- clock interval ----------
clock_iv = """  - interval: 10s
    then:
      - if:
          condition:
            lambda: 'return id(ha_time).now().is_valid();'
          then:
            - lvgl.label.update:
                id: p_clock
                text: !lambda |-
                  char b[8]; auto t = id(ha_time).now(); snprintf(b, sizeof(b), "%d:%02d", t.hour, t.minute); return std::string(b);
"""

# ---------- apply ----------
assert "  pages:\n" in txt
txt = txt.replace("  pages:\n", "  pages:\n" + printer_page, 1)
assert "\nsensor:\n" in txt
txt = txt.replace("\nsensor:\n", "\nsensor:\n" + sensors, 1)
assert "\ntext_sensor:\n" in txt
txt = txt.replace("\ntext_sensor:\n", "\ntext_sensor:\n" + tsensors, 1)
assert "\nbinary_sensor:\n" in txt
txt = txt.replace("\nbinary_sensor:\n", "\nbinary_sensor:\n" + bsensors, 1)
# add clock updater into the existing interval: section
assert "\ninterval:\n" in txt
txt = txt.replace("\ninterval:\n", "\ninterval:\n" + clock_iv, 1)

# home nav -> printer_page
txt = txt.replace("- lvgl.page.show: clock_page", "- lvgl.page.show: printer_page")
txt = txt.replace("          id: clock_page", "          id: printer_page")

# remove full-screen album-art overlay on play
before = txt
txt = txt.replace(
    '              - script.stop: debounce_not_playing\n'
    '              - lvgl.page.show: spotify_page\n'
    '              - lambda: "id(is_spotify_active) = true;"\n',
    '              - script.stop: debounce_not_playing\n', 1)
assert txt != before, "album-art overlay trigger not found"
txt = txt.replace("entity_id: sensor.spotify_album_art\n",
                  "entity_id: sensor.spd_no_album_art\n", 1)

with io.open(F, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(txt)

print("OK lines:", txt.count("\n") + 1,
      "| printer_page:", "id: printer_page" in txt,
      "| switches:", txt.count("id: p_hd2_sw") )
