import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os

url = "https://africa.espn.com/football/schedule/_/league/eng.1"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")


# -------------------------
# CONVERSION HEURE UK -> CI
# -------------------------

def convertir_heure_ci(date_str, time_str):

    texte = date_str + " " + time_str

    dt = datetime.strptime(
        texte,
        "%A, %B %d, %Y %I:%M %p"
    )

    mois = dt.month

    # Heure d'été UK (BST)
    if 4 <= mois <= 10:
        dt = dt.replace(
            hour=(dt.hour + 1) % 24
        )

    return dt


# -------------------------
# DATE DU JOUR (CI)
# -------------------------

today = datetime.utcnow().date()

print("Date du jour :", today)


# -------------------------
# FICHIER A LA RACINE
# -------------------------

filename = "matchs_du_jour.csv"

with open(
    filename,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "datetime",
        "date",
        "heure",
        "equipe_domicile",
        "equipe_exterieure",
        "lieu"
    ])

    tables = soup.find_all(
        "div",
        class_="ScheduleTables"
    )

    for table in tables:

        date_title = table.find(
            "div",
            class_="Table__Title"
        )

        if not date_title:
            continue

        date_str = date_title.get_text(strip=True)

        rows = table.find_all(
            "tr",
            class_="Table__TR"
        )

        for row in rows:

            teams = row.find_all(
                "span",
                class_="Table__Team"
            )

            if len(teams) < 2:
                continue

            team_home = teams[0].get_text(strip=True)
            team_away = teams[1].get_text(strip=True)

            time_tag = row.find(
                "td",
                class_="date__col"
            )

            venue_tag = row.find(
                "td",
                class_="venue__col"
            )

            if not time_tag:
                continue

            time_str = time_tag.get_text(strip=True)

            venue = (
                venue_tag.get_text(strip=True)
                if venue_tag
                else ""
            )

            dt_ci = convertir_heure_ci(
                date_str,
                time_str
            )

            # FILTRE MATCHS DU JOUR
            if dt_ci.date() == today:

                print(
                    dt_ci,
                    "|",
                    team_home,
                    "vs",
                    team_away
                )

                writer.writerow([
                    dt_ci.isoformat(),
                    dt_ci.date(),
                    dt_ci.time(),
                    team_home,
                    team_away,
                    venue
                ])

print("Matchs du jour enregistrés dans :", filename)
