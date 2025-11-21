from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 用户基本信息
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    birthday = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    
    # 健康信息
    height = db.Column(db.Float, nullable=True)  # 身高(cm)
    weight = db.Column(db.Float, nullable=True)  # 体重(kg)
    activity_level = db.Column(db.String(20), nullable=True)  # 活动水平
    dietary_preferences = db.Column(db.Text, nullable=True)  # 饮食偏好
    allergies = db.Column(db.Text, nullable=True)  # 过敏信息
    health_goals = db.Column(db.String(50), nullable=True)  # 健康目标
    
    # 状态信息
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 关系
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')
    meal_plans = db.relationship('MealPlan', backref='user', lazy='dynamic')
    ingredient_stocks = db.relationship('IngredientStock', backref='user', lazy='dynamic')
    shopping_lists = db.relationship('ShoppingList', backref='user', lazy='dynamic')
    recipe_ratings = db.relationship('RecipeRating', backref='user', lazy='dynamic')
    recipe_favorites = db.relationship('RecipeFavorite', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_email=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'avatar': self.avatar,
            'height': self.height,
            'weight': self.weight,
            'activity_level': self.activity_level,
            'dietary_preferences': self.dietary_preferences,
            'allergies': self.allergies,
            'health_goals': self.health_goals,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'

class Recipe(db.Model):
    """食谱模型"""
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    images = db.Column(db.Text, nullable=True)  # JSON格式存储图片URL列表
    category = db.Column(db.String(50), nullable=False, index=True)  # 早餐/午餐/晚餐/甜品等
    cuisine = db.Column(db.String(50), nullable=True, index=True)  # 菜系
    difficulty = db.Column(db.String(20), nullable=False, default='medium')  # 难度
    cooking_time = db.Column(db.Integer, nullable=False)  # 烹饪时间(分钟)
    servings = db.Column(db.Integer, nullable=False, default=1)  # 份量
    
    # 作者信息
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 统计信息
    rating = db.Column(db.Float, default=0.0)
    favorite_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    
    # 状态信息
    is_public = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    ingredients = db.relationship('RecipeIngredient', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    steps = db.relationship('RecipeStep', backref='recipe', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('RecipeRating', backref='recipe', lazy='dynamic')
    favorites = db.relationship('RecipeFavorite', backref='recipe', lazy='dynamic')
    meal_plan_items = db.relationship('MealPlanItem', backref='recipe', lazy='dynamic')
    
    def get_images_list(self):
        """获取图片列表"""
        import json
        try:
            return json.loads(self.images) if self.images else []
        except:
            return []
    
    def set_images_list(self, images_list):
        """设置图片列表"""
        import json
        self.images = json.dumps(images_list) if images_list else None
    
    def to_dict(self, include_author=False, include_ingredients=False, include_steps=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'images': self.get_images_list(),
            'category': self.category,
            'cuisine': self.cuisine,
            'difficulty': self.difficulty,
            'cooking_time': self.cooking_time,
            'servings': self.servings,
            'rating': self.rating,
            'favorite_count': self.favorite_count,
            'view_count': self.view_count,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_author and self.author:
            data['author'] = self.author.to_dict()
        
        if include_ingredients:
            data['ingredients'] = [ing.to_dict() for ing in self.ingredients]
        
        if include_steps:
            data['steps'] = [step.to_dict() for step in self.steps]
        
        return data
    
    def __repr__(self):
        return f'<Recipe {self.title}>'

class Ingredient(db.Model):
    """食材模型"""
    __tablename__ = 'ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # 蔬菜/肉类/水果等
    unit = db.Column(db.String(20), nullable=False, default='g')  # 默认单位
    
    # 营养信息（每100g）
    nutrition_per_100g = db.Column(db.Text, nullable=True)  # JSON格式存储营养数据
    
    # 存储建议
    storage_method = db.Column(db.String(100), nullable=True)
    shelf_life_days = db.Column(db.Integer, nullable=True)  # 保质期(天)
    
    # 状态信息
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    recipe_ingredients = db.relationship('RecipeIngredient', backref='ingredient', lazy='dynamic')
    stocks = db.relationship('IngredientStock', backref='ingredient', lazy='dynamic')
    
    def get_nutrition_data(self):
        """获取营养数据"""
        import json
        try:
            return json.loads(self.nutrition_per_100g) if self.nutrition_per_100g else {}
        except:
            return {}
    
    def set_nutrition_data(self, nutrition_data):
        """设置营养数据"""
        import json
        self.nutrition_per_100g = json.dumps(nutrition_data) if nutrition_data else None
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'unit': self.unit,
            'nutrition': self.get_nutrition_data(),
            'storage_method': self.storage_method,
            'shelf_life_days': self.shelf_life_days,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Ingredient {self.name}>'

class RecipeIngredient(db.Model):
    """食谱食材关联模型"""
    __tablename__ = 'recipe_ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # 数量
    unit = db.Column(db.String(20), nullable=False)  # 单位
    notes = db.Column(db.String(200), nullable=True)  # 备注（如"切丝"、"去皮"等）
    order_index = db.Column(db.Integer, default=0)  # 排序索引
    
    def to_dict(self, include_ingredient=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'quantity': self.quantity,
            'unit': self.unit,
            'notes': self.notes,
            'order_index': self.order_index
        }
        
        if include_ingredient and self.ingredient:
            data['ingredient'] = self.ingredient.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<RecipeIngredient {self.recipe.title} - {self.ingredient.name}>'

class RecipeStep(db.Model):
    """食谱步骤模型"""
    __tablename__ = 'recipe_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    instruction = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)  # 步骤图片
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'step_number': self.step_number,
            'instruction': self.instruction,
            'image': self.image
        }
    
    def __repr__(self):
        return f'<RecipeStep {self.recipe.title} - Step {self.step_number}>'

class MealPlan(db.Model):
    """膳食计划模型"""
    __tablename__ = 'meal_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # 营养目标（JSON格式）
    nutrition_targets = db.Column(db.Text, nullable=True)
    
    # 状态信息
    status = db.Column(db.String(20), default='active')  # active/completed/cancelled
    is_generated = db.Column(db.Boolean, default=False)  # 是否为自动生成
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    items = db.relationship('MealPlanItem', backref='meal_plan', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_nutrition_targets(self):
        """获取营养目标"""
        import json
        try:
            return json.loads(self.nutrition_targets) if self.nutrition_targets else {}
        except:
            return {}
    
    def set_nutrition_targets(self, targets):
        """设置营养目标"""
        import json
        self.nutrition_targets = json.dumps(targets) if targets else None
    
    def to_dict(self, include_items=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'nutrition_targets': self.get_nutrition_targets(),
            'status': self.status,
            'is_generated': self.is_generated,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_items:
            data['items'] = [item.to_dict(include_recipe=True) for item in self.items]
        
        return data
    
    def __repr__(self):
        return f'<MealPlan {self.title}>'

class MealPlanItem(db.Model):
    """膳食计划项模型"""
    __tablename__ = 'meal_plan_items'
    
    id = db.Column(db.Integer, primary_key=True)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plans.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    
    # 计划时间
    planned_date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast/lunch/dinner/snack
    
    # 份量调整
    servings = db.Column(db.Integer, nullable=False, default=1)
    
    # 状态信息
    is_completed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_recipe=False, include_meal_plan=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'planned_date': self.planned_date.isoformat(),
            'meal_type': self.meal_type,
            'servings': self.servings,
            'is_completed': self.is_completed,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_recipe and self.recipe:
            data['recipe'] = self.recipe.to_dict()
        
        if include_meal_plan and self.meal_plan:
            data['meal_plan'] = self.meal_plan.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<MealPlanItem {self.meal_plan.title} - {self.recipe.title}>'

class IngredientStock(db.Model):
    """食材库存模型"""
    __tablename__ = 'ingredient_stocks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    
    # 库存信息
    quantity = db.Column(db.Float, nullable=False, default=0)
    unit = db.Column(db.String(20), nullable=False)
    
    # 保质期信息
    purchase_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    
    # 存储信息
    storage_location = db.Column(db.String(50), nullable=True)  # 冰箱/常温/冷冻等
    notes = db.Column(db.Text, nullable=True)
    
    # 状态信息
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_ingredient=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'quantity': self.quantity,
            'unit': self.unit,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'storage_location': self.storage_location,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_ingredient and self.ingredient:
            data['ingredient'] = self.ingredient.to_dict()
        
        return data
    
    def is_expiring_soon(self, days=3):
        """检查是否即将过期"""
        if not self.expiry_date:
            return False
        
        from datetime import date
        today = date.today()
        delta = self.expiry_date - today
        return 0 <= delta.days <= days
    
    def __repr__(self):
        return f'<IngredientStock {self.user.username} - {self.ingredient.name}>'

class ShoppingList(db.Model):
    """购物清单模型"""
    __tablename__ = 'shopping_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # 生成来源
    source_type = db.Column(db.String(50), nullable=True)  # meal_plan/manual
    source_id = db.Column(db.Integer, nullable=True)
    
    # 状态信息
    status = db.Column(db.String(20), default='active')  # active/completed/cancelled
    is_generated = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # 关系
    items = db.relationship('ShoppingListItem', backref='shopping_list', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_items=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'status': self.status,
            'is_generated': self.is_generated,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
        
        if include_items:
            data['items'] = [item.to_dict(include_ingredient=True) for item in self.items]
        
        return data
    
    def __repr__(self):
        return f'<ShoppingList {self.title}>'

class ShoppingListItem(db.Model):
    """购物清单项模型"""
    __tablename__ = 'shopping_list_items'
    
    id = db.Column(db.Integer, primary_key=True)
    shopping_list_id = db.Column(db.Integer, db.ForeignKey('shopping_lists.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    
    # 购买信息
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    
    # 状态信息
    is_purchased = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    estimated_price = db.Column(db.Float, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_ingredient=False, include_shopping_list=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'quantity': self.quantity,
            'unit': self.unit,
            'is_purchased': self.is_purchased,
            'notes': self.notes,
            'estimated_price': self.estimated_price,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_ingredient and self.ingredient:
            data['ingredient'] = self.ingredient.to_dict()
        
        if include_shopping_list and self.shopping_list:
            data['shopping_list'] = self.shopping_list.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<ShoppingListItem {self.shopping_list.title} - {self.ingredient.name}>'

class RecipeRating(db.Model):
    """食谱评分模型"""
    __tablename__ = 'recipe_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5分
    comment = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 复合唯一约束
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_rating'),)
    
    def to_dict(self, include_user=False, include_recipe=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        
        if include_recipe and self.recipe:
            data['recipe'] = self.recipe.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<RecipeRating {self.user.username} - {self.recipe.title}: {self.rating}>'

class RecipeFavorite(db.Model):
    """食谱收藏模型"""
    __tablename__ = 'recipe_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 复合唯一约束
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_favorite'),)
    
    def to_dict(self, include_user=False, include_recipe=False):
        """转换为字典格式"""
        data = {
            'id': self.id,
            'created_at': self.created_at.isoformat()
        }
        
        if include_user and self.user:
            data['user'] = self.user.to_dict()
        
        if include_recipe and self.recipe:
            data['recipe'] = self.recipe.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<RecipeFavorite {self.user.username} - {self.recipe.title}>'