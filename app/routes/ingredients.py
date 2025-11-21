from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, date
from app.models import Ingredient, IngredientStock, RecipeIngredient, db

ingredients_bp = Blueprint('ingredients', __name__)

@ingredients_bp.route('/', methods=['GET'])
def get_ingredients():
    """获取食材列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        search = request.args.get('search')
        
        # 基础查询
        query = Ingredient.query.filter_by(is_active=True)
        
        # 应用筛选条件
        if category:
            query = query.filter_by(category=category)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(Ingredient.name.ilike(search_term))
        
        # 排序
        query = query.order_by(Ingredient.name.asc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        ingredients = pagination.items
        
        return jsonify({
            'ingredients': [ingredient.to_dict() for ingredient in ingredients],
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

@ingredients_bp.route('/<int:ingredient_id>', methods=['GET'])
def get_ingredient(ingredient_id):
    """获取食材详情"""
    try:
        ingredient = Ingredient.query.filter_by(id=ingredient_id, is_active=True).first()
        
        if not ingredient:
            return jsonify({'error': 'Ingredient not found'}), 404
        
        return jsonify({
            'ingredient': ingredient.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/', methods=['POST'])
@jwt_required()
def create_ingredient():
    """创建食材"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('name') or not data.get('category') or not data.get('unit'):
            return jsonify({'error': 'Name, category and unit are required'}), 400
        
        # 检查是否已存在
        existing = Ingredient.query.filter_by(name=data['name']).first()
        if existing:
            return jsonify({'error': 'Ingredient already exists'}), 400
        
        # 创建食材
        ingredient = Ingredient(
            name=data['name'],
            category=data['category'],
            unit=data['unit'],
            storage_method=data.get('storage_method'),
            shelf_life_days=int(data['shelf_life_days']) if data.get('shelf_life_days') else None
        )
        
        # 设置营养信息
        if data.get('nutrition'):
            ingredient.set_nutrition_data(data['nutrition'])
        
        db.session.add(ingredient)
        db.session.commit()
        
        return jsonify({
            'message': 'Ingredient created successfully',
            'ingredient': ingredient.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/<int:ingredient_id>', methods=['PUT'])
@jwt_required()
def update_ingredient(ingredient_id):
    """更新食材信息"""
    try:
        ingredient = Ingredient.query.get(ingredient_id)
        
        if not ingredient:
            return jsonify({'error': 'Ingredient not found'}), 404
        
        data = request.get_json()
        
        # 更新基本信息
        if 'name' in data:
            # 检查名称是否重复
            existing = Ingredient.query.filter(Ingredient.name == data['name'], Ingredient.id != ingredient_id).first()
            if existing:
                return jsonify({'error': 'Ingredient name already exists'}), 400
            ingredient.name = data['name']
        
        if 'category' in data:
            ingredient.category = data['category']
        
        if 'unit' in data:
            ingredient.unit = data['unit']
        
        if 'storage_method' in data:
            ingredient.storage_method = data['storage_method']
        
        if 'shelf_life_days' in data:
            ingredient.shelf_life_days = int(data['shelf_life_days']) if data['shelf_life_days'] else None
        
        # 更新营养信息
        if 'nutrition' in data:
            ingredient.set_nutrition_data(data['nutrition'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ingredient updated successfully',
            'ingredient': ingredient.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/<int:ingredient_id>', methods=['DELETE'])
@jwt_required()
def delete_ingredient(ingredient_id):
    """删除食材（软删除）"""
    try:
        ingredient = Ingredient.query.get(ingredient_id)
        
        if not ingredient:
            return jsonify({'error': 'Ingredient not found'}), 404
        
        # 检查是否有关联数据
        if ingredient.recipe_ingredients.count() > 0:
            return jsonify({'error': 'Cannot delete ingredient that is used in recipes'}), 400
        
        if ingredient.stocks.count() > 0:
            return jsonify({'error': 'Cannot delete ingredient that has stock records'}), 400
        
        # 软删除
        ingredient.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Ingredient deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取食材分类列表"""
    try:
        categories = db.session.query(Ingredient.category).distinct().filter(Ingredient.is_active == True).all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'categories': category_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/search', methods=['GET'])
def search_ingredients():
    """搜索食材"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({'ingredients': []}), 200
        
        # 搜索食材名称
        search_term = f"%{query}%"
        ingredients = Ingredient.query.filter(
            Ingredient.name.ilike(search_term),
            Ingredient.is_active == True
        ).limit(limit).all()
        
        return jsonify({
            'ingredients': [ingredient.to_dict() for ingredient in ingredients]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/<int:ingredient_id>/nutrition', methods=['GET'])
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

@ingredients_bp.route('/my-stock', methods=['GET'])
@jwt_required()
def get_my_stock():
    """获取我的食材库存"""
    try:
        current_user_id = get_jwt_identity()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category')
        expiring_soon = request.args.get('expiring_soon', type=bool)
        
        # 基础查询
        query = IngredientStock.query.filter_by(user_id=current_user_id, is_active=True)
        
        # 分类筛选
        if category:
            query = query.join(Ingredient).filter(Ingredient.category == category)
        
        # 即将过期筛选
        if expiring_soon:
            from datetime import date, timedelta
            soon_date = date.today() + timedelta(days=3)
            query = query.filter(IngredientStock.expiry_date <= soon_date)
        
        # 排序
        query = query.order_by(IngredientStock.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        stocks = pagination.items
        
        return jsonify({
            'stocks': [stock.to_dict(include_ingredient=True) for stock in stocks],
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

@ingredients_bp.route('/my-stock', methods=['POST'])
@jwt_required()
def add_stock():
    """添加食材库存"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('ingredient_id') or not data.get('quantity') or not data.get('unit'):
            return jsonify({'error': 'Ingredient ID, quantity and unit are required'}), 400
        
        # 检查食材是否存在
        ingredient = Ingredient.query.filter_by(id=data['ingredient_id'], is_active=True).first()
        if not ingredient:
            return jsonify({'error': 'Ingredient not found'}), 404
        
        # 解析日期
        purchase_date = None
        expiry_date = None
        if data.get('purchase_date'):
            purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
        if data.get('expiry_date'):
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        
        # 创建库存记录
        stock = IngredientStock(
            user_id=current_user_id,
            ingredient_id=data['ingredient_id'],
            quantity=float(data['quantity']),
            unit=data['unit'],
            purchase_date=purchase_date,
            expiry_date=expiry_date,
            storage_location=data.get('storage_location'),
            notes=data.get('notes')
        )
        
        db.session.add(stock)
        db.session.commit()
        
        return jsonify({
            'message': 'Stock added successfully',
            'stock': stock.to_dict(include_ingredient=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/my-stock/<int:stock_id>', methods=['PUT'])
@jwt_required()
def update_stock(stock_id):
    """更新库存信息"""
    try:
        current_user_id = get_jwt_identity()
        stock = IngredientStock.query.filter_by(id=stock_id, user_id=current_user_id).first()
        
        if not stock:
            return jsonify({'error': 'Stock not found'}), 404
        
        data = request.get_json()
        
        # 更新基本信息
        if 'quantity' in data:
            stock.quantity = float(data['quantity'])
        
        if 'unit' in data:
            stock.unit = data['unit']
        
        if 'purchase_date' in data:
            stock.purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data['purchase_date'] else None
        
        if 'expiry_date' in data:
            stock.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data['expiry_date'] else None
        
        if 'storage_location' in data:
            stock.storage_location = data['storage_location']
        
        if 'notes' in data:
            stock.notes = data['notes']
        
        if 'is_active' in data:
            stock.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Stock updated successfully',
            'stock': stock.to_dict(include_ingredient=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/my-stock/<int:stock_id>', methods=['DELETE'])
@jwt_required()
def delete_stock(stock_id):
    """删除库存记录"""
    try:
        current_user_id = get_jwt_identity()
        stock = IngredientStock.query.filter_by(id=stock_id, user_id=current_user_id).first()
        
        if not stock:
            return jsonify({'error': 'Stock not found'}), 404
        
        db.session.delete(stock)
        db.session.commit()
        
        return jsonify({'message': 'Stock deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@ingredients_bp.route('/expiring-soon', methods=['GET'])
@jwt_required()
def get_expiring_soon():
    """获取即将过期的食材"""
    try:
        current_user_id = get_jwt_identity()
        days = request.args.get('days', 3, type=int)
        
        from datetime import date, timedelta
        soon_date = date.today() + timedelta(days=days)
        
        # 查找即将过期的库存
        expiring_stocks = IngredientStock.query.filter(
            IngredientStock.user_id == current_user_id,
            IngredientStock.is_active == True,
            IngredientStock.expiry_date <= soon_date,
            IngredientStock.expiry_date >= date.today()
        ).order_by(IngredientStock.expiry_date.asc()).all()
        
        return jsonify({
            'expiring_stocks': [stock.to_dict(include_ingredient=True) for stock in expiring_stocks],
            'days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500