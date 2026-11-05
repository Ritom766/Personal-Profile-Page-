import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Get absolute path of current working directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Initialize Flask with explicit template folder path (Fixes TemplateNotFound error)
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
CORS(app)

# SQLite Database Setup (Absolute path to profile.db inside project folder)
db_path = os.path.join(basedir, 'profile.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== ORM MODELS ====================

class ProfileInfo(db.Model):
    __tablename__ = 'profile_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    degree = db.Column(db.String(150), nullable=False)
    institution = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'degree': self.degree,
            'institution': self.institution,
            'location': self.location,
            'bio': self.bio
        }

class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='General')

    def to_dict(self):
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'category': self.category
        }

# Automatic Database Initialization & Default Data Seeding
with app.app_context():
    db.create_all()
    
    # Seed Profile Info if empty
    if not db.session.get(ProfileInfo, 1):
        default_profile = ProfileInfo(
            id=1,
            name='Nafis Tahsin Ritom',
            title='CSE Student & Security Analyst',
            degree='BSc in Computer Science & Engineering (CSE)',
            institution='Independent University, Bangladesh (IUB)',
            location='Dhaka, Bangladesh',
            bio='Software Development enthusiast and Cybersecurity researcher focused on building secure web systems, backend API architecture, database optimization, and penetration testing.'
        )
        db.session.add(default_profile)

    # Seed Initial Skills if empty
    if Skill.query.count() == 0:
        initial_skills = [
            Skill(skill_name='Java', category='Programming'),
            Skill(skill_name='Python', category='Programming'),
            Skill(skill_name='HTML', category='Frontend'),
            Skill(skill_name='CSS', category='Frontend'),
            Skill(skill_name='SQL', category='Database'),
            Skill(skill_name='Database Management', category='Database'),
            Skill(skill_name='Penetration Testing', category='Security'),
            Skill(skill_name='IT Security (Ethical Hacking)', category='Security')
        ]
        db.session.add_all(initial_skills)

    db.session.commit()

# ==================== ROUTE RENDERING ====================

@app.route('/')
def public_profile():
    return render_template('index.html')  # System 1

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html') # System 2

# ==================== REST API ENDPOINTS ====================

# 1. READ Profile (GET)
@app.route('/api/profile', methods=['GET'])
def get_profile():
    try:
        profile = db.session.get(ProfileInfo, 1)
        if profile:
            return jsonify(profile.to_dict()), 200
        return jsonify({'error': 'Profile not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 2. UPDATE Profile (PUT)
@app.route('/api/profile', methods=['PUT'])
def update_profile():
    try:
        data = request.json or {}
        profile = db.session.get(ProfileInfo, 1)
        if not profile:
            profile = ProfileInfo(id=1)
            db.session.add(profile)
        
        profile.name = data.get('name', profile.name)
        profile.title = data.get('title', profile.title)
        profile.degree = data.get('degree', profile.degree)
        profile.institution = data.get('institution', profile.institution)
        profile.location = data.get('location', profile.location)
        profile.bio = data.get('bio', profile.bio)
        
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully via REST API!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 3. READ Skills (GET)
@app.route('/api/skills', methods=['GET'])
def get_skills():
    try:
        skills = Skill.query.order_by(Skill.id.desc()).all()
        return jsonify([skill.to_dict() for skill in skills]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 4. CREATE Skill (POST)
@app.route('/api/skills', methods=['POST'])
def add_skill():
    try:
        data = request.json or {}
        if not data.get('skill_name'):
            return jsonify({'error': 'skill_name is required'}), 400

        new_skill = Skill(
            skill_name=data['skill_name'],
            category=data.get('category', 'General')
        )
        db.session.add(new_skill)
        db.session.commit()
        return jsonify({'message': 'Skill added successfully!', 'id': new_skill.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# 5. DELETE Skill (DELETE)
@app.route('/api/skills/<int:skill_id>', methods=['DELETE'])
def delete_skill(skill_id):
    try:
        skill = db.session.get(Skill, skill_id)
        if not skill:
            return jsonify({'error': 'Skill not found'}), 404
            
        db.session.delete(skill)
        db.session.commit()
        return jsonify({'message': 'Skill deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)