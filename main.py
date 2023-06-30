from playwright.sync_api import sync_playwright
from datetime import date
import json

#Loads the top-30 ranking dictionary from folder
with open(r"C:\Users\Ryan\PycharmProjects\NationalsFarmProject\playersIdDictionary.json", "r") as file:
    loaded_dict = json.load(file)

with open(r"C:\Users\Ryan\PycharmProjects\NationalsFarmProject\playersNameDictionary.json", "r") as file:
    top30list = json.load(file)

def get_updated_prospects():
    star = '\u2605'
    playerDictionary = {}
    playerIds = []
    playerIdDictionary = {}

    with sync_playwright() as p:
        print('Updating top 30 prospect dictionary...')
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto('https://www.mlb.com/prospects/nationals')
        page.wait_for_timeout(500)
        button = page.locator('button.load-more__button[data-testid="load-more-button"]')
        page.wait_for_timeout(2000)
        button.click()
        button.click()
        page.wait_for_timeout(2000)
        top30list = page.query_selector('.rankings__table.rankings__table--team')
        if top30list == None:
            button.click()
            page.wait_for_timeout(10000)
        rows = top30list.query_selector_all('tbody tr')
        if len(rows) < 30:
            button.click()
            page.wait_for_timeout(10000)
        top30list = page.query_selector('.rankings__table.rankings__table--team')
        rows = top30list.query_selector_all('tbody tr')
        for row in rows:
            cells = row.query_selector_all('td')
            playerDictionary[cells[1].inner_text()] = cells[0].inner_text()
            row.click()
            playerIds.append(page.url[-6:])
            page.go_back()
        for index, value in enumerate(playerDictionary.values()):
            playerIdDictionary[playerIds[index]] = f"({star}No.{value})"

        with open(r"C:\Users\Ryan\PycharmProjects\NationalsFarmProject\playersIdDictionary.json", "w") as file:
            json.dump(playerIdDictionary, file)

        with open(r"C:\Users\Ryan\PycharmProjects\NationalsFarmProject\playersNameDictionary.json", "w") as file:
            json.dump(playerDictionary, file)
#this method simply adds a box around each batter; makes things easier to read
def print_boxed_text(text):
    lines = text.splitlines()
    max_length = max(len(line) for line in lines)
    border = '+' + '-' * (max_length + 2) + '+'

    print(border)
    for line in lines:
        print(f'| {line.ljust(max_length)} |')
    print(border)



#These are the possible team names that could show up for a nationals minor league affiliate
possibleNatsTeams =['DSL NAT', 'NAT', 'ROC', 'WIL', 'FBG','HBG']

#general user input information; also grabs the current date from the date module


while True:
    todaysDate = date.today()
    with open(r"C:\Users\Ryan\PycharmProjects\NationalsFarmProject\Title", "r") as file:
        file_contents = file.read()
        print(file_contents)
    print(
        f"Welcome to the washington nationals farm report. Enter the date you want a report (YYYY-MM-DD) on or simply type today for todays report ({todaysDate}):")
    print(
        "You can also view the current top-30 prospect list by typing view. If this list is innacurate type update. All rankings are from mlb pipeline and are noted with a ★")
    print(
        "Please note that this program displays the current date meaning that if its the next morning you may want to input the date of the night before :D")
    userInput = input().lower()
    if userInput == 'today':
        link = f"https://www.milb.com/scores/{todaysDate}/all/all/nationals"
        break
    elif userInput == 'view':
        for key, value in top30list.items():
            print(f"{value}. {key}")
    elif userInput == 'update':
        get_updated_prospects()
    else:
        link = f"https://www.milb.com/scores/{userInput}/all/all/nationals"
        break

with sync_playwright() as p:

    #grabs gameday links from the date
    print('Harvesting nationals farm system info....')
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(link)
    page.wait_for_timeout(500)
    elements = page.query_selector_all(
        '.linkstyle__AnchorElement-sc-1rt6me7-0.jfdfHw.getProductButtons__ButtonLink-sc-bgnczd-1.elIcfn.trk-box')
    href_list = []
    for element in elements:
        href_value = element.get_attribute('href')
        href_list.append(href_value)
    if len(href_list) < 1:
        print('There were no games found for this date please make sure that you inputted the proper date')
    browser.close()


    #goes through each link that is retrieved above
    for index, site in enumerate(href_list):

        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(site)
        page.wait_for_timeout(500)
        header = page.query_selector('.header')
        finalScore = header.inner_text()
        gameLine = f'Game Number {str(index + 1)}:\nFinal Score: {finalScore}'
        print(gameLine)

        tables = page.query_selector_all('table.avgops-table')  # Select the table element
        lineup = []
        for index, table in enumerate(tables):
            teamName = table.query_selector('.city-abbrev').inner_text().strip()

            if teamName not in possibleNatsTeams:
                continue

            rows = tables[index].query_selector_all('tbody tr')  # Select all rows within the table body

            for rownum, row in enumerate(rows):
                playerGameInfo = {}
                cells = row.query_selector_all('td')  # Select all cells within each row

                # first index of each row has playerinfocontainer we scrape that and assign the respective information to the dictionary

                playerInfo = cells[0].query_selector('.player-info-container')
                if playerInfo is not None:
                    # Gets the batting order of the player and adds it to the dictionary
                    battingOrder = playerInfo.query_selector('.batting-order')
                    playerGameInfo['BattingOrder'] = battingOrder.inner_text()

                    # Gets the name of the player and adds it to the dictionary
                    playerName = playerInfo.query_selector('.name')
                    playerGameInfo['playerName'] = playerName.inner_text()

                    # Gets the position of the player and adds it to the dictionary
                    position = playerInfo.query_selector('.position')
                    playerGameInfo['position'] = position.inner_text()

                    # Gets number of at bats and adds to the dictionary
                    playerGameInfo['numberofAbs'] = cells[1].inner_text()

                    # Gets rest of stats
                    playerGameInfo['runsScored'] = cells[2].inner_text()
                    playerGameInfo['playerHits'] = cells[3].inner_text()
                    playerGameInfo['playerRBIs'] = int(cells[4].inner_text())
                    playerGameInfo['playerWalks'] = int(cells[5].inner_text())
                    playerGameInfo['playerSOs'] = int(cells[6].inner_text())

                    idElement = playerInfo.query_selector('span.name a[data-player-link]')
                    thisId = idElement.get_attribute("data-player-link")
                    top30ranking = ''
                    if thisId in loaded_dict:
                        top30ranking = loaded_dict[thisId]

                    lineupString = (f"{playerGameInfo['BattingOrder']}. {playerGameInfo['playerName']} {playerGameInfo['position']} {top30ranking}\n"
                    f"{playerGameInfo['playerHits']}-{playerGameInfo['numberofAbs']}    "
                    f"{playerGameInfo['playerRBIs']}RBIS, {playerGameInfo['playerWalks']}BBS, {playerGameInfo['playerSOs']}KS")
                    print_boxed_text(lineupString)
