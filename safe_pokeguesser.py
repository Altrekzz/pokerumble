import re, time, threading, requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def make_list():
    page = requests.get("https://pokemondb.net/pokedex/national", timeout=10)
    soup = BeautifulSoup(page.text, "html.parser")
    pokedex = {}
    containers = soup.select("span.infocard-lg-data.text-muted")
    for pokemon in containers:
        num_tag = pokemon.find("small")
        if not num_tag:
            continue
        num = re.sub(r"\D", "", num_tag.text or "")
        name_tag = pokemon.select_one(".ent-name")
        if not name_tag:
            continue
        name = name_tag.text.strip()
        try:
            pokedex[int(num)] = name
        except:
            pass
    return pokedex

try:
    pokedex = make_list()
except Exception:
    pokedex = {1: "Bulbasaur", 4: "Charmander", 7: "Squirtle", 25: "Pikachu", 133: "Eevee", 150: "Mewtwo", 151: "Mew"}

driver = webdriver.Chrome()
driver.get("http://localhost:5000")

loop_running = True

def main_loop():
    last_url = None
    while loop_running:
        try:
            img = driver.find_element(By.CSS_SELECTOR, "#pokemon-img")
            current_url = img.get_attribute("src")
            if current_url != last_url:
                m = re.search(r"/pokemon/(\d+)", current_url)
                if m:
                    key = int(m.group(1))
                    name = pokedex.get(key, "")
                    if name:
                        input_box = driver.find_element(By.ID, "guess")
                        input_box.clear()
                        input_box.send_keys(name)
                        submit = driver.find_element(By.ID, "submit")
                        submit.click()
                last_url = current_url
        except Exception:
            pass
        time.sleep(0.12)

t = threading.Thread(target=main_loop, daemon=True)
t.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    loop_running = False
    driver.quit()
