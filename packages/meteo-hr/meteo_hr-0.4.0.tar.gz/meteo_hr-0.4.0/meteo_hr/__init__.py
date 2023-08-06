import requests

from bs4 import BeautifulSoup
from collections import OrderedDict


def batch(lst, n):
    for i in range(len(lst) // n):
        yield list(lst[i * n + k] for k in range(n))


def fetch(place):
    response = requests.get("https://meteo.hr/prognoze.php", params={
        "Code": place,
        "id": "prognoza",
        "section": "prognoze_model",
        "param": "3d",
    })
    response.raise_for_status()
    return response.text


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one(".table-weather-7day")

    if not table:
        raise ValueError("Cannot find table")

    rows = table.select("tr")

    times = rows[0].select("th")[1:]
    times = [t.text for t in times]
    weather_rows = rows[1:-1]

    for r1, r2, r3 in batch(weather_rows, 3):
        day, _, date = r1.find("th").contents
        values = list(parse_day(r1, r2, r3))
        zipped = zip(times, values)
        yield day, date, OrderedDict(zipped)


def parse_day(r1, r2, r3):
    for (weather, wetaher_title), temperature, (wind, wind_title) in zip(
        icons_and_titles(r1),
        temperatures(r2),
        icons_and_titles(r3),
    ):
        yield {
            "weather": weather,
            "weather_title": wetaher_title,
            "temperature": temperature,
            "wind": wind,
            "wind_title": wind_title,
        } if weather else None


def icons_and_titles(row):
    for cell in row.select("td"):
        span = cell.find("span")
        if span:
            img = span.find("img")
            title = span.attrs["title"]
            icon = img.attrs["src"].split("/")[-1].replace(".svg", "")
            yield icon, title
        else:
            yield None, None


def temperatures(row):
    for cell in row.select("td"):
        text = cell.text.replace(" °C", "")
        yield int(text) if text else None


def bold(string):
    return f"\033[1m{string}\033[0m"


def gray(string):
    return f"\033[90m{string}\033[0m"


def red(string):
    return f"\033[31m{string}\033[0m"


def yellow(string):
    return f"\033[33m{string}\033[0m"


def blue(string):
    return f"\033[34m{string}\033[0m"


WINDS = {
    "C0": gray("-"),
    "N1": gray("↓"),
    "S1": gray("↑"),
    "E1": gray("←"),
    "W1": gray("→"),
    "NE1": gray("↙"),
    "NW1": gray("↘"),
    "SE1": gray("↖"),
    "SW1": gray("↗"),
    "N2": yellow("↓"),
    "S2": yellow("↑"),
    "E2": yellow("←"),
    "W2": yellow("→"),
    "NE2": yellow("↙"),
    "NW2": yellow("↘"),
    "SE2": yellow("↖"),
    "SW2": yellow("↗"),
    "N3": red("↓"),
    "S3": red("↑"),
    "E3": red("←"),
    "W3": red("→"),
    "NE3": red("↙"),
    "NW3": red("↘"),
    "SE3": red("↖"),
    "SW3": red("↗"),
}


def dump(data):
    for day, date, times in data:
        print()
        print(bold(f"{day}, {date}"))
        for time, forecast in times.items():
            if forecast:
                wind_icon = WINDS.get(forecast['wind'], "?")
                temperature = f"{forecast['temperature']:>2}°C"
                if forecast['temperature'] >= 30:
                    temperature = red(temperature)
                if forecast['temperature'] <= 0:
                    temperature = blue(temperature)

                print(" ".join([
                    f"  {time:>5}  {temperature}  {wind_icon} ",
                    f"{forecast['weather_title']},",
                    f"vjetar {forecast['wind_title']}"
                ]))


def run(name, slug):
    data = list(parse(fetch(slug)))
    print(f"Prognoza za {name}")
    dump(data)
