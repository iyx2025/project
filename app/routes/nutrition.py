from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date, timedelta
from app.models import Recipe, Ingredient, MealPlan, MealPlanItem, db

nutrition_bp = Blueprint('nutrition', __name__)

@nutrition_bp.route('/ingredients/<int:ingredient_id>', methods=['GET'])
def get_ingredient_nutrition(ingredient_id):
    """获取食材营养信息"""
    try:
        ingredient = Ingredient.query.filter_by(id=ingredient_id, is_active=True).first()
        
        if not ingredient:
            return jsonify({'error': 'Ingredient not found'}), 404
        
        nutrition_data = ingredient.get_nutrition_data()
        
        return jsonify({
            'ingredient': ingredient.to_dict(),
            'nutrition': nutrition_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nutrition_bp.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe_nutrition(recipe_id):
    """获取食谱营养信息"""
    try:
        recipe = Recipe.query.filter_by(id=recipe_id, is_public=True).first()
        
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        # 计算食谱总营养（基于食材和用量）
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0,
            'fiber': 0,
            'sugar': 0,
            'sodium': 0,
            'ingredients': []
        }
        
        for recipe_ingredient in recipe.ingredients.all():
            ingredient = recipe_ingredient.ingredient
            nutrition_data = ingredient.get_nutrition_data()
            
            if nutrition_data:
                # 根据用量计算营养（假设营养数据是每100g）
                quantity_ratio = recipe_ingredient.quantity / 100
                
                ingredient_nutrition = {
                    'ingredient': ingredient.to_dict(),
                    'quantity': recipe_ingredient.quantity,
                    'unit': recipe_ingredient.unit,
                    'nutrition': {
                        'calories': nutrition_data.get('calories', 0) * quantity_ratio,
                        'protein': nutrition_data.get('protein', 0) * quantity_ratio,
                        'carbs': nutrition_data.get('carbs', 0) * quantity_ratio,
                        'fat': nutrition_data.get('fat', 0) * quantity_ratio,
                        'fiber': nutrition_data.get('fiber', 0) * quantity_ratio,
                        'sugar': nutrition_data.get('sugar', 0) * quantity_ratio,
                        'sodium': nutrition_data.get('sodium', 0) * quantity_ratio
                    }
                }
                
                # 累加到总量
                for key in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']:
                    total_nutrition[key] += ingredient_nutrition['nutrition'][key]
                
                total_nutrition['ingredients'].append(ingredient_nutrition)
        
        # 四舍五入到合理的小数位数
        for key in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']:
            total_nutrition[key] = round(total_nutrition[key], 1)
        
        return jsonify({
            'recipe': recipe.to_dict(),
            'nutrition': total_nutrition,
            'per_serving': {
                'calories': round(total_nutrition['calories'] / recipe.servings, 1) if recipe.servings > 0 else 0,
                'protein': round(total_nutrition['protein'] / recipe.servings, 1) if recipe.servings > 0 else 0,
                'carbs': round(total_nutrition['carbs'] / recipe.servings, 1) if recipe.servings > 0 else 0,
                'fat': round(total_nutrition['fat'] / recipe.servings, 1) if recipe.servings > 0 else 0,
                'fiber': round(total_nutrition['fiber'] / recipe.servings, 1) if recipe.servings > 0 else 0,
                'sugar': round(total_nutrition['sugar'] / recipe.servings, 1) if recipe.servings > 0 else 0,
                'sodium': round(total_nutrition['sodium'] / recipe.servings, 1) if recipe.servings > 0 else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nutrition_bp.route('/daily/<string:target_date>', methods=['GET'])
@jwt_required()
def get_daily_nutrition(target_date):
    """获取指定日期的营养摄入"""
    try:
        current_user_id = get_jwt_identity()
        
        # 解析日期
        try:
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # 查找该日期的膳食计划项
        meal_items = MealPlanItem.query.join(MealPlan).filter(
            MealPlan.user_id == current_user_id,
            MealPlanItem.planned_date == target_date,
            MealPlanItem.is_completed == True
        ).all()
        
        # 计算总营养摄入
        daily_nutrition = {
            'date': target_date.isoformat(),
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0,
            'total_fiber': 0,
            'total_sugar': 0,
            'total_sodium': 0,
            'meals': []
        }
        
        for item in meal_items:
            recipe = item.recipe
            recipe_nutrition = calculate_recipe_nutrition(recipe, item.servings)
            
            meal_data = {
                'meal_type': item.meal_type,
                'recipe': recipe.to_dict(),
                'servings': item.servings,
                'nutrition': recipe_nutrition
            }
            
            # 累加到总量
            for key in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']:
                daily_nutrition[f'total_{key}'] += recipe_nutrition[key]
            
            daily_nutrition['meals'].append(meal_data)
        
        # 四舍五入
        for key in ['total_calories', 'total_protein', 'total_carbs', 'total_fat', 'total_fiber', 'total_sugar', 'total_sodium']:
            daily_nutrition[key] = round(daily_nutrition[key], 1)
        
        return jsonify(daily_nutrition), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nutrition_bp.route('/weekly', methods=['GET'])
@jwt_required()
def get_weekly_nutrition():
    """获取最近7天的营养摄入统计"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取日期范围
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        # 获取该时间段内的营养数据
        weekly_data = []
        
        current_date = start_date
        while current_date <= end_date:
            # 获取该日期的营养数据
            daily_response = get_daily_nutrition(str(current_date))
            if daily_response[1] == 200:  # 成功获取数据
                daily_data = daily_response[0].json
                weekly_data.append({
                    'date': current_date.isoformat(),
                    'calories': daily_data['total_calories'],
                    'protein': daily_data['total_protein'],
                    'carbs': daily_data['total_carbs'],
                    'fat': daily_data['total_fat']
                })
            
            current_date += timedelta(days=1)
        
        # 计算平均值
        if weekly_data:
            avg_nutrition = {
                'avg_calories': round(sum(day['calories'] for day in weekly_data) / len(weekly_data), 1),
                'avg_protein': round(sum(day['protein'] for day in weekly_data) / len(weekly_data), 1),
                'avg_carbs': round(sum(day['carbs'] for day in weekly_data) / len(weekly_data), 1),
                'avg_fat': round(sum(day['fat'] for day in weekly_data) / len(weekly_data), 1)
            }
        else:
            avg_nutrition = {
                'avg_calories': 0,
                'avg_protein': 0,
                'avg_carbs': 0,
                'avg_fat': 0
            }
        
        return jsonify({
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'daily_data': weekly_data,
            'average': avg_nutrition
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@nutrition_bp.route('/analyze-meal-plan/<int:meal_plan_id>', methods=['GET'])
@jwt_required()
def analyze_meal_plan_nutrition(meal_plan_id):
    """分析膳食计划的营养"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证膳食计划所有权
        meal_plan = MealPlan.query.filter_by(id=meal_plan_id, user_id=current_user_id).first()
        if not meal_plan:
            return jsonify({'error': 'Meal plan not found'}), 404
        
        # 获取营养目标
        nutrition_targets = meal_plan.get_nutrition_targets()
        
        # 计算实际营养摄入
        actual_nutrition = {
            'total_calories': 0,
            'total_protein': 0,
            'total_carbs': 0,
            'total_fat': 0,
            'total_fiber': 0,
            'total_sugar': 0,
            'total_sodium': 0,
            'daily_breakdown': {}
        }
        
        for item in meal_plan.items.all():
            recipe = item.recipe
            recipe_nutrition = calculate_recipe_nutrition(recipe, item.servings)
            
            date_str = item.planned_date.isoformat()
            if date_str not in actual_nutrition['daily_breakdown']:
                actual_nutrition['daily_breakdown'][date_str] = {
                    'calories': 0,
                    'protein': 0,
                    'carbs': 0,
                    'fat': 0,
                    'fiber': 0,
                    'sugar': 0,
                    'sodium': 0,
                    'meals': []
                }
            
            daily_data = actual_nutrition['daily_breakdown'][date_str]
            daily_data['meals'].append({
                'meal_type': item.meal_type,
                'recipe': recipe.title,
                'servings': item.servings,
                'nutrition': recipe_nutrition
            })
            
            # 累加到每日总量
            for key in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']:
                daily_data[key] += recipe_nutrition[key]
                actual_nutrition[f'total_{key}'] += recipe_nutrition[key]
        
        # 四舍五入
        for key in ['total_calories', 'total_protein', 'total_carbs', 'total_fat', 'total_fiber', 'total_sugar', 'total_sodium']:
            actual_nutrition[key] = round(actual_nutrition[key], 1)
        
        for daily_data in actual_nutrition['daily_breakdown'].values():
            for key in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']:
                daily_data[key] = round(daily_data[key], 1)
        
        # 计算目标达成情况
        target_analysis = {}
        if nutrition_targets:
            for target_key, target_value in nutrition_targets.items():
                actual_key = f'total_{target_key}'
                if actual_key in actual_nutrition:
                    actual_value = actual_nutrition[actual_key]
                    achievement_rate = (actual_value / target_value * 100) if target_value > 0 else 0
                    target_analysis[target_key] = {
                        'target': target_value,
                        'actual': actual_value,
                        'achievement_rate': round(achievement_rate, 1),
                        'status': 'achieved' if achievement_rate >= 95 else 'under' if achievement_rate < 90 else 'close'
                    }
        
        return jsonify({
            'meal_plan': meal_plan.to_dict(),
            'nutrition_targets': nutrition_targets,
            'actual_nutrition': actual_nutrition,
            'target_analysis': target_analysis,
            'recommendations': generate_nutrition_recommendations(target_analysis)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_recipe_nutrition(recipe, servings=1):
    """计算食谱的营养信息"""
    nutrition = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'fiber': 0,
        'sugar': 0,
        'sodium': 0
    }
    
    for recipe_ingredient in recipe.ingredients.all():
        ingredient = recipe_ingredient.ingredient
        nutrition_data = ingredient.get_nutrition_data()
        
        if nutrition_data:
            # 根据用量计算营养（假设营养数据是每100g）
            quantity_ratio = recipe_ingredient.quantity / 100
            
            for key in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']:
                nutrition[key] += nutrition_data.get(key, 0) * quantity_ratio
    
    # 根据份量调整
    if recipe.servings > 0:
        servings_ratio = servings / recipe.servings
        for key in nutrition:
            nutrition[key] *= servings_ratio
    
    # 四舍五入
    for key in nutrition:
        nutrition[key] = round(nutrition[key], 1)
    
    return nutrition

def generate_nutrition_recommendations(target_analysis):
    """生成营养建议"""
    recommendations = []
    
    if not target_analysis:
        return recommendations
    
    for nutrient, analysis in target_analysis.items():
        if analysis['status'] == 'under':
            if nutrient == 'protein':
                recommendations.append({
                    'type': 'protein',
                    'message': '蛋白质摄入不足，建议增加肉类、蛋类、豆类等高蛋白食物',
                    'priority': 'high'
                })
            elif nutrient == 'calories':
                recommendations.append({
                    'type': 'calories',
                    'message': '热量摄入偏低，可以适当增加主食或健康脂肪的摄入',
                    'priority': 'medium'
                })
            elif nutrient == 'fiber':
                recommendations.append({
                    'type': 'fiber',
                    'message': '膳食纤维摄入不足，建议增加蔬菜、水果、全谷物的比例',
                    'priority': 'medium'
                })
        elif analysis['status'] == 'over':
            if nutrient == 'sodium':
                recommendations.append({
                    'type': 'sodium',
                    'message': '钠摄入过高，建议减少盐的使用，选择低钠食物',
                    'priority': 'high'
                })
            elif nutrient == 'sugar':
                recommendations.append({
                    'type': 'sugar',
                    'message': '糖分摄入偏高，建议减少甜食和含糖饮料',
                    'priority': 'medium'
                })
    
    return recommendations