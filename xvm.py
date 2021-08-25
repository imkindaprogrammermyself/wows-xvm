import requests
import json
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor
from importlib.resources import read_text

API_ID = "cc166381e1ed2a25fbb538bcf7d445f2"
IGNORE_FIELDS = """-pvp.losses, -pvp.draws, -pvp.max_xp, -pvp.survived_battles, -pvp.max_frags_battle, 
-pvp.dropped_capture_points, -pvp.damage_to_buildings, -pvp.max_damage_scouting, -pvp.team_dropped_capture_points, 
-pvp.art_agro, -pvp.aircraft, -pvp.max_suppressions_count, -pvp.survived_wins, -pvp.battles_since_512, 
-pvp.max_damage_dealt_to_buildings, -pvp.suppressions_count, -pvp.xp, -pvp.battles_since_510, -pvp.ramming, 
-pvp.max_damage_dealt, -pvp.max_ships_spotted, -pvp.main_battery, -pvp.capture_points, -pvp.team_capture_points, 
-pvp.torpedoes, -pvp.torpedo_agro, -pvp.ships_spotted, -pvp.planes_killed, -pvp.max_total_agro, -pvp.max_planes_killed, 
-pvp.second_battery, -pvp.damage_scouting, -last_battle_time, -account_id, -distance, -updated_at, -battles, -private"""


class Xvm:
    def __init__(self):
        self._api_realms = {
            "ASIA": "https://api.worldofwarships.asia/wows/ships/stats/",
            "NA": "https://api.worldofwarships.com/wows/ships/stats/",
            "EU": "https://api.worldofwarships.eu/wows/ships/stats/",
            "RU": "https://api.worldofwarships.ru/wows/ships/stats/",
            "CIS": "https://api.worldofwarships.ru/wows/ships/stats/"
        }
        self._expected_values = self._load_default()
        self._ship_info: dict = self._load_ship_info()

    @staticmethod
    def _load_default():
        return {int(k): v for k, v in
                json.loads(read_text(f"resources", "expected_values.json"))['data'].items()}

    @staticmethod
    def _load_ship_info():
        return json.loads(read_text("resources", "ships.json"))

    @staticmethod
    def _get_pr_color(pr: int):
        colors = {
            0xd3d3d3: (-1, 0),
            0xFE0E00: (0, 751),
            0xFE7903: (751, 1101),
            0xFFC71F: (1101, 1351),
            0x44B300: (1351, 1551),
            0x318000: (1551, 1751),
            0x02C9B3: (1751, 2101),
            0xD042F3: (2101, 2451),
            0xA00DC5: (2451, 10000)
        }
        for color, pr_range in colors.items():
            if pr in range(*pr_range):
                return int(color)

    def _fetch_ships(self, player):
        try:
            response = requests.post(self._api_realms[player['realm']], data={
                "application_id": API_ID,
                "account_id": f"{player['accountDBID']}",
                "fields": IGNORE_FIELDS,
                "language": "en"
            })
            if response.status_code != 200:
                raise Exception

            player_data = response.json()

            if player_data['status'] == "error":
                raise Exception

            if player_data['meta']['hidden']:
                raise Exception

            return player, response.json()['data'].popitem()[1]

        except Exception:
            return player, None

    @staticmethod
    def _calculate_ship_pr(data):
        pvp_data, expected_data = data
        try:
            p_battles = pvp_data['battles']
            assert p_battles > 0
            p_damage_avg = pvp_data['damage_dealt']
            p_wins = pvp_data['wins']
            p_frags = pvp_data['frags']

            e_damage_avg = expected_data['average_damage_dealt'] * p_battles
            e_win_rate = expected_data['win_rate'] * p_battles / 100
            e_frags = expected_data['average_frags'] * p_battles
            return True, p_damage_avg, p_wins, p_frags, e_damage_avg, e_win_rate, e_frags
        except AssertionError:
            return tuple([False, *map(int, "0" * 6)])
        except TypeError:
            return tuple([False, *map(int, "0" * 6)])

    def _calculate_player_pr(self, data):
        player_data, ships = data

        if player_data["accountDBID"] < 0:
            return player_data, -1

        try:
            if not ships:
                return player_data, -1

            to_calculate = []

            for ship in ships:
                ship_id = ship['ship_id']

                if ship_id not in self._expected_values:
                    continue

                pvp_data = ship['pvp']
                expected_data = self._expected_values[ship_id]
                to_calculate.append((pvp_data, expected_data))

            calculated = list(map(self._calculate_ship_pr, to_calculate))
            has_battles, a_damage, a_wins, a_frags, e_damage, e_wins, e_frags = tuple(map(sum, zip(*calculated)))

            if not has_battles:
                return player_data, -1

            def do_div(dd):
                try:
                    dvd, dvs = dd
                    assert dvd != 0
                    assert dvs != 0
                    return dvd / dvs
                except AssertionError:
                    return -1

            r_damage, r_wins, r_frags = map(do_div, [(a_damage, e_damage), (a_wins, e_wins), (a_frags, e_frags)])

            n_damage = max(0, (r_damage - 0.4) / (1 - 0.4))
            n_wins = max(0, (r_wins - 0.7) / (1 - 0.7))
            n_frags = max(0, (r_frags - 0.1) / (1 - 0.1))
            rating = round((700 * n_damage) + (300 * n_frags) + (150 * n_wins))

            return player_data, rating
        except Exception:
            return player_data, -1

    async def _get_rating(self, players):
        with ThreadPoolExecutor(max_workers=10) as tpe:
            results = tpe.map(self._fetch_ships, players)

            ally_team = []
            enemy_team = []
            for player in map(self._calculate_player_pr, results):
                player_data, rating = player
                try:
                    ship_data = self._ship_info[str(player_data["shipParamsId"])]
                    _temp = {
                        "accountDBID": player_data["accountDBID"],
                        "color": self._get_pr_color(rating),
                        "rating": rating,
                        "species": ship_data["species"],
                        "level": ship_data["level"],
                        "name": ship_data["name"]
                    }

                    if player_data["is_ally"]:
                        ally_team.append(_temp)
                    else:
                        enemy_team.append(_temp)
                except Exception:
                    pass

            ally_team.sort(key=lambda o: (o["species"], -o["level"]))
            enemy_team.sort(key=lambda o: (o["species"], -o["level"]))
            ally_team.extend(enemy_team)

            return ally_team

    async def _report(self, request):
        data = await request.json()
        ratings = await self._get_rating(data)
        return web.json_response(data=ratings)

    def start(self):
        app = web.Application()
        app.router.add_post("/report", self._report)
        web.run_app(app, port=8080)


if __name__ == '__main__':
    a = Xvm()
    a.start()
