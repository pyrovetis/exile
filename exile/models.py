from datetime import datetime, timezone
from hashlib import md5
from time import time
from typing import Optional

import jwt
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from exile import db, login


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))

    shorts: so.DynamicMapped["Short"] = so.relationship(back_populates="users")
    views: so.DynamicMapped["View"] = so.relationship(back_populates="users")

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except Exception:
            return
        return db.session.get(User, id)


class Short(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    origin: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    destination: so.Mapped[str] = so.mapped_column(sa.String(1024))
    created_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    note: so.Mapped[Optional[str]] = so.mapped_column(sa.Text())

    user_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey("user.id"), index=True, default=None
    )
    users: so.Mapped["User"] = so.relationship(back_populates="shorts")
    histories: so.DynamicMapped["History"] = so.relationship(back_populates="shorts")
    views: so.DynamicMapped["View"] = so.relationship(back_populates="shorts")

    def __repr__(self):
        return f"<Short {self.origin}>"


class View(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    time: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    referrer: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    browser: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    os: so.Mapped[Optional[str]] = so.mapped_column(sa.String(64))
    ip: so.Mapped[str] = so.mapped_column(
        sa.String(128), sa.ForeignKey("footprint.ip"), index=True
    )

    short_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("short.id"), index=True, nullable=True
    )
    shorts: so.Mapped["Short"] = so.relationship(back_populates="views")

    user_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey("user.id"), index=True
    )
    users: so.Mapped["User"] = so.relationship(back_populates="views")

    footprints: so.Mapped["Footprint"] = so.relationship(back_populates="views")

    def __repr__(self):
        return f"<View {self.id}>"


class Footprint(db.Model):
    ip: so.Mapped[str] = so.mapped_column(
        sa.String(128), index=True, unique=True, primary_key=True
    )
    continent: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    continentCode: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    country: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    countryCode: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    region: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    regionName: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    city: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    district: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    zip: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    lat: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    lon: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    timezone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    offset: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    currency: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    isp: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    org: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    as_: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    asname: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    mobile: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    proxy: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    hosting: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))

    views: so.DynamicMapped["View"] = so.relationship(back_populates="footprints")

    def __repr__(self):
        return f"<Footprint {self.ip}>"


class History(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    origin: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    destination: so.Mapped[str] = so.mapped_column(sa.String(1024))
    updated_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    note: so.Mapped[str] = so.mapped_column(sa.Text())

    short_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey("short.id"), index=True, default=None
    )
    shorts: so.Mapped["Short"] = so.relationship(back_populates="histories")

    def __repr__(self):
        return f"<Short {self.id}>"


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
