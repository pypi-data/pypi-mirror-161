#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################

CREATE_BEHAVIOR_ZONE = """
mutation {{
  createBehaviorZone(
    color: "{color}"
    demarcation: {demarcation}
    serialno: "{serial_no}"
    text: "{text}"
  ) {{
    behaviorZone {{
      zone_id: rawId
      text
      zoneType
      demarcation
      isCoverageZone
    }}
  }}
}}
"""

DELETE_BEHAVIOR_ZONE = """
mutation {{
  deleteBehaviorZone(
    zoneId: {zone_id}
  ) {{
    success
  }}
}}
"""

UPDATE_DEVICE = """
mutation {{
  updateDevice(
    device: {{
      serialno: "{device_new_serial_no}",
      name: "{device_new_name}",
    }}
    deviceId: "{device_id}"
  ) {{
    device {{
      object_id: id
      serialno
      name
      alias
      tags
      notes
      status
      created
      orgId
      locationId
      feedId
      samplingRate
      device_id: rawId
    }}
  }}
}}
"""

CREATE_DEVICE_WITH_LOCATION = """
mutation {{
  installSensor (
    device: {{
      serialno: "{device_serial_no}"
      name: "{device_name}"
      alias: "{device_alias}"
    }}
    location: {{
      lat: {device_lat}
      lon: {device_long}
      azi: {device_azimuth}
    }}
    orgId: "{organization_id}"
  ) {{
    device {{
      device_id: rawId
      device_serialno: serialno
      device_alias: alias
      device_name: name
    }}
  }}
}}
"""


UPDATE_DEVICE_ALIAS = """
mutation {{
  updateDevice (
    device: {{
      alias: "{device_alias}"
    }}
    deviceId: "{device_id}"
  ) {{
    device {{
      device_id: rawId
      device_serialno: serialno
      device_alias: alias
      device_name: name
    }}
  }}
}}
"""

UPDATE_DEVICE_SERIAL_NO = """
mutation {{
  updateDevice (
    device: {{
      serialno: "{device_serial_no}"
    }}
    deviceId: "{device_id}"
  ) {{
    device {{
      device_id: rawId
      device_serialno: serialno
      device_alias: alias
      device_name: name
    }}
  }}
}}
"""
