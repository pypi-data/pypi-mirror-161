# %%
import requests
import os
from datetime import datetime


class CatapultAPI:
    def __init__(self, api_token, version="v6"):
        self.base_url = "https://connect-eu.catapultsports.com/api"
        self.api_token = api_token
        self.version = version
        self.headers = {"Authorization": "Bearer " + self.api_token}

    # Loaders

    def _url(self, *route, **params):
        return "{base}/{version}/{route}".format(
            base=self.base_url,
            version=self.version,
            route="/".join(str(r) for r in route),
        )

    def _parse_response(self, response):
        content = response.json()
        try:
            error = content.get("error", None)
        except AttributeError:
            # API call returned a list
            return content
        return content

    def get_route_json(self, *route, **params):
        r = requests.get(self._url(*route), headers=self.headers, params=params)
        return self._parse_response(r)

    def post_route_json(self, *route, json=None, data=None):
        r = requests.post(self._url(*route), headers=self.headers, json=json, data=data)
        return self._parse_response(r)

    # API Calls

    # Activities

    def get_activities(
        self, startTime=None, endTime=None, sort=None, page_size=None, deleted=None
    ):
        """A list of activities

        Args:
            startTime (str, optional): Format: dd-mm-YYYY. Filter out activities with start time less than this value (POSIX time in seconds). Defaults to None.
            endTime (str, optional): Format: dd-mm-YYYY. Filter out activities with end time greater than this value (POSIX time in seconds). Defaults to None.
            sort (str, optional): Which field to sort by. Prepend '-' to sort in descending order. Defaults to None.
            page_size (int, optional): Number of items per page for pagination. Defaults to None.
            deleted (int, optional): Set to 1 to return deleted activities instead. Defaults to None.

        Returns:
            json: _description_
        """
        if startTime:
            startTime = datetime.strptime(startTime, "%d-%m-%Y").timestamp()
            endTime = datetime.strptime(endTime, "%d-%m-%Y").timestamp()
        return self.get_route_json(
            "activities",
            startTime=startTime,
            endTime=endTime,
            sort=sort,
            page_size=page_size,
            deleted=deleted,
        )

    def get_activity_details(self, activity_id, include=None):
        """_summary_

        Args:
            activity_id (str): Activity Id
            include (str, optional): Entities to include, comma separated. ("all" returns "deep activity" details). Defaults to None.

        Returns:
            _type_: _description_
        """
        return self.get_route_json("activities", activity_id, include=None)

    def get_activity_athletes(self, activity_id):
        """Returns the list of athletes for the provided activity id

        Args:
            activity_id (str): Activity Id

        Returns:
            _type_: _description_
        """

        return self.get_route_json("activities", activity_id, "athletes")

    def get_activity_periods(self, activity_id):
        """A list of periods for a given activity

        Args:
            activity_id ([type]): [description]

        Returns:
            [type]: [description]
        """
        return self.get_route_json("activities", activity_id, "periods")

    def get_activity_tags(self, activity_id):
        """Returns all the tags associated with the provided activity id

        Args:
            activity_id (str): Activity id

        Returns:
            _type_: _description_
        """
        return self.get_route_json("activities", activity_id, "tags")

    # Annotations

    # Athletes

    def get_athletes(self):
        """A list of athletes/players for the account

        Returns:
            [type]: [description]
        """
        return self.get_route_json("athletes")

    # Efforts Data

    def get_efforts_by_activity(
        self,
        activity_id,
        athlete_id,
        effort_types=["velocity", "acceleration"],
        velocity_bands=None,
        acceleration_bands=None,
        stream_type=None,
        startTime=None,
        endTime=None,
    ):
        """This API retrieves efforts data for athlete in an activity.

        Args:
            activity_id (str): Activity Id
            athlete_id (str): Athlete Id
            effort_types (list, optional): Comma Separated Effort Type Values (can only include 'acceleration' or 'velocity'
                                           or both separated by comma). Defaults to ["velocity", "acceleration"].
            velocity_bands (str, optional): One or more comma separated velocity band parameters may be supplied to
                                            restrict the list of bands returned, as an integer. Valid values are numbers 1 to 8.
                                            If not velocity bands values are specified, all bands are included. Defaults to None.
            acceleration_bands (str, optional): One or more comma separated acceleration band parameters may be supplied to
                                                restrict the list of bands returned, as an integer. Valid values are numbers -3 to 3,
                                                matching deceleration and acceleration bands 1 to 3 in OpenField Cloud including 0.
                                                If no band values are specified, bands -3, -2,-1 and 1, 2 and 3 will be included. Defaults to None.
            stream_type (str, optional): Stream Type ('lps' or 'gps'). Defaults to None.
            startTime (str, optional): _description_. Defaults to None.
            endTime (str, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if startTime:
            startTime = datetime.strptime(startTime, "%d-%m-%Y").timestamp()
            endTime = datetime.strptime(endTime, "%d-%m-%Y").timestamp()
        return self.get_route_json(
            "activities",
            activity_id,
            "athletes",
            athlete_id,
            "efforts",
            effort_types=effort_types,
            velocity_bands=velocity_bands,
            acceleration_bands=acceleration_bands,
            stream_type=stream_type,
            startTime=startTime,
            endTime=endTime,
        )

    def get_efforts_by_period(
        self,
        period_id,
        athlete_id,
        effort_types=["velocity", "acceleration"],
        velocity_bands=None,
        acceleration_bands=None,
        stream_type=None,
        startTime=None,
        endTime=None,
    ):
        """This API retrieves efforts data for athlete in a period.

        Args:
            period_id (str): Period Id
            athlete_id (str): Athlete Id
            effort_types (list, optional): Comma Separated Effort Type Values (can only include 'acceleration' or 'velocity'
                                           or both separated by comma). Defaults to ["velocity", "acceleration"].
            velocity_bands (str, optional): One or more comma separated velocity band parameters may be supplied to
                                            restrict the list of bands returned, as an integer. Valid values are numbers 1 to 8.
                                            If not velocity bands values are specified, all bands are included. Defaults to None.
            acceleration_bands (str, optional): One or more comma separated acceleration band parameters may be supplied to
                                                restrict the list of bands returned, as an integer. Valid values are numbers -3 to 3,
                                                matching deceleration and acceleration bands 1 to 3 in OpenField Cloud including 0.
                                                If no band values are specified, bands -3, -2,-1 and 1, 2 and 3 will be included. Defaults to None.
            stream_type (str, optional): Stream Type ('lps' or 'gps'). Defaults to None.
            startTime (str, optional): _description_. Defaults to None.
            endTime (str, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if startTime:
            startTime = datetime.strptime(startTime, "%d-%m-%Y").timestamp()
            endTime = datetime.strptime(endTime, "%d-%m-%Y").timestamp()
        return self.get_route_json(
            "activities",
            period_id,
            "athletes",
            athlete_id,
            "efforts",
            effort_types=effort_types,
            velocity_bands=velocity_bands,
            acceleration_bands=acceleration_bands,
            stream_type=stream_type,
            startTime=startTime,
            endTime=endTime,
        )

    # Events Data

    def get_ima_events_by_activity(
        self,
        activity_id,
        athlete_id,
        event_types=None,
        startTime=None,
        endTime=None,
        ima_acceleration_intensity_threshold=None,
    ):
        """This API returns the events data for an athlete in the activity.

        Args:
            activity_id (str): Activity Id
            athlete_id (str): Athlete Id
            event_types (str, optional): Comma Separated Event Type Values (can be a number, string or both for e.g. 5,6,7,ima_acceleration,ima_jump). Defaults to None.
            startTime (str, optional): _description_. Defaults to None.
            endTime (str, optional): _description_. Defaults to None.
            ima_acceleration_intensity_threshold (float, optional): If specified, only events within an intensity value
                                            greater than the threshold value should be returned. Defaults to None.

        Returns:
            _type_: _description_
        """
        if startTime:
            startTime = datetime.strptime(startTime, "%d-%m-%Y").timestamp()
            endTime = datetime.strptime(endTime, "%d-%m-%Y").timestamp()

        return self.get_route_json(
            "activities",
            activity_id,
            "athletes",
            athlete_id,
            "events",
            event_types=event_types,
            startTime=startTime,
            endTime=endTime,
            ima_acceleration_intensity_threshold=ima_acceleration_intensity_threshold,
        )

    def get_ima_events_by_period(
        self,
        period_id,
        athlete_id,
        event_types=None,
        startTime=None,
        endTime=None,
        ima_acceleration_intensity_threshold=None,
    ):
        """This API returns the events data for an athlete in the activity.

        Args:
            activity_id (str): Activity Id
            athlete_id (str): Athlete Id
            event_types (str, optional): Comma Separated Event Type Values (can be a number, string or both for e.g. 5,6,7,ima_acceleration,ima_jump). Defaults to None.
            startTime (str, optional): _description_. Defaults to None.
            endTime (str, optional): _description_. Defaults to None.
            ima_acceleration_intensity_threshold (float, optional): If specified, only events within an intensity value
                                            greater than the threshold value should be returned. Defaults to None.

        Returns:
            _type_: _description_
        """
        if startTime:
            startTime = datetime.strptime(startTime, "%d-%m-%Y").timestamp()
            endTime = datetime.strptime(endTime, "%d-%m-%Y").timestamp()

        return self.get_route_json(
            "periods",
            period_id,
            "athletes",
            athlete_id,
            "events",
            event_types=event_types,
            startTime=startTime,
            endTime=endTime,
            ima_acceleration_intensity_threshold=ima_acceleration_intensity_threshold,
        )

    # Parameters

    def get_parameters(self):
        """The /parameters endpoint provides a list of parameters (sports metrics) captured within OpenField,
        including Player Load, heart rate, banded velocity and acceleration metrics, amongst many others.

         Returns:
             [type]: [description]
        """
        return self.get_route_json("parameters")

    def get_parameter_details(self, parameter_id):
        """This API will retrieve details for a single parameter

        Args:
            parameter_id (str): Parameter Id

        Returns:
            _type_: _description_
        """
        return self.get_route_json("parameters", parameter_id)

    def get_parameter_types(self):
        """This API will retrieve all parameter types in an account.

        Returns:
            _type_: _description_
        """
        return self.get_route_json("parameter_types")

    # Periods

    def get_periods(self):
        """A list of all periods returning results in the same format

        Returns:
            _type_: _description_
        """
        return self.get_route_json("periods")

    def get_period_details(self, period_id):
        """This API returns period details for the provided period id.

        Args:
            period_id (str): Period Id

        Returns:
            _type_: _description_
        """
        return self.get_route_json("periods", period_id)

    def get_period_athletes(self, period_id):
        """This API returns all the athletes under provided period id.

        Args:
            period_id (str): Period Id

        Returns:
            _type_: _description_
        """
        return self.get_route_json("periods", period_id, "athletes")

    # Positions

    def get_positions(self):
        """This API returns all the available positions in an account.

        Returns:
            _type_: _description_
        """
        return self.get_route_json("positions")

    # 10hz Sensor Data

    def get_sensor_data_by_activity(self, activity_id, athlete_id):
        """Sensor data (sometimes referred to as '10Hz' data) is so-called because it is a representation of the data provided by inertial and positional sensors in Catapult wearables.
           Sensor data can be retrieved as a JSON time series for a single Athlete as a time, for a given Activitie or Period.

        Args:
            activity_id (str): Activity ID
            athlete_id (_type_): Athlete ID

        Returns:
            json: sensor data from a specific athlete for a specific activity
        """
        return self.get_route_json(
            "activities", activity_id, "athletes", athlete_id, "sensor"
        )

    def get_sensor_data_by_period(self, period_id, athlete_id):
        """Sensor data (sometimes referred to as '10Hz' data) is so-called because it is a representation of the data provided by inertial and positional sensors in Catapult wearables.
           Sensor data can be retrieved as a JSON time series for a single Athlete as a time, for a given Activitie or Period.

        Args:
            period_id (str): Period ID
            athlete_id (_type_): Athlete ID

        Returns:
            json: sensor data from a specific athlete for a specific activity
        """
        return self.get_route_json(
            "periods", period_id, "athletes", athlete_id, "sensor"
        )

    # Settings

    def get_user_settings(self):
        return self.get_route_json("settings")

    # Stats

    def get_stats(self, filters, group_by, parameters) -> dict:
        """The /stats endpoint provides filtered and grouped performance metrics"""

        payload = {"filters": filters, "group_by": group_by, "parameters": parameters}

        return self.post_route_json("stats", json=payload)

    # Tags

    def get_tags(self) -> dict:
        """The /tags and /tagtype endpoints provide lists of tags (text strings categorised by type) captured
        within OpenField, including athlete, activity (such as day-code) and period tags, amongst many others

        Returns:
            _type_: _description_
        """
        return self.get_route_json("tags")

    def get_tags_from_tag_type(self, tag_type):
        """Get the list of all Tags of the given Tag type.

        Args:
            tag_type (str): Tag Type name

        Returns:
            _type_: _description_
        """
        return self.get_route_json("tags", tag_type)

    # Tag Types

    def get_tag_types(self) -> dict:
        """This API retrieves the list of all tag types.

        Returns:
            _type_: _description_
        """
        return self.get_route_json("tagtype")

    def get_tag_type_details(self, tag_type_id):
        """Returns TagType details of the provided id.

        Args:
            tag_type_id (str): TagType Id

        Returns:
            _type_: _description_
        """
        return self.get_route_json("tagtype", tag_type_id)

    # Entity Tags

    # Teams

    def get_teams(self, startTime=None, endTime=None, include=None):
        """A list of Teams to which Athletes are assigned

        Args:
            include (array of strings, optional): Entities to include under each item, comma separated. Defaults to None.

        Returns:
            _type_: _description_
        """
        if startTime:
            startTime = datetime.strptime(startTime, "%d-%m-%Y").timestamp()
            endTime = datetime.strptime(endTime, "%d-%m-%Y").timestamp()
        return self.get_route_json("teams", include=include)

    def get_team_details(self, team_id, include=None):
        """Details for a specific Team

        Args:
            team_id (str): _description_
            include (array of strings, optional): Entities to include under each item, comma separated. Defaults to None.

        Returns:
            _type_: _description_
        """
        return self.get_route_json("teams", team_id, include=include)

    def get_team_athletes(self, team_id):
        """A list of athletes for a specific team

        Args:
            team_id (str): Team Id
        """
        return self.get_route_json("teams", team_id, "athletes")

    # Athlete Thresholds

    def get_threshold_sets(self):
        """List of threshold sets

        Returns:
            _type_: _description_
        """
        return self.get_route_json("threshold_sets")

    def get_threshold_set_specific(self, threshold_set_id, include=None):
        """_summary_

        Args:
            threshold_set_id (str): ThresholdSet Id
            include (array of strings, optional): Entities to include, comma separated. Defaults to None.

        Returns:
            _type_: _description_
        """
        return self.get_route_json("threshold_sets", threshold_set_id, include=include)

    def get_threshold_alerts(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.get_route_json("threshold_alerts")

    # Venues

    def get_venues(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.get_route_json("venues")

    def get_venue_details(self, venue_id, include=None):
        """_summary_

        Args:
            venue_id (str): Venue ID

        Returns:
            _type_: _description_
        """
        return self.get_route_json("venues", venue_id, include=include)

    # Live

    def get_live(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.get_route_json("live")

    def get_live_details(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.get_route_json("live", "info")
