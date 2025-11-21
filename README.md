# 家庭食谱与膳食规划应用

一个功能完整的桌面应用程序，用于管理家庭食谱、制定膳食计划、跟踪食材库存和进行营养分析。

## 🌟 功能特性

### 📖 食谱管理
- ✅ 食谱的增删改查功能
- ✅ 食谱分类管理（早餐、午餐、晚餐、甜点等）
- ✅ 食谱难度评级（简单、中等、困难）
- ✅ 制作时间和份量管理
- ✅ 食材清单和制作步骤
- ✅ 食谱搜索和筛选功能

### 📅 膳食规划
- ✅ 按日期制定膳食计划
- ✅ 智能膳食计划生成
- ✅ 多餐次支持（早餐、午餐、晚餐、加餐）
- ✅ 膳食计划可视化展示
- ✅ 食谱与膳食计划关联

### 🥬 食材管理
- ✅ 食材库存管理
- ✅ 食材分类（蔬菜、水果、肉类、海鲜等）
- ✅ 保质期提醒功能
- ✅ 食材搜索和筛选
- ✅ 库存数量管理

### 🛒 购物清单
- ✅ 从膳食计划自动生成购物清单
- ✅ 手动添加购物项
- ✅ 购物清单导出功能
- ✅ 购物项分类管理

### 📊 营养分析
- ✅ 每日营养摄入统计
- ✅ 营养成分分析（蛋白质、脂肪、碳水化合物等）
- ✅ 营养数据可视化图表
- ✅ 健康建议生成
- ✅ 营养趋势分析

### 🔐 用户系统
- ✅ 用户注册和登录
- ✅ JWT身份认证
- ✅ 用户数据隔离
- ✅ 安全的密码管理

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Flask (Python Web框架)
- **数据库**: SQLite (轻量级关系型数据库)
- **ORM**: SQLAlchemy (数据库对象关系映射)
- **认证**: JWT (JSON Web Token)
- **API**: RESTful API设计
- **依赖管理**: pip + requirements.txt

### 前端技术栈
- **GUI框架**: PyQt6 (跨平台桌面应用框架)
- **数据可视化**: Matplotlib (图表生成库)
- **HTTP客户端**: Requests (Python HTTP库)
- **日期处理**: PyQt6内置日期组件

### 项目结构
```
project/
├── simple_app.py              # 简化版Flask后端
├── main_window.py            # PyQt6主窗口应用
├── nutrition_charts.py       # 营养数据可视化
├── start_app.py              # 应用启动器
├── test_app.py               # 功能测试脚本
├── requirements.txt          # Python依赖包
├── database/                 # 数据库文件目录
│   └── recipe_app.db        # SQLite数据库
└── README.md                 # 项目说明文档
```

## 🚀 快速开始

### 环境要求
- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆或下载项目**
```bash
git clone <项目地址>
cd 家庭食谱与膳食规划应用
```

2. **安装依赖包**
```bash
pip install -r requirements.txt
```

如果 requirements.txt 安装失败，可以手动安装核心依赖：
```bash
pip install flask flask-cors flask-jwt-extended sqlalchemy requests pyqt6 matplotlib
```

3. **启动后端服务器**
```bash
python simple_app.py
```
服务器将在 http://localhost:5000 启动

4. **启动前端应用**
在新的终端窗口中：
```bash
python main_window.py
```

或者使用一键启动脚本：
```bash
python start_app.py
```

### 使用说明

1. **首次使用**
   - 启动应用后，点击"注册"创建新账户
   - 或使用测试账户登录：
     - 用户名: test_user
     - 密码: test123456

2. **食谱管理**
   - 点击"食谱管理"标签页
   - 使用"添加食谱"按钮创建新食谱
   - 填写食谱基本信息、食材清单和制作步骤
   - 支持搜索和查看现有食谱

3. **膳食规划**
   - 点击"膳食规划"标签页
   - 选择日期，查看或添加当日膳食计划
   - 使用"智能生成"自动创建膳食计划
   - 支持多餐次规划

4. **食材管理**
   - 点击"食材管理"标签页
   - 添加和管理食材库存
   - 设置食材分类和保质期
   - 查看食材库存状态

5. **购物清单**
   - 点击"购物清单"标签页
   - 从膳食计划自动生成购物清单
   - 手动添加购物项
   - 导出购物清单到文本文件

6. **营养分析**
   - 点击"营养分析"标签页
   - 查看每日营养摄入统计
   - 分析营养成分比例
   - 获取个性化健康建议

7. **数据可视化**
   - 点击"营养图表"标签页
   - 查看营养分布饼图
   - 分析卡路里摄入趋势
   - 对比不同营养素含量

## 🧪 功能测试

运行完整的功能测试：
```bash
python test_app.py
```

测试脚本将验证：
- 后端API连接
- 用户注册和登录
- 食谱管理功能
- 食材管理功能
- 膳食计划功能
- 购物清单功能
- 营养分析功能
- 数据库连接

## 📊 API接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新令牌

### 食谱接口
- `GET /api/recipes` - 获取食谱列表
- `POST /api/recipes` - 创建新食谱
- `GET /api/recipes/<id>` - 获取特定食谱
- `PUT /api/recipes/<id>` - 更新食谱
- `DELETE /api/recipes/<id>` - 删除食谱
- `GET /api/recipes/search?q=<query>` - 搜索食谱

### 食材接口
- `GET /api/ingredients` - 获取食材列表
- `POST /api/ingredients` - 创建新食材
- `PUT /api/ingredients/<id>` - 更新食材
- `DELETE /api/ingredients/<id>` - 删除食材

### 膳食计划接口
- `GET /api/meal-plans/date/<date>` - 获取指定日期膳食计划
- `POST /api/meal-plans` - 创建膳食计划
- `DELETE /api/meal-plans/<id>` - 删除膳食计划
- `POST /api/meal-plans/generate` - 智能生成膳食计划

### 购物清单接口
- `GET /api/shopping-lists` - 获取购物清单
- `POST /api/shopping-lists` - 添加购物项
- `DELETE /api/shopping-lists/<id>` - 删除购物项
- `POST /api/shopping-lists/generate` - 生成购物清单
- `GET /api/shopping-lists/export` - 导出购物清单

### 营养分析接口
- `GET /api/nutrition/daily/<date>` - 获取每日营养分析
- `GET /api/nutrition/weekly/<date>` - 获取周营养分析
- `GET /api/nutrition/recommendations` - 获取营养建议

## 🔧 配置选项

### 后端配置
在 `simple_app.py` 中可以配置：
- 服务器端口（默认5000）
- 数据库连接
- JWT密钥和过期时间
- CORS设置

### 前端配置
在 `main_window.py` 中可以配置：
- API服务器地址
- 界面主题和样式
- 图表显示选项

## 🎯 开发计划

### 已完成功能 ✅
- 基础食谱管理
- 膳食计划制定
- 食材库存管理
- 购物清单生成
- 基础营养分析
- 用户认证系统
- 数据可视化图表

### 待开发功能 📋
- 食谱图片上传功能
- 智能食谱推荐
- 营养成分数据库集成
- 移动端应用
- 云同步功能
- 社交分享功能
- 语音输入支持

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置
1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 联系方式

- 项目维护者: AI Assistant
- 邮箱: example@email.com
- 项目地址: [项目GitHub地址]

## 🙏 致谢

- 感谢 PyQt6 提供优秀的GUI框架
- 感谢 Flask 提供轻量级Web框架
- 感谢 SQLite 提供嵌入式数据库
- 感谢所有开源贡献者

---

**享受健康美味的家庭料理！** 🍽️✨
