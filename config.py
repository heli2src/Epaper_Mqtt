# Released under the MIT license see LICENSE
#
#fonts
import gc
import gui.fonts.ezFBfont_timB10_ascii_14 as tfont14
import gui.fonts.ezFBfont_timB14_full_21 as tfont21
# import gui.fonts.ezFBfont_timB24_ascii_33 as tfont33

SERVER = "your Broker IP-Adress"
WlPw = "your Wlan passwort"
WlSsid = "your Network name"
Topic = "Epaper/state"

epaper_update = 3*60           # update time for the epaper
mqtt_waittime = 5              # time to collect the mqtt news
sxroom = 20
line1 = 10
line2 = 180
line2gap = 155
syroom = 355
gap = 100

CONTENT = {
    "text": {
        "letzte Uhrzeit:   ":{
            "c": [tfont14],
            "p": [555, 5],
            "v": ["last_time"]
        },    
        "zuletzt aktualisiert:   ":{
            "c": [tfont14],
            "p": [555, syroom+110],
            "v": ["sma_time"]
        },
    }, 
    "tiles": {
        "R": {
            "c": ["windrose", tfont21],
            "p": [sxroom + 0*line2gap, line1],
            "h": ["hz_aussen"]},
        "E": {      # Netz                                       # if len("E") < 2 than no name will be placed
            "c": ["measure_power_meter", tfont21],               # c = content
            "p": [sxroom, line2],                   # p = placement (x, y)
            "v": ["current_power"]},                             # v = vertical placement under the icon, h = horizontal
        "S": {                                                   # Solar
            "c": ["measure_photovoltaic_inst", tfont21],
            "p": [sxroom + 115, line2],
            "v": ["hz_koll", "sma_solar"]},
        "B": {                                                   # Batterie
            "c": ["measure_battery_75", tfont21],
            "p": [sxroom + 220, line2],
            "h": ["battery_power", "battery_store", "battery_deliver"]},
        "K": {                                                   # Kessel
            "c": ["sani_buffer_temp_all", tfont21],
            "p": [sxroom + 395, line2],
            "h": ["hz_oben", "hz_mitte", "hz_unten", "heating_power"],
            # "h": ["heating_power"]
            },
        "W": {                                                    # Wallbox
            "c": ["wb_station", tfont21],
            "p": [sxroom + 560, line2],
            "h": ["wbox_power", "wbox_actual", "wbox_total"]},
        "Werken": {
            "c": ["scene_workshop", tfont21],
            "p": [sxroom + 0*gap, syroom],
            "v": ["kg_werken_hum", "kg_werken_temp"]},
        "Wohnen": {
            "c": ["scene_livingroom", tfont21],
            "p": [sxroom + 1*gap, syroom],
            "v": ["eg_wohnen_hum", "eg_wohnen_temp"]},
        "Buero": {
            "c": ["scene_office", tfont21],
            "p": [sxroom + 2*gap, syroom],
            "v": ["eg_buero_hum", "eg_buero_temp"]},
        "Bad EG": {
            "c": ["scene_toilet", tfont21],
            "p": [sxroom + 3*gap, syroom],
            "v": ["eg_bad_hum", "eg_bad_temp"]},
        "Schlaf": {
            "c": ["scene_sleeping", tfont21],
            "p": [sxroom + 4*gap, syroom],
            "v": ["dg_schlaf_hum", "dg_schlaf_temp"]},
        "Gaeste": {
            "c": ["scene_sleeping", tfont21],
            "p": [sxroom + 5*gap, syroom],
            "v": ["dg_gaeste_hum", "dg_gaeste_temp"]},
        "Bad DG": {
            "c": ["scene_bathroom", tfont21],
            "p": [sxroom + 6*gap, syroom],
            "v": ["dg_bad_temp"]},        
        "Logia": {
            "c": ["scene_terrace", tfont21],
            "p": [sxroom + 7*gap, syroom],
            "v": ["dg_loggia_temp"]}     
        },
    "lines": [
            [0, 335, 800, 335, 4],         # x1, y1, x2, y2, width          
        ],
    }

TOPICS = {"Epaper": {
            "update": ["update"]
            },
          "sma": {
            "P_AC": ["sma_solar", "4.0f", " W"],
            "STIME": ["sma_time"]
            },
          "Smartmeter": {
              "1-0:16.7.0": ["current_power"]
              },
          "Battery": {
              "power": ["battery_power", "4.0f", " W"],
              "store": ["battery_store", "4.0f", " Wh"],
              "deliver": ["battery_deliver", "4.0f", " Wh"],
              "bat_state": ["battery_state", "2.0f"],              
              },
          "Heizung": {
              "Aussentemperatur": ["hz_aussen", "4.1f", " C"],              
              "Kollektor": {
                  "Temperatur": ["hz_koll", "4.1f", " C"],
                  },
              "Speicher": {
                  "Oben": ["hz_oben", "4.1f", " C"],
                  "Mitte": ["hz_mitte", "4.1f", " C"],
                  "Unten": ["hz_unten", "4.1f", " C"],
                  },
              },
          "HeatingRod": {
              "power": ["heating_power", "4.0f", " W"],
              },
          "KG": {
              "Werken": {
                  "hum": ["kg_werken_hum", "2.0f", " %"],
                  "temp": ["kg_werken_temp", "4.1f", " C"],
                  },
              },
          "EG": {
              "Wohnen": {
                  "hum": ["eg_wohnen_hum", "2.0f", " %"],
                  "temp": ["eg_wohnen_temp", "4.1f", " C"],
                  },
              "Kueche": {
                  "temp": ["eg_kueche_temp", "4.1f", " C"],
                  },
              "Buero": {
                  "hum": ["eg_buero_hum", "2.0f", " %"],
                  "temp": ["eg_buero_temp", "4.1f", " C"],
                  },
              "Bad": {
                  "hum": ["eg_bad_hum", "2.0f", " %"],
                  "temp": ["eg_bad_temp", "4.1f", " C"],
                  },              
              },
          "DG": {
              "Schlafen": {
                  "hum": ["dg_schlaf_hum", "2.0f", " %"],
                  "temp": ["dg_schlaf_temp", "4.1f", " C"]
                  },
              "Loggia": {
                  "temp": ["dg_loggia_temp", "4.1f", " C"],
                  },
              "Gaeste": {
                  "hum": ["dg_gaeste_hum", "2.0f", " %"],
                  "temp": ["dg_gaeste_temp", "4.1f", " C"],
                  },
              "Bad": {
                  "temp": ["dg_bad_temp", "4.1f", " C"],
                  },              
              },
          "Wallbox": {
              "power": ["wbox_power", "4.0f", " W"],
              "actualkwh": ["wbox_actual", "4.1f", " kWh"],
              "totalkwh": ["wbox_total", "6.0f", " kWh"],             
              },
          }
gc.collect()