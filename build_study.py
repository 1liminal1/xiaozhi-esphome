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
                  height: 168
                  bg_color: 0x073642
                  bg_opa: COVER
                  radius: 18
                  border_width: 1
                  border_color: 0x2a4048
                  pad_all: 0
                  clickable: true
                  on_click:
                    then:
                      - lvgl.page.show:
                          id: detail_{idk}
                          animation: MOVE_LEFT
                          time: 250ms
                  widgets:
                    - obj:
                        id: p_{idk}_accent
                        align: LEFT_MID
                        x: 0
                        width: 7
                        height: 168
                        radius: 0
                        bg_color: 0x586e75
                        border_width: 0
                        scrollable: false
                        clickable: false
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
                        y: 90
                        width: 240
                        height: 12
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
                        x: 280
                        y: 84
                        text: "--"
                        text_color: 0xfdf6e3
                        text_font: figtree_28
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
                        clickable: false
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

# ---------- per-printer detail pages (tap a card -> detail_{idk}) ----------
def tile(x, y, w, eyebrow, vid):
    return f"""              - obj:
                  align: TOP_LEFT
                  x: {x}
                  y: {y}
                  width: {w}
                  height: 96
                  bg_color: 0x073642
                  bg_opa: COVER
                  radius: 16
                  border_width: 0
                  pad_left: 16
                  pad_right: 16
                  pad_top: 12
                  pad_bottom: 12
                  scrollable: false
                  clickable: false
                  widgets:
                    - label:
                        align: TOP_LEFT
                        text: "{eyebrow}"
                        text_color: 0x586e75
                        text_font: figtree_16
                    - label:
                        id: {vid}
                        align: BOTTOM_LEFT
                        text: "--"
                        text_color: 0xfdf6e3
                        text_font: figtree_32
"""

def detail_page(idk, label, pwr):
    tiles = (
        tile(0,   452, 220, "NOZZLE",  f"d_{idk}_noz")
        + tile(232, 452, 220, "BED",     f"d_{idk}_bed")
        + tile(464, 452, 220, "CHAMBER", f"d_{idk}_cham")
        + tile(0,   560, 336, "LAYER",   f"d_{idk}_layer")
        + tile(348, 560, 336, "ENDS",    f"d_{idk}_end")
    )
    return f"""    - id: detail_{idk}
      widgets:
        - obj:
            scrollable: false
            width: 720
            height: 720
            bg_color: 0x002b36
            bg_opa: COVER
            pad_all: 18
            border_width: 0
            radius: 0
            widgets:
              - button:
                  align: TOP_LEFT
                  x: 0
                  y: 0
                  width: 120
                  height: 52
                  radius: 14
                  bg_color: 0x073642
                  border_width: 1
                  border_color: 0x2a4048
                  on_press:
                    then:
                      - lvgl.page.show:
                          id: printer_page
                          animation: MOVE_RIGHT
                          time: 250ms
                  widgets:
                    - label:
                        align: CENTER
                        clickable: false
                        text: "< Back"
                        text_color: 0x93a1a1
                        text_font: figtree_24
              - label:
                  align: TOP_LEFT
                  x: 140
                  y: 2
                  text: "{label}"
                  text_color: 0xeee8d5
                  text_font: figtree_40
              - label:
                  id: d_{idk}_status
                  align: TOP_LEFT
                  x: 142
                  y: 58
                  text: "--"
                  text_color: 0x586e75
                  text_font: figtree_20
                  bg_color: 0x073642
                  bg_opa: COVER
                  radius: 10
                  pad_top: 3
                  pad_bottom: 3
                  pad_left: 10
                  pad_right: 10
              - switch:
                  id: d_{idk}_sw
                  align: TOP_RIGHT
                  x: -8
                  y: 6
                  on_change:
                    - if:
                        condition:
                          lambda: 'return x != id(ps_{idk}_pwr).state;'
                        then:
                          - homeassistant.service:
                              service: input_boolean.toggle
                              data:
                                entity_id: {pwr}
              - label:
                  align: TOP_RIGHT
                  x: -18
                  y: 46
                  text: "Power"
                  text_color: 0x586e75
                  text_font: figtree_20
              - arc:
                  id: d_{idk}_arc
                  align: TOP_MID
                  y: 96
                  width: 300
                  height: 300
                  min_value: 0
                  max_value: 100
                  value: 0
                  adjustable: false
                  arc_width: 18
                  arc_color: 0x073642
                  indicator:
                    arc_color: 0x2aa198
                    arc_width: 18
              - label:
                  id: d_{idk}_pct
                  align: TOP_MID
                  y: 212
                  text: "--"
                  text_color: 0xfdf6e3
                  text_font: figtree_48
              - label:
                  align: TOP_MID
                  y: 268
                  text: "COMPLETE"
                  text_color: 0x586e75
                  text_font: figtree_16
              - label:
                  id: d_{idk}_task
                  align: TOP_MID
                  y: 410
                  width: 660
                  text: ""
                  text_color: 0x839496
                  text_font: figtree_20
                  text_align: CENTER
                  long_mode: DOT
{tiles}"""

