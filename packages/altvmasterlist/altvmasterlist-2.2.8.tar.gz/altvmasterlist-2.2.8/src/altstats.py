#!/usr/bin/env python3

from json import loads
from re import compile
import requests
import logging
import secrets
import sys

logging.basicConfig(level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)


# Masterlist API Docs: https://docs.altv.mp/articles/master_list_api.html

# This is the config object for this package
# Here can you configure stuff like the api endpoint or the url format
class Config:
    base_link = "https://api.altstats.net/api/v1/"
    all_server_stats_link = f"{base_link}/master"
    all_servers_link = f"{base_link}/server"
    server_link = f"{base_link}/server/" + "{}"


logging.debug(f'starting with base link: {Config.base_link}')


# This is the server object
class Server:
    # initialize the object with all values that are available in the alt:V masterlist API
    def __init__(self, Id, FoundAt, LastActivity, Visible, ServerId, Players, Name, Locked, Ip, Port, MaxPlayers, Ping,
                 Website, Language, Description, LastUpdate, IsOfficial, PlayerRecord, PlayerRecordDate,
                 LastFetchOnline, LanguageShort, GameMode, Branch, Build, CdnUrl, EarlyAuthUrl, Verified, UseCdn,
                 UseEarlyAuth, BannerUrl, Promoted, Tags, UseVoiceChat, Level, Version):
        self.Id = Id
        self.FoundAt = FoundAt
        self.LastActivity = LastActivity
        self.Visible = Visible
        self.ServerId = ServerId
        self.Players = Players
        self.Name = Name
        self.Locked = Locked
        self.Ip = Ip
        self.Port = Port
        self.MaxPlayers = MaxPlayers
        self.Ping = Ping
        self.Website = Website
        self.Language = Language
        self.Description = Description
        self.LastUpdate = LastUpdate
        self.IsOfficial = IsOfficial
        self.PlayerRecord = PlayerRecord
        self.PlayerRecordDate = PlayerRecordDate
        self.LastFetchOnline = LastFetchOnline
        self.LanguageShort = LanguageShort
        self.GameMode = GameMode
        self.Branch = Branch
        self.Build = Build
        self.CdnUrl = CdnUrl
        self.EarlyAuthUrl = EarlyAuthUrl
        self.Verified = Verified
        self.UseCdn = UseCdn
        self.UseEarlyAuth = UseEarlyAuth
        self.BannerUrl = BannerUrl
        self.Promoted = Promoted
        self.Tags = Tags
        self.UseVoiceChat = UseVoiceChat
        self.Level = Level
        self.Version = Version

    # return the current server data as JSON object
    def get_json(self):
        return {
            "Id": self.Id,
            "FoundAt": self.FoundAt,
            "LastActivity": self.LastActivity,
            "Visible": self.Visible,
            "ServerId": self.ServerId,
            "Players": self.Players,
            "Name": self.Name,
            "Locked": self.Locked,
            "Ip": self.Ip,
            "Port": self.Port,
            "MaxPlayers": self.MaxPlayers,
            "Ping": self.Ping,
            "Website": self.Website,
            "Language": self.Language,
            "Description": self.Description,
            "LastUpdate": self.LastUpdate,
            "IsOfficial": self.IsOfficial,
            "PlayerRecord": self.PlayerRecord,
            "PlayerRecordDate": self.PlayerRecordDate,
            "LastFetchOnline": self.LastFetchOnline,
            "LanguageShort": self.LanguageShort,
            "GameMode": self.GameMode,
            "Branch": self.Branch,
            "Build": self.Build,
            "CdnUrl": self.CdnUrl,
            "EarlyAuthUrl": self.EarlyAuthUrl,
            "Verified": self.Verified,
            "UseCdn": self.UseCdn,
            "UseEarlyAuth": self.UseEarlyAuth,
            "BannerUrl": self.BannerUrl,
            "Promoted": self.Promoted,
            "Tags": self.Tags,
            "UseVoiceChat": self.UseVoiceChat,
            "Level": self.Level,
            "Version": self.Version
        }

    # fetch the server data and replace it
    def update(self):
        temp_server = get_server_by_id(self.Id)

        # check if the server is returned
        if temp_server is None:
            # don`t update the server object because the API returned invalid, broken, or no data
            logging.warning(f"the alt:V API returned nothing.")
            return

        self.Id = temp_server.Id
        self.FoundAt = temp_server.FoundAt
        self.LastActivity = temp_server.LastActivity
        self.Visible = temp_server.Visible
        self.ServerId = temp_server.ServerId
        self.Players = temp_server.Players
        self.Name = temp_server.Name
        self.Locked = temp_server.Locked
        self.Ip = temp_server.Ip
        self.Port = temp_server.Port
        self.MaxPlayers = temp_server.MaxPlayers
        self.Ping = temp_server.Ping
        self.Website = temp_server.Website
        self.Language = temp_server.Language
        self.Description = temp_server.Description
        self.LastUpdate = temp_server.LastUpdate
        self.IsOfficial = temp_server.IsOfficial
        self.PlayerRecord = temp_server.PlayerRecord
        self.PlayerRecordDate = temp_server.PlayerRecordDate
        self.LastFetchOnline = temp_server.LastFetchOnline
        self.LanguageShort = temp_server.LanguageShort
        self.GameMode = temp_server.GameMode
        self.Branch = temp_server.Branch
        self.Build = temp_server.Build
        self.CdnUrl = temp_server.CdnUrl
        self.EarlyAuthUrl = temp_server.EarlyAuthUrl
        self.Verified = temp_server.Verified
        self.UseCdn = temp_server.UseCdn
        self.UseEarlyAuth = temp_server.UseEarlyAuth
        self.BannerUrl = temp_server.BannerUrl
        self.Promoted = temp_server.Promoted
        self.Tags = temp_server.Tags
        self.UseVoiceChat = temp_server.UseVoiceChat
        self.Level = temp_server.Level
        self.Version = temp_server.Version

    # use this function to fetch the server connect json
    # this file has every resource of the server with a hash and name
    def fetch_connect_json(self):
        if not self.UseCdn and not self.Locked and self.LastFetchOnline:
            # This Server is not using a CDN.
            cdn_request = request(f"http://{self.Ip}:{self.Port}/connect.json", True, self)
            if cdn_request is None:
                # possible server error or blocked by alt:V
                return None
            else:
                return cdn_request
        else:
            # let`s try to get the connect json
            cdn_request = request(f"{self.CdnUrl}/connect.json")
            if cdn_request is None:
                # maybe the CDN is offline
                return None
            else:
                return cdn_request

    # get the "Direct Connect Protocol" url
    # e.g. altv://connect/127.0.0.1:7788?password=xyz
    # https://docs.altv.mp/articles/connectprotocol.html
    # cdn off: altv://connect/${IP_ADDRESS}:${PORT}?password=${PASSWORD}
    # cdn on: altv://connect/{CDN_URL}?password=${PASSWORD}
    def get_dtc_url(self, password=None):
        dtc_url = ""
        if self.UseCdn:
            if not "http" in self.CdnUrl:
                dtc_url += f"altv://connect/http://{self.CdnUrl}"
            else:
                dtc_url += f"altv://connect/{self.CdnUrl}"
        else:
            dtc_url += f"altv://connect/{self.Ip}:{self.Port}"

        if self.Locked and password is None:
            logging.warning(
                "Your server is password protected but you did not supply a password for the Direct Connect Url.")

        if password is not None:
            dtc_url += f"?password={password}"

        return dtc_url

    # fetch the required and optional permissions of the server
    # available permissions:
    # Screen Capture: This allows a screenshot to be taken of the alt:V process (just GTA) and any webview
    # WebRTC: This allows peer-to-peer RTC inside JS
    # Clipboard Access: This allows to copy content to users clipboard
    def get_permissions(self):
        permissions = {
            "required": {
                "Screen Capture": False,
                "WebRTC": False,
                "Clipboard Access": False
            },
            "optional": {
                "Screen Capture": False,
                "WebRTC": False,
                "Clipboard Access": False
            }
        }

        # fetch connect json
        data = self.fetch_connect_json()
        if data is None:
            return None
        optional = data["optional-permissions"]
        required = data["required-permissions"]

        if optional is not []:
            for permission in optional:
                permissions["optional"][permission] = True

        if required is not []:
            for permission in required:
                permissions["required"][permission] = True

        return permissions


