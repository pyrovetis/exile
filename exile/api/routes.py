from secrets import token_urlsafe

import sqlalchemy as sa
from flask import (
    render_template,
    current_app,
    url_for,
    request,
    make_response,
)
from flask_login import current_user, login_required

from exile import db, limiter
from exile.api import bp
from exile.api.forms import ShortForm, EditForm
from exile.models import Short, View, Footprint, History
from exile.utils import (
    last_seven_days_label,
    last_six_months_label,
    last_twelve_months_label,
    last_six_months_datetime,
    last_twelve_months_datetime,
    chart_data_overview,
    chart_data_referrer,
    chart_data_os,
    chart_data_browser,
    chart_data_country,
    chart_data_city,
    chart_data_single,
)


@bp.route("/shorts", methods=["POST"])
def shorts():
    """Create a new short link."""
    form = ShortForm()

    if not form.origin.data:
        form.origin.data = token_urlsafe(4)

    if form.validate_on_submit():
        short = Short(
            origin=form.origin.data,
            destination=form.destination.data,
            note=form.note.data,
        )
        if current_user.is_authenticated:
            short.user_id = current_user.id

        db.session.add(short)
        db.session.commit()
        short_data = {
            "o": short.origin,
            "d": short.destination,
            "t": short.created_at.isoformat(),
        }

        response = make_response(
            render_template(
                "api/create.html",
                form=ShortForm(formdata=None),
                short_data=short_data,
            )
        )
        response.headers["HX-Trigger"] = "update"
        return response

    return render_template("api/create.html", form=form)


@bp.route("/shorts/<link_id>", methods=["PUT"])
@login_required
@limiter.limit("20 per day")
def shorts_put(link_id):
    """Edit an existing short link."""
    form = EditForm()
    link = db.first_or_404(current_user.shorts.where(Short.id == link_id))
    short_history = (
        History.query.where(History.short_id == link_id)
        .order_by(History.id.desc())
        .all()
    )

    if not form.origin.data:
        form.origin.data = token_urlsafe(4)

    if form.validate_on_submit():
        history = History(
            short_id=link.id,
            origin=link.origin,
            destination=link.destination,
            note=link.note,
        )
        db.session.add(history)

        link.origin = form.origin.data
        link.destination = form.destination.data
        link.note = form.note.data

        db.session.commit()

        short_history = (
            History.query.where(History.short_id == link_id)
            .order_by(History.id.desc())
            .all()
        )
        response = make_response(
            render_template(
                "api/edit.html",
                form=form,
                link=link,
                edited=True,
                history=short_history,
            )
        )
        response.headers["HX-Trigger"] = "update"
        return response

    return render_template("api/edit.html", form=form, link=link, history=short_history)


@bp.route("/shorts/<link_id>", methods=["DELETE"])
@login_required
def shorts_delete(link_id):
    """Delete an existing short link."""
    link = db.first_or_404(current_user.shorts.where(Short.id == link_id))
    db.session.delete(link)
    db.session.commit()
    return render_template("api/delete.html", redirect_url=url_for("dashboard.shorts"))


@bp.route("/shorts/table/my-links")
@login_required
def table_shorts():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    search_args = {"search": search} if search else {}

    links = db.paginate(
        current_user.shorts.where(
            Short.origin.ilike(f"%{search}%") | Short.destination.ilike(f"%{search}%")
        ).order_by(Short.created_at.desc()),
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"] * 3,
        error_out=False,
    )
    next_url = (
        url_for("api.table_shorts", page=links.next_num, **search_args)
        if links.has_next
        else None
    )
    prev_url = (
        url_for("api.table_shorts", page=links.prev_num, **search_args)
        if links.has_prev
        else None
    )
    return render_template(
        "api/statistics/table-shorts.html",
        links=links,
        next_url=next_url,
        prev_url=prev_url,
        search=search,
    )


@bp.route("/shorts/history/<link_id>")
@login_required
def shorts_history(link_id):
    history = (
        db.session.query(History)
        .where(History.short_id == link_id)
        .order_by(History.updated_at.desc())
        .all()
    )

    return render_template(
        "api/history.html",
        history=history,
    )