detail_pages = "".join(detail_page(idk, label, pwr) for (idk, label, pf, pwr) in printers)

# ---------- sound page ----------
rooms = [
    ("bal",  "Balcony",     "media_player.balcony"),
    ("bed",  "Bedroom",     "media_player.bedroom"),
    ("kit",  "Kitchen",     "media_player.kitchen"),
    ("bath", "Bathroom",    "media_player.bathroom"),
    ("liv",  "Living Room", "media_player.living_room"),
]

def vbtn(sym, svc, ent, x, font="figtree_24"):
    return f"""                    - button:
                        align: RIGHT_MID
                        x: {x}
                        width: 46
                        height: 38
                        radius: 10
                        bg_color: 0x002b36
                        border_width: 1
                        border_color: 0x586e75
                        on_press:
                          then:
                            - homeassistant.service:
                                service: media_player.{svc}
                                data:
                                  entity_id: {ent}
                        widgets:
                          - label:
                              align: CENTER
                              clickable: false
                              text: "{sym}"
                              text_color: 0x93a1a1
                              text_font: {font}
"""

def room_row(r, name, ent):
    return f"""              - obj:
                  width: 684
                  height: 52
                  bg_color: 0x073642
                  bg_opa: COVER
                  radius: 14
                  border_width: 0
                  pad_all: 0
                  scrollable: false
                  widgets:
                    - label:
                        align: LEFT_MID
                        x: 18
                        text: "{name}"
                        text_color: 0xeee8d5
                        text_font: figtree_24
                    - slider:
                        id: snd_{r}_bar
                        align: LEFT_MID
                        x: 190
                        width: 400
                        min_value: 0
                        max_value: 100
                        value: 0
                        on_value:
                          - if:
                              condition:
                                lambda: 'return id(snd_{r}_vol).has_state() && abs((int)x - (int)(id(snd_{r}_vol).state*100.0f)) > 3;'
                              then:
                                - homeassistant.service:
                                    service: media_player.volume_set
                                    data:
                                      entity_id: {ent}
                                    data_template:
                                      volume_level: "{{{{ vol }}}}"
                                    variables:
                                      vol: !lambda 'return x / 100.0;'
                    - label:
                        id: snd_{r}_pct
                        align: RIGHT_MID
                        x: -18
                        text: "--"
                        text_color: 0xfdf6e3
                        text_font: figtree_24
"""

