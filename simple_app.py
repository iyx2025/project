#!/usr/bin/env python3
"""
家庭食谱与膳食规划应用 - 简化版Flask后端
用于测试和演示核心功能
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# 数据库配置
DATABASE = 'database/recipe_app.db'
UPLOAD_DIR = os.path.join('static', 'uploads')

# 确保数据库目录存在
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建食谱表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            difficulty TEXT,
            cooking_time INTEGER,
            servings INTEGER DEFAULT 1,
            author_id INTEGER,
            rating REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users (id)
        )
    ''')
    
    # 创建食材表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            unit TEXT NOT NULL,
            nutrition_per_100g TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建膳食计划表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            start_date DATE,
            end_date DATE,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 创建每日餐食条目表（供前端使用）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_plan_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            recipe_name TEXT NOT NULL,
            servings INTEGER DEFAULT 1,
            calories REAL DEFAULT 0,
            nutrition_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    try:
        cursor.execute('ALTER TABLE recipes ADD COLUMN image_url TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE recipes ADD COLUMN ingredients_json TEXT')
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE recipes ADD COLUMN difficulty TEXT')
    except Exception:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shopping_list_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT NOT NULL,
            quantity REAL DEFAULT 1,
            unit TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化成功！")

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 根路由
@app.route('/')
def index():
    return jsonify({
        'message': '家庭食谱与膳食规划应用 API',
        'version': '1.0.0',
        'endpoints': {
            'users': '/api/users',
            'recipes': '/api/recipes',
            'ingredients': '/api/ingredients',
            'meal_plans': '/api/meal-plans',
            'meal_plan_entries': '/api/meal-plans/date/<date>',
            'nutrition': '/api/nutrition',
            'shopping_lists': '/api/shopping-lists'
        }
    })

# 用户管理
@app.route('/api/users/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', '')
    
    if not username or not email or not password:
        return jsonify({'error': '用户名、邮箱和密码都是必填项'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查用户名是否已存在
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        return jsonify({'error': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        return jsonify({'error': '邮箱已存在'}), 400
    
    # 创建用户（简化版，实际应用中应该加密密码）
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, name)
        VALUES (?, ?, ?, ?)
    ''', (username, email, password, name))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': '用户注册成功',
        'user_id': user_id,
        'username': username
    }), 201

@app.route('/api/users/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码都是必填项'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': '用户名或密码错误'}), 401
    
    return jsonify({
        'message': '登录成功',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'name': user['name']
        }
    }), 200

# 兼容认证端点
@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', '')
    if not username or not email or not password:
        return jsonify({'error': '用户名、邮箱和密码都是必填项'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': '用户名已存在'}), 400
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': '邮箱已存在'}), 400
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, name)
        VALUES (?, ?, ?, ?)
    ''', (username, email, password, name))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'message': '用户注册成功', 'user_id': user_id, 'username': username}), 201

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': '用户名和密码都是必填项'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if not user:
        return jsonify({'error': '用户名或密码错误'}), 401
    return jsonify({
        'message': '登录成功',
        'access_token': 'dev-token',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'name': user['name']
        }
    }), 200

# 食谱管理
@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """获取食谱列表"""
    category = request.args.get('category')
    search = request.args.get('search')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM recipes WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    if search:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term])
    
    query += ' ORDER BY created_at DESC'
    
    cursor.execute(query, params)
    recipes = cursor.fetchall()
    conn.close()
    
    recipe_list = []
    for recipe in recipes:
        recipe_list.append({
            'id': recipe['id'],
            'title': recipe['title'],
            'description': recipe['description'],
            'category': recipe['category'],
            'difficulty': recipe['difficulty'] if 'difficulty' in recipe.keys() else None,
            'cooking_time': recipe['cooking_time'],
            'servings': recipe['servings'],
            'rating': recipe['rating'],
            'created_at': recipe['created_at'],
            'image_url': recipe['image_url'] if 'image_url' in recipe.keys() else None
        })
    
    return jsonify({'recipes': recipe_list})

@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    """创建食谱"""
    data = request.get_json()
    
    title = data.get('title') or data.get('name')
    description = data.get('description', '') or data.get('instructions', '')
    category = data.get('category') or '未分类'
    cooking_time = data.get('cooking_time')
    if cooking_time is None:
        prep_time = data.get('prep_time')
        cook_time = data.get('cook_time')
        try:
            if prep_time is not None and cook_time is not None:
                cooking_time = int(prep_time) + int(cook_time)
            elif cook_time is not None:
                cooking_time = int(cook_time)
            elif prep_time is not None:
                cooking_time = int(prep_time)
            else:
                cooking_time = 0
        except Exception:
            cooking_time = 0
    servings = data.get('servings', 1)
    author_id = data.get('author_id', 1)  # 默认作者ID
    
    if not title or not category:
        return jsonify({'error': '标题和分类是必填项'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    difficulty = data.get('difficulty') or '未知'
    cursor.execute('''
        INSERT INTO recipes (title, description, category, difficulty, cooking_time, servings, author_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, category, difficulty, cooking_time, servings, author_id))
    
    recipe_id = cursor.lastrowid
    try:
        ingredients = data.get('ingredients') or []
        ingredients_json = json.dumps(ingredients, ensure_ascii=False)
        cursor.execute('UPDATE recipes SET ingredients_json = ? WHERE id = ?', (ingredients_json, recipe_id))
    except Exception:
        pass
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': '食谱创建成功',
        'recipe_id': recipe_id
    }), 201

@app.route('/api/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """获取食谱详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
    recipe = cursor.fetchone()
    conn.close()
    
    if not recipe:
        return jsonify({'error': '食谱不存在'}), 404
    
    try:
        ings = recipe['ingredients_json'] if 'ingredients_json' in recipe.keys() else None
        ingredients = json.loads(ings) if ings else []
    except Exception:
        ingredients = []
    return jsonify({
        'recipe': {
            'id': recipe['id'],
            'title': recipe['title'],
            'description': recipe['description'],
            'category': recipe['category'],
            'difficulty': recipe['difficulty'] if 'difficulty' in recipe.keys() else None,
            'cooking_time': recipe['cooking_time'],
            'servings': recipe['servings'],
            'rating': recipe['rating'],
            'created_at': recipe['created_at'],
            'image_url': recipe['image_url'] if 'image_url' in recipe.keys() else None,
            'ingredients': ingredients
        }
    })

