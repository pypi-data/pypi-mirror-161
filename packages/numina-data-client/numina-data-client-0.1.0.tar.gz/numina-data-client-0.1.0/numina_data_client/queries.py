#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################

GET_ORG_DETAILS_BY_ALIAS = """
query {{
  organizations (alias: "{organization_alias}") {{
    edges {{
      node {{
        organization_id: rawId
        organization_name: name
        organization_timezone: timezone
        organization_alias: alias
        organization_latitude: orgLat
        organization_longitude: orgLon
      }}
    }}
  }}
}}
"""

GET_ALL_ORGS = """
query {
  organizations {
    edges {
      node {
        organization_id: rawId
        organization_name: name
        organization_timezone: timezone
        organization_alias: alias
        organization_latitude: orgLat
        organization_longitude: orgLon
      }
    }
  }
}
"""

SINGLE_ORG_ALL_SENSORS_FROM_ORG_NAME = """
query {{
  organizations (name: "{organization_name}") {{
    edges {{
      node {{
        rawId
        name
        joined
        alias
        timezone
        devices {{
          count
          edges {{
            node {{
              device_id: rawId
              feed_id: feedId
              device_serialno: serialno
              device_name: name
              device_alias: alias
              device_status: status
              device_created: created
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""

SINGLE_ORG_ALL_SENSORS_FROM_ORG_ALIAS = """
query {{
  organizations (alias: "{organization_alias}") {{
    edges {{
      node {{
        rawId
        name
        joined
        alias
        timezone
        devices {{
          count
          edges {{
            node {{
              device_id: rawId
              feed_id: feedId
              device_serialno: serialno
              device_name: name
              device_alias: alias
              device_status: status
              device_created: created
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""

BEHAVIOR_ZONES_FROM_DEVICE_SERIAL_NOS = """
query {{
  behaviorZones (serialnos: {serial_nos}) {{
    count
    edges {{
      node {{
        zone_id: rawId
        text
        zoneType
        demarcation
        isCoverageZone
      }}
    }}
  }}
}}
"""

FEED_COUNT_METRICS = """
query {{
  feedCountMetrics (
    serialnos: {serial_nos}
    startTime: "{start_time}"
    endTime: "{end_time}"
    interval: "{interval}"
    objClasses: {obj_classes}
    timezone: "{timezone}") {{
    edges {{
      node {{
        metric
        objClass
        result
        time
      }}
    }}
  }}
}}
"""

FEED_HEATMAP = """
query {{
   feedHeatmaps(
     serialno: "{serial_no}",
     startTime: "{start_datetime}",
     endTime: "{end_datetime}",
     objClasses: ["{obj_class}"],
     timezone: "{timezone}",
   ) {{
    edges {{
      node {{
        time
        heatmap
      }}
    }}
  }}
}}
"""

ZONE_COUNT_METRICS = """
query {{
  zoneCountMetrics (
    zoneIds: {zone_ids}
    startTime: "{start_time}"
    endTime: "{end_time}"
    interval: "{interval}"
    objClasses: {obj_classes}
    timezone: "{timezone}") {{
    edges {{
      node {{
        metric
        objClass
        result
        time
      }}
    }}
  }}
}}
"""

MAX_OCCUPANCY = """
query {{
  maxOccupancy (
    serialnos: {serial_nos}
    startTime: "{start_time}"
    endTime: "{end_time}"
    interval: "{interval}"
    objClasses: {obj_classes}
    timezone: "{timezone}") {{
    edges {{
      node {{
        metric
        objClass
        result
        time
      }}
    }}
  }}
}}
"""

ZONE_HEATMAP = """
query {{
   zoneHeatmaps(
     zoneIds: [{zone_id}],
     startTime: "{start_datetime}",
     endTime: "{end_datetime}",
     objClasses: ["{obj_class}"],
     timezone: "{timezone}",
   ) {{
    edges {{
      node {{
        objClass
        time
        heatmap
      }}
    }}
  }}
}}
"""

ZONE_DWELL_TIME = """
query {{
  zoneDwellTimeDistribution (
    zoneIds: [{zone_id}], 
    startTime: "{start_datetime}", 
    endTime: "{end_datetime}",
    objClasses: {obj_classes},
    timezone: "{timezone}",
    interval: "{interval}"
  ) {{
    edges {{
      node {{
        id
        objClass
        pct100
        pct75
        pct50
        pct25
        mean
        count
        time
      }}
    }}
  }}
}}
"""


GET_DEVICE_BY_SERIALNO = """
query {{
  devices (
    serialno: "{device_serial_no}"
  ) {{
    edges {{
      node {{
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
}}
"""

GET_DEVICE_BY_NAME = """
query {{
  devices (
    name: "{device_name}"
  ) {{
    edges {{
      node {{
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
}}
"""
