"""
 Copyright (C) 2025 Mauricio Bustos (m@bustos.org)
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import asyncio
import time

import python_weather
import colorbrewer
from pixelblaze import Pixelblaze


async def getweather() -> None:
  async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
    #weather = await client.get('San+Luis+Obispo')
    weather = await client.get('Oakland')

    temp_bucket = -max(0, min(10, int((weather.daily_forecasts[0].highest_temperature - 30) / (90.0 - 30.0) * 10))) + 10
    color = colorbrewer.diverging["RdBu"][11][temp_bucket]
    red = color.split(",")[0].split("(")[1]
    green = color.split(",")[1]
    blue = color.split(",")[2].split(")")[0]
    for ipAddress in Pixelblaze.EnumerateAddresses(timeout=1500):
      with Pixelblaze(ipAddress) as pb:
        pb.setActiveControls({"sliderTempRed": float(red) / 256.0})
        pb.setActiveControls({"sliderTempGreen": float(green) / 256.0})
        pb.setActiveControls({"sliderTempBlue": float(blue) / 256.0})

if __name__ == '__main__':

  asyncio.run(getweather())