@app.route('/api/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipe_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '食谱不存在'}), 404
    title = data.get('title') or data.get('name')
    description = data.get('description') or data.get('instructions')
    category = data.get('category')
    difficulty = data.get('difficulty')
    cooking_time = data.get('cooking_time')
    if cooking_time is None:
        prep_time = data.get('prep_time')
        cook_time = data.get('cook_time')
        try:
            if prep_time is not None and cook_time is not None:
                cooking_time = int(prep_time) + int(cook_time)
            elif cook_time is not None:
                cooking_time = int(cook_time)
            elif prep_time is not None:
                cooking_time = int(prep_time)
        except Exception:
            cooking_time = None
    servings = data.get('servings')
    rating = data.get('rating')
    image_url = data.get('image_url')
    fields = []
    params = []
    if title is not None:
        fields.append('title = ?')
        params.append(title)
    if description is not None:
        fields.append('description = ?')
        params.append(description)
    if category is not None:
        fields.append('category = ?')
        params.append(category)
    if difficulty is not None:
        fields.append('difficulty = ?')
        params.append(difficulty)
    if cooking_time is not None:
        fields.append('cooking_time = ?')
        params.append(cooking_time)
    if servings is not None:
        fields.append('servings = ?')
        params.append(servings)
    if rating is not None:
        fields.append('rating = ?')
        params.append(rating)
    if image_url is not None:
        fields.append('image_url = ?')
        params.append(image_url)
    try:
        ingredients = data.get('ingredients')
        if ingredients is not None:
            ingredients_json = json.dumps(ingredients, ensure_ascii=False)
            fields.append('ingredients_json = ?')
            params.append(ingredients_json)
    except Exception:
        pass
    if not fields:
        conn.close()
        return jsonify({'error': '没有可更新的字段'}), 400
    params.append(recipe_id)
    cursor.execute(f'UPDATE recipes SET {", ".join(fields)} WHERE id = ?', params)
    conn.commit()
    conn.close()
    return jsonify({'message': '食谱更新成功', 'recipe_id': recipe_id}), 200

@app.route('/api/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipe_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '食谱不存在'}), 404
    cursor.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': '食谱已删除'}), 200

@app.route('/api/recipes/<int:recipe_id>/image', methods=['POST'])
def upload_recipe_image(recipe_id):
    if 'image' not in request.files and not request.files:
        file = None
    else:
        file = request.files.get('image')
    if not file:
        return jsonify({'error': '缺少图片文件'}), 400
    name = file.filename or 'image'
    name = os.path.basename(name).replace(' ', '_')
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    ext = '.' + name.split('.')[-1].lower() if '.' in name else ''
    fname = f'recipe_{recipe_id}_{ts}{ext}'
    path = os.path.join(UPLOAD_DIR, fname)
    file.save(path)
    url = f'/static/uploads/{fname}'
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE recipes SET image_url = ? WHERE id = ?', (url, recipe_id))
    conn.commit()
    conn.close()
    return jsonify({'message': '图片上传成功', 'image_url': url})

@app.route('/api/recipes/recommend', methods=['GET'])
def recommend_recipes():
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    max_time = request.args.get('max_time')
    limit = int(request.args.get('limit', 10))
    conn = get_db_connection()
    cursor = conn.cursor()
    base = 'SELECT * FROM recipes'
    where = []
    params = []
    if category:
        where.append('category = ?')
        params.append(category)
    if max_time:
        where.append('cooking_time <= ?')
        params.append(int(max_time))
    if difficulty:
        where.append('difficulty = ?')
        params.append(difficulty)
    if where:
        base += ' WHERE ' + ' AND '.join(where)
    base += ' ORDER BY rating DESC, cooking_time ASC, created_at DESC'
    base += f' LIMIT {limit}'
    cursor.execute(base, params)
    recipes = cursor.fetchall()
    conn.close()
    result = []
    for r in recipes:
        result.append({
            'id': r['id'],
            'title': r['title'],
            'category': r['category'],
            'cooking_time': r['cooking_time'],
            'rating': r['rating'],
            'image_url': r['image_url'] if 'image_url' in r.keys() else None,
            'ingredients': json.loads(r['ingredients_json']) if 'ingredients_json' in r.keys() and r['ingredients_json'] else []
        })
    return jsonify({'recipes': result})

# 食材管理
@app.route('/api/ingredients', methods=['GET'])
def get_ingredients():
    """获取食材列表"""
    category = request.args.get('category')
    search = request.args.get('search')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM ingredients WHERE 1=1'
    params = []
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    if search:
        query += ' AND name LIKE ?'
        params.append(f'%{search}%')
    
    query += ' ORDER BY name'
    
    cursor.execute(query, params)
    ingredients = cursor.fetchall()
    conn.close()
    
    ingredient_list = []
    for ingredient in ingredients:
        nutrition_data = {}
        if ingredient['nutrition_per_100g']:
            try:
                nutrition_data = json.loads(ingredient['nutrition_per_100g'])
            except:
                pass
        
        ingredient_list.append({
            'id': ingredient['id'],
            'name': ingredient['name'],
            'category': ingredient['category'],
            'unit': ingredient['unit'],
            'nutrition': nutrition_data
        })
    
    return jsonify({'ingredients': ingredient_list})

@app.route('/api/ingredients', methods=['POST'])
def create_ingredient():
    """创建食材"""
    data = request.get_json()
    
    name = data.get('name')
    category = data.get('category')
    unit = data.get('unit')
    nutrition = data.get('nutrition', {})
    
    if not name or not category or not unit:
        return jsonify({'error': '名称、分类和单位是必填项'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查是否已存在
    cursor.execute('SELECT id FROM ingredients WHERE name = ?', (name,))
    if cursor.fetchone():
        return jsonify({'error': '食材已存在'}), 400
    
    nutrition_json = json.dumps(nutrition) if nutrition else None
    
    cursor.execute('''
        INSERT INTO ingredients (name, category, unit, nutrition_per_100g)
        VALUES (?, ?, ?, ?)
    ''', (name, category, unit, nutrition_json))
    
    ingredient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': '食材创建成功',
        'ingredient_id': ingredient_id
    }), 201

# 膳食计划
@app.route('/api/meal-plans', methods=['GET'])
def get_meal_plans():
    """获取膳食计划列表"""
    user_id = request.args.get('user_id', 1)  # 默认用户ID
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM meal_plans WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    meal_plans = cursor.fetchall()
    conn.close()
    
    plan_list = []
    for plan in meal_plans:
        plan_list.append({
            'id': plan['id'],
            'title': plan['title'],
            'start_date': plan['start_date'],
            'end_date': plan['end_date'],
            'status': plan['status'],
            'created_at': plan['created_at']
        })
    
    return jsonify({'meal_plans': plan_list})

@app.route('/api/meal-plans', methods=['POST'])
def create_meal_plan():
    """创建膳食计划"""
    data = request.get_json()
    
    user_id = data.get('user_id', 1)  # 默认用户ID
    title = data.get('title')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not title or not start_date or not end_date:
        return jsonify({'error': '标题、开始日期和结束日期是必填项'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO meal_plans (user_id, title, start_date, end_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, title, start_date, end_date))
    
    plan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': '膳食计划创建成功',
        'plan_id': plan_id
    }), 201

# 当日餐食获取
@app.route('/api/meal-plans/date/<date>', methods=['GET'])
def get_meal_plan_by_date(date):
    user_id = request.args.get('user_id', 1)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM meal_plan_entries WHERE user_id = ? AND date = ? ORDER BY created_at', (user_id, date))
    entries = cursor.fetchall()
    conn.close()
    result = []
    for e in entries:
        try:
            nutrition = json.loads(e['nutrition_info']) if e['nutrition_info'] else {}
        except Exception:
            nutrition = {}
        result.append({
            'id': e['id'],
            'date': e['date'],
            'meal_type': e['meal_type'],
            'recipe_name': e['recipe_name'],
            'servings': e['servings'],
            'calories': e['calories'],
            'nutrition': nutrition
        })
    return jsonify({'meals': result})

# 添加餐食条目
@app.route('/api/meal-plans', methods=['PUT', 'PATCH'])
@app.route('/api/meal-plans', methods=['POST'])
def add_meal_entry():
    data = request.get_json() or {}
    user_id = data.get('user_id', 1)
    date = data.get('date')
    meal_type = data.get('meal_type')
    recipe_name = data.get('recipe_name')
    servings = int(data.get('servings', 1))
    calories = float(data.get('calories', 0))
    nutrition = data.get('nutrition') or {}
    if not date or not meal_type or not recipe_name:
        return jsonify({'error': 'date、meal_type、recipe_name 为必填项'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO meal_plan_entries (user_id, date, meal_type, recipe_name, servings, calories, nutrition_info)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, date, meal_type, recipe_name, servings, calories, json.dumps(nutrition) if nutrition else None))
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'message': '餐食已添加', 'id': entry_id}), 201

