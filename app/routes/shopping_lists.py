from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import ShoppingList, ShoppingListItem, Ingredient, MealPlan, db

shopping_lists_bp = Blueprint('shopping_lists', __name__)

@shopping_lists_bp.route('/', methods=['GET'])
@jwt_required()
def get_shopping_lists():
    """获取购物清单列表"""
    try:
        current_user_id = get_jwt_identity()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        # 基础查询
        query = ShoppingList.query.filter_by(user_id=current_user_id)
        
        # 状态筛选
        if status:
            query = query.filter_by(status=status)
        
        # 排序
        query = query.order_by(ShoppingList.created_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        shopping_lists = pagination.items
        
        return jsonify({
            'shopping_lists': [sl.to_dict() for sl in shopping_lists],
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

@shopping_lists_bp.route('/<int:list_id>', methods=['GET'])
@jwt_required()
def get_shopping_list(list_id):
    """获取购物清单详情"""
    try:
        current_user_id = get_jwt_identity()
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user_id).first()
        
        if not shopping_list:
            return jsonify({'error': 'Shopping list not found'}), 404
        
        return jsonify({
            'shopping_list': shopping_list.to_dict(include_items=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@shopping_lists_bp.route('/', methods=['POST'])
@jwt_required()
def create_shopping_list():
    """创建购物清单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # 创建购物清单
        shopping_list = ShoppingList(
            user_id=current_user_id,
            title=data['title'],
            description=data.get('description', ''),
            source_type=data.get('source_type'),
            source_id=data.get('source_id'),
            is_generated=bool(data.get('source_type'))
        )
        
        db.session.add(shopping_list)
        db.session.flush()
        
        # 添加清单项
        if data.get('items'):
            for item_data in data['items']:
                if not item_data.get('ingredient_id') or not item_data.get('quantity'):
                    continue
                
                # 检查食材是否存在
                ingredient = Ingredient.query.filter_by(id=item_data['ingredient_id'], is_active=True).first()
                if not ingredient:
                    continue
                
                list_item = ShoppingListItem(
                    shopping_list_id=shopping_list.id,
                    ingredient_id=item_data['ingredient_id'],
                    quantity=float(item_data['quantity']),
                    unit=item_data.get('unit', ingredient.unit),
                    notes=item_data.get('notes'),
                    estimated_price=float(item_data['estimated_price']) if item_data.get('estimated_price') else None
                )
                db.session.add(list_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Shopping list created successfully',
            'shopping_list': shopping_list.to_dict(include_items=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@shopping_lists_bp.route('/<int:list_id>', methods=['PUT'])
@jwt_required()
def update_shopping_list(list_id):
    """更新购物清单"""
    try:
        current_user_id = get_jwt_identity()
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user_id).first()
        
        if not shopping_list:
            return jsonify({'error': 'Shopping list not found'}), 404
        
        data = request.get_json()
        
        # 更新基本信息
        if 'title' in data:
            shopping_list.title = data['title']
        
        if 'description' in data:
            shopping_list.description = data['description']
        
        if 'status' in data:
            shopping_list.status = data['status']
            if data['status'] == 'completed':
                shopping_list.completed_at = datetime.utcnow()
        
        # 更新清单项（如果提供）
        if 'items' in data:
            # 删除现有清单项
            ShoppingListItem.query.filter_by(shopping_list_id=list_id).delete()
            
            # 添加新的清单项
            for item_data in data['items']:
                if not item_data.get('ingredient_id') or not item_data.get('quantity'):
                    continue
                
                # 检查食材是否存在
                ingredient = Ingredient.query.filter_by(id=item_data['ingredient_id'], is_active=True).first()
                if not ingredient:
                    continue
                
                list_item = ShoppingListItem(
                    shopping_list_id=shopping_list.id,
                    ingredient_id=item_data['ingredient_id'],
                    quantity=float(item_data['quantity']),
                    unit=item_data.get('unit', ingredient.unit),
                    notes=item_data.get('notes'),
                    estimated_price=float(item_data['estimated_price']) if item_data.get('estimated_price') else None
                )
                db.session.add(list_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Shopping list updated successfully',
            'shopping_list': shopping_list.to_dict(include_items=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@shopping_lists_bp.route('/<int:list_id>', methods=['DELETE'])
@jwt_required()
def delete_shopping_list(list_id):
    """删除购物清单"""
    try:
        current_user_id = get_jwt_identity()
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user_id).first()
        
        if not shopping_list:
            return jsonify({'error': 'Shopping list not found'}), 404
        
        db.session.delete(shopping_list)
        db.session.commit()
        
        return jsonify({'message': 'Shopping list deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@shopping_lists_bp.route('/<int:list_id>/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_shopping_list_item(list_id, item_id):
    """更新购物清单项"""
    try:
        current_user_id = get_jwt_identity()
        
        # 验证清单所有权
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user_id).first()
        if not shopping_list:
            return jsonify({'error': 'Shopping list not found'}), 404
        
        # 查找清单项
        list_item = ShoppingListItem.query.filter_by(id=item_id, shopping_list_id=list_id).first()
        if not list_item:
            return jsonify({'error': 'Shopping list item not found'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'quantity' in data:
            list_item.quantity = float(data['quantity'])
        
        if 'unit' in data:
            list_item.unit = data['unit']
        
        if 'is_purchased' in data:
            list_item.is_purchased = bool(data['is_purchased'])
        
        if 'notes' in data:
            list_item.notes = data['notes']
        
        if 'estimated_price' in data:
            list_item.estimated_price = float(data['estimated_price']) if data['estimated_price'] else None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Shopping list item updated successfully',
            'item': list_item.to_dict(include_ingredient=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@shopping_lists_bp.route('/generate-from-meal-plan', methods=['POST'])
@jwt_required()
def generate_from_meal_plan():
    """从膳食计划生成购物清单"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('meal_plan_id'):
            return jsonify({'error': 'Meal plan ID is required'}), 400
        
        # 获取膳食计划
        meal_plan = MealPlan.query.filter_by(id=data['meal_plan_id'], user_id=current_user_id).first()
        if not meal_plan:
            return jsonify({'error': 'Meal plan not found'}), 404
        
        # 获取计划中的所有食谱
        recipe_ids = [item.recipe_id for item in meal_plan.items.all()]
        
        # 获取所有需要的食材
        ingredient_quantities = {}
        
        for item in meal_plan.items.all():
            recipe = item.recipe
            servings_ratio = item.servings / recipe.servings if recipe.servings > 0 else 1
            
            for recipe_ingredient in recipe.ingredients.all():
                ingredient_id = recipe_ingredient.ingredient_id
                quantity = recipe_ingredient.quantity * servings_ratio
                
                if ingredient_id in ingredient_quantities:
                    ingredient_quantities[ingredient_id] += quantity
                else:
                    ingredient_quantities[ingredient_id] = quantity
        
        # 创建购物清单
        shopping_list = ShoppingList(
            user_id=current_user_id,
            title=f"膳食计划购物清单 - {meal_plan.title}",
            description=f"基于膳食计划 '{meal_plan.title}' 自动生成的购物清单",
            source_type='meal_plan',
            source_id=meal_plan.id,
            is_generated=True
        )
        
        db.session.add(shopping_list)
        db.session.flush()
        
        # 添加购物清单项
        for ingredient_id, total_quantity in ingredient_quantities.items():
            ingredient = Ingredient.query.get(ingredient_id)
            if not ingredient:
                continue
            
            # 四舍五入到合理的数量
            rounded_quantity = round(total_quantity, 1)
            if rounded_quantity < 0.1:
                continue
            
            list_item = ShoppingListItem(
                shopping_list_id=shopping_list.id,
                ingredient_id=ingredient_id,
                quantity=rounded_quantity,
                unit=ingredient.unit,
                notes=f"来自膳食计划: {meal_plan.title}"
            )
            db.session.add(list_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Shopping list generated successfully from meal plan',
            'shopping_list': shopping_list.to_dict(include_items=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@shopping_lists_bp.route('/<int:list_id>/export', methods=['GET'])
@jwt_required()
def export_shopping_list(list_id):
    """导出购物清单"""
    try:
        current_user_id = get_jwt_identity()
        shopping_list = ShoppingList.query.filter_by(id=list_id, user_id=current_user_id).first()
        
        if not shopping_list:
            return jsonify({'error': 'Shopping list not found'}), 404
        
        # 生成导出数据
        export_data = {
            'title': shopping_list.title,
            'description': shopping_list.description,
            'created_at': shopping_list.created_at.isoformat(),
            'items': []
        }
        
        # 按分类组织食材
        categorized_items = {}
        
        for item in shopping_list.items.all():
            ingredient = item.ingredient
            category = ingredient.category
            
            if category not in categorized_items:
                categorized_items[category] = []
            
            categorized_items[category].append({
                'name': ingredient.name,
                'quantity': item.quantity,
                'unit': item.unit,
                'notes': item.notes,
                'estimated_price': item.estimated_price,
                'is_purchased': item.is_purchased
            })
        
        export_data['categorized_items'] = categorized_items
        
        # 计算总价
        total_price = sum(item.estimated_price or 0 for item in shopping_list.items.all() if not item.is_purchased)
        export_data['total_estimated_price'] = total_price
        
        return jsonify({
            'export_data': export_data,
            'format': 'json'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500