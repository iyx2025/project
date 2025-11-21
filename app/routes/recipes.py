from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models import Recipe, Ingredient, RecipeIngredient, RecipeStep, RecipeRating, RecipeFavorite, User, db
import os
import json

recipes_bp = Blueprint('recipes', __name__)

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@recipes_bp.route('/', methods=['GET'])
def get_recipes():
    """获取食谱列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        cuisine = request.args.get('cuisine')
        difficulty = request.args.get('difficulty')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 基础查询
        query = Recipe.query.filter_by(is_public=True)
        
        # 应用筛选条件
        if category:
            query = query.filter_by(category=category)
        
        if cuisine:
            query = query.filter_by(cuisine=cuisine)
        
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Recipe.title.ilike(search_term) | Recipe.description.ilike(search_term))
        
        # 排序
        if sort_order == 'desc':
            query = query.order_by(getattr(Recipe, sort_by).desc())
        else:
            query = query.order_by(getattr(Recipe, sort_by).asc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        recipes = pagination.items
        
        return jsonify({
            'recipes': [recipe.to_dict(include_author=True) for recipe in recipes],
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

@recipes_bp.route('/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """获取食谱详情"""
    try:
        recipe = Recipe.query.get(recipe_id)
        
        if not recipe or not recipe.is_public:
            return jsonify({'error': 'Recipe not found'}), 404
        
        # 增加浏览次数
        recipe.view_count += 1
        db.session.commit()
        
        return jsonify({
            'recipe': recipe.to_dict(
                include_author=True,
                include_ingredients=True,
                include_steps=True
            )
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/', methods=['POST'])
@jwt_required()
def create_recipe():
    """创建食谱"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title') or not data.get('category') or not data.get('cooking_time'):
            return jsonify({'error': 'Title, category and cooking time are required'}), 400
        
        # 创建食谱
        recipe = Recipe(
            title=data['title'],
            description=data.get('description', ''),
            category=data['category'],
            cuisine=data.get('cuisine'),
            difficulty=data.get('difficulty', 'medium'),
            cooking_time=int(data['cooking_time']),
            servings=int(data.get('servings', 1)),
            author_id=current_user_id
        )
        
        # 处理图片
        if data.get('images'):
            recipe.set_images_list(data['images'])
        
        db.session.add(recipe)
        db.session.flush()  # 获取recipe.id
        
        # 添加食材
        if data.get('ingredients'):
            for idx, ingredient_data in enumerate(data['ingredients']):
                if not ingredient_data.get('ingredient_id') or not ingredient_data.get('quantity'):
                    continue
                
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient_data['ingredient_id'],
                    quantity=float(ingredient_data['quantity']),
                    unit=ingredient_data.get('unit', 'g'),
                    notes=ingredient_data.get('notes'),
                    order_index=idx
                )
                db.session.add(recipe_ingredient)
        
        # 添加步骤
        if data.get('steps'):
            for idx, step_data in enumerate(data['steps']):
                if not step_data.get('instruction'):
                    continue
                
                recipe_step = RecipeStep(
                    recipe_id=recipe.id,
                    step_number=idx + 1,
                    instruction=step_data['instruction'],
                    image=step_data.get('image')
                )
                db.session.add(recipe_step)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Recipe created successfully',
            'recipe': recipe.to_dict(
                include_author=True,
                include_ingredients=True,
                include_steps=True
            )
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/<int:recipe_id>', methods=['PUT'])
@jwt_required()
def update_recipe(recipe_id):
    """更新食谱"""
    try:
        current_user_id = get_jwt_identity()
        recipe = Recipe.query.get(recipe_id)
        
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        # 检查权限
        if recipe.author_id != current_user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        
        # 更新基本信息
        if 'title' in data:
            recipe.title = data['title']
        
        if 'description' in data:
            recipe.description = data['description']
        
        if 'category' in data:
            recipe.category = data['category']
        
        if 'cuisine' in data:
            recipe.cuisine = data['cuisine']
        
        if 'difficulty' in data:
            recipe.difficulty = data['difficulty']
        
        if 'cooking_time' in data:
            recipe.cooking_time = int(data['cooking_time'])
        
        if 'servings' in data:
            recipe.servings = int(data['servings'])
        
        if 'images' in data:
            recipe.set_images_list(data['images'])
        
        # 更新食材（先删除现有食材，再添加新的）
        if 'ingredients' in data:
            RecipeIngredient.query.filter_by(recipe_id=recipe.id).delete()
            
            for idx, ingredient_data in enumerate(data['ingredients']):
                if not ingredient_data.get('ingredient_id') or not ingredient_data.get('quantity'):
                    continue
                
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient_data['ingredient_id'],
                    quantity=float(ingredient_data['quantity']),
                    unit=ingredient_data.get('unit', 'g'),
                    notes=ingredient_data.get('notes'),
                    order_index=idx
                )
                db.session.add(recipe_ingredient)
        
        # 更新步骤（先删除现有步骤，再添加新的）
        if 'steps' in data:
            RecipeStep.query.filter_by(recipe_id=recipe.id).delete()
            
            for idx, step_data in enumerate(data['steps']):
                if not step_data.get('instruction'):
                    continue
                
                recipe_step = RecipeStep(
                    recipe_id=recipe.id,
                    step_number=idx + 1,
                    instruction=step_data['instruction'],
                    image=step_data.get('image')
                )
                db.session.add(recipe_step)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Recipe updated successfully',
            'recipe': recipe.to_dict(
                include_author=True,
                include_ingredients=True,
                include_steps=True
            )
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id):
    """删除食谱"""
    try:
        current_user_id = get_jwt_identity()
        recipe = Recipe.query.get(recipe_id)
        
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        # 检查权限
        if recipe.author_id != current_user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        db.session.delete(recipe)
        db.session.commit()
        
        return jsonify({'message': 'Recipe deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/<int:recipe_id>/favorite', methods=['POST'])
@jwt_required()
def favorite_recipe(recipe_id):
    """收藏食谱"""
    try:
        current_user_id = get_jwt_identity()
        recipe = Recipe.query.get(recipe_id)
        
        if not recipe or not recipe.is_public:
            return jsonify({'error': 'Recipe not found'}), 404
        
        # 检查是否已经收藏
        existing_favorite = RecipeFavorite.query.filter_by(
            user_id=current_user_id,
            recipe_id=recipe_id
        ).first()
        
        if existing_favorite:
            return jsonify({'message': 'Recipe already favorited'}), 200
        
        # 创建收藏记录
        favorite = RecipeFavorite(
            user_id=current_user_id,
            recipe_id=recipe_id
        )
        db.session.add(favorite)
        
        # 更新收藏数
        recipe.favorite_count += 1
        db.session.commit()
        
        return jsonify({'message': 'Recipe favorited successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/<int:recipe_id>/favorite', methods=['DELETE'])
@jwt_required()
def unfavorite_recipe(recipe_id):
    """取消收藏食谱"""
    try:
        current_user_id = get_jwt_identity()
        recipe = Recipe.query.get(recipe_id)
        
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        
        # 查找收藏记录
        favorite = RecipeFavorite.query.filter_by(
            user_id=current_user_id,
            recipe_id=recipe_id
        ).first()
        
        if not favorite:
            return jsonify({'message': 'Recipe not favorited'}), 200
        
        # 删除收藏记录
        db.session.delete(favorite)
        
        # 更新收藏数
        recipe.favorite_count = max(0, recipe.favorite_count - 1)
        db.session.commit()
        
        return jsonify({'message': 'Recipe unfavorited successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/<int:recipe_id>/rate', methods=['POST'])
@jwt_required()
def rate_recipe(recipe_id):
    """评分食谱"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        recipe = Recipe.query.get(recipe_id)
        if not recipe or not recipe.is_public:
            return jsonify({'error': 'Recipe not found'}), 404
        
        rating_value = data.get('rating')
        if not rating_value or not 1 <= rating_value <= 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # 查找现有评分
        existing_rating = RecipeRating.query.filter_by(
            user_id=current_user_id,
            recipe_id=recipe_id
        ).first()
        
        if existing_rating:
            # 更新现有评分
            existing_rating.rating = rating_value
            existing_rating.comment = data.get('comment', '')
        else:
            # 创建新评分
            rating = RecipeRating(
                user_id=current_user_id,
                recipe_id=recipe_id,
                rating=rating_value,
                comment=data.get('comment', '')
            )
            db.session.add(rating)
        
        # 重新计算平均评分
        all_ratings = RecipeRating.query.filter_by(recipe_id=recipe_id).all()
        if all_ratings:
            avg_rating = sum(r.rating for r in all_ratings) / len(all_ratings)
            recipe.rating = round(avg_rating, 2)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Rating submitted successfully',
            'rating': recipe.rating
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@recipes_bp.route('/my-favorites', methods=['GET'])
@jwt_required()
def get_my_favorites():
    """获取我的收藏食谱"""
    try:
        current_user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 获取收藏记录
        query = RecipeFavorite.query.filter_by(user_id=current_user_id).join(Recipe).filter(Recipe.is_public == True)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        favorites = pagination.items
        
        return jsonify({
            'favorites': [{
                'id': fav.id,
                'recipe': fav.recipe.to_dict(include_author=True),
                'created_at': fav.created_at.isoformat()
            } for fav in favorites],
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

@recipes_bp.route('/my-recipes', methods=['GET'])
@jwt_required()
def get_my_recipes():
    """获取我的食谱"""
    try:
        current_user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Recipe.query.filter_by(author_id=current_user_id)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        recipes = pagination.items
        
        return jsonify({
            'recipes': [recipe.to_dict() for recipe in recipes],
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