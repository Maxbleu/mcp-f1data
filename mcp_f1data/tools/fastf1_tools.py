import json, requests
from pydantic import Field
from fastmcp import FastMCP
import fastf1.plotting as f1_plotting
from ..utils.fastf1_utils import get_laps, get_specific_lap, get_session as get_session_custom

def register_fastf1_tools(mcp:FastMCP):
    """Register all F1 analysis tools with the MCP server"""

    @mcp.tool(name="get_drivers_standing", description="This tool will return the actual drivers standing, only indicating the year")
    async def get_drivers_standing(
        year: int = Field(description="The year of the season when the session was held")
    ) -> json:
        """Get the drivers standing for a specific year"""

        response = requests.get(f"https://api.jolpi.ca/ergast/f1/{year}/driverstandings/")
        if response.status_code == 200:
            json = response.json()
            return json["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]

    @mcp.tool(name="get_specific_driver_standing", description="This tool will return a specific driver standing, only indicating the year and the driver or selecting a standing position")
    async def get_specific_driver_standing(
        year: int = Field(description="The year of the season when the session was held"),
        driver: str = Field(description="The abbreviation of the driver's name. If you don't have a specific driver indicated, you must to put -> (not_indicated)"),
        standing_position: int = Field(description="The position in the standing. If you don't have a specific stading position indicated, you must to put -> (-1)")
    ) -> json:
        """Get a specific standig for a specific year, by driver or by position"""

        url = f"https://api.jolpi.ca/ergast/f1/{year}/drivers/{driver}/driverstandings/" if standing_position == -1 else f"https://api.jolpi.ca/ergast/f1/{year}/driverstandings/{standing_position}"
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
            return json["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"][0]

    @mcp.tool(name="get_constructors_standing", description="This tool will return the actual constructors standing, only indicating the year")
    async def get_constructors_standing(
        year: int = Field(description="The year of the season when the session was held")
    ) -> json:
        """Get the constructors standing for a specific year"""

        response = requests.get(f"https://api.jolpi.ca/ergast/f1/{year}/constructorstandings/")
        if response.status_code == 200:
            json = response.json()
            return json["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]

    @mcp.tool(name="get_specific_constructor_standing", description="This tool will return a specific constructor standing, only indicating the year and the constructor or selecting a standing position")
    async def get_specific_constructor_standing(
        year: int = Field(description="The year of the season when the session was held"),
        constructor: str = Field(description="The abbreviation of the constructor's name. If you don't have a specific constructor indicated, you must to put -> (not_indicated)"),
        standing_position: int = Field(description="The position in the standing. If you don't have a specific stading position indicated, you must to put -> (-1)")
    ) -> json:
        """Get a specific standig for a specific year, by constructor or by position"""

        url = f"https://api.jolpi.ca/ergast/f1/{year}/constructors/{constructor}/constructorstandings/" if standing_position == -1 else f"https://api.jolpi.ca/ergast/f1/{year}/constructorstandings/{standing_position}"
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
            return json["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"][0]

    @mcp.tool(name="get_session_results", description="This tool will return a final classification for a specific session")
    async def get_session_results(
        type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
        year: int = Field(description="The year of the season when the session was held"),
        round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix. If round is not indicated, you must to put -> (-1)"),
        session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'. If round is not indicated, you must to put -> (not_indicated)"),
        latest_session: bool = Field(description="Indicate if you want the latest session of the event. By default is False. But if the user want the latest session, it will be True"),
    ) -> json:
        """Get the final classification for a specific session"""

        session = get_session_custom(type_event=type_session, year=year, event=round, session=session, latest_session=latest_session)
        session_results = session.results[["Position","FullName","Abbreviation"]].to_json(orient='records', lines=True)
        return session_results

    @mcp.tool(name="get_fastest_lap")
    async def get_fastest_lap(
        type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
        year: int = Field(description="The year of the season when the session was held"),
        round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
        session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'."),
        driver: str = Field(description="The abbreviation of the driver's name. If you don't have a specific driver in mind, you can leave this blank to get the fastest lap for all drivers"),
    ) -> json:
        """Get the fastest laps for a driver in a session. In case no driver is specified, it will return the fastest laps for all drivers"""

        laps = get_laps(type_session, year, round, session, driver)
        lap = get_specific_lap(
                laps,
                get_general_fastest_lap = False if driver else True,
                get_personal_fastest_lap= True if driver else False
            )
        return lap.to_json()

    @mcp.tool(name="get_top_speed")
    async def get_top_speed(
        type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
        year: int = Field(description="The year of the season when the session was held"),
        round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
        session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'."),
        driver: str = Field(description="The abbreviation of the driver's name. If you don't have a specific driver in mind, you can leave this blank to get the fastest lap for all drivers"),
    ) -> int:
        """Get the top speed for a driver in a session. In case no driver is specified, it will return the highest top speed for all drivers"""

        laps = get_laps(type_session, year, round, session, driver)
        max_speed = int(laps["SpeedST"].max())
        return max_speed

    @mcp.tool(name="get_total_laps")
    async def get_total_laps(
        type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
        year: int = Field(description="The year of the season when the session was held"),
        round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
        session: str = Field(description="The exact name of the session within the event, such as 'FP1', 'FP2', 'Q', 'R', or 'Sprint'."),
        driver: str = Field(description="The abbreviation of the driver's name. If you don't have a specific driver in mind, you can leave this blank to get the fastest lap for all drivers"),
    ) -> int:
        """Get the total laps for a driver in a session. In case no driver is specified, it will return the total laps for all drivers"""

        laps = get_laps(type_session, year, round, session, driver)
        return len(laps)

    @mcp.tool(name="get_box_laps")
    async def get_box_laps(
        type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
        year: int = Field(description="The year of the season when the session was held"),
        round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
        session: str = Field(description="The exact name of the session within the event 'R'"),
        driver: str = Field(description="The abbreviation of the driver's name."),
    ) -> json:
        """Get laps where the driver was in the pit box."""

        laps = get_laps(type_session, year, round, session,driver)
        box_laps = laps.pick_box_laps(which="in")[["Time","Driver","LapNumber","Compound","PitOutTime","PitInTime"]]
        return box_laps.to_json()

    @mcp.tool(name="get_deleted_laps")
    async def get_deleted_laps(
        type_session: str = Field(description="Type of session in general terms: official or pretest (pre-session test)"),
        year: int = Field(description="The year of the season when the session was held"),
        round: int = Field(description="The round number of the championship, for example 1 for the first Grand Prix."),
        session: str = Field(description="The exact name of the session within the event 'R'"),
        driver: str = Field(description="The abbreviation of the driver's name."),
    ) -> json:
        """Get laps where the driver was in the pit box."""

        laps = get_laps(type_session, year, round, session, driver)
        deleted_laps = laps[laps["Deleted"] == True][["Time","Driver","LapNumber","Deleted","DeletedReason"]]
        return deleted_laps.to_json()