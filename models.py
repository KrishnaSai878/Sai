from datetime import datetime
from enum import Enum
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from app import db

class UserRole(Enum):
    VOLUNTEER = 'volunteer'
    NGO = 'ngo'
    DONOR = 'donor'
    ADMIN = 'admin'

class BookingStatus(Enum):
    BOOKED = 'booked'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class VerificationStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.Enum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    total_points = db.Column(db.Integer, default=0)
    
    # NGO-specific fields
    ngo_name = db.Column(db.String(100), nullable=True)
    ngo_description = db.Column(db.Text, nullable=True)
    
    # Relationships
    projects = db.relationship('Project', backref='ngo', lazy=True, foreign_keys='Project.ngo_id')
    bookings = db.relationship('Booking', backref='volunteer', lazy=True, foreign_keys='Booking.volunteer_id')
    donations = db.relationship('Donation', backref='donor', lazy=True, foreign_keys='Donation.donor_id')
    verification_uploads = db.relationship('VerificationUpload', backref='volunteer', lazy=True, foreign_keys='VerificationUpload.volunteer_id')
    user_achievements = db.relationship('UserAchievement', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_volunteer(self):
        return self.role == UserRole.VOLUNTEER
    
    def is_ngo(self):
        return self.role == UserRole.NGO
    
    def is_donor(self):
        return self.role == UserRole.DONOR
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    points_per_slot = db.Column(db.Integer, nullable=False, default=10)
    required_skills = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Foreign keys
    ngo_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    time_slots = db.relationship('TimeSlot', backref='project', lazy=True, cascade='all, delete-orphan')
    donations = db.relationship('Donation', backref='project', lazy=True)
    
    def __repr__(self):
        return f'<Project {self.title}>'

class TimeSlot(db.Model):
    __tablename__ = 'time_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    max_volunteers = db.Column(db.Integer, nullable=False, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='time_slot', lazy=True, cascade='all, delete-orphan')
    
    @property
    def available_spots(self):
        booked_count = Booking.query.filter_by(
            time_slot_id=self.id,
            status=BookingStatus.BOOKED
        ).count()
        return max(0, self.max_volunteers - booked_count)
    
    @property
    def is_full(self):
        return self.available_spots == 0
    
    def __repr__(self):
        return f'<TimeSlot {self.start_time} - {self.end_time}>'

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.BOOKED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    points_awarded = db.Column(db.Integer, default=0)
    
    # Foreign keys
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    time_slot_id = db.Column(db.Integer, db.ForeignKey('time_slots.id'), nullable=False)
    
    # Relationships
    verification_uploads = db.relationship('VerificationUpload', backref='booking', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Booking {self.volunteer_id} - {self.time_slot_id}>'

class VerificationUpload(db.Model):
    __tablename__ = 'verification_uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(VerificationStatus), default=VerificationStatus.PENDING)
    review_notes = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # Foreign keys
    volunteer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id], backref='reviewed_verifications')
    
    def __repr__(self):
        return f'<VerificationUpload {self.filename}>'

class Donation(db.Model):
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text, nullable=True)
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    def __repr__(self):
        return f'<Donation ${self.amount}>'

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    points_required = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_achievements = db.relationship('UserAchievement', backref='achievement', lazy=True)
    
    def __repr__(self):
        return f'<Achievement {self.name}>'

class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    
    # Unique constraint to prevent duplicate achievements
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),)
    
    def __repr__(self):
        return f'<UserAchievement {self.user_id} - {self.achievement_id}>'