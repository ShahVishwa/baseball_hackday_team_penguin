#!/usr/bin/env python3
from app import db
from app.models import User, Game

db.create_all()
User.query.all()
