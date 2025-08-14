import os
from datetime import datetime
from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from models import UserRole, Achievement, UserAchievement, User
from app import db

def role_required(allowed_roles):
    """Decorator to restrict access based on user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            if isinstance(allowed_roles, str):
                roles = [allowed_roles]
            else:
                roles = allowed_roles
            
            user_role = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
            if user_role not in roles:
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder='verification'):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        return filename
    return None

def award_points(user_id, points):
    """Award points to a user and check for new achievements"""
    user = User.query.get(user_id)
    if user and user.is_volunteer():
        user.points += points
        db.session.commit()
        check_achievements(user)

def check_achievements(user):
    """Check if user has earned any new achievements"""
    if not user.is_volunteer():
        return
    
    # Get achievements user doesn't have yet
    earned_achievement_ids = db.session.query(UserAchievement.achievement_id).filter_by(user_id=user.id).all()
    earned_ids = [id[0] for id in earned_achievement_ids]
    
    available_achievements = Achievement.query.filter(~Achievement.id.in_(earned_ids)).all()
    
    for achievement in available_achievements:
        if user.total_points >= achievement.points_required:
            user_achievement = UserAchievement()
            user_achievement.user_id = user.id
            user_achievement.achievement_id = achievement.id
            db.session.add(user_achievement)
    
    db.session.commit()

def initialize_achievements():
    """Initialize default achievements if they don't exist"""
    achievements_data = [
        {'name': 'First Steps', 'description': 'Complete your first volunteer slot', 'points_required': 10, 'icon': 'award'},
        {'name': 'Dedicated Helper', 'description': 'Earn 50 points through volunteering', 'points_required': 50, 'icon': 'heart'},
        {'name': 'Community Champion', 'description': 'Earn 100 points through volunteering', 'points_required': 100, 'icon': 'star'},
        {'name': 'Volunteer Leader', 'description': 'Earn 200 points through volunteering', 'points_required': 200, 'icon': 'crown'},
        {'name': 'Change Maker', 'description': 'Earn 500 points through volunteering', 'points_required': 500, 'icon': 'zap'},
    ]
    
    for achievement_data in achievements_data:
        if not Achievement.query.filter_by(name=achievement_data['name']).first():
            achievement = Achievement()
            achievement.name = achievement_data['name']
            achievement.description = achievement_data['description']
            achievement.points_required = achievement_data['points_required']
            achievement.icon = achievement_data['icon']
            db.session.add(achievement)
    
    db.session.commit()

def get_user_stats(user):
    """Get statistics for a user based on their role"""
    if user.is_volunteer():
        from models import Booking
        total_bookings = Booking.query.filter_by(volunteer_id=user.id).count()
        completed_bookings = Booking.query.filter_by(volunteer_id=user.id, status='completed').count()
        return {
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'points': user.points,
            'achievements_count': len(user.achievements)
        }
    elif user.is_ngo():
        from models import Project, Booking
        total_projects = Project.query.filter_by(ngo_id=user.id).count()
        active_projects = Project.query.filter_by(ngo_id=user.id, is_active=True).count()
        from models import TimeSlot
        total_volunteers = db.session.query(Booking.volunteer_id).join(
            TimeSlot
        ).join(Project).filter(Project.ngo_id == user.id).distinct().count()
        return {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_volunteers': total_volunteers
        }
    elif user.is_donor():
        from models import Donation
        total_donations = Donation.query.filter_by(donor_id=user.id).count()
        total_amount = db.session.query(db.func.sum(Donation.amount)).filter_by(donor_id=user.id).scalar() or 0
        return {
            'total_donations': total_donations,
            'total_amount': total_amount
        }
    elif user.is_admin():
        from models import User, Project, Donation, VerificationUpload
        total_users = User.query.count()
        total_projects = Project.query.count()
        pending_verifications = VerificationUpload.query.filter_by(status='pending').count()
        total_donations = db.session.query(db.func.sum(Donation.amount)).scalar() or 0
        return {
            'total_users': total_users,
            'total_projects': total_projects,
            'pending_verifications': pending_verifications,
            'total_donations': total_donations
        }
    return {}
