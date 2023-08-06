# leeger

Instant stats for your fantasy football league.

![Main Build](https://github.com/joeyagreco/leeger/actions/workflows/main-build.yml/badge.svg)
![Last Commit](https://img.shields.io/github/last-commit/joeyagreco/leeger)

## Supported Fantasy Sites
Sites that you can automatically load your league data from.

| Name                                                    | Website                                   | Supported          |
|---------------------------------------------------------|-------------------------------------------|--------------------|
| [ESPN](https://github.com/joeyagreco/leeger#espn)       | https://www.espn.com/fantasy/football/    | :heavy_check_mark: |
| MyFantasyLeague                                         | http://home.myfantasyleague.com/          | :x:                |
| NFL                                                     | https://fantasy.nfl.com/                  | :x:                |
| [Sleeper](https://github.com/joeyagreco/leeger#sleeper) | https://sleeper.com/fantasy-football      | :heavy_check_mark: |
| [Yahoo](https://github.com/joeyagreco/leeger#yahoo)     | https://football.fantasysports.yahoo.com/ | :heavy_check_mark: |

If a fantasy site you use is not listed here and you would like it to be,
please [open an issue](https://github.com/joeyagreco/leeger/issues).

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install.

```bash
pip install leeger
```

## Usage

For examples on how to utilize the different features of this library, see
the [`example`](https://github.com/joeyagreco/leeger/tree/main/example) folder.

## League Loaders

### ESPN

##### [Examples](https://github.com/joeyagreco/leeger/blob/main/example/league_loader/espnLeagueLoaderExample.py)

##### League Info Needed [PUBLIC]

- League ID

##### League Info Needed [PRIVATE]

- League ID
- ESPN_S2 parameter
- SWID parameter

[How to find your ESPN league ID.](https://support.espn.com/hc/en-us/articles/360045432432-League-ID#h_01F10X0506BC0R0MYNH6VMNZ04)

To retrieve ESPN_S2 and SWID, follow these steps:

1. Visit your main league page (
   i.e. https://fantasy.espn.com/football/team?leagueId={your_league_id}seasonId={any_season})
2. Make sure you are logged in.
3. Open Developer Tools (on Chrome/Firefox, right-click anywhere on the page and select Inspect Element)
4. Go to Storage (for Firefox) or Application (for Chrome) and browse the Cookies available for fantasy.espn.com
5. The values you need are called "SWID" and "ESPN_S2". You can right-click and copy the values from here.

### Sleeper

##### [Examples](https://github.com/joeyagreco/leeger/blob/main/example/league_loader/sleeperLeagueLoaderExample.py)

##### League Info Needed

- League ID

[How to find your Sleeper league ID.](https://support.sleeper.app/en/articles/4121798-how-do-i-find-my-league-id)

### Yahoo

##### [Examples](https://github.com/joeyagreco/leeger/blob/main/example/league_loader/yahooLeagueLoaderExample.py)

##### League Info Needed

- League ID
- Client ID
- Client secret

[How to find your Yahoo league ID.](https://help.yahoo.com/kb/fantasy-football/find-league-group-number-sln8238.html)

To set up your Yahoo account, follow these steps:

- Register a new application on the [Yahoo Developer Site](https://developer.yahoo.com/apps/)
- Retrieve the Client ID and Client secret for the application
- Set the callback/redirect URI of the application to: https://localhost:8000
- Make sure the application has READ permissions

##### Notes

- When the Yahoo League Loader is run, Yahoo OAuth will open up a new tab in a browser. You can close this tab.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Credit

- [ESPN API](https://github.com/cwendt94/espn-api)
- [ESPN Private Leagues](https://cran.r-project.org/web/packages/ffscrapr/vignettes/espn_authentication.html)
- [YahooFantasy](https://github.com/mattdodge/yahoofantasy)