def request(url, cdn=False, server=[]):
    # Use the User-Agent: AltPublicAgent, because some servers protect their CDN with
    # a simple User-Agent check e.g. https://luckyv.de does that
    if "http://" in url and cdn:
        req_headers = {
            "host": "",
            'user-agent': 'AltPublicAgent',
            "accept": '*/*',
            'alt-debug': 'false',
            'alt-password': '17241709254077376921',
            'alt-branch': server.branch,
            'alt-version': server.version,
            'alt-player-name': secrets.token_urlsafe(10),
            'alt-social-id': secrets.token_hex(9),
            'alt-hardware-id2': secrets.token_hex(19),
            'alt-hardware-id': secrets.token_hex(19)
        }
    else:
        req_headers = {
            'User-Agent': 'AltPublicAgent',
            'content-type': 'application/json; charset=utf-8'
        }

    try:
        api_data = requests.get(url, headers=req_headers, timeout=60)
        if api_data.status_code != 200:
            logging.warning(f"the request returned nothing.")
            return None
        else:
            return loads(api_data.content.decode("utf-8", errors='ignore'))
    except Exception as e:
        logging.error(e)
        return None


# Fetch the stats of all servers that are currently online
# e.g. [
#   {
#     "ServerCount": 72,
#     "PlayerCount": 958,
#     "TimeStamp": "2021-01-01T12:15:00.464Z"
#   },
#   {
#     "ServerCount": 73,
#     "PlayerCount": 945,
#     "TimeStamp": "2021-01-01T12:10:00.465Z"
#   },
#   {
#     "others": "..."
#   }
# ]
def get_server_stats():
    data = request(Config.all_server_stats_link)
    if data is None:
        return None
    else:
        return data


