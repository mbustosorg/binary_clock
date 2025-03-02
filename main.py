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
import datetime
import logging
from logging.handlers import RotatingFileHandler
import math

import python_weather
import colorbrewer
from pixelblaze import Pixelblaze

FORMAT = "%(asctime)s-%(module)s-%(lineno)d-%(message)s"
logger = logging.getLogger("binary-clock")

logging.basicConfig(level=logging.INFO,
                    format=FORMAT,
                    handlers=[
                        RotatingFileHandler("binary-clock.log", maxBytes=40000, backupCount=5),
                        logging.StreamHandler()
                    ])

LOWER_TEMP_BOUND = 30.0
UPPER_TEMP_BOUND = 90.0

moonIndex = 2
MOON_PHASES = {"NEW_MOON" : 0,
    "WAXING_CRESCENT": 1,
    "FIRST_QUARTER": 2,
    "WAXING_GIBBOUS": 3,
    "FULL_MOON": 4,
    "WANING_GIBBOUS": 5,
    "LAST_QUARTER": 6,
    "WANING_CRESCENT": 7}


# SUNNY: 0
# PARTLY CLOUDY: 1
# CLOUDY: 2
# VERY CLOUDY, FOG: 3
# LIGHT SHOWERS, LIGHT_SLEET_SHOWERS, LIGHT_SLEET, THUNDERY_SHOWERS, LIGHT_RAIN, HEAVY_SHOWERS, HEAVY_RAIN, THUNDERY_HEAVY_RAIN: 4
# LIGHT_SNOW, HEAVY_SNOW, LIGHT_SNOW_SHOWERS, HEAVY_SNOW_SHOWER, THUNDERY_SNOW_SHOWERS: 5
# From: python_weather
# SUNNY = 113
# PARTLY_CLOUDY = 116
# CLOUDY = 119
# VERY_CLOUDY = 122
# FOG = 143
# LIGHT_SHOWERS = 176
# LIGHT_SLEET_SHOWERS = 179
# LIGHT_SLEET = 182
# THUNDERY_SHOWERS = 200
# LIGHT_SNOW = 227
# HEAVY_SNOW = 230
# LIGHT_RAIN = 266
# HEAVY_SHOWERS = 299
# HEAVY_RAIN = 302
# LIGHT_SNOW_SHOWERS = 323
# HEAVY_SNOW_SHOWERS = 335
# THUNDERY_HEAVY_RAIN = 389
# THUNDERY_SNOW_SHOWERS = 392


WEATHER_KIND = {113: 0,
                116: 1,
                119: 2,
                122: 3,
                143: 3,
                176: 4,
                179: 4,
                182: 4,
                200: 4,
                266: 4,
                299: 4,
                302: 4,
                389: 4,
                227: 5,
                230: 5,
                323: 5,
                335: 5,
                392: 5}


async def get_weather() -> None:
    while True:
        async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
            now = datetime.datetime.now()
            brightness = (-math.cos((now.hour + (now.minute / 60.0)) / 24.0 * 2.0 * math.pi) + 1.0) / 2.0 * 0.35 + 0.05
            logger.info("Getting weather update...")
            # weather = await client.get('San+Luis+Obispo')
            weather = await client.get('Oakland')

            temp_bucket = -max(0, min(10, int((weather.daily_forecasts[0].highest_temperature - LOWER_TEMP_BOUND) /
                                              (UPPER_TEMP_BOUND - LOWER_TEMP_BOUND) * 10))) + 10
            color = colorbrewer.diverging["RdBu"][11][temp_bucket]
            red = color.split(",")[0].split("(")[1]
            green = color.split(",")[1]
            blue = color.split(",")[2].split(")")[0]
            logger.info(f"\tMoon phase: {weather.daily_forecasts[0].moon_phase.name}")
            logger.info(f"\tWeather: {weather.daily_forecasts[0].hourly_forecasts[4].kind.name}")
            logger.info(f"\tBrightness: {brightness}")
            for ipAddress in Pixelblaze.EnumerateAddresses(timeout=1500):
                with Pixelblaze(ipAddress) as pb:
                    pb.setActivePatternByName("binary clock")
                    pb.setActiveControls({"sliderTempRed": float(red) / 256.0})
                    pb.setActiveControls({"sliderTempGreen": float(green) / 256.0})
                    pb.setActiveControls({"sliderTempBlue": float(blue) / 256.0})
                    pb.setActiveVariables({"moonIndex": float(MOON_PHASES[weather.daily_forecasts[0].moon_phase.name])})
                    pb.setBrightnessSlider(brightness)
                    if weather.daily_forecasts[0].hourly_forecasts[4].kind.value in WEATHER_KIND:
                        pb.setActiveVariables({"weatherIndex": float(WEATHER_KIND[weather.daily_forecasts[0].hourly_forecasts[4].kind.value])})
                    else:
                        pb.setActiveVariables({"weatherIndex": -1.0})

        await asyncio.sleep(900)


if __name__ == '__main__':
    asyncio.run(get_weather())