# 删除餐食条目
@app.route('/api/meal-plans/<int:entry_id>', methods=['DELETE'])
def delete_meal_entry(entry_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meal_plan_entries WHERE id = ?', (entry_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': '餐食已删除'})

# 简化版营养分析：每日
@app.route('/api/nutrition/daily/<date>', methods=['GET'])
def get_daily_nutrition(date):
    user_id = request.args.get('user_id', 1)
    try:
        # 校验日期格式
        datetime.strptime(date, '%Y-%m-%d')
    except Exception:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM meal_plan_entries WHERE user_id = ? AND date = ?', (user_id, date))
    entries = cursor.fetchall()
    conn.close()
    totals = {
        'total_calories': 0.0,
        'total_protein': 0.0,
        'total_carbs': 0.0,
        'total_fat': 0.0,
        'total_fiber': 0.0,
        'total_sugar': 0.0,
        'total_sodium': 0.0
    }
    meals = []
    for e in entries:
        try:
            nutrition = json.loads(e['nutrition_info']) if e['nutrition_info'] else {}
        except Exception:
            nutrition = {}
        totals['total_calories'] += float(nutrition.get('calories', e['calories'] or 0) or 0)
        totals['total_protein'] += float(nutrition.get('protein', 0) or 0)
        totals['total_carbs'] += float(nutrition.get('carbs', 0) or 0)
        totals['total_fat'] += float(nutrition.get('fat', 0) or 0)
        totals['total_fiber'] += float(nutrition.get('fiber', 0) or 0)
        totals['total_sugar'] += float(nutrition.get('sugar', 0) or 0)
        totals['total_sodium'] += float(nutrition.get('sodium', 0) or 0)
        meals.append({
            'meal_type': e['meal_type'],
            'recipe_name': e['recipe_name'],
            'servings': e['servings'],
            'nutrition': nutrition
        })
    recommendations = '营养摄入总体正常' if totals['total_calories'] >= 1200 else '建议适当增加能量摄入'
    return jsonify({
        'date': date,
        **totals,
        'meals': meals,
        'recommendations': recommendations
    })