def tbtn(glyph, svc, x, big=False):
    sz = 52 if big else 48
    rad = 26 if big else 24
    bg = "0x2aa198" if big else "0x002b36"
    bw = 0 if big else 1
    tcol = "0x002b36" if big else "0x93a1a1"
    idline = "                        id: snd_pp\n" if big else ""
    lblid = "                              id: snd_pp_lbl\n" if big else ""
    return f"""                    - button:
{idline}                        align: TOP_LEFT
                        x: {x}
                        y: {114 if big else 116}
                        width: {sz}
                        height: {sz}
                        radius: {rad}
                        bg_color: {bg}
                        border_width: {bw}
                        border_color: 0x586e75
                        on_press:
                          then:
                            - homeassistant.service:
                                service: media_player.{svc}
                                data:
                                  entity_id: media_player.home
                        widgets:
                          - label:
{lblid}                              align: CENTER
                              clickable: false
                              text: "{glyph}"
                              text_color: {tcol}
                              text_font: mdi_40
"""

room_rows = "".join(room_row(r, name, ent) for (r, name, ent) in rooms)
tb_prev = tbtn("\\U000F04AE", "media_previous_track", 180)
tb_pp   = tbtn("\\U000F040A", "media_play_pause", 240, big=True)
tb_next = tbtn("\\U000F04AD", "media_next_track", 304)
sound_page = f"""    - id: printers_sound
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
              pad_row: 10
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
                        text: "Study  #2aa198 Sound#"
                        text_color: 0xfdf6e3
                        text_font: figtree_32
                    - label:
                        id: snd_clock
                        text: "--:--"
                        text_color: 0x93a1a1
                        text_font: figtree_32
              - obj:
                  width: 684
                  height: 176
                  bg_color: 0x073642
                  bg_opa: COVER
                  radius: 18
                  border_width: 1
                  border_color: 0x2a4048
                  pad_all: 0
                  scrollable: false
                  widgets:
                    - image:
                        id: snd_art
                        align: LEFT_MID
                        x: 16
                        src: album_art_image
                    - label:
                        align: TOP_LEFT
                        x: 180
                        y: 18
                        text: "PLAYING - HOME GROUP"
                        text_color: 0x2aa198
                        text_font: figtree_20
                    - label:
                        id: snd_title
                        align: TOP_LEFT
                        x: 180
                        y: 42
                        text: "Nothing playing"
                        text_color: 0xfdf6e3
                        text_font: figtree_32
                    - label:
                        id: snd_artist
                        align: TOP_LEFT
                        x: 180
                        y: 84
                        text: ""
                        text_color: 0x839496
                        text_font: figtree_20
{tb_prev}{tb_pp}{tb_next}              - label:
                  text: "PLAYER VOLUMES"
                  text_color: 0x586e75
                  text_font: figtree_20
{room_rows}"""

# ---------- sound sensors ----------
snd_sensors = ""
for (r, name, ent) in rooms:
    snd_sensors += f"""  - platform: homeassistant
    id: snd_{r}_vol
    entity_id: {ent}
    attribute: volume_level
    on_value:
      then:
        - lvgl.slider.update:
            id: snd_{r}_bar
            value: !lambda 'return isnan(x) ? 0 : (int)(x*100);'
        - lvgl.label.update:
            id: snd_{r}_pct
            text: !lambda |-
              if (isnan(x)) return std::string("--");
              char b[8]; snprintf(b, sizeof(b), "%d%%", (int)(x*100)); return std::string(b);
"""

snd_tsensors = """  - platform: homeassistant
    id: snd_title_s
    entity_id: media_player.home
    attribute: media_title
    on_value:
      then:
        - lvgl.label.update:
            id: snd_title
            text: !lambda 'return x.empty() ? std::string("Nothing playing") : x;'
  - platform: homeassistant
    id: snd_artist_s
    entity_id: media_player.home
    attribute: media_artist
    on_value:
      then:
        - lvgl.label.update:
            id: snd_artist
            text: !lambda 'return x;'
  - platform: homeassistant
    id: snd_state_s
    entity_id: media_player.home
    on_value:
      then:
        - lvgl.label.update:
            id: snd_pp_lbl
            text: !lambda 'return x == std::string("playing") ? std::string("\\U000F03E4") : std::string("\\U000F040A");'
"""

