import requests
from bs4 import BeautifulSoup


class Availability:
    def __init__(self, location: str, count: int, max_count: int, room: str, shelf: str):
        self.location = location
        self.count = count
        self.max_count = max_count
        self.room = room
        self.shelf = shelf

    def is_available(self) -> bool:
        return self.count > 0

    def __repr__(self):
        return f"Availability({self.location}, {self.count}, {self.max_count}, at {self.room} > {self.shelf})"


class Availabilities:
    def __init__(self, availabilities: list[Availability]):
        self.availabilities: dict[str, Availability] = {availability.location: availability for availability in
                                                        availabilities}

    def is_available(self, location: str) -> bool:
        return self.availabilities[location].is_available()

    def __getitem__(self, location: str) -> Availability:
        return self.availabilities[location]

    def items(self) -> list[tuple[str, Availability]]:
        return self.availabilities.items()

    def __repr__(self):
        return f"Availabilities({self.availabilities})"


class Item:
    def __init__(self, url, title, availabilities):
        self.url = url
        self.title = title
        self.availabilities = availabilities

    def is_available(self, location: str) -> bool:
        return self.availabilities.is_available(location)

    def get_room(self) -> str:
        availabilities = self.availabilities.availabilities
        if len(availabilities) == 0:
            return ""
        elif "Zentralbibliothek" not in availabilities:
            return availabilities.values()[0].room
        else:
            return availabilities["Zentralbibliothek"].room

    def __repr__(self):
        return f"Item({self.title}, {self.availabilities}, {self.url})"


def parse_availability(availability: BeautifulSoup) -> Availability:
    location = availability.select(".medium-availability-item-title-location")[0].text
    count = availability.select(".medium-availability-item-title-count")[0].text
    count = count.split("/")
    room = availability.select(".item-data-location-path")[0].text
    shelf = availability.select(".item-data-shelfmark")[0].text
    return Availability(location, int(count[0]), int(count[1]), room, shelf)


def retrieve_item_details(id: str) -> Item:
    url = f"https://www.buecherhallen.de/suchergebnis-detail/medium/{id}.html"
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    title = soup.select_one(".medium-detail-title").text.strip()
    availabilities_html = soup.select(".medium-availability-item")
    availabilities = Availabilities(list(map(parse_availability, availabilities_html)))
    return Item(url=url, title=title, availabilities=availabilities)
