import re

import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, URLField, TextAreaField
from wtforms.validators import DataRequired, URL, ValidationError

from exile import db
from exile.models import Short


class ShortForm(FlaskForm):
    origin = StringField("Short Link", validators=[DataRequired()])
    destination = URLField("Destination URL", validators=[DataRequired(), URL()])
    note = TextAreaField("Note")
    submit = SubmitField("Generate Link")

    def validate_origin(self, origin):
        user = db.session.scalar(sa.select(Short).where(Short.origin == origin.data))
        if user is not None:
            raise ValidationError("Please use a different origin.")

        if not re.search("^[a-zA-Z0-9_-]*$", origin.data):
            raise ValidationError(
                "Invalid input!  Use only letters, numbers, underscores, and hyphens."
            )


class EditForm(FlaskForm):
    origin = StringField("Short Link", validators=[DataRequired()])
    destination = URLField("Destination URL", validators=[DataRequired(), URL()])
    note = TextAreaField("Note")
    submit = SubmitField("Save")

    def validate_origin(self, origin):
        if not re.search("^[a-zA-Z0-9_-]*$", origin.data):
            raise ValidationError(
                "Invalid input!  Use only letters, numbers, underscores, and hyphens."
            )
