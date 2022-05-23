# Import Meteostat library and dependencies
from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Point, Monthly, Stations

# Set time period
start = datetime(2018, 1, 1)
end = datetime(2022, 5, 21)

# Create Point for Vancouver, BC
city = Point(50.883331, 8.016667)

# Get daily data for 2018
data = Monthly(city, start, end)
data = data.fetch()

stations = Stations()

stations = stations.nearby(50.883331, 8.016667)

station = stations.fetch(1)

print(station)