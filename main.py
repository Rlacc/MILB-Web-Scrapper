from playwright.sync_api import sync_playwright
from datetime import date
import json
def print_boxed_text(text):
    lines = text.splitlines()
    max_length = max(len(line) for line in lines)
    border = '+' + '-' * (max_length + 2) + '+'

    print(border)
    for line in lines:
        print(f'| {line.ljust(max_length)} |')
    print(border)

def top_30_prospects():
    print('poop')

#These are the possible team names that could show up for a nationals minor league affiliate
possibleNatsTeams =['DSL NAT', 'NAT', 'ROC', 'WIL', 'FBG','HBG']

#general user input information; also grabs the current date from the date module
todaysDate = date.today()
with open(r"C:\Users\Ryan\PycharmProjects\NationalsFarmProject\Title", "r") as file:
    file_contents = file.read()
    print(file_contents)
print(f"Welcome to the washington nationals farm report. Enter the date you want a report (YYYY-MM-DD) on or simply type today for todays report {todaysDate}:")
print("Please note that this program displays the current date meaning that if its the next morning you may want to input the date of the night before :D")
userInput = input()


if userInput == 'today':
    link = f"https://www.milb.com/scores/{todaysDate}/all/all/nationals"
else:
    link = f"https://www.milb.com/scores/{userInput}/all/all/nationals"

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


                    lineupString = (f"{playerGameInfo['BattingOrder']}. {playerGameInfo['playerName']} {playerGameInfo['position']} \n"
                    f"{playerGameInfo['playerHits']}-{playerGameInfo['numberofAbs']}    "
                    f"{playerGameInfo['playerRBIs']}RBIS, {playerGameInfo['playerWalks']}BBS, {playerGameInfo['playerSOs']}KS")
                    print_boxed_text(lineupString)
