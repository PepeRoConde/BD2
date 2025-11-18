import csv
import random
from datetime import date, timedelta

INPUT_PLACES_CSV = "place.csv"
OUTPUT_EVENTS_CSV = "events.csv"

MIN_EVENTS_PER_PLACE = 0
MAX_EVENTS_PER_PLACE = 5

START_DATE = date(2014, 1, 1)
END_DATE   = date(2025, 12, 31)

random.seed(42)

EVENT_TYPES = {
    "Festival": [
        "Music Festival", "Food Festival", "Cultural Festival", "Film Festival"
    ],
    "Sports": [
        "Marathon", "Football Match", "Basketball Tournament", "Triathlon"
    ],
    "Conference": [
        "Tech Conference", "Business Summit", "Startup Meetup", "AI Congress"
    ],
    "Holiday": [
        "Local Holiday", "National Celebration", "Heritage Day", "City Anniversary"
    ],
    "Concert": [
        "Rock Concert", "Classical Concert", "Jazz Night", "Pop Music Live"
    ],
}

IMPACT_LEVELS = ["Low", "Medium", "High"]


def random_date(start: date, end: date) -> date:
    delta_days = (end - start).days
    offset = random.randint(0, delta_days)
    return start + timedelta(days=offset)


def main():
    places = []
    with open(INPUT_PLACES_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required_cols = {"STREET", "CITY", "COUNTRY"}
        if not required_cols.issubset(reader.fieldnames):
            raise ValueError(f"Input CSV must contain columns: {required_cols}")

        for row in reader:
            street = (row["STREET"] or "").strip()
            city   = (row["CITY"] or "").strip()
            country= (row["COUNTRY"] or "").strip()

            # Mismo PLACE_ID que en Hop: SUBSTITUTE([STREET]&"_"&[CITY]&"_"&[COUNTRY]," ","")
            place_id = f"{street}_{city}_{country}".replace(" ", "")

            row["PLACE_ID"] = place_id
            places.append(row)

    print(f"Loaded {len(places)} places from {INPUT_PLACES_CSV}")

    with open(OUTPUT_EVENTS_CSV, "w", newline="", encoding="utf-8") as f_out:
        fieldnames = ["EVENT_NAME", "EVENT_TYPE", "IMPACT", "PLACE_ID", "EVENT_DATE"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        total_events = 0

        for place in places:
            place_id = place["PLACE_ID"]
            street   = place.get("STREET", "")
            city     = place.get("CITY", "")
            country  = place.get("COUNTRY", "")

            num_events = random.randint(MIN_EVENTS_PER_PLACE, MAX_EVENTS_PER_PLACE)

            for _ in range(num_events):
                event_type = random.choice(list(EVENT_TYPES.keys()))
                base_name  = random.choice(EVENT_TYPES[event_type])

                name_parts = [base_name]
                if city:
                    name_parts.append(f"in {city}")
                if country:
                    name_parts.append(f"({country})")

                event_name = " ".join(name_parts).strip()
                impact = random.choice(IMPACT_LEVELS)
                event_date = random_date(START_DATE, END_DATE)

                writer.writerow({
                    "EVENT_NAME": event_name,
                    "EVENT_TYPE": event_type,
                    "IMPACT": impact,
                    "PLACE_ID": place_id,
                    "EVENT_DATE": event_date.strftime("%Y-%m-%d"),
                })

                total_events += 1

    print(f"Generated {total_events} events into {OUTPUT_EVENTS_CSV}")


if __name__ == "__main__":
    main()
