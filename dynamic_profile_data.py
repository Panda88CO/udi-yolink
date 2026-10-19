"""
Pre-generated dynamic profile structures for IoX/PG3.
Generated in code from profile directory.
"""

DYNAMIC_EDITORS = [
  {
    "id": "status",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Not Connected",
          "1": "Connected"
        }
      }
    ]
  },
  {
    "id": "connect",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Off-line",
          "1": "On-line"
        }
      }
    ]
  },
  {
    "id": "swstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Off",
          "1": "On",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "swctrl",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,5",
        "names": {
          "0": "Off",
          "1": "On",
          "2": "Toggle",
          "3": "Fast Off",
          "4": "Fast On",
          "5": "Set Delays"
        }
      }
    ]
  },
  {
    "id": "watt",
    "ranges": [
      {
        "uom": "73",
        "min": "-1",
        "max": "2000",
        "prec": "2"
      },
      {
        "uom": "25",
        "subset": "0,98,99",
        "names": {
          "0": "No Support",
          "98": "No Support",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "energy",
    "ranges": [
      {
        "uom": "119",
        "min": "-1",
        "max": "2000",
        "prec": "2"
      },
      {
        "uom": "25",
        "subset": "0,98,99",
        "names": {
          "0": "No Support",
          "98": "No Support",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "waterlevel",
    "ranges": [
      {
        "uom": "56",
        "min": "0",
        "max": "1000",
        "prec": "0"
      },
      {
        "uom": "25",
        "subset": "0,97,99",
        "names": {
          "99": "Unknown",
          "98": "Updating (may take up to 1 hour)"
        }
      }
    ]
  },
  {
    "id": "delay",
    "ranges": [
      {
        "uom": "57",
        "min": "0",
        "max": "86400",
        "prec": "0"
      }
    ]
  },
  {
    "id": "delaymin",
    "ranges": [
      {
        "uom": "44",
        "min": "0",
        "max": "1440",
        "prec": "0"
      }
    ]
  },
  {
    "id": "celsius",
    "ranges": [
      {
        "uom": "4",
        "min": "-40",
        "max": "105",
        "prec": "1"
      },
      {
        "uom": "25",
        "subset": "98,99",
        "names": {
          "99": "Unknown",
          "98": "Updating (may take up to 1 hour)"
        }
      }
    ]
  },
  {
    "id": "celsiusSet",
    "ranges": [
      {
        "uom": "4",
        "min": "5",
        "max": "38",
        "prec": "0"
      }
    ]
  },
  {
    "id": "farenheit",
    "ranges": [
      {
        "uom": "17",
        "min": "-40",
        "max": "221",
        "prec": "1"
      },
      {
        "uom": "25",
        "subset": "98,99",
        "names": {
          "99": "Unknown",
          "98": "Updating (may take up to 1 hour)"
        }
      }
    ]
  },
  {
    "id": "farenheitSet",
    "ranges": [
      {
        "uom": "17",
        "min": "40",
        "max": "100",
        "prec": "0"
      }
    ]
  },
  {
    "id": "humidity",
    "ranges": [
      {
        "uom": "51",
        "min": "0",
        "max": "100",
        "prec": "1"
      },
      {
        "uom": "25",
        "subset": "0,98,99",
        "names": {
          "0": "No Support",
          "98": "No Support",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "batlevel",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4,98,99",
        "names": {
          "0": "Low",
          "1": "Medium Low",
          "2": "Medium",
          "3": "Medium High",
          "4": "High",
          "98": "Ext Power",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "doorstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Closed",
          "1": "Open",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "motionstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "No Motion",
          "1": "Motion",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "waterstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Dry",
          "1": "Wet",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "manstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Closed",
          "1": "Open",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "manctrl",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,5",
        "names": {
          "0": "Close",
          "1": "Open",
          "5": "Set Delays"
        }
      }
    ]
  },
  {
    "id": "usbstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Disabled",
          "1": "Enabled",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "usbctrl",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2",
        "names": {
          "0": "Disable",
          "1": "Enable",
          "2": "Toggle"
        }
      }
    ]
  },
  {
    "id": "outletnbr",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4,5,6,7",
        "names": {
          "0": "Outlet 1",
          "1": "Outlet 2",
          "2": "Outlet 3",
          "3": "Outlet 4",
          "4": "Outlet 5",
          "5": "Outlet 6",
          "6": "Outlet 7",
          "7": "Outlet 8",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "vibrastate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "No Vibration",
          "1": "Vibration",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "volume",
    "ranges": [
      {
        "uom": "56",
        "min": "0",
        "max": "16",
        "prec": "0"
      }
    ]
  },
  {
    "id": "mute",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Muted",
          "1": "Unmuted",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "muteSet",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Muted",
          "1": "Unmuted",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "repeat",
    "ranges": [
      {
        "uom": "56",
        "min": "0",
        "max": "10",
        "prec": "0"
      }
    ]
  },
  {
    "id": "beepEn",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Disabled",
          "1": "Enabled",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "beepEnSet",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Disabled",
          "1": "Enabled",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "tone",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4,99",
        "names": {
          "0": "No Tone",
          "1": "Emergency",
          "2": "Alert",
          "3": "Warning",
          "4": "Tip"
        }
      }
    ]
  },
  {
    "id": "toneSet",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4",
        "names": {
          "0": "No Tone",
          "1": "Emergency",
          "2": "Alert",
          "3": "Warning",
          "4": "Tip"
        }
      }
    ]
  },
  {
    "id": "messages",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4,5",
        "names": {
          "0": "Mes1",
          "1": "Mess2",
          "2": "Messa3",
          "3": "Messag4",
          "4": "Message 5",
          "5": "mes77"
        }
      }
    ]
  },
  {
    "id": "lockstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Unlocked",
          "1": "Locked",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "lock",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Unlocked",
          "1": "Locked",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "lockaction",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4,99",
        "names": {
          "0": "No Action",
          "1": "Lock",
          "2": "Unlock",
          "3": "Lock Failed",
          "4": "Unlock Failed",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "locksource",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,99",
        "names": {
          "0": "Password",
          "1": "Manual",
          "2": "Key",
          "3": "Auto Lock",
          "4": "Fingerprint",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "doorbell",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Idle",
          "1": "Activated",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "dimlvl",
    "ranges": [
      {
        "uom": "51",
        "min": "0",
        "max": "100",
        "prec": "0"
      }
    ]
  },
  {
    "id": "nbrcodes",
    "ranges": [
      {
        "uom": "56",
        "min": "0",
        "max": "64",
        "prec": "0"
      }
    ]
  },
  {
    "id": "cmdstatus",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,99",
        "names": {
          "0": "Fail",
          "1": "Success",
          "2": "TX Key Wrong",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "ircmdstatus",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,99",
        "names": {
          "0": "Ready",
          "1": "Success",
          "2": "Fail",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "poweralert",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,99",
        "names": {
          "0": "No Alert (normal)",
          "1": "Alert",
          "2": "Unit Off",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "powerstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,99",
        "names": {
          "0": "TBD-Unknown?",
          "1": "Supplying?",
          "2": "Charging",
          "3": "Full",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "alertstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "No Alert",
          "1": "Alert Active",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "powered",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "No Power",
          "1": "Unit powered",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "remotetype",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Single Press",
          "1": "Dual Press",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "pfamute",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Not muted",
          "1": "Muted",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "keyscenedef",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4,5,99",
        "names": {
          "0": "OFF (DOF)",
          "1": "ON (DON)",
          "2": "Fast OFF (DFOF)",
          "3": "Fast ON (DFON)",
          "4": "TOGGLE DON/DOF (DON/DOF)",
          "5": "TOGGLE DFON/DFOF (DFON/DFOF)",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "keyscene",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4,5",
        "names": {
          "0": "Send OFF (DOF)",
          "1": "Send ON (DON)",
          "2": "Send FAST OFF (DFOF)",
          "3": "Send FAST ON (DFON)",
          "4": "Toggle State (DON/DOF)",
          "5": "Toggle Fast State (DFON/DFOF)"
        }
      }
    ]
  },
  {
    "id": "sirenstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,99",
        "names": {
          "0": "Normal",
          "1": "Alert",
          "2": "Off",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "sirenduration",
    "ranges": [
      {
        "uom": "58",
        "min": "0",
        "max": "3600",
        "prec": "0"
      }
    ]
  },
  {
    "id": "sirenbatlevel",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4,98,99",
        "names": {
          "0": "Low",
          "1": "Medium Low",
          "2": "Medium",
          "3": "Medium High",
          "4": "High",
          "98": "External Power",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "sirenctrl",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Normal",
          "1": "Alert"
        }
      }
    ]
  },
  {
    "id": "soundlevel",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,98,99",
        "names": {
          "0": "Off",
          "1": "Low (100dB)",
          "2": "Mid (104dB)",
          "3": "High (110dB)",
          "98": "No Support",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "cmdsetting",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3",
        "names": {
          "0": "DON/DOF",
          "1": "DON Only",
          "2": "DOF Only",
          "3": "None"
        }
      }
    ]
  },
  {
    "id": "suspendstate",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4,5,99",
        "names": {
          "0": "Online",
          "1": "Suspended",
          "2": "Offline",
          "3": "Online - Local",
          "4": "Suspended - Local",
          "5": "Offline - Local",
          "6": "Low Power Mode - Control Not Possible",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "alarm",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,98,99",
        "names": {
          "0": "No Alarm (normal)",
          "1": "Alarm",
          "98": "No Support",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "deviceAlert",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Normal",
          "1": "Alert",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "SmokeAlert",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,98,99",
        "names": {
          "0": "Normal",
          "1": "Smoke Alert",
          "98": "No Support",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "COAlert",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,98,99",
        "names": {
          "0": "Normal",
          "1": "CO Alert",
          "98": "No Support",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "TempAlert",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,98,99",
        "names": {
          "0": "Normal",
          "1": "High Temp Alert",
          "98": "No Support",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "BatteryAlert",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,98,99",
        "names": {
          "0": "Normal",
          "1": "Low Battery Alert",
          "98": "No Support",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "SelfcheckState",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Not recommended",
          "1": "Recommended",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "outport",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,99",
        "names": {
          "0": "Outlet 1",
          "1": "Outlet 2",
          "2": "Outlet 3",
          "3": "Outlet 4",
          "4": "Outlet 5",
          "5": "Outlet 6",
          "6": "Outlet 7",
          "7": "Outlet 8",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "schActive",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,98,99",
        "names": {
          "0": "Disabled",
          "1": "Active",
          "2": "Not Defined",
          "98": "No Schedules",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "schActiveI",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Disabled",
          "1": "Active",
          "2": "Not Defined",
          "98": "No Schedules",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "schIndex",
    "ranges": [
      {
        "uom": "25",
        "subset": "0-9,98,99",
        "names": {
          "0": "Schedule 0",
          "1": "Schedule 1",
          "2": "Schedule 2",
          "3": "Schedule 3",
          "4": "Schedule 4",
          "5": "Schedule 5",
          "6": "Schedule 6",
          "7": "Schedule 7",
          "8": "Schedule 8",
          "9": "Schedule 9",
          "99": "No Schedules"
        }
      }
    ]
  },
  {
    "id": "schCount",
    "ranges": [
      {
        "uom": "70",
        "min": "0",
        "max": "20"
      }
    ]
  },
  {
    "id": "schIndexS",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,3,4,5,99",
        "names": {
          "0": "Schedule 0",
          "1": "Schedule 1",
          "2": "Schedule 2",
          "3": "Schedule 3",
          "4": "Schedule 4",
          "5": "Schedule 5",
          "99": "No Schedules"
        }
      }
    ]
  },
  {
    "id": "stHour",
    "ranges": [
      {
        "uom": "19",
        "min": "0",
        "max": "24"
      },
      {
        "uom": "25",
        "subset": "98,99",
        "names": {
          "98": "Not used",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "stMin",
    "ranges": [
      {
        "uom": "44",
        "min": "0",
        "max": "59"
      },
      {
        "uom": "25",
        "subset": "98,99",
        "names": {
          "98": "Not used",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "stSec",
    "ranges": [
      {
        "uom": "57",
        "min": "0",
        "max": "59"
      },
      {
        "uom": "25",
        "subset": "0,99",
        "names": {
          "98": "Not used",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "stHourI",
    "ranges": [
      {
        "uom": "19",
        "min": "0",
        "max": "24"
      },
      {
        "uom": "25",
        "subset": "98",
        "names": {
          "98": "Not used",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "stMinI",
    "ranges": [
      {
        "uom": "44",
        "min": "0",
        "max": "59"
      },
      {
        "uom": "25",
        "subset": "98",
        "names": {
          "98": "Not used",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "stSecI",
    "ranges": [
      {
        "uom": "57",
        "min": "0",
        "max": "59"
      },
      {
        "uom": "25",
        "subset": "0",
        "names": {
          "98": "Not used",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "binDays",
    "ranges": [
      {
        "uom": "25",
        "subset": "0-127",
        "names": {
          "0": "Not defined",
          "1": "Sxxxxxx",
          "2": "xMxxxxx",
          "3": "SMxxxxx",
          "4": "xxTxxxx",
          "5": "SxTxxxx",
          "6": "xMTxxxx",
          "7": "SMTxxxx",
          "8": "xxxWxxx",
          "9": "SxxWxxx",
          "10": "xMxWxxx",
          "11": "SMxWxxx",
          "12": "xxTWxxx",
          "13": "SxTWxxx",
          "14": "xMTWxxx",
          "15": "SMTWxxx",
          "16": "xxxxTxx",
          "17": "SxxxTxx",
          "18": "xMxxTxx",
          "19": "SMxxTxx",
          "20": "xxTxTxx",
          "21": "SxTxTxx",
          "22": "xMTxTxx",
          "23": "SMTxTxx",
          "24": "xxxWTxx",
          "25": "SxxWTxx",
          "26": "xMxWTxx",
          "27": "SMxWTxx",
          "28": "xxTWTxx",
          "29": "SxTWTxx",
          "30": "xMTWTxx",
          "31": "SMTWTxx",
          "32": "xxxxxFx",
          "33": "SxxxxFx",
          "34": "xMxxxFx",
          "35": "SMxxxFx",
          "36": "xxTxxFx",
          "37": "SxTxxFx",
          "38": "xMTxxFx",
          "39": "SMTxxFx",
          "40": "xxxWxFx",
          "41": "SxxWxFx",
          "42": "xMxWxFx",
          "43": "SMxWxFx",
          "44": "xxTWxFx",
          "45": "SxTWxFx",
          "46": "xMTWxFx",
          "47": "SMTWxFx",
          "48": "xxxxTFx",
          "49": "SxxxTFx",
          "50": "xMxxTFx",
          "51": "SMxxTFx",
          "52": "xxTxTFx",
          "53": "SxTxTFx",
          "54": "xMTxTFx",
          "55": "SMTxTFx",
          "56": "xxxWTFx",
          "57": "SxxWTFx",
          "58": "xMxWTFx",
          "59": "SMxWTFx",
          "60": "xxTWTFx",
          "61": "SxTWTFx",
          "62": "xMTWTFx",
          "63": "SMTWTFx",
          "64": "xxxxxxS",
          "65": "SxxxxxS",
          "66": "xMxxxxS",
          "67": "SMxxxxS",
          "68": "xxTxxxS",
          "69": "SxTxxxS",
          "70": "xMTxxxS",
          "71": "SMTxxxS",
          "72": "xxxWxxS",
          "73": "SxxWxxS",
          "74": "xMxWxxS",
          "75": "SMxWxxS",
          "76": "xxTWxxS",
          "77": "SxTWxxS",
          "78": "xMTWxxS",
          "79": "SMTWxxS",
          "80": "xxxxTxS",
          "81": "SxxxTxS",
          "82": "xMxxTxS",
          "83": "SMxxTxS",
          "84": "xxTxTxS",
          "85": "SxTxTxS",
          "86": "xMTxTxS",
          "87": "SMTxTxS",
          "88": "xxxWTxS",
          "89": "SxxWTxS",
          "90": "xMxWTxS",
          "91": "SMxWTxS",
          "92": "xxTWTxS",
          "93": "SxTWTxS",
          "94": "xMTWTxS",
          "95": "SMTWTxS",
          "96": "xxxxxFS",
          "97": "SxxxxFS",
          "98": "xMxxxFS",
          "99": "SMxxxFS",
          "100": "xxTxxFS",
          "101": "SxTxxFS",
          "102": "xMTxxFS",
          "103": "SMTxxFS",
          "104": "xxxWxFS",
          "105": "SxxWxFS",
          "106": "xMxWxFS",
          "107": "SMxWxFS",
          "108": "xxTWxFS",
          "109": "SxTWxFS",
          "110": "xMTWxFS",
          "111": "SMTWxFS",
          "112": "xxxxTFS",
          "113": "SxxxTFS",
          "114": "xMxxTFS",
          "115": "SMxxTFS",
          "116": "xxTxTFS",
          "117": "SxTxTFS",
          "118": "xMTxTFS",
          "119": "SMTxTFS",
          "120": "xxxWTFS",
          "121": "SxxWTFS",
          "122": "xMxWTFS",
          "123": "SMxWTFS",
          "124": "xxTWTFS",
          "125": "SxTWTFS",
          "126": "xMTWTFS",
          "127": "SMTWTFS"
        }
      }
    ]
  },
  {
    "id": "unixtime",
    "ranges": [
      {
        "uom": "151",
        "min": "1737400000",
        "max": "9999999999",
        "prec": "0"
      },
      {
        "uom": "25",
        "subset": "0,99",
        "names": {
          "0": "Unknown",
          "99": "Unknown/Not reported"
        }
      }
    ]
  },
  {
    "id": "ready",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Initializing",
          "1": "Ready"
        }
      }
    ]
  },
  {
    "id": "leaklimit",
    "ranges": [
      {
        "uom": "69",
        "min": "0",
        "max": "100",
        "prec": "0"
      },
      {
        "uom": "6",
        "min": "0",
        "max": "100",
        "prec": "0"
      },
      {
        "uom": "8",
        "min": "0",
        "max": "10",
        "prec": "1"
      },
      {
        "uom": "35",
        "min": "0",
        "max": "400",
        "prec": "0"
      }
    ]
  },
  {
    "id": "liter",
    "ranges": [
      {
        "uom": "35",
        "min": "0",
        "max": "100000",
        "prec": "1"
      },
      {
        "uom": "25",
        "subset": "0,99",
        "names": {
          "0": "Unknown",
          "99": "Unknown/Not reported"
        }
      }
    ]
  },
  {
    "id": "literSet",
    "ranges": [
      {
        "uom": "35",
        "min": "0",
        "max": "100000",
        "prec": "1"
      }
    ]
  },
  {
    "id": "gallon",
    "ranges": [
      {
        "uom": "69",
        "min": "0",
        "max": "10000",
        "prec": "1"
      },
      {
        "uom": "25",
        "subset": "0,99",
        "names": {
          "0": "Unknown",
          "99": "Unknown/Not reported"
        }
      }
    ]
  },
  {
    "id": "gallonSet",
    "ranges": [
      {
        "uom": "69",
        "min": "0",
        "max": "10000",
        "prec": "1"
      }
    ]
  },
  {
    "id": "flow",
    "ranges": [
      {
        "uom": "69",
        "min": "0",
        "max": "10000",
        "prec": "1"
      },
      {
        "uom": "6",
        "min": "0",
        "max": "10000",
        "prec": "1"
      },
      {
        "uom": "8",
        "min": "0",
        "max": "10000",
        "prec": "2"
      },
      {
        "uom": "35",
        "min": "0",
        "max": "100000",
        "prec": "1"
      },
      {
        "uom": "25",
        "subset": "0,99",
        "names": {
          "0": "Unknown",
          "99": "Unknown/Not reported"
        }
      }
    ]
  },
  {
    "id": "enable",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Disabled",
          "1": "Enabled",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "enableSet",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Disabled",
          "1": "Enabled",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "waterrun",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Stopped",
          "1": "Water Running",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "minutes",
    "ranges": [
      {
        "uom": "44",
        "min": "0",
        "max": "1440"
      },
      {
        "uom": "25",
        "subset": "0,99",
        "names": {
          "0": "Unknown",
          "99": "Unknown/Not reported"
        }
      }
    ]
  },
  {
    "id": "minutesSet",
    "ranges": [
      {
        "uom": "44",
        "min": "0",
        "max": "1440"
      }
    ]
  },
  {
    "id": "count",
    "ranges": [
      {
        "uom": "70",
        "min": "0",
        "max": "1440"
      },
      {
        "uom": "25",
        "subset": "0,99",
        "names": {
          "0": "Unknown",
          "99": "Unknown/Not reported"
        }
      }
    ]
  },
  {
    "id": "conductivity",
    "ranges": [
      {
        "uom": "70",
        "min": "0",
        "max": "20",
        "prec": "1"
      },
      {
        "uom": "25",
        "subset": "0,99",
        "names": {
          "0": "Unknown",
          "99": "Unknown/Not reported"
        }
      }
    ]
  },
  {
    "id": "startstop",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Stop",
          "1": "Start"
        }
      }
    ]
  },
  {
    "id": "sprinklermethod",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Water Volume",
          "1": "Time"
        }
      }
    ]
  },
  {
    "id": "wamount",
    "ranges": [
      {
        "uom": "70",
        "min": "0",
        "max": "1440"
      }
    ]
  },
  {
    "id": "runningvalue",
    "ranges": [
      {
        "uom": "44",
        "min": "0",
        "max": "1440"
      },
      {
        "uom": "35",
        "min": "0",
        "max": "2000"
      },
      {
        "uom": "69",
        "min": "0",
        "max": "600"
      },
      {
        "uom": "25",
        "subset": "0,99",
        "names": {
          "0": "Unknown",
          "99": "Unknown/Not reported"
        }
      }
    ]
  },
  {
    "id": "runningmode",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Fixed Water Amount",
          "1": "Fixed Run Time",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "watermode",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "1": "Scheduled",
          "0": "Manual",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "nowateralarm",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Normal (No alarm)",
          "1": "Alarm - No Water Detected",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "beeping",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "No Beep",
          "1": "Beeping",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "leakOpMode",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Detect Water",
          "1": "Detect No Water",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "sensitivity",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Low",
          "1": "High",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "moveAlert",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Not Moved",
          "1": "Sensor Moved",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "freezeAlert",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "No Alert",
          "1": "Freeze Alert",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "sensorError",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Normal",
          "1": "Sensor Error Detected",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "reminder",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Normal"
        }
      }
    ]
  },
  {
    "id": "LED",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Off",
          "1": "On",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "LEDctrl",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1",
        "names": {
          "0": "Off",
          "1": "On",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "ITSTATMODE",
    "ranges": [
      {
        "uom": "67",
        "subset": "0,1,2,3,99",
        "names": {
          "0": "Off",
          "1": "Heat",
          "2": "Cool",
          "3": "Auto",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "ITSTATFAN",
    "ranges": [
      {
        "uom": "68",
        "subset": "0,1,99",
        "names": {
          "0": "Auto",
          "1": "On",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "ICLISMDDEG",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Run",
          "1": "Hold",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "ITSTATHCS",
    "ranges": [
      {
        "uom": "66",
        "subset": "0,1,2,99",
        "names": {
          "0": "Idle",
          "1": "Heating",
          "2": "Cooling",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "IHUMIDITY",
    "ranges": [
      {
        "uom": "51",
        "min": "0",
        "max": "100",
        "prec": "1"
      },
      {
        "uom": "25",
        "subset": "98,99",
        "names": {
          "0": "Unknown",
          "99": "Unknown/Not reported"
        }
      }
    ]
  },
  {
    "id": "IAUXHEAT",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "No",
          "1": "Yes",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "ISTAGE2",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "No",
          "1": "Yes",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "IECOMODE",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Off",
          "1": "On",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "IDRRUNNING",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "No",
          "1": "Yes",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "IMINRUNTIME",
    "ranges": [
      {
        "uom": "44",
        "min": "0",
        "max": "120",
        "prec": "0"
      }
    ]
  },
  {
    "id": "IMUTE",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Off",
          "1": "On",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "IMENULOCK",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,99",
        "names": {
          "0": "Unlocked",
          "1": "Locked",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "IHOURS",
    "ranges": [
      {
        "uom": "20",
        "min": "0",
        "max": "24",
        "prec": "0"
      }
    ]
  },
  {
    "id": "IMASTERSRC",
    "ranges": [
      {
        "uom": "25",
        "subset": "0,1,2,99",
        "names": {
          "0": "Local",
          "1": "Sensor 1",
          "2": "Sensor 2",
          "99": "Unknown"
        }
      }
    ]
  },
  {
    "id": "ecoSet",
    "ranges": [
      {
        "uom": "4",
        "min": "0",
        "max": "5",
        "prec": "1"
      }
    ]
  },
  {
    "id": "ecoSetF",
    "ranges": [
      {
        "uom": "17",
        "min": "0",
        "max": "9",
        "prec": "1"
      }
    ]
  }
]

DYNAMIC_NODEDEFS = [
  {
    "id": "setup",
    "name": "YoLink Setup",
    "icon": "GenericCtrl",
    "properties": [
      {
        "id": "ST",
        "editor": "connect",
        "name": "Node Server"
      },
      {
        "id": "GV1",
        "editor": "ready",
        "name": "Status"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "LastPoll Time"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Heart Beat On"
        },
        {
          "id": "DOF",
          "name": "Heart Beat Off"
        }
      ],
      "accepts": []
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoScheduleSec",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "stSec",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "stSec",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "stSecI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "stSecI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoMScheduleSec",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "nbrcodes",
        "name": "Selected code/port"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "stSec",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "stSec",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "ch",
              "editor": "schIndexS",
              "init": "GV12"
            },
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "stSecI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "stSecI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoirScheduleSec",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "nbrcodes",
        "name": "Selected code/port"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "stSec",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "stSec",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "key",
              "editor": "nbrcodes",
              "init": "GV12"
            },
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "stSecI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "stSecI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoMoutletSchSec",
    "name": "yoMoutletSchSec",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "outport",
        "name": "Selected code/port"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "stSec",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "stSec",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "key",
              "editor": "outport",
              "init": "GV12"
            },
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "stSecI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "stSecI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoirSchedule",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "nbrcodes",
        "name": "Selected code/port"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoMSchedule",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "outport",
        "name": "Selected code/port"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoSchedule",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoSprinklerScheduleSec",
    "name": "Sprinkler Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "stSec",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "stSec",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "stSecI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "stSecI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoSprinklerSchedule",
    "name": "Sprinkler Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoWMVlScheduleSec",
    "name": "Water Meter Valve Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "count",
        "name": "Reserved"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "stSec",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "stSec",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "stSecI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "stSecI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoWMVlSchedule",
    "name": "Water Meter Valve Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "count",
        "name": "Reserved"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoWMLkScheduleSec",
    "name": "Water Meter Leak Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "count",
        "name": "GV12"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "stSec",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "GV17"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "stSec",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "DEFINESCH",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "L_LIMIT",
              "editor": "leaklimit",
              "init": "GV12"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "stSecI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "stSecI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoWMLkSchedule",
    "name": "Water Meter Leak Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "count",
        "name": "GV12"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "GV17"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "DEFINESCH",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "L_LIMIT",
              "editor": "leaklimit",
              "init": "GV12"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoWMScheduleSec",
    "name": "Water Meter Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "count",
        "name": "Leak Limit"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "stSec",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "stSec",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "LLIMIT",
              "editor": "leaklimit",
              "init": "GV12"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "stSecI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "stSecI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoWMSchedule",
    "name": "Water Meter Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "count",
        "name": "Leak Limit"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "schCount",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "LOOKUPSCH",
          "name": "Lookup Schedule",
          "parameters": [
            {
              "id": "",
              "editor": "schIndexS",
              "init": "GV13"
            }
          ]
        },
        {
          "id": "DEFINESCH",
          "name": "Define Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            },
            {
              "id": "LLIMIT",
              "editor": "leaklimit",
              "init": "GV12"
            },
            {
              "id": "onH",
              "editor": "stHourI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "stMinI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "stHourI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "stMinI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "binDays",
              "init": "GV19"
            }
          ]
        },
        {
          "id": "CTRLSCH",
          "name": "Set Schedule",
          "parameters": [
            {
              "id": "index",
              "editor": "schIndexS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "schActiveI",
              "init": "GV14"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoswitchPwr",
    "name": "yoswitchPwr",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "swstate",
        "name": "Switch State"
      },
      {
        "id": "GV0",
        "editor": "swstate",
        "name": "Switch State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "delay",
        "name": "On Delay (min)"
      },
      {
        "id": "GV2",
        "editor": "delay",
        "name": "Off Delay (min)"
      },
      {
        "id": "GV3",
        "editor": "watt",
        "name": "Watt"
      },
      {
        "id": "GV4",
        "editor": "energy",
        "name": "Energy"
      },
      {
        "id": "GV5",
        "editor": "poweralert",
        "name": "Overload Alert"
      },
      {
        "id": "GV6",
        "editor": "poweralert",
        "name": "High Load Alert"
      },
      {
        "id": "GV7",
        "editor": "poweralert",
        "name": "Low Load Alert"
      },
      {
        "id": "GV8",
        "editor": "poweralert",
        "name": "High Temperature Alert"
      },
      {
        "id": "GV9",
        "editor": "LED",
        "name": "Led State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        },
        {
          "id": "DFON",
          "name": "Switch Fast On"
        },
        {
          "id": "DFOF",
          "name": "Switch Fast Off"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        },
        {
          "id": "DFON",
          "name": "Switch Fast On"
        },
        {
          "id": "DFOF",
          "name": "Switch Fast Off"
        },
        {
          "id": "SWCTRL",
          "name": "Switch control",
          "parameters": [
            {
              "id": "",
              "editor": "swctrl",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "SETATTRIB",
          "name": "LED control",
          "parameters": [
            {
              "id": "",
              "editor": "LEDctrl",
              "init": "GV9"
            }
          ]
        },
        {
          "id": "DELAYCTRL",
          "name": "Program Delays",
          "parameters": [
            {
              "id": "ondelay",
              "editor": "delaymin",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "delaymin",
              "init": "GV2"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoswitch",
    "name": "YoLink Switch",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "swstate",
        "name": "Switch State"
      },
      {
        "id": "GV0",
        "editor": "swstate",
        "name": "Switch State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "delay",
        "name": "On Delay (min)"
      },
      {
        "id": "GV2",
        "editor": "delay",
        "name": "Off Delay (min)"
      },
      {
        "id": "GV5",
        "editor": "poweralert",
        "name": "Overload Alert"
      },
      {
        "id": "GV6",
        "editor": "poweralert",
        "name": "High Load Alert"
      },
      {
        "id": "GV7",
        "editor": "poweralert",
        "name": "Low Load Alert"
      },
      {
        "id": "GV8",
        "editor": "poweralert",
        "name": "High Temperature Alert"
      },
      {
        "id": "GV9",
        "editor": "LED",
        "name": "Led State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        },
        {
          "id": "DFON",
          "name": "Switch Fast On"
        },
        {
          "id": "DFOF",
          "name": "Switch Fast Off"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        },
        {
          "id": "DFON",
          "name": "Switch Fast On"
        },
        {
          "id": "DFOF",
          "name": "Switch Fast Off"
        },
        {
          "id": "SWCTRL",
          "name": "Switch control",
          "parameters": [
            {
              "id": "",
              "editor": "swctrl",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "DELAYCTRL",
          "name": "Program Delays",
          "parameters": [
            {
              "id": "ondelay",
              "editor": "delaymin",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "delaymin",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "SETATTRIB",
          "name": "LED control",
          "parameters": [
            {
              "id": "",
              "editor": "LEDctrl",
              "init": "GV9"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoswitchBat",
    "name": "YoLink Battery Switch",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "swstate",
        "name": "Switch State"
      },
      {
        "id": "GV0",
        "editor": "swstate",
        "name": "Switch State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "delay",
        "name": "On Delay (min)"
      },
      {
        "id": "GV2",
        "editor": "delay",
        "name": "Off Delay (min)"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV9",
        "editor": "LED",
        "name": "Led State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        },
        {
          "id": "DFON",
          "name": "Switch Fast On"
        },
        {
          "id": "DFOF",
          "name": "Switch Fast Off"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        },
        {
          "id": "DFON",
          "name": "Switch Fast On"
        },
        {
          "id": "DFOF",
          "name": "Switch Fast Off"
        },
        {
          "id": "SWCTRL",
          "name": "Switch control",
          "parameters": [
            {
              "id": "",
              "editor": "swctrl",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "DELAYCTRL",
          "name": "Program Delays",
          "parameters": [
            {
              "id": "ondelay",
              "editor": "delaymin",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "delaymin",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "SETATTRIB",
          "name": "LED control",
          "parameters": [
            {
              "id": "",
              "editor": "LEDctrl",
              "init": "GV9"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yodimmer",
    "name": "YoLink Dimmer",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "dimlvl",
        "name": "Dim Setting"
      },
      {
        "id": "GV0",
        "editor": "swstate",
        "name": "Switch State"
      },
      {
        "id": "GV1",
        "editor": "delay",
        "name": "On Delay"
      },
      {
        "id": "GV2",
        "editor": "delay",
        "name": "Off Delay"
      },
      {
        "id": "GV3",
        "editor": "dimlvl",
        "name": "Light Level"
      },
      {
        "id": "GV4",
        "editor": "dimlvl",
        "name": "Light Down Level"
      },
      {
        "id": "GV5",
        "editor": "dimlvl",
        "name": "Light Up Level"
      },
      {
        "id": "GV9",
        "editor": "LED",
        "name": "LED Status"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "stSec",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "stSec",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        },
        {
          "id": "DFON",
          "name": "DFON"
        },
        {
          "id": "DFOF",
          "name": "DFOF"
        },
        {
          "id": "FDUP",
          "name": "FDUP"
        },
        {
          "id": "FDDOWN",
          "name": "FDDOWN"
        },
        {
          "id": "FDSTOP",
          "name": "FDSTOP"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        },
        {
          "id": "DFON",
          "name": "DFON"
        },
        {
          "id": "DFOF",
          "name": "DFOF"
        },
        {
          "id": "FDUP",
          "name": "FDUP"
        },
        {
          "id": "FDDOWN",
          "name": "FDDOWN"
        },
        {
          "id": "FDSTOP",
          "name": "FDSTOP"
        },
        {
          "id": "DIMLVL",
          "name": "Light Level (%)",
          "parameters": [
            {
              "id": "",
              "editor": "dimlvl",
              "init": "GV3"
            }
          ]
        },
        {
          "id": "DIMDOWN",
          "name": "Light Down Level (%)",
          "parameters": [
            {
              "id": "",
              "editor": "dimlvl",
              "init": "GV4"
            }
          ]
        },
        {
          "id": "DIMUP",
          "name": "Light Up Level (%)",
          "parameters": [
            {
              "id": "",
              "editor": "dimlvl",
              "init": "GV5"
            }
          ]
        },
        {
          "id": "SWCTRL",
          "name": "Switch control",
          "parameters": [
            {
              "id": "",
              "editor": "swctrl",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "DELAYCTRL",
          "name": "Program Delays",
          "parameters": [
            {
              "id": "ondelay",
              "editor": "delaymin",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "delaymin",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "SETATTRIB",
          "name": "LED control",
          "parameters": [
            {
              "id": "",
              "editor": "LEDctrl",
              "init": "GV9"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yooutlet",
    "name": "YoLink Outlet",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "swstate",
        "name": "Outlet State"
      },
      {
        "id": "GV0",
        "editor": "swstate",
        "name": "Outlet State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "delay",
        "name": "On Delay Remaining"
      },
      {
        "id": "GV2",
        "editor": "delay",
        "name": "Off Delay Remaining"
      },
      {
        "id": "GV5",
        "editor": "poweralert",
        "name": "Overload Alert"
      },
      {
        "id": "GV6",
        "editor": "poweralert",
        "name": "High Load Alert"
      },
      {
        "id": "GV7",
        "editor": "poweralert",
        "name": "Low Load Alert"
      },
      {
        "id": "GV8",
        "editor": "poweralert",
        "name": "High Temperature Alert"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        },
        {
          "id": "SWCTRL",
          "name": "Switch control",
          "parameters": [
            {
              "id": "",
              "editor": "swctrl",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "DELAYCTRL",
          "name": "Program Delays",
          "parameters": [
            {
              "id": "ondelay",
              "editor": "delaymin",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "delaymin",
              "init": "GV2"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yooutletPwr",
    "name": "YoLink Outlet",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "swstate",
        "name": "Outlet State"
      },
      {
        "id": "GV0",
        "editor": "swstate",
        "name": "Outlet State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "delay",
        "name": "On Delay Remaining"
      },
      {
        "id": "GV2",
        "editor": "delay",
        "name": "Off Delay Remaining"
      },
      {
        "id": "GV3",
        "editor": "watt",
        "name": "Watt"
      },
      {
        "id": "GV4",
        "editor": "energy",
        "name": "Energy"
      },
      {
        "id": "GV5",
        "editor": "poweralert",
        "name": "Overload Alert"
      },
      {
        "id": "GV6",
        "editor": "poweralert",
        "name": "High Load Alert"
      },
      {
        "id": "GV7",
        "editor": "poweralert",
        "name": "Low Load Alert"
      },
      {
        "id": "GV8",
        "editor": "poweralert",
        "name": "High Temperature Alert"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        },
        {
          "id": "SWCTRL",
          "name": "Switch control",
          "parameters": [
            {
              "id": "",
              "editor": "swctrl",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "DELAYCTRL",
          "name": "Program Delays",
          "parameters": [
            {
              "id": "ondelay",
              "editor": "delaymin",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "delaymin",
              "init": "GV2"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yomultiout",
    "name": "YoLink Outlet",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "status",
        "name": "Node Server Status"
      },
      {
        "id": "GV12",
        "editor": "outport",
        "name": "Port"
      },
      {
        "id": "GV13",
        "editor": "schIndex",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "schActive",
        "name": "Activated"
      },
      {
        "id": "GV15",
        "editor": "stHour",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "stMin",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "stSec",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "stHour",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "stMin",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "stSec",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "binDays",
        "name": "Active Days"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yosubout",
    "name": "YoLink subOutlet",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "swstate",
        "name": "Outlet State"
      },
      {
        "id": "GV0",
        "editor": "swstate",
        "name": "Outlet State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "delay",
        "name": "On Delay Remaining"
      },
      {
        "id": "GV2",
        "editor": "delay",
        "name": "Off Delay Remaining"
      },
      {
        "id": "GV4",
        "editor": "outletnbr",
        "name": "Outlet"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "DON",
          "name": "Switch On"
        },
        {
          "id": "DOF",
          "name": "Switch Off"
        },
        {
          "id": "SWCTRL",
          "name": "Switch control",
          "parameters": [
            {
              "id": "",
              "editor": "swctrl",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "DELAYCTRL",
          "name": "Program Delays",
          "parameters": [
            {
              "id": "ondelay",
              "editor": "delaymin",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "delaymin",
              "init": "GV2"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yosubusb",
    "name": "YoLink USB Ports",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "usbstate",
        "name": "USB Power State"
      },
      {
        "id": "GV0",
        "editor": "usbstate",
        "name": "USB Power"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Enabled"
        },
        {
          "id": "DOF",
          "name": "Disabled"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "DON",
          "name": "Enabled"
        },
        {
          "id": "DOF",
          "name": "Disabled"
        },
        {
          "id": "USBCTRL",
          "name": "USB Power",
          "parameters": [
            {
              "id": "",
              "editor": "usbctrl",
              "init": "GV0"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yomanipu",
    "name": "YoLink Manipulator",
    "icon": "GenericCtrl",
    "properties": [
      {
        "id": "ST",
        "editor": "manstate",
        "name": "Manipulator State"
      },
      {
        "id": "GV0",
        "editor": "manstate",
        "name": "Manipulator State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "delay",
        "name": "On Delay Remaining"
      },
      {
        "id": "GV2",
        "editor": "delay",
        "name": "Off Delay Remaining"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "MOPEN",
          "name": "Open"
        },
        {
          "id": "MCLOSE",
          "name": "Closed"
        },
        {
          "id": "MANCTRL",
          "name": "Switch control",
          "parameters": [
            {
              "id": "",
              "editor": "manctrl",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "DELAYCTRL",
          "name": "Program Delays",
          "parameters": [
            {
              "id": "ondelay",
              "editor": "delaymin",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "delaymin",
              "init": "GV2"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yosprinkler",
    "name": "yosprinkler",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Current State"
      },
      {
        "id": "GV0",
        "editor": "manstate",
        "name": "GV0"
      },
      {
        "id": "GV1",
        "editor": "liter",
        "name": "Current No Water Alarm"
      },
      {
        "id": "GV10",
        "editor": "liter",
        "name": "Time for Latest operation Update"
      },
      {
        "id": "GV2",
        "editor": "liter",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV3",
        "editor": "minutes",
        "name": "GV3"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "Latest Operation"
      },
      {
        "id": "GV6",
        "editor": "alarm",
        "name": "GV6"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Latest Water Method"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Latest Water Amount target"
      },
      {
        "id": "GV9",
        "editor": "alarm",
        "name": "Latest Water Alarm"
      },
      {
        "id": "GV11",
        "editor": "alarm",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "alarm",
        "name": "Time Delay"
      },
      {
        "id": "GV13",
        "editor": "alarm",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "alarm",
        "name": "GV14"
      },
      {
        "id": "GV22",
        "editor": "liter",
        "name": "Off Sec"
      },
      {
        "id": "GV23",
        "editor": "count",
        "name": "Total Schedules"
      },
      {
        "id": "GV24",
        "editor": "minutes",
        "name": "GV24"
      },
      {
        "id": "GV25",
        "editor": "enable",
        "name": "GV25"
      },
      {
        "id": "GV26",
        "editor": "enable",
        "name": "GV26"
      },
      {
        "id": "GV27",
        "editor": "enable",
        "name": "GV27"
      },
      {
        "id": "GV28",
        "editor": "enable",
        "name": "GV28"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last Data Update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "STARTSTOP",
          "name": "Start/Stop",
          "parameters": [
            {
              "id": "startstop",
              "editor": "startstop"
            },
            {
              "id": "watermode",
              "editor": "watermode"
            }
          ]
        },
        {
          "id": "SETATTRIB",
          "name": "SETATTRIB",
          "parameters": [
            {
              "id": "LLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "LOFF",
              "editor": "enableSet"
            },
            {
              "id": "ORLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "OROFF",
              "editor": "enableSet"
            },
            {
              "id": "ORTLIMIT",
              "editor": "minutesSet"
            },
            {
              "id": "ORTOFF",
              "editor": "enableSet"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yowatermeterCtrl",
    "name": "YoLink Water Meter Controller",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Water Running"
      },
      {
        "id": "GV0",
        "editor": "manstate",
        "name": "Valve State"
      },
      {
        "id": "GV1",
        "editor": "liter",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "liter",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "liter",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "minutes",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Water Temperature"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "Leak Alarm"
      },
      {
        "id": "GV6",
        "editor": "alarm",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Nbr Times Overrun 24H Alarm"
      },
      {
        "id": "GV9",
        "editor": "alarm",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV11",
        "editor": "alarm",
        "name": "Open Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "alarm",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV13",
        "editor": "alarm",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV14",
        "editor": "alarm",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV22",
        "editor": "liter",
        "name": "Overrun Amount 24H Limit"
      },
      {
        "id": "GV23",
        "editor": "count",
        "name": "Overrun Duration Once Limit"
      },
      {
        "id": "GV24",
        "editor": "minutes",
        "name": "Overrun Count 24H Limit"
      },
      {
        "id": "GV25",
        "editor": "enable",
        "name": "Leak Auto Close"
      },
      {
        "id": "GV26",
        "editor": "enable",
        "name": "Overrun Amount Auto Close"
      },
      {
        "id": "GV27",
        "editor": "enable",
        "name": "Overrun Duration Auto Close"
      },
      {
        "id": "GV28",
        "editor": "enable",
        "name": "Overrun Times Auto Close"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Node"
        },
        {
          "id": "VOPEN",
          "name": "Open Valve"
        },
        {
          "id": "VCLOSE",
          "name": "Close Valve"
        },
        {
          "id": "SETATTRIB",
          "name": "Set Parameters",
          "parameters": [
            {
              "id": "LLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "LOFF",
              "editor": "enableSet"
            },
            {
              "id": "ORLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "OROFF",
              "editor": "enableSet"
            },
            {
              "id": "ORTLIMIT",
              "editor": "minutesSet"
            },
            {
              "id": "ORTOFF",
              "editor": "enableSet"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yowatermeterCtrlF",
    "name": "yowatermeterCtrlF",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Water Running"
      },
      {
        "id": "GV0",
        "editor": "manstate",
        "name": "Valve State"
      },
      {
        "id": "GV1",
        "editor": "gallon",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "gallon",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "gallon",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "minutes",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "farenheit",
        "name": "Water Temperature"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "Leak Alarm"
      },
      {
        "id": "GV6",
        "editor": "alarm",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Nbr Times Overrun 24H Alarm"
      },
      {
        "id": "GV9",
        "editor": "alarm",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV11",
        "editor": "alarm",
        "name": "Open Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "alarm",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV13",
        "editor": "alarm",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV14",
        "editor": "alarm",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV22",
        "editor": "gallon",
        "name": "Overrun Amount 24H Limit"
      },
      {
        "id": "GV23",
        "editor": "count",
        "name": "Overrun Duration Once Limit"
      },
      {
        "id": "GV24",
        "editor": "minutes",
        "name": "Overrun Count 24H Limit"
      },
      {
        "id": "GV25",
        "editor": "enable",
        "name": "Leak Auto Close"
      },
      {
        "id": "GV26",
        "editor": "enable",
        "name": "Overrun Amount Auto Close"
      },
      {
        "id": "GV27",
        "editor": "enable",
        "name": "Overrun Duration Auto Close"
      },
      {
        "id": "GV28",
        "editor": "enable",
        "name": "Overrun Times Auto Close"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Node"
        },
        {
          "id": "VOPEN",
          "name": "Open Valve"
        },
        {
          "id": "VCLOSE",
          "name": "Close Valve"
        },
        {
          "id": "SETATTRIB",
          "name": "Set Parameters",
          "parameters": [
            {
              "id": "LLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "LOFF",
              "editor": "enableSet"
            },
            {
              "id": "ORLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "OROFF",
              "editor": "enableSet"
            },
            {
              "id": "ORTLIMIT",
              "editor": "minutesSet"
            },
            {
              "id": "ORTOFF",
              "editor": "enableSet"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yowatermeterMulti",
    "name": "YoLink Water Meter Multi Controller",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Water Running"
      },
      {
        "id": "GV1",
        "editor": "count",
        "name": "Water Meter Total"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "Leak Alarm"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Node"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yowatermeterMultiF",
    "name": "yowatermeterMultiF",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Water Running"
      },
      {
        "id": "GV1",
        "editor": "count",
        "name": "Water Meter Total"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "Leak Alarm"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Node"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yowatermeterSub",
    "name": "YoLink Water Meter Sub Controller",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Water Running"
      },
      {
        "id": "GV0",
        "editor": "manstate",
        "name": "Valve State"
      },
      {
        "id": "GV1",
        "editor": "flow",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "flow",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "flow",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "minutes",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "GV6",
        "editor": "alarm",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Nbr Times Overrun 24H Alarm"
      },
      {
        "id": "GV9",
        "editor": "alarm",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "alarm",
        "name": "Valve Error Alarm"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "VOPEN",
          "name": "Open Valve"
        },
        {
          "id": "VCLOSE",
          "name": "Close Valve"
        },
        {
          "id": "SETATTRIB",
          "name": "Set Parameters",
          "parameters": [
            {
              "id": "LLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "LOFF",
              "editor": "enableSet"
            },
            {
              "id": "ORLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "OROFF",
              "editor": "enableSet"
            },
            {
              "id": "ORTLIMIT",
              "editor": "minutesSet"
            },
            {
              "id": "ORTOFF",
              "editor": "enableSet"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yowatermeterSubL",
    "name": "YoLink Water Meter Sub Controller",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Water Running"
      },
      {
        "id": "GV0",
        "editor": "manstate",
        "name": "Valve State"
      },
      {
        "id": "GV1",
        "editor": "liter",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "liter",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "liter",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "minutes",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "GV6",
        "editor": "alarm",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Nbr Times Overrun 24H Alarm"
      },
      {
        "id": "GV9",
        "editor": "alarm",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "alarm",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV22",
        "editor": "liter",
        "name": "Overrun Amount 24H Limit"
      },
      {
        "id": "GV23",
        "editor": "count",
        "name": "Overrun Duration Once Limit"
      },
      {
        "id": "GV24",
        "editor": "minutes",
        "name": "Overrun Count 24H Limit"
      },
      {
        "id": "GV25",
        "editor": "enable",
        "name": "Leak Auto Close"
      },
      {
        "id": "GV26",
        "editor": "enable",
        "name": "Overrun Amount Auto Close"
      },
      {
        "id": "GV27",
        "editor": "enable",
        "name": "Overrun Duration Auto Close"
      },
      {
        "id": "GV28",
        "editor": "enable",
        "name": "Overrun Times Auto Close"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "VOPEN",
          "name": "Open Valve"
        },
        {
          "id": "VCLOSE",
          "name": "Close Valve"
        },
        {
          "id": "SETATTRIB",
          "name": "Set Parameters",
          "parameters": [
            {
              "id": "LLIMIT",
              "editor": "literSet"
            },
            {
              "id": "LOFF",
              "editor": "enableSet"
            },
            {
              "id": "ORLIMIT",
              "editor": "literSet"
            },
            {
              "id": "OROFF",
              "editor": "enableSet"
            },
            {
              "id": "ORTLIMIT",
              "editor": "minutesSet"
            },
            {
              "id": "ORTOFF",
              "editor": "enableSet"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yowatermeterSubG",
    "name": "YoLink Water Meter Sub Controller",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Water Running"
      },
      {
        "id": "GV0",
        "editor": "manstate",
        "name": "Valve State"
      },
      {
        "id": "GV1",
        "editor": "gallon",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "gallon",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "gallon",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "minutes",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "GV6",
        "editor": "alarm",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Nbr Times Overrun 24H Alarm"
      },
      {
        "id": "GV9",
        "editor": "alarm",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "alarm",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV22",
        "editor": "gallon",
        "name": "Overrun Amount 24H Limit"
      },
      {
        "id": "GV23",
        "editor": "minutes",
        "name": "Overrun Duration Once Limit"
      },
      {
        "id": "GV24",
        "editor": "count",
        "name": "Overrun Count 24H Limit"
      },
      {
        "id": "GV25",
        "editor": "enable",
        "name": "Leak Auto Close"
      },
      {
        "id": "GV26",
        "editor": "enable",
        "name": "Overrun Amount Auto Close"
      },
      {
        "id": "GV27",
        "editor": "enable",
        "name": "Overrun Duration Auto Close"
      },
      {
        "id": "GV28",
        "editor": "enable",
        "name": "Overrun Times Auto Close"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "VOPEN",
          "name": "Open Valve"
        },
        {
          "id": "VCLOSE",
          "name": "Close Valve"
        },
        {
          "id": "SETATTRIB",
          "name": "Set Parameters",
          "parameters": [
            {
              "id": "LLIMIT",
              "editor": "gallonSet"
            },
            {
              "id": "LOFF",
              "editor": "enableSet"
            },
            {
              "id": "ORLIMIT",
              "editor": "gallonSet"
            },
            {
              "id": "OROFF",
              "editor": "enableSet"
            },
            {
              "id": "ORTLIMIT",
              "editor": "minutesSet"
            },
            {
              "id": "ORTOFF",
              "editor": "enableSet"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yowatermeterOnly",
    "name": "YoLink Water Meter",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Water Running"
      },
      {
        "id": "GV1",
        "editor": "flow",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "flow",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "flow",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "minutes",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Water Temperature"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "Leak Alarm"
      },
      {
        "id": "GV6",
        "editor": "alarm",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV9",
        "editor": "alarm",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV11",
        "editor": "alarm",
        "name": "Open Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "alarm",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV13",
        "editor": "alarm",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV14",
        "editor": "alarm",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV16",
        "editor": "minutes",
        "name": "Overrun time Limit"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Node"
        },
        {
          "id": "SETATTRIB",
          "name": "Set Parameters",
          "parameters": [
            {
              "id": "LLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "ORLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "ORTLIMIT",
              "editor": "minutesSet"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yowatermeterOnlyF",
    "name": "YoLink Water Meter",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Water Running"
      },
      {
        "id": "GV1",
        "editor": "flow",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "flow",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "flow",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "minutes",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "farenheit",
        "name": "Water Temperature"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "Leak Alarm"
      },
      {
        "id": "GV6",
        "editor": "alarm",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV9",
        "editor": "alarm",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV11",
        "editor": "alarm",
        "name": "Open Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "alarm",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV13",
        "editor": "alarm",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV14",
        "editor": "alarm",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV16",
        "editor": "minutes",
        "name": "Overrun time Limit"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Node"
        },
        {
          "id": "SETATTRIB",
          "name": "Set Parameters",
          "parameters": [
            {
              "id": "LLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "ORLIMIT",
              "editor": "leaklimit"
            },
            {
              "id": "ORTLIMIT",
              "editor": "minutesSet"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yosprinklerv2",
    "name": "YoLink Smart Sprinkler V2",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterrun",
        "name": "Current State"
      },
      {
        "id": "GV1",
        "editor": "nowateralarm",
        "name": "Current No Water Alarm"
      },
      {
        "id": "GV10",
        "editor": "unixtime",
        "name": "Time for Latest operation Update"
      },
      {
        "id": "GV5",
        "editor": "waterrun",
        "name": "Latest Operation"
      },
      {
        "id": "GV7",
        "editor": "runningmode",
        "name": "Latest Water Method"
      },
      {
        "id": "GV8",
        "editor": "runningvalue",
        "name": "Latest Water Amount target"
      },
      {
        "id": "GV9",
        "editor": "nowateralarm",
        "name": "Latest Water Alarm"
      },
      {
        "id": "GV12",
        "editor": "minutes",
        "name": "Time Delay"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last Data Update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "STARTSTOP",
          "name": "Start/Stop",
          "parameters": [
            {
              "id": "startstop",
              "editor": "startstop"
            },
            {
              "id": "watermode",
              "editor": "watermode"
            }
          ]
        },
        {
          "id": "WATTRIB",
          "name": "Set watering Attributes",
          "parameters": [
            {
              "id": "wmethod",
              "editor": "sprinklermethod"
            },
            {
              "id": "wamount",
              "editor": "wamount"
            }
          ]
        },
        {
          "id": "WDELAY",
          "name": "Set water delay",
          "parameters": [
            {
              "id": "",
              "editor": "minutesSet"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yothsens",
    "name": "YoLink THsensor",
    "icon": "TempSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "celsius",
        "name": "Sensor Temperature"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Sensor Temperature (legacy)"
      },
      {
        "id": "GV1",
        "editor": "alarm",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV2",
        "editor": "alarm",
        "name": "High Temp Alarm"
      },
      {
        "id": "CLIHUM",
        "editor": "humidity",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV4",
        "editor": "alarm",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "High Humidity Alarm"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Battery Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Alarm triggered"
      },
      {
        "id": "GV9",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "celsius",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "celsius",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "humidity",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "humidity",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "celsius",
        "name": "Low Temp 24H"
      },
      {
        "id": "GV15",
        "editor": "celsius",
        "name": "High Temp 24H"
      },
      {
        "id": "GV16",
        "editor": "humidity",
        "name": "Low Humidity  24H"
      },
      {
        "id": "GV17",
        "editor": "humidity",
        "name": "High Humidity 24H"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command (Alert) Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yosoilsensor",
    "name": "YoLink Soil Sensor",
    "icon": "Weather",
    "properties": [
      {
        "id": "ST",
        "editor": "conductivity",
        "name": "Soil Conductivity (mS/cm)"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Sensor Temperature"
      },
      {
        "id": "CLIHUM",
        "editor": "humidity",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV1",
        "editor": "alarm",
        "name": "Low Conductivity Alarm"
      },
      {
        "id": "GV2",
        "editor": "alarm",
        "name": "High Conductivity Alarm"
      },
      {
        "id": "GV3",
        "editor": "alarm",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV4",
        "editor": "alarm",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV6",
        "editor": "alarm",
        "name": "High Humidity Alarm"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Period Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Alarm triggered"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV9",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "celsius",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "celsius",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "humidity",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "humidity",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "conductivity",
        "name": "Low Conductivity Alarm Limit (mS/cm)"
      },
      {
        "id": "GV15",
        "editor": "conductivity",
        "name": "High Conductivity Alarm Limit (mS/cm)"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command (Alert) Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yosoilsensorF",
    "name": "YoLink Soil Sensor",
    "icon": "Weather",
    "properties": [
      {
        "id": "ST",
        "editor": "farenheit",
        "name": "Soil Conductivity (mS/cm)"
      },
      {
        "id": "CLITEMP",
        "editor": "farenheit",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV1",
        "editor": "alarm",
        "name": "Low Conductivity Alarm"
      },
      {
        "id": "GV2",
        "editor": "alarm",
        "name": "High Conductivity Alarm"
      },
      {
        "id": "GV3",
        "editor": "alarm",
        "name": "Low Temp Alarm"
      },
      {
        "id": "CLIHUM",
        "editor": "humidity",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV4",
        "editor": "alarm",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV6",
        "editor": "alarm",
        "name": "High Humidity Alarm"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Period Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Alarm triggered"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV9",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "farenheit",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "farenheit",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "humidity",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "humidity",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "farenheit",
        "name": "Low Conductivity Alarm Limit (mS/cm)"
      },
      {
        "id": "GV15",
        "editor": "farenheit",
        "name": "High Conductivity Alarm Limit (mS/cm)"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command (Alert) Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yothsensF",
    "name": "YoLink THsensor",
    "icon": "TempSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "farenheit",
        "name": "Sensor Temperature"
      },
      {
        "id": "CLITEMP",
        "editor": "farenheit",
        "name": "Sensor Temperature (legacy)"
      },
      {
        "id": "GV1",
        "editor": "alarm",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV2",
        "editor": "alarm",
        "name": "High Temp Alarm"
      },
      {
        "id": "CLIHUM",
        "editor": "humidity",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV4",
        "editor": "alarm",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "High Humidity Alarm"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Battery Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Alarm triggered"
      },
      {
        "id": "GV9",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "farenheit",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "farenheit",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "humidity",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "humidity",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "farenheit",
        "name": "Low Temp 24H"
      },
      {
        "id": "GV15",
        "editor": "farenheit",
        "name": "High Temp 24H"
      },
      {
        "id": "GV16",
        "editor": "humidity",
        "name": "Low Humidity  24H"
      },
      {
        "id": "GV17",
        "editor": "humidity",
        "name": "High Humidity 24H"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command (Alert) Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yotsens",
    "name": "YoLink T Sensor",
    "icon": "TempSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "celsius",
        "name": "Sensor Temperature"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Sensor Temperature (legacy)"
      },
      {
        "id": "GV1",
        "editor": "alarm",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV2",
        "editor": "alarm",
        "name": "High Temp Alarm"
      },
      {
        "id": "CLIHUM",
        "editor": "humidity",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV4",
        "editor": "alarm",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "High Humidity Alarm"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Battery Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Alarm triggered"
      },
      {
        "id": "GV9",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "celsius",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "celsius",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "humidity",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "humidity",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "celsius",
        "name": "Low Temp 24H"
      },
      {
        "id": "GV15",
        "editor": "celsius",
        "name": "High Temp 24H"
      },
      {
        "id": "GV16",
        "editor": "humidity",
        "name": "Low Humidity 24H"
      },
      {
        "id": "GV17",
        "editor": "humidity",
        "name": "High Humidity 24H"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command (Alert) Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yotsensF",
    "name": "YoLink T Sensor",
    "icon": "TempSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "farenheit",
        "name": "Sensor Temperature"
      },
      {
        "id": "CLITEMP",
        "editor": "farenheit",
        "name": "Sensor Temperature (legacy)"
      },
      {
        "id": "GV1",
        "editor": "alarm",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV2",
        "editor": "alarm",
        "name": "High Temp Alarm"
      },
      {
        "id": "CLIHUM",
        "editor": "humidity",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV4",
        "editor": "alarm",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "High Humidity Alarm"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV7",
        "editor": "alarm",
        "name": "Battery Alarm"
      },
      {
        "id": "GV8",
        "editor": "alarm",
        "name": "Alarm triggered"
      },
      {
        "id": "GV9",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "farenheit",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "farenheit",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "humidity",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "humidity",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "farenheit",
        "name": "Low Temp 24H"
      },
      {
        "id": "GV15",
        "editor": "farenheit",
        "name": "High Temp 24H"
      },
      {
        "id": "GV16",
        "editor": "humidity",
        "name": "Low Humidity 24H"
      },
      {
        "id": "GV17",
        "editor": "humidity",
        "name": "High Humidity 24H"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command (Alert) Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yodoorsens",
    "name": "YoLink Door Sensor",
    "icon": "DoorLock",
    "properties": [
      {
        "id": "ST",
        "editor": "doorstate",
        "name": "Door State"
      },
      {
        "id": "GV0",
        "editor": "doorstate",
        "name": "Door State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "batlevel",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV2",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "GV3",
        "editor": "unixtime",
        "name": "Last State Change"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Open"
        },
        {
          "id": "DOF",
          "name": "Closed"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yogarage",
    "name": "YoLink Garage Controller",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "status",
        "name": "Node Server Status"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        },
        {
          "id": "TOGGLE",
          "name": "Toggle Door"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yomotionsens",
    "name": "YoLink Motion Sensor",
    "icon": "MotionSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "motionstate",
        "name": "Motion State"
      },
      {
        "id": "GV0",
        "editor": "motionstate",
        "name": "Motion State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "batlevel",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV2",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Motion"
        },
        {
          "id": "DOF",
          "name": "No Motion"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yomotionsensF",
    "name": "YoLink Motion Sensor",
    "icon": "MotionSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "motionstate",
        "name": "Motion State"
      },
      {
        "id": "GV0",
        "editor": "motionstate",
        "name": "Motion State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "batlevel",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV2",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "farenheit",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Motion"
        },
        {
          "id": "DOF",
          "name": "No Motion"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoleaksensF",
    "name": "YoLink Water Sensor",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterstate",
        "name": "Water State"
      },
      {
        "id": "GV0",
        "editor": "waterstate",
        "name": "Water State (Legacy)"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV2",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "farenheit",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV3",
        "editor": "unixtime",
        "name": "Last State Change"
      },
      {
        "id": "GV4",
        "editor": "beeping",
        "name": "Sensor Sound"
      },
      {
        "id": "GV5",
        "editor": "leakOpMode",
        "name": "Operating Mode"
      },
      {
        "id": "GV6",
        "editor": "sensitivity",
        "name": "Sensitivity"
      },
      {
        "id": "GV7",
        "editor": "moveAlert",
        "name": "Sensor Move Alert"
      },
      {
        "id": "GV8",
        "editor": "freezeAlert",
        "name": "Sensor Freeze Alert"
      },
      {
        "id": "GV9",
        "editor": "sensorError",
        "name": "Sensor Error"
      },
      {
        "id": "GV10",
        "editor": "reminder",
        "name": "Reminder"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Water Alert Detected"
        },
        {
          "id": "DOF",
          "name": "Normal"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "SETBEEP",
          "name": "Set Beep Alert",
          "parameters": [
            {
              "id": "",
              "editor": "beeping",
              "init": "GV4"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoleaksens",
    "name": "YoLink Water Sensor",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterstate",
        "name": "Water State"
      },
      {
        "id": "GV0",
        "editor": "waterstate",
        "name": "Water State (Legacy)"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV2",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV3",
        "editor": "unixtime",
        "name": "Last State Change"
      },
      {
        "id": "GV4",
        "editor": "beeping",
        "name": "Sensor Sound"
      },
      {
        "id": "GV5",
        "editor": "leakOpMode",
        "name": "Operating Mode"
      },
      {
        "id": "GV6",
        "editor": "sensitivity",
        "name": "Sensitivity"
      },
      {
        "id": "GV7",
        "editor": "moveAlert",
        "name": "Sensor Move Alert"
      },
      {
        "id": "GV8",
        "editor": "freezeAlert",
        "name": "Sensor Freeze Alert"
      },
      {
        "id": "GV9",
        "editor": "sensorError",
        "name": "Sensor Error"
      },
      {
        "id": "GV10",
        "editor": "reminder",
        "name": "Reminder"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Water Alert Detected"
        },
        {
          "id": "DOF",
          "name": "Normal"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "SETBEEP",
          "name": "Set Beep Alert",
          "parameters": [
            {
              "id": "",
              "editor": "beeping",
              "init": "GV4"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoCOSmokesens",
    "name": "YoLink COSmokeSensor",
    "icon": "SmokeSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "deviceAlert",
        "name": "Alarm"
      },
      {
        "id": "ALARM",
        "editor": "deviceAlert",
        "name": "Alert Detected"
      },
      {
        "id": "GV0",
        "editor": "SmokeAlert",
        "name": "Smoke Detection"
      },
      {
        "id": "GV1",
        "editor": "COAlert",
        "name": "CO Detection"
      },
      {
        "id": "GV2",
        "editor": "TempAlert",
        "name": "High Temp Detection"
      },
      {
        "id": "GV3",
        "editor": "BatteryAlert",
        "name": "Battery Problem Detection"
      },
      {
        "id": "GV4",
        "editor": "batlevel",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV5",
        "editor": "SelfcheckState",
        "name": "Self-check"
      },
      {
        "id": "GV7",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Alert Detected"
        },
        {
          "id": "DOF",
          "name": "Normal"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV7"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoCOSmokesensF",
    "name": "YoLink COSmokeSensor",
    "icon": "SmokeSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "deviceAlert",
        "name": "Alarm"
      },
      {
        "id": "ALARM",
        "editor": "deviceAlert",
        "name": "Alert Detected"
      },
      {
        "id": "GV0",
        "editor": "SmokeAlert",
        "name": "Smoke Detection"
      },
      {
        "id": "GV1",
        "editor": "COAlert",
        "name": "CO Detection"
      },
      {
        "id": "GV2",
        "editor": "TempAlert",
        "name": "High Temp Detection"
      },
      {
        "id": "GV3",
        "editor": "BatteryAlert",
        "name": "Battery Problem Detection"
      },
      {
        "id": "GV4",
        "editor": "batlevel",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV5",
        "editor": "SelfcheckState",
        "name": "Self-check"
      },
      {
        "id": "GV7",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "farenheit",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Alert Detected"
        },
        {
          "id": "DOF",
          "name": "Normal"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV7"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yovibrasens",
    "name": "YoLink Vibration Sensor",
    "icon": "MotionSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "vibrastate",
        "name": "Vibration State"
      },
      {
        "id": "GV0",
        "editor": "vibrastate",
        "name": "Vibration State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "batlevel",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV2",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Vibration Detected"
        },
        {
          "id": "DOF",
          "name": "Normal"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yovibrasensF",
    "name": "YoLink Vibration Sensor",
    "icon": "MotionSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "vibrastate",
        "name": "Vibration State"
      },
      {
        "id": "GV0",
        "editor": "vibrastate",
        "name": "Vibration State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "batlevel",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV2",
        "editor": "cmdsetting",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "farenheit",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "Vibration Detected"
        },
        {
          "id": "DOF",
          "name": "Normal"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yohubbat",
    "name": "YoLink Hub w Battery",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "poweralert",
        "name": "Supply Status"
      },
      {
        "id": "GV0",
        "editor": "powerstate",
        "name": "Battery Status"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yohub",
    "name": "YoLink Hub",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "status",
        "name": "Status"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yospeakerh",
    "name": "YoLink Speaker Hub",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "status",
        "name": "Nodeserver Status"
      },
      {
        "id": "GV0",
        "editor": "volume",
        "name": "Speaker volume"
      },
      {
        "id": "GV1",
        "editor": "beepEn",
        "name": "Command Beep"
      },
      {
        "id": "GV2",
        "editor": "mute",
        "name": "Mute"
      },
      {
        "id": "GV3",
        "editor": "tone",
        "name": "Tone Type"
      },
      {
        "id": "GV4",
        "editor": "messages",
        "name": "Message"
      },
      {
        "id": "GV5",
        "editor": "repeat",
        "name": "Repeat"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update Status"
        },
        {
          "id": "PLAY",
          "name": "Play Message",
          "parameters": [
            {
              "id": "message",
              "editor": "messages",
              "init": "GV4"
            },
            {
              "id": "volume",
              "editor": "volume",
              "init": "GV0"
            },
            {
              "id": "tone",
              "editor": "toneSet",
              "init": "GV3"
            },
            {
              "id": "repeat",
              "editor": "repeat",
              "init": "GV5"
            }
          ]
        },
        {
          "id": "BEEP",
          "name": "Beep",
          "parameters": [
            {
              "id": "",
              "editor": "beepEnSet",
              "init": "GV1"
            }
          ]
        },
        {
          "id": "MUTE",
          "name": "Mute",
          "parameters": [
            {
              "id": "",
              "editor": "muteSet",
              "init": "GV2"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yolockv2",
    "name": "yolockv2",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "lockstate",
        "name": "Lock State"
      },
      {
        "id": "GV0",
        "editor": "lockstate",
        "name": "Lock State (legacy)"
      },
      {
        "id": "GV1",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV2",
        "editor": "doorbell",
        "name": "Doorbell Active"
      },
      {
        "id": "GV3",
        "editor": "doorstate",
        "name": "Door State"
      },
      {
        "id": "GV4",
        "editor": "lockaction",
        "name": "Lock Action"
      },
      {
        "id": "GV5",
        "editor": "locksource",
        "name": "Source"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "LOCK",
          "name": "Lock"
        },
        {
          "id": "UNLOCK",
          "name": "Unlock"
        },
        {
          "id": "LOCKCTRL",
          "name": "Set Lock",
          "parameters": [
            {
              "id": "",
              "editor": "lock",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yolock",
    "name": "YoLink Smart Lock",
    "icon": "DoorLock",
    "properties": [
      {
        "id": "ST",
        "editor": "lockstate",
        "name": "Lock State"
      },
      {
        "id": "GV0",
        "editor": "lockstate",
        "name": "Lock State (legacy)"
      },
      {
        "id": "GV1",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV3",
        "editor": "doorstate",
        "name": "Door State"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "LOCK",
          "name": "Lock"
        },
        {
          "id": "UNLOCK",
          "name": "Unlock"
        },
        {
          "id": "LOCKCTRL",
          "name": "Set Lock",
          "parameters": [
            {
              "id": "",
              "editor": "lock",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoirremote",
    "name": "YoLink Ir Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "ircmdstatus",
        "name": "Last Command Status"
      },
      {
        "id": "GV0",
        "editor": "nbrcodes",
        "name": "Number of Learned codes"
      },
      {
        "id": "GV1",
        "editor": "batlevel",
        "name": "Battery Level (legacy)"
      },
      {
        "id": "GV2",
        "editor": "ircmdstatus",
        "name": "Last Command Status (legacy)"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "LEARNCODE",
          "name": "Learn New Code"
        },
        {
          "id": "UPDATE",
          "name": "Update"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yoircode",
    "name": "YoLink Ir Code",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "ircmdstatus",
        "name": "TX success"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        }
      ],
      "accepts": [
        {
          "id": "TXCODE",
          "name": "Send IR Code"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yopwralarm",
    "name": "YoLink Power Failure Alarm",
    "icon": "Input",
    "properties": [
      {
        "id": "ST",
        "editor": "poweralert",
        "name": "Unit State"
      },
      {
        "id": "GV0",
        "editor": "poweralert",
        "name": "Unit State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV2",
        "editor": "alertstate",
        "name": "Alert Pending"
      },
      {
        "id": "GV3",
        "editor": "powered",
        "name": "Power on Unit"
      },
      {
        "id": "GV4",
        "editor": "pfamute",
        "name": "Muted"
      },
      {
        "id": "GV7",
        "editor": "cmdstatus",
        "name": "Command Setting"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "SETCMD",
          "name": "Select Command Action",
          "parameters": [
            {
              "id": "",
              "editor": "cmdsetting",
              "init": "GV7"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yowaterdept",
    "name": "YoLink Water Level Sensor",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "waterlevel",
        "name": "Water Level (0-1000)"
      },
      {
        "id": "GV0",
        "editor": "waterlevel",
        "name": "Water Level (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "waterlevel",
        "name": "Low water Level Alarm setting"
      },
      {
        "id": "GV2",
        "editor": "waterlevel",
        "name": "High water Level Alarm setting"
      },
      {
        "id": "GV3",
        "editor": "alarm",
        "name": "Low Water Level"
      },
      {
        "id": "GV4",
        "editor": "alarm",
        "name": "High Water Level"
      },
      {
        "id": "GV5",
        "editor": "alarm",
        "name": "Sensor Error"
      },
      {
        "id": "BATLVL",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last Data Update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "SETATTR",
          "name": "Set water level alarms",
          "parameters": [
            {
              "id": "waterLowAlarm",
              "editor": "waterlevel",
              "init": "GV1"
            },
            {
              "id": "waterHighAlarm",
              "editor": "waterlevel",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "UPDATE"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yosiren",
    "name": "YoLink Siren",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "sirenstate",
        "name": "Siren State"
      },
      {
        "id": "GV0",
        "editor": "sirenstate",
        "name": "Siren State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "sirenduration",
        "name": "Siren Duration"
      },
      {
        "id": "GV2",
        "editor": "sirenbatlevel",
        "name": "Supply State"
      },
      {
        "id": "GV3",
        "editor": "soundlevel",
        "name": "Sound Level"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last device update"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        }
      ],
      "accepts": [
        {
          "id": "SIRENCTRL",
          "name": "Set Control",
          "parameters": [
            {
              "id": "",
              "editor": "sirenctrl",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "UPDATE",
          "name": "Update Status"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yosmremote",
    "name": "YoLink Smart Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "remotetype",
        "name": "Remote Type"
      },
      {
        "id": "GV3",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "celsius",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yosmremoteF",
    "name": "YoLink Smart Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "remotetype",
        "name": "Remote Type"
      },
      {
        "id": "GV3",
        "editor": "batlevel",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "farenheit",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update"
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "smremotekey",
    "name": "YoLink Smart Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "keyscenedef",
        "name": "Last Command"
      },
      {
        "id": "GV1",
        "editor": "keyscenedef",
        "name": "Short Press Command Type"
      },
      {
        "id": "GV2",
        "editor": "keyscenedef",
        "name": "Long Press Type"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last key press"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        },
        {
          "id": "DFON",
          "name": "DFON"
        },
        {
          "id": "DFOF",
          "name": "DFOF"
        }
      ],
      "accepts": [
        {
          "id": "KEYPRESS",
          "name": "Short Press Command Type",
          "parameters": [
            {
              "id": "",
              "editor": "keyscene",
              "init": "GV1"
            }
          ]
        },
        {
          "id": "KEYLPRESS",
          "name": "Long Press Command Type",
          "parameters": [
            {
              "id": "",
              "editor": "keyscene",
              "init": "GV2"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "smremotekeydual",
    "name": "YoLink Smart Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "keyscenedef",
        "name": "Last Command"
      },
      {
        "id": "GV1",
        "editor": "keyscenedef",
        "name": "Short Press Command Type"
      },
      {
        "id": "GV2",
        "editor": "keyscenedef",
        "name": "Long Press Command Type"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last key press"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        },
        {
          "id": "DFON",
          "name": "DFON"
        },
        {
          "id": "DFOF",
          "name": "DFOF"
        }
      ],
      "accepts": [
        {
          "id": "KEYPRESS",
          "name": "Short Press Command",
          "parameters": [
            {
              "id": "",
              "editor": "keyscene"
            }
          ]
        },
        {
          "id": "KEYLPRESS",
          "name": "Long Press Command",
          "parameters": [
            {
              "id": "",
              "editor": "keyscene"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "smremotekeysingle",
    "name": "YoLink Smart Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "keyscenedef",
        "name": "Last Command"
      },
      {
        "id": "GV1",
        "editor": "keyscenedef",
        "name": "Press Command"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last key press"
      }
    ],
    "cmds": {
      "sends": [
        {
          "id": "DON",
          "name": "DON"
        },
        {
          "id": "DOF",
          "name": "DOF"
        },
        {
          "id": "DFON",
          "name": "DFON"
        },
        {
          "id": "DFOF",
          "name": "DFOF"
        }
      ],
      "accepts": [
        {
          "id": "PRESSCMD",
          "name": "Press Command",
          "parameters": [
            {
              "id": "",
              "editor": "keyscene",
              "init": "GV1"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yothermostat",
    "name": "YoLink Thermostat (C)",
    "icon": "Thermostat",
    "properties": [
      {
        "id": "ST",
        "editor": "celsius",
        "name": "Temperature"
      },
      {
        "id": "CLIHCS",
        "editor": "ITSTATHCS",
        "name": "Running State"
      },
      {
        "id": "CLIHUM",
        "editor": "IHUMIDITY",
        "name": "Humidity"
      },
      {
        "id": "CLISPH",
        "editor": "celsius",
        "name": "Heat Setpoint"
      },
      {
        "id": "CLISPC",
        "editor": "celsius",
        "name": "Cool Setpoint"
      },
      {
        "id": "CLIMD",
        "editor": "ITSTATMODE",
        "name": "Mode"
      },
      {
        "id": "CLIFS",
        "editor": "ITSTATFAN",
        "name": "Fan Setting"
      },
      {
        "id": "CLISMD",
        "editor": "celsius",
        "name": "Schedule Mode"
      },
      {
        "id": "GV0",
        "editor": "celsius",
        "name": "Sensor 1 Temp"
      },
      {
        "id": "GV1",
        "editor": "celsius",
        "name": "Sensor 2 Temp"
      },
      {
        "id": "GV2",
        "editor": "IAUXHEAT",
        "name": "Aux Heat Running"
      },
      {
        "id": "GV3",
        "editor": "ISTAGE2",
        "name": "Stage 2 Running"
      },
      {
        "id": "CLIEMD",
        "editor": "IECOMODE",
        "name": "ECO Mode"
      },
      {
        "id": "GV18",
        "editor": "celsius",
        "name": "ECO Low Temp"
      },
      {
        "id": "GV19",
        "editor": "celsius",
        "name": "ECO High Temp"
      },
      {
        "id": "GV5",
        "editor": "IDRRUNNING",
        "name": "Demand Response Running"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last Update"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update"
        },
        {
          "id": "SETHEATTEMP",
          "name": "Set Heat Setpoint",
          "parameters": [
            {
              "id": "",
              "editor": "celsiusSet",
              "init": "CLISPH"
            }
          ]
        },
        {
          "id": "SETCOOLTEMP",
          "name": "Set Cool Setpoint",
          "parameters": [
            {
              "id": "",
              "editor": "celsiusSet",
              "init": "CLISPC"
            }
          ]
        },
        {
          "id": "SETMODE",
          "name": "Set Mode",
          "parameters": [
            {
              "id": "",
              "editor": "ITSTATMODE",
              "init": "CLIMD"
            }
          ]
        },
        {
          "id": "SETFAN",
          "name": "Set Fan",
          "parameters": [
            {
              "id": "",
              "editor": "ITSTATFAN",
              "init": "CLIFS"
            }
          ]
        },
        {
          "id": "SETSCHE",
          "name": "Set Schedule Mode",
          "parameters": [
            {
              "id": "",
              "editor": "ICLISMDDEG"
            }
          ]
        },
        {
          "id": "SETECO",
          "name": "Set ECO Mode",
          "parameters": [
            {
              "id": "ecomodeth",
              "editor": "IECOMODE",
              "init": "CLIEMD"
            },
            {
              "id": "ecoLowth",
              "editor": "ecoSet",
              "init": "GV18"
            },
            {
              "id": "ecoHighth",
              "editor": "ecoSet",
              "init": "GV19"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yothermostatf",
    "name": "YoLink Thermostat (F)",
    "icon": "Thermostat",
    "properties": [
      {
        "id": "ST",
        "editor": "farenheit",
        "name": "Temperature"
      },
      {
        "id": "CLIHCS",
        "editor": "ITSTATHCS",
        "name": "Running State"
      },
      {
        "id": "CLIHUM",
        "editor": "IHUMIDITY",
        "name": "Humidity"
      },
      {
        "id": "CLISPH",
        "editor": "farenheit",
        "name": "Heat Setpoint"
      },
      {
        "id": "CLISPC",
        "editor": "farenheit",
        "name": "Cool Setpoint"
      },
      {
        "id": "CLIMD",
        "editor": "ITSTATMODE",
        "name": "Mode"
      },
      {
        "id": "CLIFS",
        "editor": "ITSTATFAN",
        "name": "Fan Setting"
      },
      {
        "id": "CLISMD",
        "editor": "ICLISMDDEG",
        "name": "Schedule Mode"
      },
      {
        "id": "GV0",
        "editor": "farenheit",
        "name": "Sensor 1 Temp"
      },
      {
        "id": "GV1",
        "editor": "farenheit",
        "name": "Sensor 2 Temp"
      },
      {
        "id": "GV2",
        "editor": "IAUXHEAT",
        "name": "Aux Heat Running"
      },
      {
        "id": "GV3",
        "editor": "ISTAGE2",
        "name": "Stage 2 Running"
      },
      {
        "id": "CLIEMD",
        "editor": "IECOMODE",
        "name": "ECO Mode"
      },
      {
        "id": "GV18",
        "editor": "farenheit",
        "name": "ECO Low Temp"
      },
      {
        "id": "GV19",
        "editor": "farenheit",
        "name": "ECO High Temp"
      },
      {
        "id": "GV5",
        "editor": "IDRRUNNING",
        "name": "Demand Response Running"
      },
      {
        "id": "GV20",
        "editor": "suspendstate",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "status",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "unixtime",
        "name": "Last Update"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update"
        },
        {
          "id": "SETHEATTEMP",
          "name": "Set Heat Setpoint",
          "parameters": [
            {
              "id": "",
              "editor": "farenheitSet",
              "init": "CLISPH"
            }
          ]
        },
        {
          "id": "SETCOOLTEMP",
          "name": "Set Cool Setpoint",
          "parameters": [
            {
              "id": "",
              "editor": "farenheitSet",
              "init": "CLISPC"
            }
          ]
        },
        {
          "id": "SETMODE",
          "name": "Set Mode",
          "parameters": [
            {
              "id": "",
              "editor": "ITSTATMODE",
              "init": "CLIMD"
            }
          ]
        },
        {
          "id": "SETFAN",
          "name": "Set Fan",
          "parameters": [
            {
              "id": "",
              "editor": "ITSTATFAN",
              "init": "CLIFS"
            }
          ]
        },
        {
          "id": "SETSCHE",
          "name": "Set Schedule Mode",
          "parameters": [
            {
              "id": "",
              "editor": "ICLISMDDEG"
            }
          ]
        },
        {
          "id": "SETECO",
          "name": "Set ECO Mode",
          "parameters": [
            {
              "id": "ecomodeth",
              "editor": "IECOMODE",
              "init": "CLIEMD"
            },
            {
              "id": "ecoLowth",
              "editor": "ecoSetF",
              "init": "GV18"
            },
            {
              "id": "ecoHighth",
              "editor": "ecoSetF",
              "init": "GV19"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yothermprop",
    "name": "Thermostat Properties (C)",
    "icon": "Thermostat",
    "properties": [
      {
        "id": "GV6",
        "editor": "IMINRUNTIME",
        "name": "Min Runtime"
      },
      {
        "id": "GV7",
        "editor": "celsius",
        "name": "Cool Limit"
      },
      {
        "id": "GV8",
        "editor": "celsius",
        "name": "Heat Limit"
      },
      {
        "id": "GV9",
        "editor": "IMUTE",
        "name": "Mute"
      },
      {
        "id": "GV10",
        "editor": "IMENULOCK",
        "name": "Menu Lock"
      },
      {
        "id": "GV11",
        "editor": "IMINRUNTIME",
        "name": "Aux Standby"
      },
      {
        "id": "GV12",
        "editor": "IHOURS",
        "name": "Aux Max Span"
      },
      {
        "id": "GV13",
        "editor": "celsius",
        "name": "Aux Threshold"
      },
      {
        "id": "GV14",
        "editor": "IMINRUNTIME",
        "name": "Stage2 Standby"
      },
      {
        "id": "GV15",
        "editor": "IHOURS",
        "name": "Stage2 Max Span"
      },
      {
        "id": "GV16",
        "editor": "celsius",
        "name": "Stage2 Threshold"
      },
      {
        "id": "GV17",
        "editor": "IMASTERSRC",
        "name": "Master Source"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update"
        },
        {
          "id": "SETMINRUNTIME",
          "name": "Set Min Runtime",
          "parameters": [
            {
              "id": "",
              "editor": "IMINRUNTIME",
              "init": "GV6"
            }
          ]
        },
        {
          "id": "SETCOOLLIMIT",
          "name": "Set Cool Limit",
          "parameters": [
            {
              "id": "",
              "editor": "celsiusSet",
              "init": "GV7"
            }
          ]
        },
        {
          "id": "SETHEATLIMIT",
          "name": "Set Heat Limit",
          "parameters": [
            {
              "id": "",
              "editor": "celsiusSet",
              "init": "GV8"
            }
          ]
        },
        {
          "id": "SETMUTE",
          "name": "Set Mute",
          "parameters": [
            {
              "id": "",
              "editor": "IMUTE",
              "init": "GV9"
            }
          ]
        },
        {
          "id": "SETMENULOCK",
          "name": "Set Menu Lock",
          "parameters": [
            {
              "id": "",
              "editor": "IMENULOCK",
              "init": "GV10"
            }
          ]
        },
        {
          "id": "SETMASTER",
          "name": "Set Master Source",
          "parameters": [
            {
              "id": "",
              "editor": "IMASTERSRC",
              "init": "GV17"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  },
  {
    "id": "yothermpropf",
    "name": "Thermostat Properties (F)",
    "icon": "Thermostat",
    "properties": [
      {
        "id": "GV6",
        "editor": "IMINRUNTIME",
        "name": "Min Runtime"
      },
      {
        "id": "GV7",
        "editor": "farenheit",
        "name": "Cool Limit"
      },
      {
        "id": "GV8",
        "editor": "farenheit",
        "name": "Heat Limit"
      },
      {
        "id": "GV9",
        "editor": "IMUTE",
        "name": "Mute"
      },
      {
        "id": "GV10",
        "editor": "IMENULOCK",
        "name": "Menu Lock"
      },
      {
        "id": "GV11",
        "editor": "IMINRUNTIME",
        "name": "Aux Standby"
      },
      {
        "id": "GV12",
        "editor": "IHOURS",
        "name": "Aux Max Span"
      },
      {
        "id": "GV13",
        "editor": "farenheit",
        "name": "Aux Threshold"
      },
      {
        "id": "GV14",
        "editor": "IMINRUNTIME",
        "name": "Stage2 Standby"
      },
      {
        "id": "GV15",
        "editor": "IHOURS",
        "name": "Stage2 Max Span"
      },
      {
        "id": "GV16",
        "editor": "farenheit",
        "name": "Stage2 Threshold"
      },
      {
        "id": "GV17",
        "editor": "IMASTERSRC",
        "name": "Master Source"
      }
    ],
    "cmds": {
      "sends": [],
      "accepts": [
        {
          "id": "UPDATE",
          "name": "Update"
        },
        {
          "id": "SETMINRUNTIME",
          "name": "Set Min Runtime",
          "parameters": [
            {
              "id": "",
              "editor": "IMINRUNTIME",
              "init": "GV6"
            }
          ]
        },
        {
          "id": "SETCOOLLIMIT",
          "name": "Set Cool Limit",
          "parameters": [
            {
              "id": "",
              "editor": "farenheitSet",
              "init": "GV7"
            }
          ]
        },
        {
          "id": "SETHEATLIMIT",
          "name": "Set Heat Limit",
          "parameters": [
            {
              "id": "",
              "editor": "farenheitSet",
              "init": "GV8"
            }
          ]
        },
        {
          "id": "SETMUTE",
          "name": "Set Mute",
          "parameters": [
            {
              "id": "",
              "editor": "IMUTE",
              "init": "GV9"
            }
          ]
        },
        {
          "id": "SETMENULOCK",
          "name": "Set Menu Lock",
          "parameters": [
            {
              "id": "",
              "editor": "IMENULOCK",
              "init": "GV10"
            }
          ]
        },
        {
          "id": "SETMASTER",
          "name": "Set Master Source",
          "parameters": [
            {
              "id": "",
              "editor": "IMASTERSRC",
              "init": "GV17"
            }
          ]
        }
      ]
    },
    "links": {
      "ctl": [],
      "rsp": []
    }
  }
]
