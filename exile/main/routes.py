from threading import Thread

import httpx
import sqlalchemy as sa
from flask import render_template, redirect, request, current_app
from user_agents import parse

from exile import db
from exile.api.forms import ShortForm
from exile.main import bp
from exile.models import Footprint
from exile.models import Short, View


@bp.route("/")
@bp.route("/index")
def index():
    """
    Home page.
    """
    form = ShortForm()

    return render_template("index.html", title="Home", form=form)


@bp.route("/<string:origin>")
def redirects(origin):
    """
    Redirects to the destination of a short link.
    """
    short = db.first_or_404(sa.select(Short).where(Short.origin == origin))

    user_agents = parse(request.headers.get("User-Agent"))
    referrer = request.referrer.split("/")[2] if request.referrer else "None"
    ip = request.remote_addr

    def async_add_data(app):
        with app.app_context():
            footprint_query = (
                db.session.query(Footprint).filter(Footprint.ip == ip).first()
            )

            if footprint_query is None:
                r = httpx.get(f"http://ip-api.com/json/{ip}").json()

                footprint = Footprint(
                    ip=ip,
                    continent=r.get("continent", None),
                    continentCode=r.get("continentCode", None),
                    country=r.get("country", None),
                    countryCode=r.get("countryCode", None),
                    region=r.get("region", None),
                    regionName=r.get("regionName", None),
                    city=r.get("city", None),
                    district=r.get("district", None),
                    zip=r.get("zip", None),
                    lat=r.get("lat", None),
                    lon=r.get("lon", None),
                    timezone=r.get("timezone", None),
                    offset=r.get("offset", None),
                    currency=r.get("currency", None),
                    isp=r.get("isp", None),
                    org=r.get("org", None),
                    as_=r.get("as", None),
                    asname=r.get("asname", None),
                    mobile=r.get("mobile", None),
                    proxy=r.get("proxy", None),
                    hosting=r.get("hosting", None),
                )

                db.session.add(footprint)

            view = View(
                short_id=short.id,
                referrer=referrer,
                ip=ip,
                browser=user_agents.browser.family,
                os=user_agents.os.family,
                user_id=short.user_id,
            )

            db.session.add(view)
            db.session.commit()

    Thread(
        target=async_add_data, args=(current_app._get_current_object(),), daemon=True
    ).start()

    return redirect(short.destination, 301)
