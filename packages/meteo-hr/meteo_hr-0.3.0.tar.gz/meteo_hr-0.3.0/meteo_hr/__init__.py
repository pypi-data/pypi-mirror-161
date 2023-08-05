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
        values = parse_day(r1, r2, r3)
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


def dump(data):
    for day, date, times in data:
        print()
        print(f"{day}, {date}")
        for time, forecast in times.items():
            if forecast:
                print(" ".join([
                    f"  {time:>5}  {forecast['temperature']:>2} °C",
                    f"{forecast['weather_title']},",
                    f"vjetar {forecast['wind_title']}"
                ]))


def run(name, slug):
    data = parse(fetch(slug))
    print(f"Prognoza za {name}")
    dump(data)
