from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, db
from werkzeug.utils import secure_filename
import os

users_bp = Blueprint('users', __name__)

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户个人信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(include_email=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户个人信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # 更新基本信息
        if 'name' in data:
            user.name = data['name']
        
        if 'phone' in data:
            user.phone = data['phone']
        
        if 'birthday' in data and data['birthday']:
            from datetime import datetime
            user.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
        
        if 'gender' in data:
            user.gender = data['gender']
        
        # 更新健康信息
        if 'height' in data:
            user.height = float(data['height']) if data['height'] else None
        
        if 'weight' in data:
            user.weight = float(data['weight']) if data['weight'] else None
        
        if 'activity_level' in data:
            user.activity_level = data['activity_level']
        
        if 'dietary_preferences' in data:
            user.dietary_preferences = data['dietary_preferences']
        
        if 'allergies' in data:
            user.allergies = data['allergies']
        
        if 'health_goals' in data:
            user.health_goals = data['health_goals']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict(include_email=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    """上传用户头像"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'avatar' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            from flask import current_app
            filename = secure_filename(f"user_{user.id}_{file.filename}")
            filepath = os.path.join(current_app.config['USER_AVATARS_PATH'], filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 保存文件
            file.save(filepath)
            
            # 更新用户头像路径
            user.avatar = f"images/avatars/{filename}"
            db.session.commit()
            
            return jsonify({
                'message': 'Avatar uploaded successfully',
                'avatar_url': user.avatar
            }), 200
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    """获取用户偏好设置"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        preferences = {
            'dietary_preferences': user.dietary_preferences,
            'allergies': user.allergies,
            'health_goals': user.health_goals,
            'activity_level': user.activity_level
        }
        
        return jsonify({'preferences': preferences}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_preferences():
    """更新用户偏好设置"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'dietary_preferences' in data:
            user.dietary_preferences = data['dietary_preferences']
        
        if 'allergies' in data:
            user.allergies = data['allergies']
        
        if 'health_goals' in data:
            user.health_goals = data['health_goals']
        
        if 'activity_level' in data:
            user.activity_level = data['activity_level']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Preferences updated successfully',
            'preferences': {
                'dietary_preferences': user.dietary_preferences,
                'allergies': user.allergies,
                'health_goals': user.health_goals,
                'activity_level': user.activity_level
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """获取用户仪表板数据"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        from sqlalchemy import func
        
        # 统计信息
        stats = {
            'total_recipes': user.recipes.count(),
            'total_meal_plans': user.meal_plans.count(),
            'total_ingredients': user.ingredient_stocks.count(),
            'total_shopping_lists': user.shopping_lists.count()
        }
        
        # 最近的食谱
        recent_recipes = user.recipes.order_by(Recipe.created_at.desc()).limit(5).all()
        
        # 活跃的计划
        active_plans = user.meal_plans.filter_by(status='active').order_by(MealPlan.created_at.desc()).limit(3).all()
        
        # 即将过期的食材
        expiring_ingredients = []
        for stock in user.ingredient_stocks.filter_by(is_active=True).all():
            if stock.is_expiring_soon():
                expiring_ingredients.append(stock.to_dict(include_ingredient=True))
        
        dashboard_data = {
            'user': user.to_dict(include_email=True),
            'stats': stats,
            'recent_recipes': [recipe.to_dict() for recipe in recent_recipes],
            'active_plans': [plan.to_dict(include_items=True) for plan in active_plans],
            'expiring_ingredients': expiring_ingredients
        }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500