from datetime import datetime
import urllib.request
import time
import os
import json
import re

class Scraping:
    def __init__(self, driver, country, championship, year):
        self.__date = datetime.now().strftime('%Y%m%d%H%M%S')

        self.__driver = driver
        self.__country = country
        self.__championship = championship
        self.__year = year
        
        self.__path = f'./data/{country}-{championship}-{year}/'
        self.__teams_path = f'{self.__path}/teams/'
        self.__teams_images_path = f'{self.__path}/teams/images/'
        self.__players_path = f'{self.__path}/players/'
        self.__players_images_path = f'{self.__path}/players/images/'
        self.__rounds_path = f'{self.__path}/rounds/'

        try: os.makedirs(self.__path)
        except: pass
        try: os.makedirs(self.__teams_path)
        except: pass
        try: os.makedirs(self.__teams_images_path)
        except: pass
        try: os.makedirs(self.__players_path)
        except: pass
        try: os.makedirs(self.__players_images_path)
        except: pass
        try: os.makedirs(self.__rounds_path)
        except: 
            rounds = range(50)
            for round in rounds:
                try: os.remove(f'{self.__rounds_path}{round}/round.json')
                except: pass

    def __scroll_to_bottom_home_page(self):
        while True:
            try:
                time.sleep(2)
                self.__driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(2)
                self.__driver.find_element_by_css_selector('a.event__more.event__more--static').click()
            except:
                break

    def __get_last_matches_id(self):
        url = f'https://www.flashscore.com/football/{self.__country}/{self.__championship}-{self.__year}/results/'
        self.__driver.get(url)

        self.__scroll_to_bottom_home_page()
        last_matches_id = self.__driver.find_elements_by_css_selector('div.event__match.event__match--static.event__match--oneLine')
        last_matches_id = [div.get_attribute('id') for div in last_matches_id]  
        last_matches_id = list(map(lambda match_id: match_id.replace('g_1_', ''), last_matches_id))

        return last_matches_id

    def __get_next_matches_id(self):
        url = f'https://www.flashscore.com/football/{self.__country}/{self.__championship}-{self.__year}/fixtures/'
        self.__driver.get(url)

        self.__scroll_to_bottom_home_page()
        next_matches_id = self.__driver.find_elements_by_css_selector('div.event__match.event__match--static.event__match--oneLine')
        next_matches_id = [div.get_attribute('id') for div in next_matches_id]  
        next_matches_id = list(map(lambda match_id: match_id.replace('g_1_', ''), next_matches_id))

        return next_matches_id

    def __get_matches_id(self):
        last_matches_id = self.__get_last_matches_id()
        next_matches_id = self.__get_next_matches_id()
        matches_id = last_matches_id + next_matches_id

        return matches_id

    def get_match_data(self, match_id):
        url = f'https://www.flashscore.com/match/{match_id}/#match-summary'
        self.__driver.get(url)

        round = self.__driver.find_element_by_css_selector('span.description__country a').text
        round = round.split('- ')[1]
        round = re.search(r'\d+', round).group()

        path = f'{self.__rounds_path}{round}/'
        try: os.makedirs(path)
        except: pass

        path_data_round = f'{path}round.json'
        with open(path_data_round, 'a', encoding='utf-8') as file:
            file.write(f'{match_id},')

        try:
            path_data = f'{path}{match_id}.json'
            with open(path_data) as file:
                match_data = json.load(file)
                statistics = match_data['statistics'] 
                status = match_data['status']
                if not statistics:
                    raise Exception('Empty')
                return match_data
        except:
            pass

        date = self.__driver.find_element_by_css_selector('div#utime').text

        teams = self.__driver.find_elements_by_css_selector('div.tomyteams')
        teams = [a.get_attribute('id').replace('tomyteams_1_', '') for a in teams]
        home_id = teams[0]
        away_id = teams[1]

        teams = self.__driver.find_elements_by_css_selector('div.side-images-row a.participant-imglink')
        teams = [a.get_attribute('onclick') for a in teams]
        home_url = teams[0].replace('window.open(\'', 'https://www.flashscore.com')
        home_url = home_url.replace('\'); return false;', '')
        away_url = teams[1].replace('window.open(\'', 'https://www.flashscore.com')
        away_url = away_url.replace('\'); return false;', '')

        time.sleep(2)
        status = self.__driver.find_element_by_css_selector('div.match-info div.mstat').text
        
        home_score = away_score = stadium = ''
        statistics = {}
        try:
            match_information = self.__driver.find_elements_by_css_selector('div.content')
            match_information = [content for content in match_information]
            stadium = match_information[1].text.replace('Venue: ', '')

            score = self.__driver.find_elements_by_css_selector('div.current-result span.scoreboard')
            score = [span.text for span in score]
            home_score = score[0]
            away_score = score[1]

            url = f'https://www.flashscore.com/match/{match_id}/#match-statistics;0'
            self.__driver.get(url)

            time.sleep(2)
            statistics_title = self.__driver.find_elements_by_css_selector('div.statText--titleValue')
            statistics_title = [div.text for div in statistics_title]
            statistics_title = list(filter(None, statistics_title))

            statistics_home = self.__driver.find_elements_by_css_selector('div.statText--homeValue')
            statistics_home = [div.text.replace('%', '') for div in statistics_home]
            statistics_home = list(filter(None, statistics_home))

            statistics_away = self.__driver.find_elements_by_css_selector('div.statText--awayValue')
            statistics_away = [div.text.replace('%', '') for div in statistics_away]
            statistics_away = list(filter(None, statistics_away))

            for index, statistic in enumerate(statistics_title):
                statistics[statistic] = {}
                statistics[statistic]['home'] = statistics_home[index]
                statistics[statistic]['away'] = statistics_away[index]
        except:
            pass

        match_data = {}
        match_data['id'] = match_id

        match_data['home'] = {}
        match_data['home']['id'] = home_id
        match_data['home']['url'] = home_url
        match_data['home']['score'] = home_score

        match_data['away'] = {}
        match_data['away']['id'] = away_id
        match_data['away']['url'] = away_url
        match_data['away']['score'] = away_score

        match_data['date'] = date
        match_data['stadium'] = stadium
        match_data['round'] = round
        match_data['status'] = status
        match_data['statistics'] = statistics

        with open(path_data, 'w', encoding='utf-8') as file:
            json.dump(match_data, file, ensure_ascii=False, indent=4)

        if not statistics:
            return match_data

        self.get_team_data(home_id, home_url)
        self.get_team_data(away_id, away_url)

        return match_data

    def __get_players_data(self, team_url):
        url = f'{team_url}/squad'
        self.__driver.get(url)

        table = self.__driver.find_element_by_css_selector('div#league-4pP4CTWM-table')

        players_number = table.find_elements_by_css_selector('div.tableTeam__squadNumber')
        players_number = [div.get_attribute('innerHTML') for div in players_number]
        del players_number[0]

        players_nationality = table.find_elements_by_css_selector('div.tableTeam__squadName span')
        players_nationality = [span.get_attribute('title') for span in players_nationality]
        players_nationality = list(filter(lambda nationality: nationality != 'Injury', players_nationality))
        
        players_url = table.find_elements_by_css_selector('div.tableTeam__squadName--playerName a')
        players_url = [a.get_attribute('href') for a in players_url]

        players_id = [url.split('/')[5] for url in players_url]

        players_name = table.find_elements_by_css_selector('div.tableTeam__squadName--playerName a')
        players_name = [a.get_attribute('innerHTML') for a in players_name]

        players_statistics_container = table.find_elements_by_css_selector('div.playerTable__icons.playerTable__icons--squad')
        players_age = []
        players_matches_played = []
        players_goals_scored = []
        players_yellow_cards = []
        players_red_cards =[]
        for players_statistics in players_statistics_container:
            statistics = players_statistics.find_elements_by_css_selector('div.playerTable__sportIcon')
            
            age = statistics[0].get_attribute('innerHTML')
            matches_played = statistics[1].get_attribute('innerHTML')
            goals_scored = statistics[2].get_attribute('innerHTML')
            yellow_cards = statistics[3].get_attribute('innerHTML')
            red_cards = statistics[4].get_attribute('innerHTML')

            players_age.append(age)
            players_matches_played.append(matches_played)
            players_goals_scored.append(goals_scored)
            players_yellow_cards.append(yellow_cards)
            players_red_cards.append(red_cards)

        players_image = []
        players_position = []
        for index, url in enumerate(players_url):
            try:
                path_data = f'{self.__players_images_path}{players_id[index]}.png'
                with open(path_data) as file:
                    pass
                path_data = f'{self.__players_path}{players_id[index]}.json'
                with open(path_data) as file:
                    player_data = json.load(file)
                    players_image.append(player_data['image'])
                    players_position.append(player_data['position'])
            except:
                self.__driver.get(url)
                
                image = self.__driver.find_element_by_css_selector('div.teamHeader__logo').get_attribute('style')
                image = image.replace('background-image: url("', 'https://www.flashscore.com')
                image = image.replace('");', '')

                position = self.__driver.find_element_by_css_selector('div.teamHeader__info--player-type-name').get_attribute('innerHTML')
                position = position.split(' (<a')[0]

                players_image.append(image)
                players_position.append(position)

        for index, player_id in enumerate(players_id):
            player_data = {}
            player_data['id'] = player_id
            player_data['name'] = players_name[index]
            player_data['image'] = players_image[index]
            player_data['number'] = players_number[index]
            player_data['nationality'] = players_nationality[index]
            player_data['position'] = players_position[index]
            player_data['url'] = players_url[index]
            player_data['age'] = players_age[index]
            player_data['matches_played'] = players_matches_played[index]
            player_data['goals_scored'] = players_goals_scored[index]
            player_data['yellow_cards'] = players_yellow_cards[index]
            player_data['red_cards'] = players_red_cards[index]

            try:
                urllib.request.urlretrieve(players_image[index], f'{self.__players_images_path}{player_id}.png')
            except:
                pass

            path_data = f'{self.__players_path}{player_id}.json'

            with open(path_data, 'w', encoding='utf-8') as file:
                json.dump(player_data, file, ensure_ascii=False, indent=4)

        return players_id

    def get_team_data(self, team_id, team_url):
        path_data = f'{self.__teams_path}{team_id}.json'

        url = team_url
        self.__driver.get(url)

        image = self.__driver.find_element_by_css_selector('div.teamHeader__logo')
        image = image.get_attribute('style')
        image = image.replace('background-image: url("', 'https://www.flashscore.com')
        image = image.replace('");', '')

        try:
            urllib.request.urlretrieve(image, f'{self.__teams_images_path}{team_id}.png')
        except:
            pass

        name = self.__driver.find_element_by_css_selector('div.teamHeader__name').text

        players = self.__get_players_data(team_url)

        team_data = {}
        team_data['id'] = team_id
        team_data['name'] = name
        team_data['image'] = image
        team_data['players'] = players

        with open(path_data, 'w', encoding='utf-8') as file:
            json.dump(team_data, file, ensure_ascii=False, indent=4)

        return team_data

    def collect(self):
        matches_id = self.__get_matches_id()
        for match_id in matches_id:
            self.get_match_data(match_id)
            print(f'Collect {match_id}')

        path_data = f'{self.__path}data.json'
        timestamp = int(time.time())
        with open(path_data, 'w', encoding='utf-8') as file:
            file.write(str(timestamp))
