import os
import time
import argparse
import asyncio
import discord

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import file_handler
from webdriver_handler import WebDriverFactory

intents = discord.Intents.default()
client = discord.Client(intents=intents)

link = "https://sco.polytech.unice.fr/1/etudiant"
login, password = file_handler.return_datas("credentials.txt")
DISCORD_TOKEN, DISCORD_CHANNEL_ID = file_handler.return_datas("tokens.txt")
DISCORD_CHANNEL_ID = int(DISCORD_CHANNEL_ID)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--webdriver", "-wd", type=str, default=WebDriverFactory.DEFAULT)
arg_parser.add_argument("--no-headless", action='store_false', default=True)
args = arg_parser.parse_args()

driver = WebDriverFactory.get(args.webdriver).get_driver(headless=args.no_headless)

def login_and_get_to_notes():
    driver.get(link)
    driver.find_element(By.ID, 'username').send_keys(login)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.NAME, 'submit').click()

    WebDriverWait(driver, 10).until(lambda d: d.find_element(By.XPATH, "//header[@title='Les 10 dernières notes']")).click()
    WebDriverWait(driver, 10).until(lambda d: d.find_elements(By.CLASS_NAME, "ie-titre-gros"))

def calcDico():
    dico = dict()
    isFirst = True
    cat = ""
    tab = []

    liste_celluleGrid = driver.find_elements(By.CLASS_NAME, "liste_celluleGrid")

    for celluleGrid in liste_celluleGrid:
        celluleGrid_children = celluleGrid \
            .find_elements(By.XPATH, "./*")[0] \
            .find_elements(By.XPATH, "./*")[0] \
            .find_elements(By.XPATH, "./*")[0]

        zone_gauche = celluleGrid_children.find_elements(By.XPATH, "./*")[0]
        zone_centrale = celluleGrid_children.find_elements(By.XPATH, "./*")[1]

        if zone_gauche.find_elements(By.XPATH, "./*")[0].tag_name == "span":
            category = zone_centrale.find_elements(By.XPATH, "./*")[0] \
                .find_elements(By.XPATH, "./*")[0] \
                .find_elements(By.XPATH, "./*")[0] \
                .find_elements(By.XPATH, "./*")[0] \
                .get_attribute('innerHTML').replace("&amp;", "&")
            if isFirst:
                isFirst = False
            else:
                dico[cat] = tab
                tab = []
            cat = category
        elif zone_gauche.find_elements(By.XPATH, "./*")[0].tag_name == "time":
            nom_note = zone_centrale \
                .find_elements(By.XPATH, "./*")[0] \
                .find_elements(By.XPATH, "./*")[0] \
                .find_elements(By.XPATH, "./*")[-1] \
                .find_elements(By.XPATH, "./*")[0] \
                .get_attribute('innerHTML')
            tab.append(nom_note)
        else:
            print("error")
    dico[cat] = tab
    return dico

def isNewNotes(oldDico, dico):
    new_notes = []
    for subject, notes in dico.items():
        old_notes = oldDico.get(subject, [])
        for note in notes:
            if note not in old_notes:
                new_notes.append((subject, note))
    return new_notes

@client.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {client.user}")
    login_and_get_to_notes()
    oldDico = calcDico()
    await asyncio.sleep(5)

    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        print("❌ Channel introuvable ! Vérifie l’ID.")
        return

    while True:
        try:
            # Recharge la page pour voir les nouvelles notes
            driver.get(link)
            login_and_get_to_notes()  # Re-login + accéder à la page des notes
            dico = calcDico()
            new = isNewNotes(oldDico, dico)
            oldDico = dico

            if new:
                for subject, note in new:
                    msg = f"Nouvelle note en **{subject}** : **{note}**"
                    print(msg)
                    await channel.send(msg)
            else:
                print("✅ Pas de nouvelles notes.")

        except Exception as e:
            print(f"❌ Erreur pendant le refresh : {e}")

        await asyncio.sleep(60)


client.run(DISCORD_TOKEN)