# ---------- swipe nav between overview <-> sound ----------
nav_scripts = """  - id: nav_to_sound
    then:
      - lvgl.page.show:
          id: printers_sound
          animation: MOVE_TOP
          time: 250ms
  - id: nav_to_overview
    then:
      - lvgl.page.show:
          id: printer_page
          animation: MOVE_BOTTOM
          time: 250ms
"""

# ---------- numeric sensors ----------
sensors = ""
for (idk, label, pf, pwr) in printers:
    sensors += f"""  - platform: homeassistant
    id: ps_{idk}_noz
    entity_id: sensor.{pf}_nozzle_temperature
    on_value:
      then:
        - lvgl.label.update:
            id: d_{idk}_noz
            text: !lambda |-
              if (isnan(x)) return std::string("--");
              int t = isnan(id(ps_{idk}_noz_t).state) ? 0 : (int)id(ps_{idk}_noz_t).state;
              char b[24]; snprintf(b, sizeof(b), "%d° / %d°", (int)x, t); return std::string(b);
  - platform: homeassistant
    id: ps_{idk}_noz_t
    entity_id: sensor.{pf}_nozzle_target_temperature
    on_value:
      then:
        - lvgl.label.update:
            id: d_{idk}_noz
            text: !lambda |-
              if (isnan(id(ps_{idk}_noz).state)) return std::string("--");
              char b[24]; snprintf(b, sizeof(b), "%d° / %d°", (int)id(ps_{idk}_noz).state, (int)x); return std::string(b);
  - platform: homeassistant
    id: ps_{idk}_prog
    entity_id: sensor.{pf}_print_progress
    on_value:
      then:
        - lvgl.bar.update:
            id: p_{idk}_bar
            value: !lambda 'return isnan(x) ? 0 : (int)x;'
        - lvgl.arc.update:
            id: d_{idk}_arc
            value: !lambda 'return isnan(x) ? 0 : (int)x;'
        - lvgl.label.update:
            id: p_{idk}_pct
            text: !lambda |-
              if (isnan(x)) return std::string("--");
              char b[8]; snprintf(b, sizeof(b), "%d%%", (int)x); return std::string(b);
        - lvgl.label.update:
            id: d_{idk}_pct
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
        - lvgl.label.update:
            id: d_{idk}_bed
            text: !lambda |-
              if (isnan(x)) return std::string("--");
              int t = isnan(id(ps_{idk}_bed_t).state) ? 0 : (int)id(ps_{idk}_bed_t).state;
              char b[24]; snprintf(b, sizeof(b), "%d° / %d°", (int)x, t); return std::string(b);
  - platform: homeassistant
    id: ps_{idk}_bed_t
    entity_id: sensor.{pf}_bed_target_temperature
    on_value:
      then:
        - lvgl.label.update:
            id: d_{idk}_bed
            text: !lambda |-
              if (isnan(id(ps_{idk}_bed).state)) return std::string("--");
              char b[24]; snprintf(b, sizeof(b), "%d° / %d°", (int)id(ps_{idk}_bed).state, (int)x); return std::string(b);
  - platform: homeassistant
    id: ps_{idk}_cham
    entity_id: sensor.{pf}_chamber_temperature
    on_value:
      then:
        - lvgl.label.update:
            id: d_{idk}_cham
            text: !lambda |-
              if (isnan(x)) return std::string("--");
              char b[16]; snprintf(b, sizeof(b), "%d°", (int)x); return std::string(b);
  - platform: homeassistant
    id: ps_{idk}_layer
    entity_id: sensor.{pf}_current_layer
    on_value:
      then:
        - lvgl.label.update:
            id: d_{idk}_layer
            text: !lambda |-
              if (isnan(x)) return std::string("--");
              char b[16]; snprintf(b, sizeof(b), "%d", (int)x); return std::string(b);
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
        - lvgl.label.update:
            id: d_{idk}_status
            text: !lambda |-
              std::string s = x; for (auto &c : s) c = toupper(c); return s;
        - if:
            condition:
              lambda: 'return x == std::string("printing");'
            then:
              - lvgl.label.update: {{ id: p_{idk}_status, text_color: 0x859900 }}
              - lvgl.label.update: {{ id: d_{idk}_status, text_color: 0x859900 }}
              - lvgl.widget.update: {{ id: p_{idk}_accent, bg_color: 0x859900 }}
            else:
              - if:
                  condition:
                    lambda: 'return x == std::string("idle");'
                  then:
                    - lvgl.label.update: {{ id: p_{idk}_status, text_color: 0xb58900 }}
                    - lvgl.label.update: {{ id: d_{idk}_status, text_color: 0xb58900 }}
                    - lvgl.widget.update: {{ id: p_{idk}_accent, bg_color: 0xb58900 }}
                  else:
                    - lvgl.label.update: {{ id: p_{idk}_status, text_color: 0x586e75 }}
                    - lvgl.label.update: {{ id: d_{idk}_status, text_color: 0x586e75 }}
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
            text: !lambda 'return (x.empty() || x == std::string("Not Available")) ? std::string("--") : (x + std::string(" left"));'
  - platform: homeassistant
    id: pt_{idk}_task
    entity_id: sensor.{pf}_task_name
    on_value:
      then:
        - lvgl.label.update:
            id: p_{idk}_sub
            text: !lambda 'return (x.empty() || x == std::string("unknown")) ? std::string("") : x;'
        - lvgl.label.update:
            id: d_{idk}_task
            text: !lambda 'return (x.empty() || x == std::string("unknown")) ? std::string("") : x;'
  - platform: homeassistant
    id: pt_{idk}_end
    entity_id: sensor.{pf}_end
    on_value:
      then:
        - lvgl.label.update:
            id: d_{idk}_end
            text: !lambda |-
              std::string s = x;
              if (s.empty() || s == std::string("unavailable") || s == std::string("Not Available")) return std::string("--");
              auto p = s.find(", ");
              return p == std::string::npos ? s : s.substr(p + 2);
"""

