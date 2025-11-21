#!/usr/bin/env python3
"""
数据库初始化脚本
"""

from app import create_app, db
from app.models import User, Recipe, Ingredient, MealPlan, MealPlanItem, IngredientStock, ShoppingList, ShoppingListItem, RecipeRating, RecipeFavorite, RecipeIngredient, RecipeStep

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功！")
        
        # 创建示例数据
        create_sample_data()
        print("✅ 示例数据创建成功！")
        
        print("🎉 数据库初始化完成！")

def create_sample_data():
    """创建示例数据"""
    # 检查是否已有数据
    if User.query.first():
        print("数据已存在，跳过创建示例数据")
        return
    
    # 创建管理员用户
    admin = User(
        username='admin',
        email='admin@example.com',
        name='管理员',
        is_admin=True
    )
    admin.set_password('admin123')
    
    # 创建普通用户
    user = User(
        username='user',
        email='user@example.com',
        name='普通用户'
    )
    user.set_password('user123')
    
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()
    
    # 创建示例食材
    ingredients_data = [
        {'name': '鸡蛋', 'category': '蛋类', 'unit': '个', 'nutrition_per_100g': '{"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1}'},
        {'name': '大米', 'category': '谷物', 'unit': 'g', 'nutrition_per_100g': '{"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28}'},
        {'name': '鸡胸肉', 'category': '肉类', 'unit': 'g', 'nutrition_per_100g': '{"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0}'},
        {'name': '西红柿', 'category': '蔬菜', 'unit': '个', 'nutrition_per_100g': '{"calories": 18, "protein": 0.9, "fat": 0.2, "carbs": 3.9}'},
        {'name': '胡萝卜', 'category': '蔬菜', 'unit': '根', 'nutrition_per_100g': '{"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10}'},
        {'name': '牛奶', 'category': '乳制品', 'unit': 'ml', 'nutrition_per_100g': '{"calories": 42, "protein": 3.4, "fat": 1, "carbs": 5}'}
    ]
    
    for ingredient_data in ingredients_data:
        ingredient = Ingredient(
            name=ingredient_data['name'],
            category=ingredient_data['category'],
            unit=ingredient_data['unit'],
            nutrition_per_100g=ingredient_data['nutrition_per_100g']
        )
        db.session.add(ingredient)
    
    db.session.commit()
    
    # 创建示例食谱
    recipe = Recipe(
        title='番茄鸡蛋炒饭',
        description='简单又美味的家常菜',
        category='午餐',
        cuisine='中式',
        difficulty='easy',
        cooking_time=15,
        servings=2,
        author_id=user.id,
        rating=4.5,
        favorite_count=10
    )
    db.session.add(recipe)
    db.session.flush()
    
    # 添加食谱食材
    recipe_ingredients = [
        {'recipe_id': recipe.id, 'ingredient_id': 1, 'quantity': 3, 'unit': '个', 'notes': '打散'},
        {'recipe_id': recipe.id, 'ingredient_id': 2, 'quantity': 200, 'unit': 'g', 'notes': '隔夜饭更佳'},
        {'recipe_id': recipe.id, 'ingredient_id': 4, 'quantity': 2, 'unit': '个', 'notes': '切块'}
    ]
    
    for ri_data in recipe_ingredients:
        ri = RecipeIngredient(**ri_data)
        db.session.add(ri)
    
    # 添加食谱步骤
    steps = [
        {'recipe_id': recipe.id, 'step_number': 1, 'instruction': '热锅下油，倒入蛋液炒熟盛起'},
        {'recipe_id': recipe.id, 'step_number': 2, 'instruction': '锅中再加少许油，下米饭炒散'},
        {'recipe_id': recipe.id, 'step_number': 3, 'instruction': '加入西红柿块炒出汁水'},
        {'recipe_id': recipe.id, 'step_number': 4, 'instruction': '倒入炒好的鸡蛋，调味炒匀即可'}
    ]
    
    for step_data in steps:
        step = RecipeStep(**step_data)
        db.session.add(step)
    
    db.session.commit()

if __name__ == '__main__':
    init_database()