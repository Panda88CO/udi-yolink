"""
Pre-generated dynamic profile structures for IoX/PG3.
Generated in code from profile directory.
"""

DYNAMIC_EDITORS = [
  {
    "id": "STATUS",
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
    "id": "CONNECT",
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
    "id": "SWSTATE",
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
    "id": "SWCTRL",
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
    "id": "WATT",
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
    "id": "ENERGY",
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
    "id": "WATERLEVEL",
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
    "id": "DELAY",
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
    "id": "DELAYMIN",
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
    "id": "CELSIUS",
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
    "id": "CELSIUSSET",
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
    "id": "FARENHEIT",
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
    "id": "FARENHEITSET",
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
    "id": "HUMIDITY",
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
    "id": "BATLEVEL",
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
    "id": "DOORSTATE",
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
    "id": "MOTIONSTATE",
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
    "id": "WATERSTATE",
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
    "id": "MANSTATE",
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
    "id": "MANCTRL",
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
    "id": "USBSTATE",
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
    "id": "USBCTRL",
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
    "id": "OUTLETNBR",
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
    "id": "VIBRASTATE",
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
    "id": "VOLUME",
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
    "id": "MUTE",
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
    "id": "MUTESET",
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
    "id": "REPEAT",
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
    "id": "BEEPEN",
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
    "id": "BEEPENSET",
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
    "id": "TONE",
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
    "id": "TONESET",
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
    "id": "MESSAGES",
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
    "id": "LOCKSTATE",
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
    "id": "LOCK",
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
    "id": "LOCKACTION",
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
    "id": "LOCKSOURCE",
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
    "id": "DOORBELL",
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
    "id": "DIMLVL",
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
    "id": "NBRCODES",
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
    "id": "CMDSTATUS",
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
    "id": "IRCMDSTATUS",
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
    "id": "POWERALERT",
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
    "id": "POWERSTATE",
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
    "id": "ALERTSTATE",
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
    "id": "POWERED",
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
    "id": "REMOTETYPE",
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
    "id": "PFAMUTE",
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
    "id": "KEYSCENEDEF",
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
    "id": "KEYSCENE",
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
    "id": "SIRENSTATE",
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
    "id": "SIRENDURATION",
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
    "id": "SIRENBATLEVEL",
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
    "id": "SIRENCTRL",
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
    "id": "SOUNDLEVEL",
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
    "id": "CMDSETTING",
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
    "id": "SUSPENDSTATE",
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
    "id": "ALARM",
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
    "id": "DEVICEALERT",
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
    "id": "SMOKEALERT",
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
    "id": "COALERT",
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
    "id": "TEMPALERT",
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
    "id": "BATTERYALERT",
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
    "id": "SELFCHECKSTATE",
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
    "id": "OUTPORT",
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
    "id": "SCHACTIVE",
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
    "id": "SCHACTIVEI",
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
    "id": "SCHINDEX",
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
    "id": "SCHCOUNT",
    "ranges": [
      {
        "uom": "70",
        "min": "0",
        "max": "20"
      }
    ]
  },
  {
    "id": "SCHINDEXS",
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
    "id": "STHOUR",
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
    "id": "STMIN",
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
    "id": "STSEC",
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
    "id": "STHOURI",
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
    "id": "STMINI",
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
    "id": "STSECI",
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
    "id": "BINDAYS",
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
    "id": "UNIXTIME",
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
    "id": "READY",
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
    "id": "LEAKLIMIT",
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
    "id": "LITER",
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
    "id": "LITERSET",
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
    "id": "GALLON",
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
    "id": "GALLONSET",
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
    "id": "FLOW",
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
    "id": "ENABLE",
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
    "id": "ENABLESET",
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
    "id": "WATERRUN",
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
    "id": "MINUTES",
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
    "id": "MINUTESSET",
    "ranges": [
      {
        "uom": "44",
        "min": "0",
        "max": "1440"
      }
    ]
  },
  {
    "id": "COUNT",
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
    "id": "CONDUCTIVITY",
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
    "id": "STARTSTOP",
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
    "id": "SPRINKLERMETHOD",
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
    "id": "WAMOUNT",
    "ranges": [
      {
        "uom": "70",
        "min": "0",
        "max": "1440"
      }
    ]
  },
  {
    "id": "RUNNINGVALUE",
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
    "id": "RUNNINGMODE",
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
    "id": "WATERMODE",
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
    "id": "NOWATERALARM",
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
    "id": "BEEPING",
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
    "id": "LEAKOPMODE",
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
    "id": "SENSITIVITY",
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
    "id": "MOVEALERT",
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
    "id": "FREEZEALERT",
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
    "id": "SENSORERROR",
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
    "id": "REMINDER",
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
    "id": "LEDCTRL",
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
    "id": "ECOSET",
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
    "id": "ECOSETF",
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
    "id": "SETUP",
    "name": "YoLink Setup",
    "icon": "GenericCtrl",
    "properties": [
      {
        "id": "ST",
        "editor": "CONNECT",
        "name": "Node Server"
      },
      {
        "id": "GV1",
        "editor": "READY",
        "name": "Status"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
    "id": "YOSCHEDULESEC",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "STSEC",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "STSEC",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "STSECI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "STSECI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOMSCHEDULESEC",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "NBRCODES",
        "name": "Selected code/port"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "STSEC",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "STSEC",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV12"
            },
            {
              "id": "index",
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "STSECI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "STSECI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOIRSCHEDULESEC",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "NBRCODES",
        "name": "Selected code/port"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "STSEC",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "STSEC",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "NBRCODES",
              "init": "GV12"
            },
            {
              "id": "index",
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "STSECI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "STSECI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOMOUTLETSCHSEC",
    "name": "YOMOUTLETSCHSEC",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "OUTPORT",
        "name": "Selected code/port"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "STSEC",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "STSEC",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "OUTPORT",
              "init": "GV12"
            },
            {
              "id": "index",
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "STSECI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "STSECI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOIRSCHEDULE",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "NBRCODES",
        "name": "Selected code/port"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOMSCHEDULE",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "OUTPORT",
        "name": "Selected code/port"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOSCHEDULE",
    "name": "Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOSPRINKLERSCHEDULESEC",
    "name": "Sprinkler Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "STSEC",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "STSEC",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "STSECI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "STSECI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOSPRINKLERSCHEDULE",
    "name": "Sprinkler Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOWMVLSCHEDULESEC",
    "name": "Water Meter Valve Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "COUNT",
        "name": "Reserved"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "STSEC",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "STSEC",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "STSECI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "STSECI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOWMVLSCHEDULE",
    "name": "Water Meter Valve Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "COUNT",
        "name": "Reserved"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOWMLKSCHEDULESEC",
    "name": "Water Meter Leak Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "COUNT",
        "name": "GV12"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "STSEC",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "GV17"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "STSEC",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "LLIMIT",
              "editor": "LEAKLIMIT",
              "init": "GV12"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "STSECI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "STSECI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOWMLKSCHEDULE",
    "name": "Water Meter Leak Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "COUNT",
        "name": "GV12"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "GV17"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "LLIMIT",
              "editor": "LEAKLIMIT",
              "init": "GV12"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOWMSCHEDULESEC",
    "name": "Water Meter Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "COUNT",
        "name": "Leak Limit"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "STSEC",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "STSEC",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "LLIMIT",
              "editor": "LEAKLIMIT",
              "init": "GV12"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "onS",
              "editor": "STSECI",
              "init": "GV21"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "offS",
              "editor": "STSECI",
              "init": "GV22"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOWMSCHEDULE",
    "name": "Water Meter Schedules",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "GV12",
        "editor": "COUNT",
        "name": "Leak Limit"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV23",
        "editor": "SCHCOUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
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
              "id": "LOOKUPSCH",
              "editor": "SCHINDEXS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
              "init": "GV14"
            },
            {
              "id": "LLIMIT",
              "editor": "LEAKLIMIT",
              "init": "GV12"
            },
            {
              "id": "onH",
              "editor": "STHOURI",
              "init": "GV15"
            },
            {
              "id": "onM",
              "editor": "STMINI",
              "init": "GV16"
            },
            {
              "id": "offH",
              "editor": "STHOURI",
              "init": "GV17"
            },
            {
              "id": "offM",
              "editor": "STMINI",
              "init": "GV18"
            },
            {
              "id": "bindays",
              "editor": "BINDAYS",
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
              "editor": "SCHINDEXS",
              "init": "GV13"
            },
            {
              "id": "active",
              "editor": "SCHACTIVEI",
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
    "id": "YOSWITCHPWR",
    "name": "YOSWITCHPWR",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "SWSTATE",
        "name": "Switch State"
      },
      {
        "id": "GV0",
        "editor": "SWSTATE",
        "name": "Switch State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "DELAY",
        "name": "On Delay (min)"
      },
      {
        "id": "GV2",
        "editor": "DELAY",
        "name": "Off Delay (min)"
      },
      {
        "id": "GV3",
        "editor": "WATT",
        "name": "Watt"
      },
      {
        "id": "GV4",
        "editor": "ENERGY",
        "name": "Energy"
      },
      {
        "id": "GV5",
        "editor": "POWERALERT",
        "name": "Overload Alert"
      },
      {
        "id": "GV6",
        "editor": "POWERALERT",
        "name": "High Load Alert"
      },
      {
        "id": "GV7",
        "editor": "POWERALERT",
        "name": "Low Load Alert"
      },
      {
        "id": "GV8",
        "editor": "POWERALERT",
        "name": "High Temperature Alert"
      },
      {
        "id": "GV9",
        "editor": "LED",
        "name": "Led State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SWCTRL",
              "editor": "SWCTRL",
              "init": "GV0"
            }
          ]
        },
        {
          "id": "SETATTRIB",
          "name": "LED control",
          "parameters": [
            {
              "id": "SETATTRIB",
              "editor": "LEDCTRL",
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
              "editor": "DELAYMIN",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "DELAYMIN",
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
    "id": "YOSWITCH",
    "name": "YoLink Switch",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "SWSTATE",
        "name": "Switch State"
      },
      {
        "id": "GV0",
        "editor": "SWSTATE",
        "name": "Switch State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "DELAY",
        "name": "On Delay (min)"
      },
      {
        "id": "GV2",
        "editor": "DELAY",
        "name": "Off Delay (min)"
      },
      {
        "id": "GV5",
        "editor": "POWERALERT",
        "name": "Overload Alert"
      },
      {
        "id": "GV6",
        "editor": "POWERALERT",
        "name": "High Load Alert"
      },
      {
        "id": "GV7",
        "editor": "POWERALERT",
        "name": "Low Load Alert"
      },
      {
        "id": "GV8",
        "editor": "POWERALERT",
        "name": "High Temperature Alert"
      },
      {
        "id": "GV9",
        "editor": "LED",
        "name": "Led State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SWCTRL",
              "editor": "SWCTRL",
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
              "editor": "DELAYMIN",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "DELAYMIN",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "SETATTRIB",
          "name": "LED control",
          "parameters": [
            {
              "id": "SETATTRIB",
              "editor": "LEDCTRL",
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
    "id": "YOSWITCHBAT",
    "name": "YoLink Battery Switch",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "SWSTATE",
        "name": "Switch State"
      },
      {
        "id": "GV0",
        "editor": "SWSTATE",
        "name": "Switch State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "DELAY",
        "name": "On Delay (min)"
      },
      {
        "id": "GV2",
        "editor": "DELAY",
        "name": "Off Delay (min)"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV9",
        "editor": "LED",
        "name": "Led State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SWCTRL",
              "editor": "SWCTRL",
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
              "editor": "DELAYMIN",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "DELAYMIN",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "SETATTRIB",
          "name": "LED control",
          "parameters": [
            {
              "id": "SETATTRIB",
              "editor": "LEDCTRL",
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
    "id": "YODIMMER",
    "name": "YoLink Dimmer",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "DIMLVL",
        "name": "Dim Setting"
      },
      {
        "id": "GV0",
        "editor": "SWSTATE",
        "name": "Switch State"
      },
      {
        "id": "GV1",
        "editor": "DELAY",
        "name": "On Delay"
      },
      {
        "id": "GV2",
        "editor": "DELAY",
        "name": "Off Delay"
      },
      {
        "id": "GV3",
        "editor": "DIMLVL",
        "name": "Light Level"
      },
      {
        "id": "GV4",
        "editor": "DIMLVL",
        "name": "Light Down Level"
      },
      {
        "id": "GV5",
        "editor": "DIMLVL",
        "name": "Light Up Level"
      },
      {
        "id": "GV9",
        "editor": "LED",
        "name": "LED Status"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "STSEC",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "STSEC",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
        "name": "Active Days"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "DIMLVL",
              "editor": "DIMLVL",
              "init": "GV3"
            }
          ]
        },
        {
          "id": "DIMDOWN",
          "name": "Light Down Level (%)",
          "parameters": [
            {
              "id": "DIMDOWN",
              "editor": "DIMLVL",
              "init": "GV4"
            }
          ]
        },
        {
          "id": "DIMUP",
          "name": "Light Up Level (%)",
          "parameters": [
            {
              "id": "DIMUP",
              "editor": "DIMLVL",
              "init": "GV5"
            }
          ]
        },
        {
          "id": "SWCTRL",
          "name": "Switch control",
          "parameters": [
            {
              "id": "SWCTRL",
              "editor": "SWCTRL",
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
              "editor": "DELAYMIN",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "DELAYMIN",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "SETATTRIB",
          "name": "LED control",
          "parameters": [
            {
              "id": "SETATTRIB",
              "editor": "LEDCTRL",
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
    "id": "YOOUTLET",
    "name": "YoLink Outlet",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "SWSTATE",
        "name": "Outlet State"
      },
      {
        "id": "GV0",
        "editor": "SWSTATE",
        "name": "Outlet State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "DELAY",
        "name": "On Delay Remaining"
      },
      {
        "id": "GV2",
        "editor": "DELAY",
        "name": "Off Delay Remaining"
      },
      {
        "id": "GV5",
        "editor": "POWERALERT",
        "name": "Overload Alert"
      },
      {
        "id": "GV6",
        "editor": "POWERALERT",
        "name": "High Load Alert"
      },
      {
        "id": "GV7",
        "editor": "POWERALERT",
        "name": "Low Load Alert"
      },
      {
        "id": "GV8",
        "editor": "POWERALERT",
        "name": "High Temperature Alert"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SWCTRL",
              "editor": "SWCTRL",
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
              "editor": "DELAYMIN",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "DELAYMIN",
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
    "id": "YOOUTLETPWR",
    "name": "YoLink Outlet",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "SWSTATE",
        "name": "Outlet State"
      },
      {
        "id": "GV0",
        "editor": "SWSTATE",
        "name": "Outlet State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "DELAY",
        "name": "On Delay Remaining"
      },
      {
        "id": "GV2",
        "editor": "DELAY",
        "name": "Off Delay Remaining"
      },
      {
        "id": "GV3",
        "editor": "WATT",
        "name": "Watt"
      },
      {
        "id": "GV4",
        "editor": "ENERGY",
        "name": "Energy"
      },
      {
        "id": "GV5",
        "editor": "POWERALERT",
        "name": "Overload Alert"
      },
      {
        "id": "GV6",
        "editor": "POWERALERT",
        "name": "High Load Alert"
      },
      {
        "id": "GV7",
        "editor": "POWERALERT",
        "name": "Low Load Alert"
      },
      {
        "id": "GV8",
        "editor": "POWERALERT",
        "name": "High Temperature Alert"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SWCTRL",
              "editor": "SWCTRL",
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
              "editor": "DELAYMIN",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "DELAYMIN",
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
    "id": "YOMULTIOUT",
    "name": "YoLink Outlet",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "STATUS",
        "name": "Node Server Status"
      },
      {
        "id": "GV12",
        "editor": "OUTPORT",
        "name": "Port"
      },
      {
        "id": "GV13",
        "editor": "SCHINDEX",
        "name": "Schedule Index"
      },
      {
        "id": "GV14",
        "editor": "SCHACTIVE",
        "name": "Activated"
      },
      {
        "id": "GV15",
        "editor": "STHOUR",
        "name": "On Hour"
      },
      {
        "id": "GV16",
        "editor": "STMIN",
        "name": "On Minute"
      },
      {
        "id": "GV21",
        "editor": "STSEC",
        "name": "On Sec"
      },
      {
        "id": "GV17",
        "editor": "STHOUR",
        "name": "Off Hour"
      },
      {
        "id": "GV18",
        "editor": "STMIN",
        "name": "Off Minute"
      },
      {
        "id": "GV22",
        "editor": "STSEC",
        "name": "Off Sec"
      },
      {
        "id": "GV19",
        "editor": "BINDAYS",
        "name": "Active Days"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
    "id": "YOSUBOUT",
    "name": "YoLink subOutlet",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "SWSTATE",
        "name": "Outlet State"
      },
      {
        "id": "GV0",
        "editor": "SWSTATE",
        "name": "Outlet State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "DELAY",
        "name": "On Delay Remaining"
      },
      {
        "id": "GV2",
        "editor": "DELAY",
        "name": "Off Delay Remaining"
      },
      {
        "id": "GV4",
        "editor": "OUTLETNBR",
        "name": "Outlet"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
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
              "id": "SWCTRL",
              "editor": "SWCTRL",
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
              "editor": "DELAYMIN",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "DELAYMIN",
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
    "id": "YOSUBUSB",
    "name": "YoLink USB Ports",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "USBSTATE",
        "name": "USB Power State"
      },
      {
        "id": "GV0",
        "editor": "USBSTATE",
        "name": "USB Power"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
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
              "id": "USBCTRL",
              "editor": "USBCTRL",
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
    "id": "YOMANIPU",
    "name": "YoLink Manipulator",
    "icon": "GenericCtrl",
    "properties": [
      {
        "id": "ST",
        "editor": "MANSTATE",
        "name": "Manipulator State"
      },
      {
        "id": "GV0",
        "editor": "MANSTATE",
        "name": "Manipulator State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "DELAY",
        "name": "On Delay Remaining"
      },
      {
        "id": "GV2",
        "editor": "DELAY",
        "name": "Off Delay Remaining"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "MANCTRL",
              "editor": "MANCTRL",
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
              "editor": "DELAYMIN",
              "init": "GV1"
            },
            {
              "id": "offdelay",
              "editor": "DELAYMIN",
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
    "id": "YOSPRINKLER",
    "name": "YOSPRINKLER",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Current State"
      },
      {
        "id": "GV0",
        "editor": "MANSTATE",
        "name": "GV0"
      },
      {
        "id": "GV1",
        "editor": "LITER",
        "name": "Current No Water Alarm"
      },
      {
        "id": "GV10",
        "editor": "LITER",
        "name": "Time for Latest operation Update"
      },
      {
        "id": "GV2",
        "editor": "LITER",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV3",
        "editor": "MINUTES",
        "name": "GV3"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "Latest Operation"
      },
      {
        "id": "GV6",
        "editor": "ALARM",
        "name": "GV6"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Latest Water Method"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Latest Water Amount target"
      },
      {
        "id": "GV9",
        "editor": "ALARM",
        "name": "Latest Water Alarm"
      },
      {
        "id": "GV11",
        "editor": "ALARM",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "ALARM",
        "name": "Time Delay"
      },
      {
        "id": "GV13",
        "editor": "ALARM",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "ALARM",
        "name": "GV14"
      },
      {
        "id": "GV22",
        "editor": "LITER",
        "name": "Off Sec"
      },
      {
        "id": "GV23",
        "editor": "COUNT",
        "name": "Total Schedules"
      },
      {
        "id": "GV24",
        "editor": "MINUTES",
        "name": "GV24"
      },
      {
        "id": "GV25",
        "editor": "ENABLE",
        "name": "GV25"
      },
      {
        "id": "GV26",
        "editor": "ENABLE",
        "name": "GV26"
      },
      {
        "id": "GV27",
        "editor": "ENABLE",
        "name": "GV27"
      },
      {
        "id": "GV28",
        "editor": "ENABLE",
        "name": "GV28"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "editor": "STARTSTOP"
            },
            {
              "id": "watermode",
              "editor": "WATERMODE"
            }
          ]
        },
        {
          "id": "SETATTRIB",
          "name": "SETATTRIB",
          "parameters": [
            {
              "id": "LLIMIT",
              "editor": "LEAKLIMIT"
            },
            {
              "id": "LOFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORLIMIT",
              "editor": "LEAKLIMIT"
            },
            {
              "id": "OROFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORTLIMIT",
              "editor": "MINUTESSET"
            },
            {
              "id": "ORTOFF",
              "editor": "ENABLESET"
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
    "id": "YOWATERMETERCTRL",
    "name": "YoLink Water Meter Controller",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Water Running"
      },
      {
        "id": "GV0",
        "editor": "MANSTATE",
        "name": "Valve State"
      },
      {
        "id": "GV1",
        "editor": "LITER",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "LITER",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "LITER",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "MINUTES",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Water Temperature"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "Leak Alarm"
      },
      {
        "id": "GV6",
        "editor": "ALARM",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Nbr Times Overrun 24H Alarm"
      },
      {
        "id": "GV9",
        "editor": "ALARM",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV11",
        "editor": "ALARM",
        "name": "Open Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "ALARM",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV13",
        "editor": "ALARM",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV14",
        "editor": "ALARM",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV22",
        "editor": "LITER",
        "name": "Overrun Amount 24H Limit"
      },
      {
        "id": "GV23",
        "editor": "COUNT",
        "name": "Overrun Duration Once Limit"
      },
      {
        "id": "GV24",
        "editor": "MINUTES",
        "name": "Overrun Count 24H Limit"
      },
      {
        "id": "GV25",
        "editor": "ENABLE",
        "name": "Leak Auto Close"
      },
      {
        "id": "GV26",
        "editor": "ENABLE",
        "name": "Overrun Amount Auto Close"
      },
      {
        "id": "GV27",
        "editor": "ENABLE",
        "name": "Overrun Duration Auto Close"
      },
      {
        "id": "GV28",
        "editor": "ENABLE",
        "name": "Overrun Times Auto Close"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "editor": "LEAKLIMIT"
            },
            {
              "id": "LOFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORLIMIT",
              "editor": "LEAKLIMIT"
            },
            {
              "id": "OROFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORTLIMIT",
              "editor": "MINUTESSET"
            },
            {
              "id": "ORTOFF",
              "editor": "ENABLESET"
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
    "id": "YOWATERMETERCTRLF",
    "name": "YOWATERMETERCTRLF",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Water Running"
      },
      {
        "id": "GV0",
        "editor": "MANSTATE",
        "name": "Valve State"
      },
      {
        "id": "GV1",
        "editor": "GALLON",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "GALLON",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "GALLON",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "MINUTES",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "FARENHEIT",
        "name": "Water Temperature"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "Leak Alarm"
      },
      {
        "id": "GV6",
        "editor": "ALARM",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Nbr Times Overrun 24H Alarm"
      },
      {
        "id": "GV9",
        "editor": "ALARM",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV11",
        "editor": "ALARM",
        "name": "Open Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "ALARM",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV13",
        "editor": "ALARM",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV14",
        "editor": "ALARM",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV22",
        "editor": "GALLON",
        "name": "Overrun Amount 24H Limit"
      },
      {
        "id": "GV23",
        "editor": "COUNT",
        "name": "Overrun Duration Once Limit"
      },
      {
        "id": "GV24",
        "editor": "MINUTES",
        "name": "Overrun Count 24H Limit"
      },
      {
        "id": "GV25",
        "editor": "ENABLE",
        "name": "Leak Auto Close"
      },
      {
        "id": "GV26",
        "editor": "ENABLE",
        "name": "Overrun Amount Auto Close"
      },
      {
        "id": "GV27",
        "editor": "ENABLE",
        "name": "Overrun Duration Auto Close"
      },
      {
        "id": "GV28",
        "editor": "ENABLE",
        "name": "Overrun Times Auto Close"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "editor": "LEAKLIMIT"
            },
            {
              "id": "LOFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORLIMIT",
              "editor": "LEAKLIMIT"
            },
            {
              "id": "OROFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORTLIMIT",
              "editor": "MINUTESSET"
            },
            {
              "id": "ORTOFF",
              "editor": "ENABLESET"
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
    "id": "YOWATERMETERMULTI",
    "name": "YoLink Water Meter Multi Controller",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Water Running"
      },
      {
        "id": "GV1",
        "editor": "COUNT",
        "name": "Water Meter Total"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "Leak Alarm"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
    "id": "YOWATERMETERMULTIF",
    "name": "YOWATERMETERMULTIF",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Water Running"
      },
      {
        "id": "GV1",
        "editor": "COUNT",
        "name": "Water Meter Total"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "Leak Alarm"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
    "id": "YOWATERMETERSUB",
    "name": "YoLink Water Meter Sub Controller",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Water Running"
      },
      {
        "id": "GV0",
        "editor": "MANSTATE",
        "name": "Valve State"
      },
      {
        "id": "GV1",
        "editor": "LITER",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "LITER",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "LITER",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "MINUTES",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "GV6",
        "editor": "ALARM",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Nbr Times Overrun 24H Alarm"
      },
      {
        "id": "GV9",
        "editor": "ALARM",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "ALARM",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV22",
        "editor": "LITER",
        "name": "Overrun Amount 24H Limit"
      },
      {
        "id": "GV23",
        "editor": "COUNT",
        "name": "Overrun Duration Once Limit"
      },
      {
        "id": "GV24",
        "editor": "MINUTES",
        "name": "Overrun Count 24H Limit"
      },
      {
        "id": "GV25",
        "editor": "ENABLE",
        "name": "Leak Auto Close"
      },
      {
        "id": "GV26",
        "editor": "ENABLE",
        "name": "Overrun Amount Auto Close"
      },
      {
        "id": "GV27",
        "editor": "ENABLE",
        "name": "Overrun Duration Auto Close"
      },
      {
        "id": "GV28",
        "editor": "ENABLE",
        "name": "Overrun Times Auto Close"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
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
              "editor": "LITERSET"
            },
            {
              "id": "LOFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORLIMIT",
              "editor": "LITERSET"
            },
            {
              "id": "OROFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORTLIMIT",
              "editor": "MINUTESSET"
            },
            {
              "id": "ORTOFF",
              "editor": "ENABLESET"
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
    "id": "YOWATERMETERSUBL",
    "name": "YoLink Water Meter Sub Controller",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Water Running"
      },
      {
        "id": "GV0",
        "editor": "MANSTATE",
        "name": "Valve State"
      },
      {
        "id": "GV1",
        "editor": "LITER",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "LITER",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "LITER",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "MINUTES",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "GV6",
        "editor": "ALARM",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Nbr Times Overrun 24H Alarm"
      },
      {
        "id": "GV9",
        "editor": "ALARM",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "ALARM",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV22",
        "editor": "LITER",
        "name": "Overrun Amount 24H Limit"
      },
      {
        "id": "GV23",
        "editor": "COUNT",
        "name": "Overrun Duration Once Limit"
      },
      {
        "id": "GV24",
        "editor": "MINUTES",
        "name": "Overrun Count 24H Limit"
      },
      {
        "id": "GV25",
        "editor": "ENABLE",
        "name": "Leak Auto Close"
      },
      {
        "id": "GV26",
        "editor": "ENABLE",
        "name": "Overrun Amount Auto Close"
      },
      {
        "id": "GV27",
        "editor": "ENABLE",
        "name": "Overrun Duration Auto Close"
      },
      {
        "id": "GV28",
        "editor": "ENABLE",
        "name": "Overrun Times Auto Close"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
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
              "editor": "LITERSET"
            },
            {
              "id": "LOFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORLIMIT",
              "editor": "LITERSET"
            },
            {
              "id": "OROFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORTLIMIT",
              "editor": "MINUTESSET"
            },
            {
              "id": "ORTOFF",
              "editor": "ENABLESET"
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
    "id": "YOWATERMETERSUBG",
    "name": "YoLink Water Meter Sub Controller",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Water Running"
      },
      {
        "id": "GV0",
        "editor": "MANSTATE",
        "name": "Valve State"
      },
      {
        "id": "GV1",
        "editor": "GALLON",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "GALLON",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "GALLON",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "MINUTES",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "GV6",
        "editor": "ALARM",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Nbr Times Overrun 24H Alarm"
      },
      {
        "id": "GV9",
        "editor": "ALARM",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "ALARM",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV22",
        "editor": "GALLON",
        "name": "Overrun Amount 24H Limit"
      },
      {
        "id": "GV23",
        "editor": "MINUTES",
        "name": "Overrun Duration Once Limit"
      },
      {
        "id": "GV24",
        "editor": "COUNT",
        "name": "Overrun Count 24H Limit"
      },
      {
        "id": "GV25",
        "editor": "ENABLE",
        "name": "Leak Auto Close"
      },
      {
        "id": "GV26",
        "editor": "ENABLE",
        "name": "Overrun Amount Auto Close"
      },
      {
        "id": "GV27",
        "editor": "ENABLE",
        "name": "Overrun Duration Auto Close"
      },
      {
        "id": "GV28",
        "editor": "ENABLE",
        "name": "Overrun Times Auto Close"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
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
              "editor": "GALLONSET"
            },
            {
              "id": "LOFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORLIMIT",
              "editor": "GALLONSET"
            },
            {
              "id": "OROFF",
              "editor": "ENABLESET"
            },
            {
              "id": "ORTLIMIT",
              "editor": "MINUTESSET"
            },
            {
              "id": "ORTOFF",
              "editor": "ENABLESET"
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
    "id": "YOWATERMETERONLY",
    "name": "YoLink Water Meter",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Water Running"
      },
      {
        "id": "GV1",
        "editor": "FLOW",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "FLOW",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "FLOW",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "MINUTES",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Water Temperature"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "Leak Alarm"
      },
      {
        "id": "GV6",
        "editor": "ALARM",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV9",
        "editor": "ALARM",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV11",
        "editor": "ALARM",
        "name": "Open Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "ALARM",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV13",
        "editor": "ALARM",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV14",
        "editor": "ALARM",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV16",
        "editor": "MINUTES",
        "name": "Overrun time Limit"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "editor": "LEAKLIMIT"
            },
            {
              "id": "ORLIMIT",
              "editor": "LEAKLIMIT"
            },
            {
              "id": "ORTLIMIT",
              "editor": "MINUTESSET"
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
    "id": "YOWATERMETERONLYF",
    "name": "YoLink Water Meter",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Water Running"
      },
      {
        "id": "GV1",
        "editor": "FLOW",
        "name": "Water Meter Total"
      },
      {
        "id": "GV10",
        "editor": "FLOW",
        "name": "Water Meter Day Use"
      },
      {
        "id": "GV2",
        "editor": "FLOW",
        "name": "Water Meter Recent Use"
      },
      {
        "id": "GV3",
        "editor": "MINUTES",
        "name": "Water Meter Recent Duration"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "FARENHEIT",
        "name": "Water Temperature"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "Leak Alarm"
      },
      {
        "id": "GV6",
        "editor": "ALARM",
        "name": "Amount Overrun Alarm"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Duration Overrun Alarm"
      },
      {
        "id": "GV9",
        "editor": "ALARM",
        "name": "Reminder Alarm"
      },
      {
        "id": "GV11",
        "editor": "ALARM",
        "name": "Open Reminder Alarm"
      },
      {
        "id": "GV12",
        "editor": "ALARM",
        "name": "Valve Error Alarm"
      },
      {
        "id": "GV13",
        "editor": "ALARM",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV14",
        "editor": "ALARM",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV16",
        "editor": "MINUTES",
        "name": "Overrun time Limit"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "editor": "LEAKLIMIT"
            },
            {
              "id": "ORLIMIT",
              "editor": "LEAKLIMIT"
            },
            {
              "id": "ORTLIMIT",
              "editor": "MINUTESSET"
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
    "id": "YOSPRINKLERV2",
    "name": "YoLink Smart Sprinkler V2",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERRUN",
        "name": "Current State"
      },
      {
        "id": "GV1",
        "editor": "NOWATERALARM",
        "name": "Current No Water Alarm"
      },
      {
        "id": "GV10",
        "editor": "UNIXTIME",
        "name": "Time for Latest operation Update"
      },
      {
        "id": "GV5",
        "editor": "WATERRUN",
        "name": "Latest Operation"
      },
      {
        "id": "GV7",
        "editor": "RUNNINGMODE",
        "name": "Latest Water Method"
      },
      {
        "id": "GV8",
        "editor": "RUNNINGVALUE",
        "name": "Latest Water Amount target"
      },
      {
        "id": "GV9",
        "editor": "NOWATERALARM",
        "name": "Latest Water Alarm"
      },
      {
        "id": "GV12",
        "editor": "MINUTES",
        "name": "Time Delay"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "editor": "STARTSTOP"
            },
            {
              "id": "watermode",
              "editor": "WATERMODE"
            }
          ]
        },
        {
          "id": "WATTRIB",
          "name": "Set watering Attributes",
          "parameters": [
            {
              "id": "wmethod",
              "editor": "SPRINKLERMETHOD"
            },
            {
              "id": "wamount",
              "editor": "WAMOUNT"
            }
          ]
        },
        {
          "id": "WDELAY",
          "name": "Set water delay",
          "parameters": [
            {
              "id": "WDELAY",
              "editor": "MINUTESSET"
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
    "id": "YOTHSENS",
    "name": "YoLink THsensor",
    "icon": "TempSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "CELSIUS",
        "name": "Sensor Temperature"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Sensor Temperature (legacy)"
      },
      {
        "id": "GV1",
        "editor": "ALARM",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV2",
        "editor": "ALARM",
        "name": "High Temp Alarm"
      },
      {
        "id": "CLIHUM",
        "editor": "HUMIDITY",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV4",
        "editor": "ALARM",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "High Humidity Alarm"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Battery Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Alarm triggered"
      },
      {
        "id": "GV9",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "CELSIUS",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "CELSIUS",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "HUMIDITY",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "HUMIDITY",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "CELSIUS",
        "name": "Low Temp 24H"
      },
      {
        "id": "GV15",
        "editor": "CELSIUS",
        "name": "High Temp 24H"
      },
      {
        "id": "GV16",
        "editor": "HUMIDITY",
        "name": "Low Humidity  24H"
      },
      {
        "id": "GV17",
        "editor": "HUMIDITY",
        "name": "High Humidity 24H"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOSOILSENSOR",
    "name": "YoLink Soil Sensor",
    "icon": "Weather",
    "properties": [
      {
        "id": "ST",
        "editor": "CONDUCTIVITY",
        "name": "Soil Conductivity (mS/cm)"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Sensor Temperature"
      },
      {
        "id": "CLIHUM",
        "editor": "HUMIDITY",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV1",
        "editor": "ALARM",
        "name": "Low Conductivity Alarm"
      },
      {
        "id": "GV2",
        "editor": "ALARM",
        "name": "High Conductivity Alarm"
      },
      {
        "id": "GV3",
        "editor": "ALARM",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV4",
        "editor": "ALARM",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV6",
        "editor": "ALARM",
        "name": "High Humidity Alarm"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Period Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Alarm triggered"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV9",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "CELSIUS",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "CELSIUS",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "HUMIDITY",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "HUMIDITY",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "CONDUCTIVITY",
        "name": "Low Conductivity Alarm Limit (mS/cm)"
      },
      {
        "id": "GV15",
        "editor": "CONDUCTIVITY",
        "name": "High Conductivity Alarm Limit (mS/cm)"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOSOILSENSORF",
    "name": "YoLink Soil Sensor",
    "icon": "Weather",
    "properties": [
      {
        "id": "ST",
        "editor": "FARENHEIT",
        "name": "Soil Conductivity (mS/cm)"
      },
      {
        "id": "CLITEMP",
        "editor": "FARENHEIT",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV1",
        "editor": "ALARM",
        "name": "Low Conductivity Alarm"
      },
      {
        "id": "GV2",
        "editor": "ALARM",
        "name": "High Conductivity Alarm"
      },
      {
        "id": "GV3",
        "editor": "ALARM",
        "name": "Low Temp Alarm"
      },
      {
        "id": "CLIHUM",
        "editor": "HUMIDITY",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV4",
        "editor": "ALARM",
        "name": "High Temp Alarm"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV6",
        "editor": "ALARM",
        "name": "High Humidity Alarm"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Period Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Alarm triggered"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV9",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "FARENHEIT",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "FARENHEIT",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "HUMIDITY",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "HUMIDITY",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "FARENHEIT",
        "name": "Low Conductivity Alarm Limit (mS/cm)"
      },
      {
        "id": "GV15",
        "editor": "FARENHEIT",
        "name": "High Conductivity Alarm Limit (mS/cm)"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOTHSENSF",
    "name": "YoLink THsensor",
    "icon": "TempSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "FARENHEIT",
        "name": "Sensor Temperature"
      },
      {
        "id": "CLITEMP",
        "editor": "FARENHEIT",
        "name": "Sensor Temperature (legacy)"
      },
      {
        "id": "GV1",
        "editor": "ALARM",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV2",
        "editor": "ALARM",
        "name": "High Temp Alarm"
      },
      {
        "id": "CLIHUM",
        "editor": "HUMIDITY",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV4",
        "editor": "ALARM",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "High Humidity Alarm"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Battery Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Alarm triggered"
      },
      {
        "id": "GV9",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "FARENHEIT",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "FARENHEIT",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "HUMIDITY",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "HUMIDITY",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "FARENHEIT",
        "name": "Low Temp 24H"
      },
      {
        "id": "GV15",
        "editor": "FARENHEIT",
        "name": "High Temp 24H"
      },
      {
        "id": "GV16",
        "editor": "HUMIDITY",
        "name": "Low Humidity  24H"
      },
      {
        "id": "GV17",
        "editor": "HUMIDITY",
        "name": "High Humidity 24H"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOTSENS",
    "name": "YoLink T Sensor",
    "icon": "TempSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "CELSIUS",
        "name": "Sensor Temperature"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Sensor Temperature (legacy)"
      },
      {
        "id": "GV1",
        "editor": "ALARM",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV2",
        "editor": "ALARM",
        "name": "High Temp Alarm"
      },
      {
        "id": "CLIHUM",
        "editor": "HUMIDITY",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV4",
        "editor": "ALARM",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "High Humidity Alarm"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Battery Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Alarm triggered"
      },
      {
        "id": "GV9",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "CELSIUS",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "CELSIUS",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "HUMIDITY",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "HUMIDITY",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "CELSIUS",
        "name": "Low Temp 24H"
      },
      {
        "id": "GV15",
        "editor": "CELSIUS",
        "name": "High Temp 24H"
      },
      {
        "id": "GV16",
        "editor": "HUMIDITY",
        "name": "Low Humidity 24H"
      },
      {
        "id": "GV17",
        "editor": "HUMIDITY",
        "name": "High Humidity 24H"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOTSENSF",
    "name": "YoLink T Sensor",
    "icon": "TempSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "FARENHEIT",
        "name": "Sensor Temperature"
      },
      {
        "id": "CLITEMP",
        "editor": "FARENHEIT",
        "name": "Sensor Temperature (legacy)"
      },
      {
        "id": "GV1",
        "editor": "ALARM",
        "name": "Low Temp Alarm"
      },
      {
        "id": "GV2",
        "editor": "ALARM",
        "name": "High Temp Alarm"
      },
      {
        "id": "CLIHUM",
        "editor": "HUMIDITY",
        "name": "Current Rel Humidity (%)"
      },
      {
        "id": "GV4",
        "editor": "ALARM",
        "name": "Low Humidity Alarm"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "High Humidity Alarm"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV7",
        "editor": "ALARM",
        "name": "Battery Alarm"
      },
      {
        "id": "GV8",
        "editor": "ALARM",
        "name": "Alarm triggered"
      },
      {
        "id": "GV9",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "GV10",
        "editor": "FARENHEIT",
        "name": "Low Temp Alarm Limit"
      },
      {
        "id": "GV11",
        "editor": "FARENHEIT",
        "name": "High Temp Alarm Limit"
      },
      {
        "id": "GV12",
        "editor": "HUMIDITY",
        "name": "Low Humidity Alarm Limit"
      },
      {
        "id": "GV13",
        "editor": "HUMIDITY",
        "name": "High Humidity Alarm Limit"
      },
      {
        "id": "GV14",
        "editor": "FARENHEIT",
        "name": "Low Temp 24H"
      },
      {
        "id": "GV15",
        "editor": "FARENHEIT",
        "name": "High Temp 24H"
      },
      {
        "id": "GV16",
        "editor": "HUMIDITY",
        "name": "Low Humidity 24H"
      },
      {
        "id": "GV17",
        "editor": "HUMIDITY",
        "name": "High Humidity 24H"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YODOORSENS",
    "name": "YoLink Door Sensor",
    "icon": "DoorLock",
    "properties": [
      {
        "id": "ST",
        "editor": "DOORSTATE",
        "name": "Door State"
      },
      {
        "id": "GV0",
        "editor": "DOORSTATE",
        "name": "Door State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "BATLEVEL",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV2",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "GV3",
        "editor": "UNIXTIME",
        "name": "Last State Change"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOGARAGE",
    "name": "YoLink Garage Controller",
    "icon": "Switch",
    "properties": [
      {
        "id": "ST",
        "editor": "STATUS",
        "name": "Node Server Status"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
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
    "id": "YOMOTIONSENS",
    "name": "YoLink Motion Sensor",
    "icon": "MotionSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "MOTIONSTATE",
        "name": "Motion State"
      },
      {
        "id": "GV0",
        "editor": "MOTIONSTATE",
        "name": "Motion State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "BATLEVEL",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV2",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOMOTIONSENSF",
    "name": "YoLink Motion Sensor",
    "icon": "MotionSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "MOTIONSTATE",
        "name": "Motion State"
      },
      {
        "id": "GV0",
        "editor": "MOTIONSTATE",
        "name": "Motion State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "BATLEVEL",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV2",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "FARENHEIT",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOLEAKSENSF",
    "name": "YoLink Water Sensor",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERSTATE",
        "name": "Water State"
      },
      {
        "id": "GV0",
        "editor": "WATERSTATE",
        "name": "Water State (Legacy)"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV2",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "FARENHEIT",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV3",
        "editor": "UNIXTIME",
        "name": "Last State Change"
      },
      {
        "id": "GV4",
        "editor": "BEEPING",
        "name": "Sensor Sound"
      },
      {
        "id": "GV5",
        "editor": "LEAKOPMODE",
        "name": "Operating Mode"
      },
      {
        "id": "GV6",
        "editor": "SENSITIVITY",
        "name": "Sensitivity"
      },
      {
        "id": "GV7",
        "editor": "MOVEALERT",
        "name": "Sensor Move Alert"
      },
      {
        "id": "GV8",
        "editor": "FREEZEALERT",
        "name": "Sensor Freeze Alert"
      },
      {
        "id": "GV9",
        "editor": "SENSORERROR",
        "name": "Sensor Error"
      },
      {
        "id": "GV10",
        "editor": "REMINDER",
        "name": "Reminder"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "SETBEEP",
          "name": "Set Beep Alert",
          "parameters": [
            {
              "id": "SETBEEP",
              "editor": "BEEPING",
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
    "id": "YOLEAKSENS",
    "name": "YoLink Water Sensor",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERSTATE",
        "name": "Water State"
      },
      {
        "id": "GV0",
        "editor": "WATERSTATE",
        "name": "Water State (Legacy)"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV2",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV3",
        "editor": "UNIXTIME",
        "name": "Last State Change"
      },
      {
        "id": "GV4",
        "editor": "BEEPING",
        "name": "Sensor Sound"
      },
      {
        "id": "GV5",
        "editor": "LEAKOPMODE",
        "name": "Operating Mode"
      },
      {
        "id": "GV6",
        "editor": "SENSITIVITY",
        "name": "Sensitivity"
      },
      {
        "id": "GV7",
        "editor": "MOVEALERT",
        "name": "Sensor Move Alert"
      },
      {
        "id": "GV8",
        "editor": "FREEZEALERT",
        "name": "Sensor Freeze Alert"
      },
      {
        "id": "GV9",
        "editor": "SENSORERROR",
        "name": "Sensor Error"
      },
      {
        "id": "GV10",
        "editor": "REMINDER",
        "name": "Reminder"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
              "init": "GV2"
            }
          ]
        },
        {
          "id": "SETBEEP",
          "name": "Set Beep Alert",
          "parameters": [
            {
              "id": "SETBEEP",
              "editor": "BEEPING",
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
    "id": "YOCOSMOKESENS",
    "name": "YoLink COSmokeSensor",
    "icon": "SmokeSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "DEVICEALERT",
        "name": "Alarm"
      },
      {
        "id": "ALARM",
        "editor": "DEVICEALERT",
        "name": "Alert Detected"
      },
      {
        "id": "GV0",
        "editor": "SMOKEALERT",
        "name": "Smoke Detection"
      },
      {
        "id": "GV1",
        "editor": "COALERT",
        "name": "CO Detection"
      },
      {
        "id": "GV2",
        "editor": "TEMPALERT",
        "name": "High Temp Detection"
      },
      {
        "id": "GV3",
        "editor": "BATTERYALERT",
        "name": "Battery Problem Detection"
      },
      {
        "id": "GV4",
        "editor": "BATLEVEL",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV5",
        "editor": "SELFCHECKSTATE",
        "name": "Self-check"
      },
      {
        "id": "GV7",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOCOSMOKESENSF",
    "name": "YoLink COSmokeSensor",
    "icon": "SmokeSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "DEVICEALERT",
        "name": "Alarm"
      },
      {
        "id": "ALARM",
        "editor": "DEVICEALERT",
        "name": "Alert Detected"
      },
      {
        "id": "GV0",
        "editor": "SMOKEALERT",
        "name": "Smoke Detection"
      },
      {
        "id": "GV1",
        "editor": "COALERT",
        "name": "CO Detection"
      },
      {
        "id": "GV2",
        "editor": "TEMPALERT",
        "name": "High Temp Detection"
      },
      {
        "id": "GV3",
        "editor": "BATTERYALERT",
        "name": "Battery Problem Detection"
      },
      {
        "id": "GV4",
        "editor": "BATLEVEL",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV5",
        "editor": "SELFCHECKSTATE",
        "name": "Self-check"
      },
      {
        "id": "GV7",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "FARENHEIT",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOVIBRASENS",
    "name": "YoLink Vibration Sensor",
    "icon": "MotionSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "VIBRASTATE",
        "name": "Vibration State"
      },
      {
        "id": "GV0",
        "editor": "VIBRASTATE",
        "name": "Vibration State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "BATLEVEL",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV2",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOVIBRASENSF",
    "name": "YoLink Vibration Sensor",
    "icon": "MotionSensor",
    "properties": [
      {
        "id": "ST",
        "editor": "VIBRASTATE",
        "name": "Vibration State"
      },
      {
        "id": "GV0",
        "editor": "VIBRASTATE",
        "name": "Vibration State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "BATLEVEL",
        "name": "Sensor Battery Level"
      },
      {
        "id": "GV2",
        "editor": "CMDSETTING",
        "name": "Command Setting"
      },
      {
        "id": "CLITEMP",
        "editor": "FARENHEIT",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOHUBBAT",
    "name": "YoLink Hub w Battery",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "POWERALERT",
        "name": "Supply Status"
      },
      {
        "id": "GV0",
        "editor": "POWERSTATE",
        "name": "Battery Status"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
    "id": "YOHUB",
    "name": "YoLink Hub",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "STATUS",
        "name": "Status"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
    "id": "YOSPEAKERH",
    "name": "YoLink Speaker Hub",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "STATUS",
        "name": "Nodeserver Status"
      },
      {
        "id": "GV0",
        "editor": "VOLUME",
        "name": "Speaker volume"
      },
      {
        "id": "GV1",
        "editor": "BEEPEN",
        "name": "Command Beep"
      },
      {
        "id": "GV2",
        "editor": "MUTE",
        "name": "Mute"
      },
      {
        "id": "GV3",
        "editor": "TONE",
        "name": "Tone Type"
      },
      {
        "id": "GV4",
        "editor": "MESSAGES",
        "name": "Message"
      },
      {
        "id": "GV5",
        "editor": "REPEAT",
        "name": "Repeat"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "editor": "MESSAGES",
              "init": "GV4"
            },
            {
              "id": "volume",
              "editor": "VOLUME",
              "init": "GV0"
            },
            {
              "id": "tone",
              "editor": "TONESET",
              "init": "GV3"
            },
            {
              "id": "repeat",
              "editor": "REPEAT",
              "init": "GV5"
            }
          ]
        },
        {
          "id": "BEEP",
          "name": "Beep",
          "parameters": [
            {
              "id": "BEEP",
              "editor": "BEEPENSET",
              "init": "GV1"
            }
          ]
        },
        {
          "id": "MUTE",
          "name": "Mute",
          "parameters": [
            {
              "id": "MUTE",
              "editor": "MUTESET",
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
    "id": "YOLOCKV2",
    "name": "YOLOCKV2",
    "icon": "GenericCtl",
    "properties": [
      {
        "id": "ST",
        "editor": "LOCKSTATE",
        "name": "Lock State"
      },
      {
        "id": "GV0",
        "editor": "LOCKSTATE",
        "name": "Lock State (legacy)"
      },
      {
        "id": "GV1",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV2",
        "editor": "DOORBELL",
        "name": "Doorbell Active"
      },
      {
        "id": "GV3",
        "editor": "DOORSTATE",
        "name": "Door State"
      },
      {
        "id": "GV4",
        "editor": "LOCKACTION",
        "name": "Lock Action"
      },
      {
        "id": "GV5",
        "editor": "LOCKSOURCE",
        "name": "Source"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "LOCKCTRL",
              "editor": "LOCK",
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
    "id": "YOLOCK",
    "name": "YoLink Smart Lock",
    "icon": "DoorLock",
    "properties": [
      {
        "id": "ST",
        "editor": "LOCKSTATE",
        "name": "Lock State"
      },
      {
        "id": "GV0",
        "editor": "LOCKSTATE",
        "name": "Lock State (legacy)"
      },
      {
        "id": "GV1",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV3",
        "editor": "DOORSTATE",
        "name": "Door State"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "LOCKCTRL",
              "editor": "LOCK",
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
    "id": "YOIRREMOTE",
    "name": "YoLink Ir Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "IRCMDSTATUS",
        "name": "Last Command Status"
      },
      {
        "id": "GV0",
        "editor": "NBRCODES",
        "name": "Number of Learned codes"
      },
      {
        "id": "GV1",
        "editor": "BATLEVEL",
        "name": "Battery Level (legacy)"
      },
      {
        "id": "GV2",
        "editor": "IRCMDSTATUS",
        "name": "Last Command Status (legacy)"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
    "id": "YOIRCODE",
    "name": "YoLink Ir Code",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "IRCMDSTATUS",
        "name": "TX success"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
    "id": "YOPWRALARM",
    "name": "YoLink Power Failure Alarm",
    "icon": "Input",
    "properties": [
      {
        "id": "ST",
        "editor": "POWERALERT",
        "name": "Unit State"
      },
      {
        "id": "GV0",
        "editor": "POWERALERT",
        "name": "Unit State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV2",
        "editor": "ALERTSTATE",
        "name": "Alert Pending"
      },
      {
        "id": "GV3",
        "editor": "POWERED",
        "name": "Power on Unit"
      },
      {
        "id": "GV4",
        "editor": "PFAMUTE",
        "name": "Muted"
      },
      {
        "id": "GV7",
        "editor": "CMDSTATUS",
        "name": "Command Setting"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETCMD",
              "editor": "CMDSETTING",
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
    "id": "YOWATERDEPT",
    "name": "YoLink Water Level Sensor",
    "icon": "Irrigation",
    "properties": [
      {
        "id": "ST",
        "editor": "WATERLEVEL",
        "name": "Water Level (0-1000)"
      },
      {
        "id": "GV0",
        "editor": "WATERLEVEL",
        "name": "Water Level (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "WATERLEVEL",
        "name": "Low water Level Alarm setting"
      },
      {
        "id": "GV2",
        "editor": "WATERLEVEL",
        "name": "High water Level Alarm setting"
      },
      {
        "id": "GV3",
        "editor": "ALARM",
        "name": "Low Water Level"
      },
      {
        "id": "GV4",
        "editor": "ALARM",
        "name": "High Water Level"
      },
      {
        "id": "GV5",
        "editor": "ALARM",
        "name": "Sensor Error"
      },
      {
        "id": "BATLVL",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "editor": "WATERLEVEL",
              "init": "GV1"
            },
            {
              "id": "waterHighAlarm",
              "editor": "WATERLEVEL",
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
    "id": "YOSIREN",
    "name": "YoLink Siren",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "SIRENSTATE",
        "name": "Siren State"
      },
      {
        "id": "GV0",
        "editor": "SIRENSTATE",
        "name": "Siren State (Legacy)"
      },
      {
        "id": "GV1",
        "editor": "SIRENDURATION",
        "name": "Siren Duration"
      },
      {
        "id": "GV2",
        "editor": "SIRENBATLEVEL",
        "name": "Supply State"
      },
      {
        "id": "GV3",
        "editor": "SOUNDLEVEL",
        "name": "Sound Level"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SIRENCTRL",
              "editor": "SIRENCTRL",
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
    "id": "YOSMREMOTE",
    "name": "YoLink Smart Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "REMOTETYPE",
        "name": "Remote Type"
      },
      {
        "id": "GV3",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "CELSIUS",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
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
    "id": "YOSMREMOTEF",
    "name": "YoLink Smart Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "REMOTETYPE",
        "name": "Remote Type"
      },
      {
        "id": "GV3",
        "editor": "BATLEVEL",
        "name": "Battery Level"
      },
      {
        "id": "CLITEMP",
        "editor": "FARENHEIT",
        "name": "Sensor Temperature"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
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
    "id": "SMREMOTEKEY",
    "name": "YoLink Smart Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "KEYSCENEDEF",
        "name": "Last Command"
      },
      {
        "id": "GV1",
        "editor": "KEYSCENEDEF",
        "name": "Short Press Command Type"
      },
      {
        "id": "GV2",
        "editor": "KEYSCENEDEF",
        "name": "Long Press Type"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "KEYPRESS",
              "editor": "KEYSCENE",
              "init": "GV1"
            }
          ]
        },
        {
          "id": "KEYLPRESS",
          "name": "Long Press Command Type",
          "parameters": [
            {
              "id": "KEYLPRESS",
              "editor": "KEYSCENE",
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
    "id": "SMREMOTEKEYDUAL",
    "name": "YoLink Smart Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "KEYSCENEDEF",
        "name": "Last Command"
      },
      {
        "id": "GV1",
        "editor": "KEYSCENEDEF",
        "name": "Short Press Command Type"
      },
      {
        "id": "GV2",
        "editor": "KEYSCENEDEF",
        "name": "Long Press Command Type"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "KEYPRESS",
              "editor": "KEYSCENE"
            }
          ]
        },
        {
          "id": "KEYLPRESS",
          "name": "Long Press Command",
          "parameters": [
            {
              "id": "KEYLPRESS",
              "editor": "KEYSCENE"
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
    "id": "SMREMOTEKEYSINGLE",
    "name": "YoLink Smart Remoter",
    "icon": "Output",
    "properties": [
      {
        "id": "ST",
        "editor": "KEYSCENEDEF",
        "name": "Last Command"
      },
      {
        "id": "GV1",
        "editor": "KEYSCENEDEF",
        "name": "Press Command"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "PRESSCMD",
              "editor": "KEYSCENE",
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
    "id": "YOTHERMOSTAT",
    "name": "YoLink Thermostat (C)",
    "icon": "Thermostat",
    "properties": [
      {
        "id": "ST",
        "editor": "CELSIUS",
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
        "editor": "CELSIUS",
        "name": "Heat Setpoint"
      },
      {
        "id": "CLISPC",
        "editor": "CELSIUS",
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
        "editor": "CELSIUS",
        "name": "Schedule Mode"
      },
      {
        "id": "GV0",
        "editor": "CELSIUS",
        "name": "Sensor 1 Temp"
      },
      {
        "id": "GV1",
        "editor": "CELSIUS",
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
        "editor": "CELSIUS",
        "name": "ECO Low Temp"
      },
      {
        "id": "GV19",
        "editor": "CELSIUS",
        "name": "ECO High Temp"
      },
      {
        "id": "GV5",
        "editor": "IDRRUNNING",
        "name": "Demand Response Running"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETHEATTEMP",
              "editor": "CELSIUSSET",
              "init": "CLISPH"
            }
          ]
        },
        {
          "id": "SETCOOLTEMP",
          "name": "Set Cool Setpoint",
          "parameters": [
            {
              "id": "SETCOOLTEMP",
              "editor": "CELSIUSSET",
              "init": "CLISPC"
            }
          ]
        },
        {
          "id": "SETMODE",
          "name": "Set Mode",
          "parameters": [
            {
              "id": "SETMODE",
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
              "id": "SETFAN",
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
              "id": "SETSCHE",
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
              "editor": "ECOSET",
              "init": "GV18"
            },
            {
              "id": "ecoHighth",
              "editor": "ECOSET",
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
    "id": "YOTHERMOSTATF",
    "name": "YoLink Thermostat (F)",
    "icon": "Thermostat",
    "properties": [
      {
        "id": "ST",
        "editor": "FARENHEIT",
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
        "editor": "FARENHEIT",
        "name": "Heat Setpoint"
      },
      {
        "id": "CLISPC",
        "editor": "FARENHEIT",
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
        "editor": "FARENHEIT",
        "name": "Sensor 1 Temp"
      },
      {
        "id": "GV1",
        "editor": "FARENHEIT",
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
        "editor": "FARENHEIT",
        "name": "ECO Low Temp"
      },
      {
        "id": "GV19",
        "editor": "FARENHEIT",
        "name": "ECO High Temp"
      },
      {
        "id": "GV5",
        "editor": "IDRRUNNING",
        "name": "Demand Response Running"
      },
      {
        "id": "GV20",
        "editor": "SUSPENDSTATE",
        "name": "Connection State"
      },
      {
        "id": "GV30",
        "editor": "STATUS",
        "name": "Online State"
      },
      {
        "id": "TIME",
        "editor": "UNIXTIME",
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
              "id": "SETHEATTEMP",
              "editor": "FARENHEITSET",
              "init": "CLISPH"
            }
          ]
        },
        {
          "id": "SETCOOLTEMP",
          "name": "Set Cool Setpoint",
          "parameters": [
            {
              "id": "SETCOOLTEMP",
              "editor": "FARENHEITSET",
              "init": "CLISPC"
            }
          ]
        },
        {
          "id": "SETMODE",
          "name": "Set Mode",
          "parameters": [
            {
              "id": "SETMODE",
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
              "id": "SETFAN",
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
              "id": "SETSCHE",
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
              "editor": "ECOSETF",
              "init": "GV18"
            },
            {
              "id": "ecoHighth",
              "editor": "ECOSETF",
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
    "id": "YOTHERMPROP",
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
        "editor": "CELSIUS",
        "name": "Cool Limit"
      },
      {
        "id": "GV8",
        "editor": "CELSIUS",
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
        "editor": "CELSIUS",
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
        "editor": "CELSIUS",
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
              "id": "SETMINRUNTIME",
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
              "id": "SETCOOLLIMIT",
              "editor": "CELSIUSSET",
              "init": "GV7"
            }
          ]
        },
        {
          "id": "SETHEATLIMIT",
          "name": "Set Heat Limit",
          "parameters": [
            {
              "id": "SETHEATLIMIT",
              "editor": "CELSIUSSET",
              "init": "GV8"
            }
          ]
        },
        {
          "id": "SETMUTE",
          "name": "Set Mute",
          "parameters": [
            {
              "id": "SETMUTE",
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
              "id": "SETMENULOCK",
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
              "id": "SETMASTER",
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
    "id": "YOTHERMPROPF",
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
        "editor": "FARENHEIT",
        "name": "Cool Limit"
      },
      {
        "id": "GV8",
        "editor": "FARENHEIT",
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
        "editor": "FARENHEIT",
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
        "editor": "FARENHEIT",
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
              "id": "SETMINRUNTIME",
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
              "id": "SETCOOLLIMIT",
              "editor": "FARENHEITSET",
              "init": "GV7"
            }
          ]
        },
        {
          "id": "SETHEATLIMIT",
          "name": "Set Heat Limit",
          "parameters": [
            {
              "id": "SETHEATLIMIT",
              "editor": "FARENHEITSET",
              "init": "GV8"
            }
          ]
        },
        {
          "id": "SETMUTE",
          "name": "Set Mute",
          "parameters": [
            {
              "id": "SETMUTE",
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
              "id": "SETMENULOCK",
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
              "id": "SETMASTER",
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
