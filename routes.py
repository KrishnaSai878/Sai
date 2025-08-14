import os
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, UserRole, Project, TimeSlot, Booking, VerificationUpload, Donation, Achievement, UserAchievement
from forms import (LoginForm, RegistrationForm, ProjectForm, TimeSlotForm, 
                   VerificationUploadForm, DonationForm, VerificationReviewForm)
from utils import role_required, save_uploaded_file, award_points, initialize_achievements, get_user_stats
from sqlalchemy import desc, func

# Initialize achievements on startup
with app.app_context():
    initialize_achievements()

@app.route('/')
def index():
    """Landing page with role-based redirection"""
    if current_user.is_authenticated:
        if current_user.is_volunteer():
            return redirect(url_for('volunteer_dashboard'))
        elif current_user.is_ngo():
            return redirect(url_for('ngo_dashboard'))
        elif current_user.is_donor():
            return redirect(url_for('donor_dashboard'))
        elif current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
            return render_template('auth/register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return render_template('auth/register.html', form=form)
        
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data
        user.role = UserRole(form.role.data)
        user.ngo_name = form.ngo_name.data if form.role.data == 'ngo' else None
        user.ngo_description = form.ngo_description.data if form.role.data == 'ngo' else None
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Volunteer Routes
@app.route('/volunteer/dashboard')
@login_required
@role_required('volunteer')
def volunteer_dashboard():
    stats = get_user_stats(current_user)
    recent_bookings = Booking.query.filter_by(volunteer_id=current_user.id).order_by(desc(Booking.created_at)).limit(5).all()
    upcoming_slots = Booking.query.join(TimeSlot).filter(
        Booking.volunteer_id == current_user.id,
        TimeSlot.start_time > datetime.utcnow(),
        Booking.status == 'confirmed'
    ).order_by(TimeSlot.start_time).limit(5).all()
    
    return render_template('volunteer/dashboard.html', stats=stats, 
                         recent_bookings=recent_bookings, upcoming_slots=upcoming_slots)

@app.route('/volunteer/projects')
@login_required
@role_required('volunteer')
def volunteer_projects():
    projects = Project.query.filter_by(is_active=True).all()
    return render_template('volunteer/projects.html', projects=projects)

@app.route('/volunteer/book_slot/<int:slot_id>')
@login_required
@role_required('volunteer')
def book_slot(slot_id):
    slot = TimeSlot.query.get_or_404(slot_id)
    
    # Check if slot is available
    if not slot.is_available or slot.available_spots <= 0:
        flash('This slot is no longer available', 'warning')
        return redirect(url_for('volunteer_projects'))
    
    # Check if user already booked this slot
    existing_booking = Booking.query.filter_by(volunteer_id=current_user.id, time_slot_id=slot_id).first()
    if existing_booking:
        flash('You have already booked this slot', 'warning')
        return redirect(url_for('volunteer_projects'))
    
    booking = Booking()
    booking.volunteer_id = current_user.id
    booking.time_slot_id = slot_id
    db.session.add(booking)
    db.session.commit()
    
    flash('Slot booked successfully!', 'success')
    return redirect(url_for('volunteer_bookings'))

@app.route('/volunteer/bookings')
@login_required
@role_required('volunteer')
def volunteer_bookings():
    bookings = Booking.query.filter_by(volunteer_id=current_user.id).order_by(desc(Booking.created_at)).all()
    return render_template('volunteer/bookings.html', bookings=bookings)

@app.route('/volunteer/upload_verification/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@role_required('volunteer')
def upload_verification(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.volunteer_id != current_user.id:
        abort(403)
    
    form = VerificationUploadForm()
    if form.validate_on_submit():
        filename = save_uploaded_file(form.file.data, 'verification')
        if filename:
            upload = VerificationUpload()
            upload.booking_id = booking_id
            upload.volunteer_id = current_user.id
            upload.filename = filename
            upload.original_filename = form.file.data.filename
            upload.notes = form.notes.data
            db.session.add(upload)
            db.session.commit()
            flash('Verification uploaded successfully!', 'success')
            return redirect(url_for('volunteer_bookings'))
        else:
            flash('Invalid file format. Please upload an image.', 'danger')
    
    return render_template('volunteer/upload_verification.html', form=form, booking=booking)

@app.route('/volunteer/leaderboards')
@login_required
@role_required('volunteer')
def volunteer_leaderboards():
    # Global leaderboard
    global_leaders = User.query.filter_by(role=UserRole.VOLUNTEER).order_by(desc(User.total_points)).limit(10).all()
    
    # NGO-specific leaderboards (volunteers who worked for each NGO)
    ngo_leaders = {}
    ngos = User.query.filter_by(role=UserRole.NGO).all()
    
    for ngo in ngos:
        # Get top volunteers for this NGO
        volunteers = db.session.query(User, func.sum(Booking.points_awarded)).join(
            Booking, User.id == Booking.volunteer_id
        ).join(
            TimeSlot, Booking.time_slot_id == TimeSlot.id
        ).join(
            Project, TimeSlot.project_id == Project.id
        ).filter(
            Project.ngo_id == ngo.id,
            Booking.status == 'completed'
        ).group_by(User.id).order_by(desc(func.sum(Booking.points_awarded))).limit(5).all()
        
        ngo_leaders[ngo] = volunteers
    
    return render_template('volunteer/leaderboards.html', 
                         global_leaders=global_leaders, ngo_leaders=ngo_leaders)

@app.route('/volunteer/achievements')
@login_required
@role_required('volunteer')
def volunteer_achievements():
    earned_achievements = db.session.query(Achievement, UserAchievement.earned_at).join(
        UserAchievement, Achievement.id == UserAchievement.achievement_id
    ).filter(UserAchievement.user_id == current_user.id).all()
    
    available_achievements = db.session.query(Achievement).filter(
        ~Achievement.id.in_([ua.achievement_id for ua in current_user.achievements])
    ).all()
    
    return render_template('volunteer/achievements.html', 
                         earned_achievements=earned_achievements,
                         available_achievements=available_achievements)

# NGO Routes
@app.route('/ngo/dashboard')
@login_required
@role_required('ngo')
def ngo_dashboard():
    stats = get_user_stats(current_user)
    recent_projects = Project.query.filter_by(ngo_id=current_user.id).order_by(desc(Project.created_at)).limit(3).all()
    pending_verifications = VerificationUpload.query.join(Booking).join(TimeSlot).join(Project).filter(
        Project.ngo_id == current_user.id,
        VerificationUpload.status == VerificationStatus.PENDING
    ).count()
    
    return render_template('ngo/dashboard.html', stats=stats, 
                         recent_projects=recent_projects, 
                         pending_verifications=pending_verifications)

@app.route('/ngo/manage_projects')
@login_required
@role_required('ngo')
def ngo_manage_projects():
    projects = Project.query.filter_by(ngo_id=current_user.id).order_by(desc(Project.created_at)).all()
    return render_template('ngo/manage_projects.html', projects=projects)

@app.route('/ngo/create_project', methods=['GET', 'POST'])
@login_required
@role_required('ngo')
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project()
        project.title = form.title.data
        project.description = form.description.data
        project.location = form.location.data
        project.points_per_slot = form.points_per_slot.data
        project.required_skills = form.required_skills.data
        project.ngo_id = current_user.id
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('ngo_manage_projects'))
    
    return render_template('ngo/create_project.html', form=form)

@app.route('/ngo/project/<int:project_id>/add_slots', methods=['GET', 'POST'])
@login_required
@role_required('ngo')
def add_time_slots(project_id):
    project = Project.query.get_or_404(project_id)
    if project.ngo_id != current_user.id:
        abort(403)
    
    form = TimeSlotForm()
    if form.validate_on_submit():
        # Ensure end time is after start time and duration is 2 hours
        if form.end_time.data and form.start_time.data:
            duration = form.end_time.data - form.start_time.data
            if duration.total_seconds() != 7200:  # 2 hours
                flash('Time slots must be exactly 2 hours long', 'warning')
            elif form.start_time.data < datetime.now():
                flash('Start time cannot be in the past', 'warning')
            else:
                slot = TimeSlot()
                slot.project_id = project_id
                slot.start_time = form.start_time.data
                slot.end_time = form.end_time.data
                slot.max_volunteers = form.max_volunteers.data
            db.session.add(slot)
            db.session.commit()
            flash('Time slot added successfully!', 'success')
            return redirect(url_for('ngo_manage_projects'))
    
    return render_template('ngo/add_slots.html', form=form, project=project)

@app.route('/ngo/volunteer_management')
@login_required
@role_required('ngo')
def ngo_volunteer_management():
    # Get all volunteers who have booked slots for this NGO's projects
    volunteers = db.session.query(User).join(
        Booking, User.id == Booking.volunteer_id
    ).join(
        TimeSlot, Booking.time_slot_id == TimeSlot.id
    ).join(
        Project, TimeSlot.project_id == Project.id
    ).filter(Project.ngo_id == current_user.id).distinct().all()
    
    return render_template('ngo/volunteer_management.html', volunteers=volunteers)

@app.route('/ngo/verification_gallery')
@login_required
@role_required('ngo')
def ngo_verification_gallery():
    verifications = VerificationUpload.query.join(Booking).join(TimeSlot).join(Project).filter(
        Project.ngo_id == current_user.id
    ).order_by(desc(VerificationUpload.uploaded_at)).all()
    
    return render_template('ngo/verification_gallery.html', verifications=verifications)

@app.route('/ngo/review_verification/<int:verification_id>', methods=['GET', 'POST'])
@login_required
@role_required('ngo')
def review_verification(verification_id):
    verification = VerificationUpload.query.get_or_404(verification_id)
    
    # Ensure this verification belongs to this NGO's project
    if verification.booking.time_slot.project.ngo_id != current_user.id:
        abort(403)
    
    form = VerificationReviewForm()
    if form.validate_on_submit():
        verification.status = form.status.data
        verification.notes = form.notes.data
        
        if form.status.data == 'approved':
            # Award points and mark booking as completed
            booking = verification.booking
            points = booking.time_slot.project.points_per_slot
            booking.status = 'completed'
            booking.points_awarded = points
            award_points(booking.volunteer_id, points)
            
        db.session.commit()
        flash('Verification reviewed successfully!', 'success')
        return redirect(url_for('ngo_verification_gallery'))
    
    return render_template('ngo/review_verification.html', form=form, verification=verification)

# Donor Routes
@app.route('/donor/dashboard')
@login_required
@role_required('donor')
def donor_dashboard():
    stats = get_user_stats(current_user)
    recent_donations = Donation.query.filter_by(donor_id=current_user.id).order_by(desc(Donation.created_at)).limit(5).all()
    
    return render_template('donor/dashboard.html', stats=stats, recent_donations=recent_donations)

@app.route('/donor/browse_projects')
@login_required
@role_required('donor')
def donor_browse_projects():
    projects = Project.query.filter_by(is_active=True).all()
    return render_template('donor/browse_projects.html', projects=projects)

@app.route('/donor/donate/<int:project_id>', methods=['GET', 'POST'])
@login_required
@role_required('donor')
def donate_to_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = DonationForm()
    
    if form.validate_on_submit():
        donation = Donation()
        donation.donor_id = current_user.id
        donation.project_id = project_id
        donation.amount = form.amount.data
        donation.message = form.message.data
        donation.is_anonymous = form.is_anonymous.data
        db.session.add(donation)
        db.session.commit()
        flash(f'Thank you for your donation of ${form.amount.data}!', 'success')
        return redirect(url_for('donor_donation_history'))
    
    return render_template('donor/donate.html', form=form, project=project)

@app.route('/donor/donation_history')
@login_required
@role_required('donor')
def donor_donation_history():
    donations = Donation.query.filter_by(donor_id=current_user.id).order_by(desc(Donation.created_at)).all()
    return render_template('donor/donation_history.html', donations=donations)

@app.route('/donor/impact_reports')
@login_required
@role_required('donor')
def donor_impact_reports():
    # Calculate impact metrics
    total_donated = db.session.query(func.sum(Donation.amount)).filter_by(donor_id=current_user.id).scalar() or 0
    projects_supported = db.session.query(Donation.project_id).filter_by(donor_id=current_user.id).distinct().count()
    
    # Get projects with donation amounts
    project_donations = db.session.query(
        Project, func.sum(Donation.amount)
    ).join(Donation).filter(
        Donation.donor_id == current_user.id
    ).group_by(Project.id).all()
    
    return render_template('donor/impact_reports.html', 
                         total_donated=total_donated,
                         projects_supported=projects_supported,
                         project_donations=project_donations)

# Admin Routes
@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    stats = get_user_stats(current_user)
    
    # Additional admin stats
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    recent_projects = Project.query.order_by(desc(Project.created_at)).limit(5).all()
    
    return render_template('admin/dashboard.html', stats=stats, 
                         recent_users=recent_users, recent_projects=recent_projects)

@app.route('/admin/user_management')
@login_required
@role_required('admin')
def admin_user_management():
    users = User.query.order_by(desc(User.created_at)).all()
    return render_template('admin/user_management.html', users=users)

@app.route('/admin/verification_queue')
@login_required
@role_required('admin')
def admin_verification_queue():
    pending_verifications = VerificationUpload.query.filter_by(status=VerificationStatus.PENDING).order_by(desc(VerificationUpload.uploaded_at)).all()
    return render_template('admin/verification_queue.html', verifications=pending_verifications)

@app.route('/admin/platform_analytics')
@login_required
@role_required('admin')
def admin_platform_analytics():
    # Calculate platform metrics
    total_users = User.query.count()
    users_by_role = db.session.query(User.role, func.count(User.id)).group_by(User.role).all()
    total_projects = Project.query.count()
    total_bookings = Booking.query.count()
    completed_bookings = Booking.query.filter_by(status='completed').count()
    total_donations = db.session.query(func.sum(Donation.amount)).scalar() or 0
    
    return render_template('admin/platform_analytics.html',
                         total_users=total_users,
                         users_by_role=users_by_role,
                         total_projects=total_projects,
                         total_bookings=total_bookings,
                         completed_bookings=completed_bookings,
                         total_donations=total_donations)

@app.route('/admin/toggle_user/<int:user_id>')
@login_required
@role_required('admin')
def admin_toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate yourself', 'warning')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.username} has been {status}', 'success')
    
    return redirect(url_for('admin_user_management'))

# Error handlers
@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