# ---------- power binary sensors (input_boolean state -> switch) ----------
bsensors = ""
for (idk, label, pf, pwr) in printers:
    bsensors += f"""  - platform: homeassistant
    id: ps_{idk}_pwr
    entity_id: {pwr}
    on_state:
      then:
        - lvgl.widget.update:
            id: p_{idk}_sw
            state:
              checked: !lambda 'return x;'
        - lvgl.widget.update:
            id: d_{idk}_sw
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
txt = txt.replace("  pages:\n", "  pages:\n" + printer_page + detail_pages + sound_page, 1)
assert "\nsensor:\n" in txt
txt = txt.replace("\nsensor:\n", "\nsensor:\n" + sensors + snd_sensors, 1)
assert "\ntext_sensor:\n" in txt
txt = txt.replace("\ntext_sensor:\n", "\ntext_sensor:\n" + tsensors + snd_tsensors, 1)
assert "\nbinary_sensor:\n" in txt
txt = txt.replace("\nbinary_sensor:\n", "\nbinary_sensor:\n" + bsensors, 1)
# add clock updater into the existing interval: section
assert "\ninterval:\n" in txt
txt = txt.replace("\ninterval:\n", "\ninterval:\n" + clock_iv, 1)
# nav scripts + swipe between overview and sound
assert "\nscript:\n" in txt
txt = txt.replace("\nscript:\n", "\nscript:\n" + nav_scripts, 1)
GESTURE_OLD = """          if (is_left)  id(pulse_swipe_left).execute();
          if (is_right) id(pulse_swipe_right).execute();
          if (is_up)    id(pulse_swipe_up).execute();
          if (is_down)  id(pulse_swipe_down).execute();
          // Controls → swipe down → back to album art
          if (id(is_controls_active)) {
            if (is_down) id(close_controls).execute();
            return;
          }
          // Album art → swipe up → controls, left/right → tracks
          if (id(is_spotify_active)) {
            if (is_up)    id(open_controls).execute();
            if (is_right) id(media_prev).execute();
            if (is_left)  id(media_next).execute();
            return;
          }
          // Clock page: swipe up opens controls
          if (is_up) id(open_controls).execute();"""
GESTURE_NEW = """          if (is_left)  id(pulse_swipe_left).execute();
          if (is_right) id(pulse_swipe_right).execute();
          if (is_up)    id(pulse_swipe_up).execute();
          if (is_down)  id(pulse_swipe_down).execute();
          // Study dashboard nav: swipe up -> Music, swipe down -> Printers
          if (is_up)   id(nav_to_sound).execute();
          if (is_down) id(nav_to_overview).execute();"""
assert GESTURE_OLD in txt, "gesture tail not found (swipe nav rewrite failed)"
txt = txt.replace(GESTURE_OLD, GESTURE_NEW, 1)

# home nav -> printer_page (also neutralise every path to the bedroom pages so
# clock/spotify/controls can never surface — they stay defined but unreachable)
txt = txt.replace("- lvgl.page.show: clock_page", "- lvgl.page.show: printer_page")
txt = txt.replace("          id: clock_page", "          id: printer_page")
txt = txt.replace("- lvgl.page.show: spotify_page", "- lvgl.page.show: printer_page")
txt = txt.replace("          id: spotify_page", "          id: printer_page")
txt = txt.replace("- lvgl.page.show: controls_page", "- lvgl.page.show: printer_page")
txt = txt.replace("          id: controls_page", "          id: printer_page")
# don't auto-jump back to the overview when music pauses/stops (stay put)
txt = txt.replace("      - delay: 2000ms\n      - lvgl.page.show: printer_page\n",
                  "      - delay: 2000ms\n", 1)

# remove full-screen album-art overlay on play
before = txt
txt = txt.replace(
    '              - script.stop: debounce_not_playing\n'
    '              - lvgl.page.show: spotify_page\n'
    '              - lambda: "id(is_spotify_active) = true;"\n',
    '              - script.stop: debounce_not_playing\n', 1)
assert txt != before, "album-art overlay trigger not found"
# small album-art tile: source = media_player.home art; drawn on the Sound page
# (small 150px image, NOT the old full-screen 720px takeover)
txt = txt.replace("    entity_id: sensor.spotify_album_art\n",
                  "    entity_id: media_player.home\n    attribute: entity_picture\n", 1)
NEW_OI = '''online_image:
  - id: album_art_image
    url: "https://placehold.co/150x150/073642/268bd2.png"
    format: JPEG
    type: RGB565
    byte_order: little_endian
    resize: 150x150
    buffer_size: 32768
    update_interval: never
    on_download_finished:
      then:
        - lvgl.image.update:
            id: snd_art
            src: album_art_image'''
# repair broken glyphs line (the `"` after `!` closes the YAML string early, so
# figtree_28/gotham_42/gotham_54 only ever contained "!" -> digits/% render as tofu)
GLYPH_BROKEN = '    glyphs: "!"#%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_abcdefghijklmnopqrstuvwxyz{|}~ °"'
GLYPH_FIXED  = '    glyphs: "!\\"#%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_abcdefghijklmnopqrstuvwxyz{|}~ °"'
n_glyph = txt.count(GLYPH_BROKEN)
txt = txt.replace(GLYPH_BROKEN, GLYPH_FIXED)
assert n_glyph >= 1, "broken glyphs line not found (font fix did not apply)"

txt = re.sub(r'online_image:.*?(\n## LVGL)', NEW_OI + r'\1', txt, count=1, flags=re.DOTALL)

with io.open(F, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(txt)

print("OK lines:", txt.count("\n") + 1,
      "| printer_page:", "id: printer_page" in txt,
      "| detail pages:", txt.count("    - id: detail_"),
      "| arcs:", txt.count("id: d_") and (txt.count("_arc\n") ),
      "| glyphs fixed:", n_glyph,
      "| snd_master gone:", "id: snd_master" not in txt )