@app.route('/api/nutrition/weekly', methods=['GET'])
def get_weekly_nutrition():
    user_id = request.args.get('user_id', 1)
    end = datetime.now()
    start = end - timedelta(days=6)
    conn = get_db_connection()
    cursor = conn.cursor()
    weekly = []
    day = start
    while day <= end:
        d = day.strftime('%Y-%m-%d')
        cursor.execute('SELECT nutrition_info, calories FROM meal_plan_entries WHERE user_id = ? AND date = ?', (user_id, d))
        rows = cursor.fetchall()
        cal = 0.0
        prot = 0.0
        carbs = 0.0
        fat = 0.0
        for row in rows:
            try:
                n = json.loads(row['nutrition_info']) if row['nutrition_info'] else {}
            except Exception:
                n = {}
            cal += float(n.get('calories', row['calories'] or 0) or 0)
            prot += float(n.get('protein', 0) or 0)
            carbs += float(n.get('carbs', 0) or 0)
            fat += float(n.get('fat', 0) or 0)
        weekly.append({'date': d, 'calories': round(cal, 1), 'protein': round(prot, 1), 'carbs': round(carbs, 1), 'fat': round(fat, 1)})
        day += timedelta(days=1)
    conn.close()
    avg = {'avg_calories': round(sum(x['calories'] for x in weekly) / len(weekly), 1) if weekly else 0,
           'avg_protein': round(sum(x['protein'] for x in weekly) / len(weekly), 1) if weekly else 0,
           'avg_carbs': round(sum(x['carbs'] for x in weekly) / len(weekly), 1) if weekly else 0,
           'avg_fat': round(sum(x['fat'] for x in weekly) / len(weekly), 1) if weekly else 0}
    return jsonify({'weekly': weekly, 'average': avg})

