import logging
from datetime import datetime

import dateutil
import flask_pymongo
from flask import request

from common.common_consts.telem_categories import TelemCategoryEnum
from monkey_island.cc.database import mongo
from monkey_island.cc.resources.AbstractResource import AbstractResource
from monkey_island.cc.resources.request_authentication import jwt_required
from monkey_island.cc.services.node import NodeService

logger = logging.getLogger(__name__)


class TelemetryFeed(AbstractResource):
    urls = ["/api/telemetry-feed"]

    @jwt_required
    def get(self, **kw):
        timestamp = request.args.get("timestamp")
        if "null" == timestamp or timestamp is None:  # special case to avoid ugly JS code...
            telemetries = mongo.db.telemetry.find({})
        else:
            telemetries = mongo.db.telemetry.find(
                {"timestamp": {"$gt": dateutil.parser.parse(timestamp)}}
            )
            telemetries = telemetries.sort([("timestamp", flask_pymongo.ASCENDING)])

        try:
            return {
                "telemetries": [
                    TelemetryFeed.get_displayed_telemetry(telem)
                    for telem in telemetries
                    if TelemetryFeed.should_show_brief(telem)
                ],
                "timestamp": datetime.now().isoformat(),
            }
        except KeyError as err:
            logger.error("Failed parsing telemetries. Error: {0}.".format(err))
            # API Spec: Should return HTTP status code 404 (?)
            return {"telemetries": [], "timestamp": datetime.now().isoformat()}

    @staticmethod
    def get_displayed_telemetry(telem):
        monkey = NodeService.get_monkey_by_guid(telem["monkey_guid"])
        default_hostname = "GUID-" + telem["monkey_guid"]
        return {
            "id": telem["_id"],
            "timestamp": telem["timestamp"].strftime("%d/%m/%Y %H:%M:%S"),
            "hostname": monkey.get("hostname", default_hostname) if monkey else default_hostname,
            "brief": TelemetryFeed.get_telem_brief(telem),
        }

    @staticmethod
    def get_telem_brief(telem):
        telem_brief_parser = TelemetryFeed.get_telem_brief_parser_by_category(
            telem["telem_category"]
        )
        return telem_brief_parser(telem)

    @staticmethod
    def get_telem_brief_parser_by_category(telem_category):
        return TELEM_PROCESS_DICT[telem_category]

    @staticmethod
    def get_state_telem_brief(telem):
        if telem["data"]["done"]:
            return """Monkey finishing its execution."""
        else:
            return "Monkey started."

    @staticmethod
    def get_exploit_telem_brief(telem):
        target = telem["data"]["machine"]["ip_addr"]
        exploiter = telem["data"]["exploiter"]
        result = telem["data"]["exploitation_result"]
        if result:
            return "Monkey successfully exploited %s using the %s exploiter." % (target, exploiter)
        else:
            return "Monkey failed exploiting %s using the %s exploiter." % (target, exploiter)

    @staticmethod
    def get_scan_telem_brief(telem):
        return "Monkey discovered machine %s." % telem["data"]["machine"]["ip_addr"]

    @staticmethod
    def get_trace_telem_brief(telem):
        return "Trace: %s" % telem["data"]["msg"]

    @staticmethod
    def get_post_breach_telem_brief(telem):
        return "%s post breach action executed on %s (%s) machine." % (
            telem["data"][0]["name"],
            telem["data"][0]["hostname"],
            telem["data"][0]["ip"],
        )

    @staticmethod
    def should_show_brief(telem) -> bool:
        should_process_telem = SHOULD_PROCESS_TELEM.get(telem["telem_category"], lambda _: True)
        return telem["telem_category"] in TELEM_PROCESS_DICT and should_process_telem(telem)

    @staticmethod
    def should_process_scan_telem(telem) -> bool:
        return TelemetryFeed._machine_responded(telem["data"]["machine"])

    @staticmethod
    def _machine_responded(machine) -> bool:
        return machine["icmp"] and len(machine["services"].keys()) > 0


TELEM_PROCESS_DICT = {
    TelemCategoryEnum.EXPLOIT: TelemetryFeed.get_exploit_telem_brief,
    TelemCategoryEnum.POST_BREACH: TelemetryFeed.get_post_breach_telem_brief,
    TelemCategoryEnum.SCAN: TelemetryFeed.get_scan_telem_brief,
    TelemCategoryEnum.STATE: TelemetryFeed.get_state_telem_brief,
    TelemCategoryEnum.TRACE: TelemetryFeed.get_trace_telem_brief,
}


SHOULD_PROCESS_TELEM = {TelemCategoryEnum.SCAN: TelemetryFeed.should_process_scan_telem}
