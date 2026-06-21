from datetime import datetime
from ..extensions import db


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(40), nullable=False)
    group = db.Column(db.String(40), nullable=False)


class UserAchievement(db.Model):
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id'),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
