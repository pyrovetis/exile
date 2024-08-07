import sqlalchemy as sa
from flask import render_template
from flask_login import login_required, current_user

from exile import db
from exile.api.forms import ShortForm, EditForm
from exile.dashboard import bp
from exile.models import Short, View, Footprint, History


@bp.route("/")
@login_required
def dashboard():
    """
    Dashboard page.
    """
    form = ShortForm()
    return render_template("dashboard/dashboard.html", title="Dashboard", form=form)


@bp.route("/shorts")
@login_required
def shorts():
    """
    Shorts page.
    """
    return render_template("dashboard/shorts.html", title="Short links")


@bp.route("/short", defaults={"link_id": 1})
@bp.route("/short/<link_id>")
@login_required
def single_short(link_id):
    """
    Single short link page.
    """
    return render_template(
        "dashboard/short.html",
        title="Short link statistics",
        current_id=link_id,
        is_single=True,
    )


@bp.route("/edit", defaults={"link_id": 1})
@bp.route("/edit/<link_id>")
@login_required
def edit(link_id):
    """
    Edit short link page.
    """
    link = db.first_or_404(current_user.shorts.where(Short.id == link_id))
    form = EditForm()

    form.origin.data = link.origin
    form.destination.data = link.destination
    form.note.data = link.note

    history = (
        History.query.where(History.short_id == link_id)
        .order_by(History.id.desc())
        .all()
    )

    return render_template(
        "dashboard/edit.html",
        title="Edit short link",
        current_id=link_id,
        is_editing=True,
        form=form,
        link=link,
        history=history,
    )


@bp.route("/statistics")
@bp.route("/statistics/overview")
@login_required
def statistics():
    links = (
        db.session.query(Short.origin)
        .where(Short.user_id == current_user.id)
        .add_columns(
            sa.func.count(Short.views).label("views"),
        )
        .where(View.short_id == Short.id)
        .group_by(Short.id)
        .order_by(sa.desc("views"))
        .limit(5)
        .all()
    )

    referrers = (
        db.session.query(View.referrer)
        .group_by(View.referrer)
        .where(View.user_id == current_user.id)
        .add_columns(sa.func.count(View.id).label("views"))
        .order_by(sa.desc("views"))
        .limit(5)
        .all()
    )

    browsers = (
        db.session.query(View.browser)
        .group_by(View.browser)
        .where(View.user_id == current_user.id)
        .add_columns(sa.func.count(View.id).label("views"))
        .order_by(sa.desc("views"))
        .limit(5)
        .all()
    )

    os_ = (
        db.session.query(View.os)
        .group_by(View.os)
        .where(View.user_id == current_user.id)
        .add_columns(sa.func.count(View.id).label("views"))
        .order_by(sa.desc("views"))
        .limit(5)
        .all()
    )

    countries = (
        db.session.query(Footprint.country)
        .where(Footprint.ip.in_([s.ip for s in current_user.views]))
        .group_by(Footprint.country)
        .add_columns(sa.func.count(Footprint.ip).label("views"))
        .order_by(sa.desc("views"))
        .limit(5)
        .all()
    )

    cities = (
        db.session.query(Footprint.city)
        .where(Footprint.ip.in_([s.ip for s in current_user.views]))
        .group_by(Footprint.city)
        .add_columns(sa.func.count(Footprint.ip).label("views"))
        .order_by(sa.desc("views"))
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard/statistics/overview.html",
        title="Statistics",
        shorts=links,
        referrers=referrers,
        browsers=browsers,
        os=os_,
        countries=countries,
        cities=cities,
    )


@bp.route("/statistics/short")
@login_required
def statistics_short():
    return render_template("dashboard/statistics/short.html", title="Shorts statistics")


@bp.route("/statistics/referrer")
@login_required
def statistics_referrer():
    return render_template(
        "dashboard/statistics/referrer.html", title="Referrers statistics"
    )


@bp.route("/statistics/browser")
@login_required
def statistics_browser():
    return render_template(
        "dashboard/statistics/browser.html", title="Browser statistics"
    )


@bp.route("/statistics/os")
@login_required
def statistics_os():
    return render_template("dashboard/statistics/os.html", title="OS statistics")


@bp.route("/statistics/country")
@login_required
def statistics_country():
    return render_template(
        "dashboard/statistics/country.html", title="Country statistics"
    )


@bp.route("/statistics/city")
@login_required
def statistics_city():
    return render_template("dashboard/statistics/city.html", title="City statistics")