# 智能生成当日餐食
@app.route('/api/meal-plans/generate', methods=['POST'])
def generate_meal_plan():
    data = request.get_json() or {}
    user_id = data.get('user_id', 1)
    date = data.get('date') or datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT title, category, cooking_time, rating FROM recipes ORDER BY rating DESC, created_at DESC')
    recipes = cursor.fetchall()
    def pick_recipe(default_name):
        return (recipes[0]['title'] if recipes else default_name)
    suggestions = [
        ('早餐', pick_recipe('牛奶麦片'), 400),
        ('午餐', pick_recipe('番茄炒蛋'), 600),
        ('晚餐', pick_recipe('清蒸鱼'), 500)
    ]
    created = []
    for meal_type, name, kcal in suggestions:
        cursor.execute('''
            INSERT INTO meal_plan_entries (user_id, date, meal_type, recipe_name, servings, calories, nutrition_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, date, meal_type, name, 1, float(kcal), json.dumps({'calories': kcal}) ))
        created.append({'meal_type': meal_type, 'recipe_name': name, 'servings': 1, 'calories': kcal})
    conn.commit()
    conn.close()
    return jsonify({'message': '智能膳食生成成功', 'date': date, 'meals': created}), 201

@app.route('/api/shopping-lists', methods=['GET'])
def get_shopping_list_items():
    user_id = request.args.get('user_id', 1)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shopping_list_items WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    items = cursor.fetchall()
    conn.close()
    result = []
    for it in items:
        result.append({
            'id': it['id'],
            'item_name': it['item_name'],
            'quantity': it['quantity'],
            'unit': it['unit'],
            'notes': it['notes']
        })
    return jsonify(result)

@app.route('/api/shopping-lists', methods=['POST'])
def add_shopping_list_item():
    data = request.get_json() or {}
    user_id = data.get('user_id', 1)
    name = data.get('item_name')
    quantity = float(data.get('quantity', 1))
    unit = data.get('unit')
    notes = data.get('notes')
    if not name:
        return jsonify({'error': 'item_name 不能为空'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO shopping_list_items (user_id, item_name, quantity, unit, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, name, quantity, unit, notes))
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'message': '物品添加成功', 'id': item_id}), 201

@app.route('/api/shopping-lists/<int:item_id>', methods=['DELETE'])
def delete_shopping_list_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM shopping_list_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': '物品已删除'})

@app.route('/api/shopping-lists/generate', methods=['POST'])
def generate_shopping_list():
    data = request.get_json() or {}
    user_id = data.get('user_id', 1)
    date = data.get('date')
    conn = get_db_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute('SELECT meal_type, recipe_name, servings FROM meal_plan_entries WHERE user_id = ? AND date = ?', (user_id, date))
    else:
        cursor.execute('SELECT meal_type, recipe_name, servings FROM meal_plan_entries WHERE user_id = ?', (user_id,))
    entries = cursor.fetchall()
    for e in entries:
        cursor.execute('''
            INSERT INTO shopping_list_items (user_id, item_name, quantity, unit, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, e['recipe_name'], float(e['servings'] or 1), '份', e['meal_type']))
    conn.commit()
    cursor.execute('SELECT * FROM shopping_list_items WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    items = cursor.fetchall()
    conn.close()
    result = []
    for it in items:
        result.append({
            'id': it['id'],
            'item_name': it['item_name'],
            'quantity': it['quantity'],
            'unit': it['unit'],
            'notes': it['notes']
        })
    return jsonify(result), 201

@app.route('/api/shopping-lists/export', methods=['GET'])
def export_shopping_list():
    user_id = request.args.get('user_id', 1)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT item_name, quantity, unit, notes FROM shopping_list_items WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    items = cursor.fetchall()
    conn.close()
    lines = []
    for it in items:
        note = it['notes'] or ''
        lines.append(f"{it['item_name']}\t{it['quantity']}\t{it['unit'] or ''}\t{note}")
    return '\n'.join(lines)

# 健康检查
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    
    print("🎉 家庭食谱与膳食规划应用后端服务器启动！")
    print("📋 API端点:")
    print("  - 用户注册: POST /api/users/register")
    print("  - 用户登录: POST /api/users/login")
    print("  - 认证注册: POST /api/auth/register")
    print("  - 认证登录: POST /api/auth/login")
    print("  - 食谱列表: GET /api/recipes")
    print("  - 创建食谱: POST /api/recipes")
    print("  - 食材列表: GET /api/ingredients")
    print("  - 创建食材: POST /api/ingredients")
    print("  - 膳食计划: GET /api/meal-plans")
    print("  - 当日餐食: GET /api/meal-plans/date/<date>")
    print("  - 添加餐食: POST /api/meal-plans")
    print("  - 删除餐食: DELETE /api/meal-plans/<id>")
    print("  - 智能生成: POST /api/meal-plans/generate")
    print("  - 每日营养: GET /api/nutrition/daily/<date>")
    print("  - 周营养: GET /api/nutrition/weekly")
    print("  - 购物清单: GET /api/shopping-lists")
    print("  - 添加物品: POST /api/shopping-lists")
    print("  - 删除物品: DELETE /api/shopping-lists/<id>")
    print("  - 生成清单: POST /api/shopping-lists/generate")
    print("  - 导出清单: GET /api/shopping-lists/export")
    print("  - 推荐食谱: GET /api/recipes/recommend")
    print("  - 健康检查: GET /health")
    print("\n🚀 服务器运行在: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)