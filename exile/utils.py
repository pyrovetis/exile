from datetime import timedelta, datetime, timezone
from typing import List

import sqlalchemy as sa
from dateutil.relativedelta import relativedelta
from flask_login import current_user

from exile import db
from exile.models import View, Footprint


def last_seven_days_label():
    """Return a list of dates for the last 7 days."""
    now = datetime.now(timezone.utc)
    return [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7, -1, -1)]


def last_six_months_label():
    """Return a list of months for the last 6 months."""
    now = datetime.now(timezone.utc)
    result = [now.strftime("%B")]
    for _ in range(0, 5):
        now = now - relativedelta(months=1)
        result.append(now.strftime("%B"))

    return result[::-1]


def last_twelve_months_label():
    """Return a list of months for the last 12 months."""
    now = datetime.now(timezone.utc)
    result = [now.strftime("%B")]
    for _ in range(0, 11):
        now = now - relativedelta(months=1)
        result.append(now.strftime("%B"))

    return result[::-1]


def last_six_months_datetime():
    """Return a list of datetimes for the last 6 months."""
    now = datetime.now(timezone.utc)
    result = [now.replace(day=1).strftime("%Y-%m-%d")]
    for _ in range(0, 5):
        now = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        result.append(now.strftime("%Y-%m-%d"))

    return result[::-1]


def last_twelve_months_datetime():
    """Return a list of datetimes for the last 12 months."""
    now = datetime.now(timezone.utc)
    result = [now.replace(day=1).strftime("%Y-%m-%d")]
    for _ in range(0, 11):
        now = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
        result.append(now.strftime("%Y-%m-%d"))

    return result[::-1]


def chart_data_overview(times: List[str]):
    """Return a list of integers representing the number of views for each time period."""
    result = []
    for index, label in enumerate(times):
        start = datetime.strptime(label, "%Y-%m-%d")
        end = (
            datetime.strptime(times[index + 1], "%Y-%m-%d")
            if index + 1 < len(times)
            else datetime.now(timezone.utc)
        )
        result.append(
            current_user.views.where(View.time >= start, View.time <= end).count()
        )
    return result


def chart_data_single(times: List[str], link_id: str):
    """Return a list of integers representing the number of views for each time period."""
    result = []
    for index, label in enumerate(times):
        start = datetime.strptime(label, "%Y-%m-%d")
        end = (
            datetime.strptime(times[index + 1], "%Y-%m-%d")
            if index + 1 < len(times)
            else datetime.now(timezone.utc)
        )
        result.append(
            db.session.query(sa.func.count(View.id))
            .where(View.user_id == current_user.id)
            .where(View.time >= start, View.time <= end)
            .where(View.short_id == link_id)
            .scalar()
        )

    return result


def get_pie_chart_timeframe(timeframe: int):
    now = datetime.now(timezone.utc)

    match timeframe:
        case 1:
            threshold = now - timedelta(days=7)
        case 2:
            threshold = now - relativedelta(months=6)
        case 3:
            threshold = now - relativedelta(months=12)
        case _:
            pass

    return threshold.strftime("%Y-%m-%d")


def chart_data_referrer(timeframe: int):
    threshold = datetime.strptime(get_pie_chart_timeframe(timeframe), "%Y-%m-%d")

    result: list = (
        db.session.query(View.referrer)
        .where(View.user_id == current_user.id)
        .where(View.time >= threshold)
        .group_by(View.referrer)
        .add_columns(sa.func.count(View.id).label("views"))
        .order_by(sa.desc("views"))
        .limit(10)
        .all()
    )

    if len(result) == 0:
        return [None, None]
    return zip(*result)


def chart_data_os(timeframe: int):
    threshold = datetime.strptime(get_pie_chart_timeframe(timeframe), "%Y-%m-%d")

    result: list = (
        db.session.query(View.os)
        .where(View.user_id == current_user.id)
        .where(View.time >= threshold)
        .group_by(View.os)
        .add_columns(sa.func.count(View.id).label("views"))
        .order_by(sa.desc("views"))
        .limit(10)
        .all()
    )

    if len(result) == 0:
        return [None, None]
    return zip(*result)


def chart_data_browser(timeframe: int):
    threshold = datetime.strptime(get_pie_chart_timeframe(timeframe), "%Y-%m-%d")

    result: list = (
        db.session.query(View.browser)
        .where(View.user_id == current_user.id)
        .where(View.time >= threshold)
        .group_by(View.browser)
        .add_columns(sa.func.count(View.id).label("views"))
        .order_by(sa.desc("views"))
        .limit(10)
        .all()
    )

    if len(result) == 0:
        return [None, None]
    return zip(*result)


def chart_data_country(timeframe: int):
    threshold = datetime.strptime(get_pie_chart_timeframe(timeframe), "%Y-%m-%d")

    result: list = (
        db.session.query(Footprint.country)
        .where(Footprint.ip.in_([s.ip for s in current_user.views]))
        .where(View.time >= threshold)
        .group_by(Footprint.country)
        .add_columns(sa.func.count(Footprint.ip).label("views"))
        .order_by(sa.desc("views"))
        .join(View, Footprint.ip == View.ip)
        .limit(10)
        .all()
    )

    if len(result) == 0:
        return [None, None]
    return zip(*result)


def chart_data_city(timeframe: int):
    threshold = datetime.strptime(get_pie_chart_timeframe(timeframe), "%Y-%m-%d")

    result: list = (
        db.session.query(Footprint.city)
        .where(Footprint.ip.in_([s.ip for s in current_user.views]))
        .where(View.time >= threshold)
        .group_by(Footprint.city)
        .add_columns(sa.func.count(Footprint.ip).label("views"))
        .order_by(sa.desc("views"))
        .join(View, Footprint.ip == View.ip)
        .limit(10)
        .all()
    )

    if len(result) == 0:
        return [None, None]
    return zip(*result)
