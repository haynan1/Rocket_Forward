from datetime import datetime
from ..extensions import db


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    scheduled_for = db.Column(db.DateTime, nullable=False)
    sent_at = db.Column(db.DateTime)
