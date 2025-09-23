# PaperFinder

一个简单的命令行工具，用于管理学者的论文信息。通过集成 DBLP 和 OpenAlex 数据库，可以轻松添加作者、获取论文列表并保持更新。

---

## 功能亮点

- 添加和管理多个作者信息
- 自动从 DBLP 和 OpenAlex 获取作者论文数据
- 智能去重，避免重复论文
- 命令行界面，操作简单直观
- 数据本地保存，断电不丢失
- 支持Excel格式导出数据

---

## 快速开始

### 环境准备
```bash
# 安装依赖
pip install requests openpyxl pandas
```

### 运行程序
```bash
python main.py
```

首次运行会自动创建数据文件 `data.json`。

---

## 常用命令

### 帮助信息
```
help
```

### 作者管理
```
# 添加作者
author add John_Doe [显示名称]

# 查看所有作者
author list

# 查看作者详情
author info 作者名

# 修改作者信息
author modify 作者名 [displayName/oaid] [search/set] 值

# 删除作者
author remove 作者名
```

### 论文管理
```
# 获取论文列表
paper get 作者名

# 更新论文数据
paper update [作者名]

# 查看所有论文
paper list
```

### Excel导出
```
# 导出所有作者信息
excel output authors

# 导出所有论文信息
excel output papers

# 导出特定作者的论文信息
excel output papers 作者名
```

---

## 使用示例

1. 添加新作者：
   ```
   author add John_Smith
   ```

2. 设置 OpenAlex ID（通过搜索）：
   ```
   author modify John_Smith oaid search
   ```

3. 更新论文：
   ```
   paper update John_Smith
   ```

4. 查看论文：
   ```
   paper get John_Smith
   ```

5. 导出所有数据到Excel：
   ```
   excel output authors
   excel output papers
   ```

---

## 数据存储

所有数据保存在 [data.json](file://c:\Users\Lunaunde\OneDrive\paperfinder\data.json) 文件中，采用 JSON 格式，可直接编辑。

---

## 项目结构

- [main.py](file://c:\Users\Lunaunde\OneDrive\paperfinder\main.py) - 程序入口
- [models.py](file://c:\Users\Lunaunde\OneDrive\paperfinder\models.py) - 数据模型定义
- `ui/cli.py` - 命令行界面
- `api/dblp.py` - DBLP 接口调用
- `api/openalex.py` - OpenAlex 接口调用
- [json_file_operations.py](file://c:\Users\Lunaunde\OneDrive\paperfinder\json_file_operations.py) - 数据读写
- [excel_file_operations.py](file://c:\Users\Lunaunde\OneDrive\paperfinder\excel_file_operations.py) - Excel导出功能

---

## 后续计划

- 支持更多导出格式
- 增强搜索功能
- 美化命令行界面
- 添加更多元数据字段

---

欢迎提 Issue 和 PR！

-version 25w39b