# Tables
@bp.route("/shorts/table/dashboard")
@login_required
def table_dashboard():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    search_args = {"search": search} if search else {}

    links = db.paginate(
        current_user.shorts.order_by(Short.created_at.desc()).where(
            Short.origin.ilike(f"%{search}%") | Short.destination.ilike(f"%{search}%")
        ),
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    next_url = (
        url_for("api.table_dashboard", page=links.next_num, **search_args)
        if links.has_next
        else None
    )
    prev_url = (
        url_for("api.table_dashboard", page=links.prev_num, **search_args)
        if links.has_prev
        else None
    )
    return render_template(
        "api/statistics/table-dashboard.html",
        links=links,
        next_url=next_url,
        prev_url=prev_url,
        search=search,
    )


@bp.route("/shorts/table/browser")
@login_required
def table_browser():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    search_args = {"search": search} if search else {}

    total_browsers_count = (
        db.session.query(sa.func.count(View.id))
        .filter(View.user_id == current_user.id)
        .scalar()
    )

    data = (
        View.query.where(View.user_id == current_user.id)
        .add_columns(
            sa.func.count(View.id).label("views"),
            (sa.func.count(View.id) / total_browsers_count).label("percentage"),
            sa.func.count(sa.distinct(View.short_id)).label("links"),
        )
        .group_by(View.browser, View.id)
        .order_by(sa.desc("views"), sa.desc(sa.text("percentage")))
        .where(View.browser.ilike(f"%{search}%"))
        .paginate(
            page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
        )
    )

    next_url = (
        url_for("api.table_browser", page=data.next_num, **search_args)
        if data.has_next
        else None
    )
    prev_url = (
        url_for("api.table_browser", page=data.prev_num, **search_args)
        if data.has_prev
        else None
    )
    return render_template(
        "api/statistics/table-browser.html",
        data=data,
        next_url=next_url,
        prev_url=prev_url,
        search=search,
    )


@bp.route("/shorts/table/city")
@login_required
def table_city():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    search_args = {"search": search} if search else {}

    total_footprints_count = (
        db.session.query(sa.func.count(Footprint.city))
        .where(Footprint.ip.in_([s.ip for s in current_user.views]))
        .scalar()
    )
    data = (
        Footprint.query.where(Footprint.ip.in_([s.ip for s in current_user.views]))
        .add_columns(
            sa.func.count(Footprint.ip).label("views"),
            (sa.func.count(Footprint.ip) / total_footprints_count).label("percentage"),
        )
        .group_by(Footprint.city, Footprint.ip)
        .order_by(sa.desc("views"), sa.desc(sa.text("percentage")))
        .where(Footprint.city.ilike(f"%{search}%"))
        .paginate(
            page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
        )
    )

    next_url = (
        url_for("api.table_city", page=data.next_num, **search_args)
        if data.has_next
        else None
    )
    prev_url = (
        url_for("api.table_city", page=data.prev_num, **search_args)
        if data.has_prev
        else None
    )
    return render_template(
        "api/statistics/table-city.html",
        data=data,
        next_url=next_url,
        prev_url=prev_url,
        search=search,
    )


@bp.route("/shorts/table/country")
@login_required
def table_country():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    search_args = {"search": search} if search else {}

    total_footprints_count = (
        db.session.query(sa.func.count(Footprint.country))
        .where(Footprint.ip.in_([s.ip for s in current_user.views]))
        .scalar()
    )
    data = (
        Footprint.query.where(Footprint.ip.in_([s.ip for s in current_user.views]))
        .add_columns(
            sa.func.count(Footprint.ip).label("views"),
            (sa.func.count(Footprint.ip) / total_footprints_count).label("percentage"),
        )
        .group_by(Footprint.country, Footprint.ip)
        .order_by(sa.desc("views"), sa.desc(sa.text("percentage")))
        .where(Footprint.country.ilike(f"%{search}%"))
        .paginate(
            page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
        )
    )

    next_url = (
        url_for("api.table_country", page=data.next_num, **search_args)
        if data.has_next
        else None
    )
    prev_url = (
        url_for("api.table_country", page=data.prev_num, **search_args)
        if data.has_prev
        else None
    )
    return render_template(
        "api/statistics/table-country.html",
        data=data,
        next_url=next_url,
        prev_url=prev_url,
        search=search,
    )


@bp.route("/shorts/table/os")
@login_required
def table_os():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    search_args = {"search": search} if search else {}

    total_browsers_count = (
        db.session.query(sa.func.count(View.id))
        .filter(View.user_id == current_user.id)
        .scalar()
    )

    data = (
        View.query.where(View.user_id == current_user.id)
        .add_columns(
            sa.func.count(View.id).label("views"),
            (sa.func.count(View.id) / total_browsers_count).label("percentage"),
            sa.func.count(sa.distinct(View.short_id)).label("links"),
        )
        .group_by(View.os, View.id)
        .order_by(sa.desc("views"), sa.desc(sa.text("percentage")))
        .where(View.os.ilike(f"%{search}%"))
        .paginate(
            page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
        )
    )

    next_url = (
        url_for("api.table_os", page=data.next_num, **search_args)
        if data.has_next
        else None
    )
    prev_url = (
        url_for("api.table_os", page=data.prev_num, **search_args)
        if data.has_prev
        else None
    )
    return render_template(
        "api/statistics/table-os.html",
        data=data,
        next_url=next_url,
        prev_url=prev_url,
        search=search,
    )


@bp.route("/shorts/table/referrer")
@login_required
def table_referrer():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    search_args = {"search": search} if search else {}

    total_browsers_count = (
        db.session.query(sa.func.count(View.id))
        .filter(View.user_id == current_user.id)
        .scalar()
    )

    data = (
        View.query.where(View.user_id == current_user.id)
        .add_columns(
            sa.func.count(View.id).label("views"),
            (sa.func.count(View.id) / total_browsers_count).label("percentage"),
            sa.func.count(sa.distinct(View.short_id)).label("links"),
        )
        .group_by(View.referrer, View.id)
        .order_by(sa.desc("views"), sa.desc(sa.text("percentage")))
        .where(View.referrer.ilike(f"%{search}%"))
        .paginate(
            page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
        )
    )

    next_url = (
        url_for("api.table_referrer", page=data.next_num, **search_args)
        if data.has_next
        else None
    )
    prev_url = (
        url_for("api.table_referrer", page=data.prev_num, **search_args)
        if data.has_prev
        else None
    )
    return render_template(
        "api/statistics/table-referrer.html",
        data=data,
        next_url=next_url,
        prev_url=prev_url,
        search=search,
    )


@bp.route("/shorts/table/single/<link_id>")
@login_required
def table_single(link_id):
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    search_args = {"search": search} if search else {}

    links = db.paginate(
        current_user.views.where(View.short_id == link_id)
        .join(Footprint, View.ip == Footprint.ip)
        .order_by(View.time.desc())
        .where(
            View.referrer.ilike(f"%{search}%")
            | View.browser.ilike(f"%{search}%")
            | View.os.ilike(f"%{search}%")
            | View.ip.ilike(f"%{search}%")
            | Footprint.country.ilike(f"%{search}%")
            | Footprint.city.ilike(f"%{search}%")
            | Footprint.isp.ilike(f"%{search}%")
        ),
        page=page,
        per_page=current_app.config["POSTS_PER_PAGE"] * 3,
        error_out=False,
    )

    next_url = (
        url_for("api.table_single", link_id=link_id, page=links.next_num, **search_args)
        if links.has_next
        else None
    )
    prev_url = (
        url_for("api.table_single", link_id=link_id, page=links.prev_num, **search_args)
        if links.has_prev
        else None
    )
    return render_template(
        "api/statistics/table-single.html",
        links=links,
        next_url=next_url,
        prev_url=prev_url,
        search=search,
        link_id=link_id,
    )


# Charts
@bp.route("/shorts/chart/overview")
@login_required
def chart_overview():
    """Return a chart of the number of views over time."""
    timeframe = request.args.get("timeframe", 1, type=int)

    match timeframe:
        case 1:
            labels = last_seven_days_label()
            times = labels
            data = chart_data_overview(times)
        case 2:
            labels = last_six_months_label()
            times = last_six_months_datetime()
            data = chart_data_overview(times)
        case 3:
            labels = last_twelve_months_label()
            times = last_twelve_months_datetime()
            data = chart_data_overview(times)
        case _:
            labels = []
            data = []

    return render_template(
        "api/statistics/chart-overview.html",
        labels=labels,
        data=data,
        shorts=shorts,
        timeframe=timeframe,
    )


@bp.route("/shorts/chart/browser")
@login_required
def chart_browser():
    timeframe = request.args.get("timeframe", 1, type=int)
    labels, data = chart_data_browser(timeframe)

    return render_template(
        "api/statistics/chart-browser.html",
        labels=labels,
        data=data,
        shorts=shorts,
        timeframe=timeframe,
    )


@bp.route("/shorts/chart/city")
@login_required
def chart_city():
    timeframe = request.args.get("timeframe", 1, type=int)
    labels, data = chart_data_city(timeframe)

    return render_template(
        "api/statistics/chart-city.html",
        labels=labels,
        data=data,
        shorts=shorts,
        timeframe=timeframe,
    )


@bp.route("/shorts/chart/country")
@login_required
def chart_country():
    timeframe = request.args.get("timeframe", 1, type=int)
    labels, data = chart_data_country(timeframe)

    return render_template(
        "api/statistics/chart-country.html",
        labels=labels,
        data=data,
        shorts=shorts,
        timeframe=timeframe,
    )


@bp.route("/shorts/chart/os")
@login_required
def chart_os():
    timeframe = request.args.get("timeframe", 1, type=int)
    labels, data = chart_data_os(timeframe)

    return render_template(
        "api/statistics/chart-os.html",
        labels=labels,
        data=data,
        shorts=shorts,
        timeframe=timeframe,
    )


@bp.route("/shorts/chart/referrer")
@login_required
def chart_referrer():
    timeframe = request.args.get("timeframe", 1, type=int)
    labels, data = chart_data_referrer(timeframe)

    return render_template(
        "api/statistics/chart-referrer.html",
        labels=labels,
        data=data,
        shorts=shorts,
        timeframe=timeframe,
    )


@bp.route("/shorts/chart/single/<link_id>")
@login_required
def chart_single(link_id):
    timeframe = request.args.get("timeframe", 1, type=int)
    match timeframe:
        case 1:
            labels = last_seven_days_label()
            times = labels
            data = chart_data_single(times, link_id)
        case 2:
            labels = last_six_months_label()
            times = last_six_months_datetime()
            data = chart_data_single(times, link_id)
        case 3:
            labels = last_twelve_months_label()
            times = last_twelve_months_datetime()
            data = chart_data_single(times, link_id)
        case _:
            labels = []
            data = []

    return render_template(
        "api/statistics/chart-single.html",
        labels=labels,
        data=data,
        link_id=link_id,
        timeframe=timeframe,
    )
