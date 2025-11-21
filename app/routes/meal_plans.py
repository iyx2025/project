from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.models import MealPlan, MealPlanItem, Recipe, User, db

meal_plans_bp = Blueprint('meal_plans', __name__)

@meal_plans_bp.route('/', methods=['GET'])
@jwt_required()
def get_meal_plans():
    """获取用户的膳食计划列表"""
    try:
        current_user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        # 基础查询
        query = MealPlan.query.filter_by(user_id=current_user_id)
        
        # 状态筛选
        if status:
            query = query.filter_by(status=status)
        
        # 排序
        query = query.order_by(MealPlan.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        meal_plans = pagination.items
        
        return jsonify({
            'meal_plans': [plan.to_dict() for plan in meal_plans],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/<int:plan_id>', methods=['GET'])
@jwt_required()
def get_meal_plan(plan_id):
    """获取膳食计划详情"""
    try:
        current_user_id = get_jwt_identity()
        meal_plan = MealPlan.query.filter_by(id=plan_id, user_id=current_user_id).first()
        
        if not meal_plan:
            return jsonify({'error': 'Meal plan not found'}), 404
        
        return jsonify({
            'meal_plan': meal_plan.to_dict(include_items=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/', methods=['POST'])
@jwt_required()
def create_meal_plan():
    """创建膳食计划"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title') or not data.get('start_date') or not data.get('end_date'):
            return jsonify({'error': 'Title, start_date and end_date are required'}), 400
        
        # 解析日期
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if start_date >= end_date:
            return jsonify({'error': 'End date must be after start date'}), 400
        
        # 创建膳食计划
        meal_plan = MealPlan(
            user_id=current_user_id,
            title=data['title'],
            description=data.get('description', ''),
            start_date=start_date,
            end_date=end_date,
            is_generated=False
        )
        
        # 设置营养目标
        if data.get('nutrition_targets'):
            meal_plan.set_nutrition_targets(data['nutrition_targets'])
        
        db.session.add(meal_plan)
        db.session.flush()  # 获取meal_plan.id
        
        # 添加计划项
        if data.get('items'):
            for item_data in data['items']:
                if not item_data.get('recipe_id') or not item_data.get('planned_date') or not item_data.get('meal_type'):
                    continue
                
                planned_date = datetime.strptime(item_data['planned_date'], '%Y-%m-%d').date()
                
                # 检查食谱是否存在且公开
                recipe = Recipe.query.filter_by(id=item_data['recipe_id'], is_public=True).first()
                if not recipe:
                    continue
                
                plan_item = MealPlanItem(
                    meal_plan_id=meal_plan.id,
                    recipe_id=item_data['recipe_id'],
                    planned_date=planned_date,
                    meal_type=item_data['meal_type'],
                    servings=int(item_data.get('servings', 1)),
                    notes=item_data.get('notes', '')
                )
                db.session.add(plan_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Meal plan created successfully',
            'meal_plan': meal_plan.to_dict(include_items=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_meal_plan(plan_id):
    """更新膳食计划"""
    try:
        current_user_id = get_jwt_identity()
        meal_plan = MealPlan.query.filter_by(id=plan_id, user_id=current_user_id).first()
        
        if not meal_plan:
            return jsonify({'error': 'Meal plan not found'}), 404
        
        data = request.get_json()
        
        # 更新基本信息
        if 'title' in data:
            meal_plan.title = data['title']
        
        if 'description' in data:
            meal_plan.description = data['description']
        
        if 'start_date' in data:
            meal_plan.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        
        if 'end_date' in data:
            meal_plan.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if 'status' in data:
            meal_plan.status = data['status']
        
        if 'nutrition_targets' in data:
            meal_plan.set_nutrition_targets(data['nutrition_targets'])
        
        # 更新计划项（如果提供）
        if 'items' in data:
            # 删除现有计划项
            MealPlanItem.query.filter_by(meal_plan_id=plan_id).delete()
            
            # 添加新的计划项
            for item_data in data['items']:
                if not item_data.get('recipe_id') or not item_data.get('planned_date') or not item_data.get('meal_type'):
                    continue
                
                planned_date = datetime.strptime(item_data['planned_date'], '%Y-%m-%d').date()
                
                # 检查食谱是否存在且公开
                recipe = Recipe.query.filter_by(id=item_data['recipe_id'], is_public=True).first()
                if not recipe:
                    continue
                
                plan_item = MealPlanItem(
                    meal_plan_id=meal_plan.id,
                    recipe_id=item_data['recipe_id'],
                    planned_date=planned_date,
                    meal_type=item_data['meal_type'],
                    servings=int(item_data.get('servings', 1)),
                    notes=item_data.get('notes', '')
                )
                db.session.add(plan_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Meal plan updated successfully',
            'meal_plan': meal_plan.to_dict(include_items=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/<int:plan_id>', methods=['DELETE'])
@jwt_required()
def delete_meal_plan(plan_id):
    """删除膳食计划"""
    try:
        current_user_id = get_jwt_identity()
        meal_plan = MealPlan.query.filter_by(id=plan_id, user_id=current_user_id).first()
        
        if not meal_plan:
            return jsonify({'error': 'Meal plan not found'}), 404
        
        db.session.delete(meal_plan)
        db.session.commit()
        
        return jsonify({'message': 'Meal plan deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_meal_plan():
    """智能生成膳食计划"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('start_date') or not data.get('end_date'):
            return jsonify({'error': 'Start date and end date are required'}), 400
        
        # 解析日期
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if start_date >= end_date:
            return jsonify({'error': 'End date must be after start date'}), 400
        
        # 获取用户偏好
        user = User.query.get(current_user_id)
        preferences = {
            'dietary_preferences': user.dietary_preferences,
            'allergies': user.allergies,
            'health_goals': user.health_goals
        }
        
        # 营养目标
        nutrition_targets = data.get('nutrition_targets', {})
        
        # 获取可用食谱
        available_recipes = Recipe.query.filter_by(is_public=True).all()
        
        if not available_recipes:
            return jsonify({'error': 'No recipes available for planning'}), 400
        
        # 简单的膳食规划算法
        # 这里可以实现更复杂的算法，考虑营养平衡、用户偏好等
        meal_plan = MealPlan(
            user_id=current_user_id,
            title=data.get('title', f'智能膳食计划 {start_date} - {end_date}'),
            description='基于您的偏好自动生成的膳食计划',
            start_date=start_date,
            end_date=end_date,
            is_generated=True
        )
        
        # 设置营养目标
        if nutrition_targets:
            meal_plan.set_nutrition_targets(nutrition_targets)
        
        db.session.add(meal_plan)
        db.session.flush()
        
        # 生成计划项
        current_date = start_date
        meal_types = ['breakfast', 'lunch', 'dinner']
        
        while current_date <= end_date:
            for meal_type in meal_types:
                # 随机选择一个食谱（实际应用中应该基于算法选择）
                import random
                recipe = random.choice(available_recipes)
                
                plan_item = MealPlanItem(
                    meal_plan_id=meal_plan.id,
                    recipe_id=recipe.id,
                    planned_date=current_date,
                    meal_type=meal_type,
                    servings=1,
                    notes='自动生成的膳食安排'
                )
                db.session.add(plan_item)
            
            current_date += timedelta(days=1)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Meal plan generated successfully',
            'meal_plan': meal_plan.to_dict(include_items=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/<int:plan_id>/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_meal_plan_item(plan_id, item_id):
    """更新膳食计划项"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证计划所有权
        meal_plan = MealPlan.query.filter_by(id=plan_id, user_id=current_user_id).first()
        if not meal_plan:
            return jsonify({'error': 'Meal plan not found'}), 404
        
        # 查找计划项
        plan_item = MealPlanItem.query.filter_by(id=item_id, meal_plan_id=plan_id).first()
        if not plan_item:
            return jsonify({'error': 'Meal plan item not found'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'recipe_id' in data:
            # 验证食谱是否存在且公开
            recipe = Recipe.query.filter_by(id=data['recipe_id'], is_public=True).first()
            if not recipe:
                return jsonify({'error': 'Recipe not found'}), 404
            plan_item.recipe_id = data['recipe_id']
        
        if 'planned_date' in data:
            plan_item.planned_date = datetime.strptime(data['planned_date'], '%Y-%m-%d').date()
        
        if 'meal_type' in data:
            plan_item.meal_type = data['meal_type']
        
        if 'servings' in data:
            plan_item.servings = int(data['servings'])
        
        if 'notes' in data:
            plan_item.notes = data['notes']
        
        if 'is_completed' in data:
            plan_item.is_completed = bool(data['is_completed'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Meal plan item updated successfully',
            'item': plan_item.to_dict(include_recipe=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@meal_plans_bp.route('/<int:plan_id>/nutrition', methods=['GET'])
@jwt_required()
def get_meal_plan_nutrition(plan_id):
    """获取膳食计划的营养分析"""
    try:
        current_user_id = get_jwt_identity()
        meal_plan = MealPlan.query.filter_by(id=plan_id, user_id=current_user_id).first()
        
        if not meal_plan:
            return jsonify({'error': 'Meal plan not found'}), 404
        
        # 计算营养数据（简化版本）
        nutrition_summary = {
            'total_days': (meal_plan.end_date - meal_plan.start_date).days + 1,
            'total_meals': meal_plan.items.count(),
            'nutrition_by_day': {}
        }
        
        # 按日期分组统计
        for item in meal_plan.items.all():
            date_str = item.planned_date.isoformat()
            if date_str not in nutrition_summary['nutrition_by_day']:
                nutrition_summary['nutrition_by_day'][date_str] = {
                    'meals': [],
                    'total_calories': 0,
                    'total_protein': 0,
                    'total_carbs': 0,
                    'total_fat': 0
                }
            
            day_data = nutrition_summary['nutrition_by_day'][date_str]
            day_data['meals'].append({
                'meal_type': item.meal_type,
                'recipe': item.recipe.title,
                'servings': item.servings
            })
            
            # 这里应该计算实际的营养数据，现在用模拟数据
            day_data['total_calories'] += 500  # 模拟数据
            day_data['total_protein'] += 20
            day_data['total_carbs'] += 60
            day_data['total_fat'] += 15
        
        return jsonify(nutrition_summary), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500