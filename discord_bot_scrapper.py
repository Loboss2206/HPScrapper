import os
import time
import argparse
import asyncio
import discord
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

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
    driver.find_element(By.ID, 'username').send_keys(login)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.NAME, 'submit').click()

    get_to_notes()

def get_to_notes():
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.XPATH, "//header[@title='Les 10 dernières notes']")).click()
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


def is_login_page():
    try:
        driver.find_element(By.ID, 'username')
        return True
    except:
        return False


@client.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {client.user}")

    driver.get(link)
    if is_login_page():
        login_and_get_to_notes()
    else:
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, "//header[@title='Les 10 dernières notes']")).click()
        WebDriverWait(driver, 10).until(lambda d: d.find_elements(By.CLASS_NAME, "ie-titre-gros"))

    oldDico = calcDico()
    await asyncio.sleep(5)

    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        print("❌ Channel introuvable ! Vérifie l’ID.")
        return

    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] 🔄 Rafraîchissement de la page...")
            driver.refresh()

            if is_login_page():
                print(f"[{current_time}] 🛑 Sur la page de login, relogin...")
                login_and_get_to_notes()
            else:
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_element(By.XPATH, "//header[@title='Les 10 dernières notes']")).click()
                WebDriverWait(driver, 10).until(lambda d: d.find_elements(By.CLASS_NAME, "ie-titre-gros"))

            dico = calcDico()
            new = isNewNotes(oldDico, dico)
            oldDico = dico

            if new:
                for subject, note in new:
                    msg = f"@everyone Nouvelle note en **{subject}** : **{note}**"
                    print(f"[{current_time}]",msg)
                    await channel.send(msg)
            else:
                print(f"[{current_time}] ✅ Pas de nouvelles notes.")

        except Exception as e:
            print(f"❌ Erreur pendant le refresh : {e}")

        await asyncio.sleep(120)


client.run(DISCORD_TOKEN)