# Get all Servers that are online as Server object
def get_servers():
    return_servers = []
    servers = request(Config.all_servers_link)
    if servers is None or servers == "{}":
        return None
    else:
        for server in servers:
            # Now change every JSON response to a server object that we can e.g. update it when we want
            temp_server = Server(server["id"], None, None, None,
                                 None, server["playerCount"], server["name"],
                                 bool(server["locked"]), None, None,
                                 server["slots"], None,
                                 None, server["language"]["full"],
                                 None, None,
                                 bool(server["official"]), None, None,
                                 None, server["language"]["short"], server["gameMode"],
                                 None, None, None, None,
                                 bool(server["verified"]), None, None, None,
                                 bool(server["promoted"]), server["tags"], None, None,
                                 None)
            return_servers.append(temp_server)

        return return_servers


# get all servers and calculate the average values
def get_servers_average():
    data = get_server_stats()
    if data is None:
        return None
    start_date = data[-1]["TimeStamp"]
    end_date = data[0]["TimeStamp"]

    server_count_total = 0
    player_count_total = 0

    for entry in data:
        server_count_total += entry["ServerCount"]
        player_count_total += entry["PlayerCount"]

    server_count_avg = round(server_count_total / len(data), 0)
    player_count_avg = round(player_count_total / len(data), 0)

    return start_date, end_date, server_count_avg, player_count_avg


# get a single server by their server id
def get_server_by_id(server_id):
    temp_data = request(Config.server_link.format(server_id))
    if temp_data is None or temp_data == {}:
        # the api returned no data
        return None
    else:
        # Create a Server object with the data and return that
        return Server(server_id, temp_data["FoundAt"], temp_data["LastActivity"], temp_data["Visible"],
                      temp_data["ServerId"], temp_data["Players"], temp_data["Name"],
                      temp_data["Locked"], temp_data["Ip"], temp_data["Port"],
                      temp_data["MaxPlayers"], temp_data["Ping"],
                      temp_data["Website"], temp_data["Language"],
                      temp_data["Description"], temp_data["LastUpdate"],
                      temp_data["IsOfficial"], temp_data["PlayerRecord"], temp_data["PlayerRecordDate"],
                      temp_data["LastFetchOnline"], temp_data["LanguageShort"], temp_data["GameMode"],
                      temp_data["Branch"], temp_data["Build"], temp_data["CdnUrl"], temp_data["EarlyAuthUrl"],
                      temp_data["Verified"], temp_data["UseCdn"], temp_data["UseEarlyAuth"], temp_data["BannerUrl"],
                      temp_data["Promoted"], temp_data["Tags"], temp_data["UseVoiceChat"], temp_data["Level"],
                      temp_data["Version"])


# validate a given alt:V server id
def validate_id(server_id):
    server_id = str(server_id)
    regex = compile(r"^[0-9]{1,}$")
    result = regex.match(server_id)
    if result is not None:
        return True
    else:
        return False


if __name__ == "__main__":
    print("This is a Module!")
    sys.exit()
