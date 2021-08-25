import time
API_VERSION = 'API_v1.0'
MOD_NAME = 'WowsXvm'

URL_ENCODED = 'WxwAAABpziMAAGkbXwAAaRtfAABpomoAAGlkGgAAaSJDAABpIkMAAGmsMQAAaYxdAABpC2kAAGkYOgAAaawxAABpziMAAGmMXQAAaZJxAABpG18AAGlkGgAAaZ4jAABpX0wAAGmeIwAAaV9MAABpIkMAAGlTVAAAabo+AABpomoAAGmMXQAAaVNUAABpG18AAA=='
DECODED_URL = "http://localhost:8080/report"
web.addAllowedUrl(URL_ENCODED)
# devmenu.enable()

class WowsXvm:
    def __init__(self):
        events.onSFMEvent(self._on_sfm_event)
        events.onBattleEnd(self._clear)
        events.onBattleQuit(self._clear)
        events.onKeyEvent(self._on_key_event)
        self._last = 0.0
        self._players = {}

    def _clear(self, *args, **kwargs):
        flash.call('wowsxvm.clear', [])
        self._players.clear()

    def _on_key_event(self, event):
        if event.key == 199:
            if (time.time() - self._last) > 0.250:
                self._last = time.time()
                flash.call('wowsxvm.showHide', [])

    def _on_sfm_event(self, name, data):
        try:
            if name == "window.show" and data["windowName"] == "Battle":
                player_info = battle.getSelfPlayerInfo()
                keys = ["accountDBID", "teamId", "name", "clanID", "realm", "clanColor", "shipParamsId", "clanTag"]
                players = []

                for _, _info in battle.getPlayersInfo().items():
                    player = {
                        "is_ally": _info["teamId"] == player_info["teamId"],
                        "is_player": _info["accountDBID"] == player_info["accountDBID"],
                        "is_bot": True if _info["accountDBID"] < 0 else False
                    }
                    for key in keys:
                        player[key] = _info[key]
                    players.append(player)
                    self._players[_info['accountDBID']] = player

                try:
                    web.openUrlAsync(DECODED_URL, self._web_callback, data = utils.jsonEncode(players))
                except Exception:
                    pass
        except Exception as e:
            raise e

    def _web_callback(self, socket_fp):
        pr_data = utils.jsonDecode(socket_fp.read())
        for data in pr_data:
            local_data = self._players[int(data["accountDBID"])]
            player_name = local_data["name"]
            player_clan = local_data["clanTag"]
            player_pr_color = data["color"]
            player_pr_rating = data["rating"]
            clan_color = local_data["clanColor"]
            is_ally = local_data["is_ally"]
            flash.call('wowsxvm.addPlayer', [player_name, player_pr_color, player_clan, clan_color, is_ally])

            
wx = WowsXvm()