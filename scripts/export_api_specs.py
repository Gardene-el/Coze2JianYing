#!/usr/bin/env python3
"""
API 规范导出工具

此脚本用于从 FastAPI 应用导出各种 API 规范文件：
1. OpenAPI 3.1.0 规范 (JSON 和 YAML)
2. Swagger 2.0 规范 (JSON)
3. Postman Collection v2.1 (JSON)

这些文件可用于：
- 在 Coze 平台创建"基于已有服务"的云侧插件
- 导入到 API 测试工具（Postman、Insomnia 等）
- 生成客户端 SDK
- API 文档生成

使用方法：
    python scripts/export_api_specs.py

生成的文件将保存在 api_specs/ 目录下。
"""

import json
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.api_main import app


def export_openapi_json(output_dir: Path):
    """导出 OpenAPI 3.1.0 JSON 格式"""
    openapi_spec = app.openapi()
    output_file = output_dir / "openapi.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OpenAPI 3.1.0 JSON 已导出: {output_file}")
    return openapi_spec


def export_openapi_yaml(openapi_spec: dict, output_dir: Path):
    """导出 OpenAPI 3.1.0 YAML 格式"""
    try:
        import yaml
    except ImportError:
        print("⚠️  yaml 模块未安装，跳过 YAML 导出")
        print("   安装命令: pip install pyyaml")
        return
    
    output_file = output_dir / "openapi.yaml"
    
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(openapi_spec, f, allow_unicode=True, sort_keys=False)
    
    print(f"✅ OpenAPI 3.1.0 YAML 已导出: {output_file}")


def convert_to_swagger_2(openapi_spec: dict) -> dict:
    """将 OpenAPI 3.x 转换为 Swagger 2.0 格式
    
    注意：这是简化的转换，不包含所有高级特性
    """
    swagger = {
        "swagger": "2.0",
        "info": openapi_spec.get("info", {}),
        "host": "localhost:8000",  # 默认主机，用户需要根据实际部署修改
        "basePath": "/",
        "schemes": ["http", "https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "paths": {},
        "definitions": {}
    }
    
    # 转换路径
    for path, methods in openapi_spec.get("paths", {}).items():
        swagger["paths"][path] = {}
        for method, details in methods.items():
            # 基本信息
            operation = {
                "summary": details.get("summary", ""),
                "description": details.get("description", ""),
                "operationId": details.get("operationId", ""),
                "tags": details.get("tags", []),
                "produces": ["application/json"],
                "responses": {}
            }
            
            # 转换参数
            if "parameters" in details:
                operation["parameters"] = details["parameters"]
            
            # 转换请求体为参数
            if "requestBody" in details:
                content = details["requestBody"].get("content", {})
                if "application/json" in content:
                    schema_ref = content["application/json"].get("schema", {})
                    operation["parameters"] = operation.get("parameters", [])
                    operation["parameters"].append({
                        "in": "body",
                        "name": "body",
                        "required": details["requestBody"].get("required", False),
                        "schema": schema_ref
                    })
            
            # 转换响应
            for status_code, response in details.get("responses", {}).items():
                swagger_response = {
                    "description": response.get("description", "")
                }
                content = response.get("content", {})
                if "application/json" in content:
                    swagger_response["schema"] = content["application/json"].get("schema", {})
                operation["responses"][status_code] = swagger_response
            
            swagger["paths"][path][method] = operation
    
    # 转换组件/定义
    components = openapi_spec.get("components", {})
    if "schemas" in components:
        swagger["definitions"] = components["schemas"]
    
    return swagger


def export_swagger_json(openapi_spec: dict, output_dir: Path):
    """导出 Swagger 2.0 JSON 格式"""
    swagger_spec = convert_to_swagger_2(openapi_spec)
    output_file = output_dir / "swagger.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(swagger_spec, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Swagger 2.0 JSON 已导出: {output_file}")


def convert_to_postman_collection(openapi_spec: dict) -> dict:
    """将 OpenAPI 规范转换为 Postman Collection v2.1 格式"""
    collection = {
        "info": {
            "name": openapi_spec["info"]["title"],
            "description": openapi_spec["info"].get("description", ""),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "_postman_id": "coze2jianying-api-collection",
            "version": openapi_spec["info"]["version"]
        },
        "item": [],
        "variable": [
            {
                "key": "baseUrl",
                "value": "http://localhost:8000",
                "type": "string"
            }
        ]
    }
    
    # 按标签组织请求
    tag_items = {}
    
    for path, methods in openapi_spec.get("paths", {}).items():
        for method, details in methods.items():
            # 创建 Postman 请求项
            request_item = {
                "name": details.get("summary", path),
                "request": {
                    "method": method.upper(),
                    "header": [
                        {
                            "key": "Content-Type",
                            "value": "application/json",
                            "type": "text"
                        }
                    ],
                    "url": {
                        "raw": "{{baseUrl}}" + path,
                        "host": ["{{baseUrl}}"],
                        "path": path.strip("/").split("/")
                    },
                    "description": details.get("description", "")
                }
            }
            
            # 添加路径参数
            if "parameters" in details:
                path_params = [p for p in details["parameters"] if p.get("in") == "path"]
                if path_params:
                    request_item["request"]["url"]["variable"] = [
                        {
                            "key": param["name"],
                            "value": "",
                            "description": param.get("description", "")
                        }
                        for param in path_params
                    ]
            
            # 添加请求体示例
            if "requestBody" in details:
                content = details["requestBody"].get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    # 生成示例数据
                    example_body = generate_example_from_schema(schema, openapi_spec.get("components", {}))
                    request_item["request"]["body"] = {
                        "mode": "raw",
                        "raw": json.dumps(example_body, indent=2, ensure_ascii=False),
                        "options": {
                            "raw": {
                                "language": "json"
                            }
                        }
                    }
            
            # 按标签分组
            tags = details.get("tags", ["未分类"])
            tag = tags[0] if tags else "未分类"
            
            if tag not in tag_items:
                tag_items[tag] = {
                    "name": tag,
                    "item": []
                }
            
            tag_items[tag]["item"].append(request_item)
    
    # 添加所有分组到集合
    collection["item"] = list(tag_items.values())
    
    return collection


def generate_example_from_schema(schema: dict, components: dict) -> dict:
    """从 JSON Schema 生成示例数据"""
    # 处理引用
    if "$ref" in schema:
        ref_path = schema["$ref"].split("/")
        if ref_path[0] == "#" and ref_path[1] == "components":
            ref_schema = components
            for key in ref_path[2:]:
                ref_schema = ref_schema.get(key, {})
            return generate_example_from_schema(ref_schema, components)
    
    # 处理不同类型
    schema_type = schema.get("type", "object")
    
    if schema_type == "object":
        example = {}
        properties = schema.get("properties", {})
        for prop_name, prop_schema in properties.items():
            example[prop_name] = generate_example_from_schema(prop_schema, components)
        return example
    
    elif schema_type == "array":
        items_schema = schema.get("items", {})
        return [generate_example_from_schema(items_schema, components)]
    
    elif schema_type == "string":
        return schema.get("example", "string")
    
    elif schema_type == "integer":
        return schema.get("example", 0)
    
    elif schema_type == "number":
        return schema.get("example", 0.0)
    
    elif schema_type == "boolean":
        return schema.get("example", False)
    
    else:
        return None


def export_postman_collection(openapi_spec: dict, output_dir: Path):
    """导出 Postman Collection v2.1 格式"""
    collection = convert_to_postman_collection(openapi_spec)
    output_file = output_dir / "postman_collection.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Postman Collection v2.1 已导出: {output_file}")


def create_readme(output_dir: Path):
    """创建说明文档"""
    readme_content = """# API 规范文件说明

本目录包含 Coze2JianYing API 的各种规范文件，用于集成和测试。

## 📁 文件说明

### 1. OpenAPI 规范

#### `openapi.json`
- **格式**: OpenAPI 3.1.0 (JSON)
- **用途**: 
  - 在 Coze 平台创建"基于已有服务"的云侧插件
  - 生成客户端 SDK
  - API 文档生成
- **导入方式**: 
  - Coze 插件配置页面 → "导入 OpenAPI 规范" → 上传此文件

#### `openapi.yaml`
- **格式**: OpenAPI 3.1.0 (YAML)
- **用途**: 与 JSON 格式相同，但更易读
- **注意**: 需要安装 PyYAML: `pip install pyyaml`

### 2. Swagger 规范

#### `swagger.json`
- **格式**: Swagger 2.0 (JSON)
- **用途**: 
  - 兼容旧版 Swagger 工具
  - 某些 API 网关要求 Swagger 2.0 格式
- **注意**: 这是从 OpenAPI 3.x 简化转换的，可能不包含所有高级特性

### 3. Postman 集合

#### `postman_collection.json`
- **格式**: Postman Collection v2.1
- **用途**:
  - 导入 Postman 进行 API 测试
  - 生成自动化测试脚本
  - 团队协作和 API 共享
- **导入方式**:
  1. 打开 Postman
  2. 点击 "Import" 按钮
  3. 选择此文件导入

## 🚀 在 Coze 中使用

### 步骤 1: 启动 API 服务

```bash
# 本地启动
python start_api.py

# 或使用 uvicorn
uvicorn app.api_main:app --host 0.0.0.0 --port 8000
```

### 步骤 2: 配置内网穿透（本地部署需要）

```bash
# 使用 ngrok
ngrok http 8000

# 记录 ngrok 提供的公网 URL
# 例如: https://abc123.ngrok.io
```

### 步骤 3: 在 Coze 创建插件

1. 登录 [Coze 平台](https://www.coze.cn/)
2. 进入"扣子空间" → "资源库"
3. 点击 "创建插件" → 选择"云侧插件 - 基于已有服务创建"
4. 上传 `openapi.json` 文件
5. 修改 Base URL 为你的服务地址（ngrok URL 或云服务器地址）
6. 测试工具函数
7. 发布插件

### 详细指南

查看完整的集成指南：
- [Coze 集成指南](../docs/guides/COZE_INTEGRATION_GUIDE.md)
- [API 使用示例](../docs/API_USAGE_EXAMPLES.md)

## 🔧 重新生成规范文件

当 API 接口有更新时，运行以下命令重新生成：

```bash
python scripts/export_api_specs.py
```

## ⚙️ 自定义配置

### 修改 Base URL

生成的规范文件中的 Base URL 默认为 `localhost:8000`，部署到生产环境时需要修改：

**OpenAPI/Swagger**:
```json
{{
  "servers": [
    {{
      "url": "https://your-domain.com",
      "description": "生产环境"
    }}
  ]
}}
```

**Postman Collection**:
```json
{{
  "variable": [
    {{
      "key": "baseUrl",
      "value": "https://your-domain.com"
    }}
  ]
}}
```

### 添加认证

如果 API 需要认证，在 Coze 插件配置中添加：

1. 选择认证方式（Bearer Token、API Key 等）
2. 配置认证参数
3. 测试认证是否生效

## 📚 相关资源

- [OpenAPI 规范文档](https://swagger.io/specification/)
- [Postman 文档](https://learning.postman.com/)
- [Coze 开发者文档](https://www.coze.cn/open/docs/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

## 🆘 常见问题

### Q: OpenAPI 文件导入 Coze 后无法识别？

A: 确保：
1. 文件格式正确（valid JSON/YAML）
2. OpenAPI 版本为 3.0.0 或以上
3. 所有必需字段都已填写

### Q: Postman 导入后请求失败？

A: 检查：
1. Base URL 是否正确
2. API 服务是否正在运行
3. 如使用 ngrok，URL 是否已过期

### Q: 如何添加自定义请求头？

A: 在 Postman 中：
1. 选择请求
2. 切换到 "Headers" 标签
3. 添加自定义头部

在 Coze 中：
- 通过插件配置的"认证"部分添加

## 📝 版本信息

- 生成时间: {generation_time}
- API 版本: {api_version}
- OpenAPI 版本: 3.1.0
- Swagger 版本: 2.0
- Postman Collection 版本: 2.1.0
"""
    
    from datetime import datetime
    readme_content = readme_content.format(
        generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        api_version=app.version
    )
    
    readme_file = output_dir / "README.md"
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"✅ README 文档已创建: {readme_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("Coze2JianYing API 规范导出工具")
    print("=" * 60)
    print()
    
    # 创建输出目录
    output_dir = project_root / "api_specs"
    output_dir.mkdir(exist_ok=True)
    print(f"📁 输出目录: {output_dir}")
    print()
    
    # 导出 OpenAPI JSON
    openapi_spec = export_openapi_json(output_dir)
    
    # 导出 OpenAPI YAML
    export_openapi_yaml(openapi_spec, output_dir)
    
    # 导出 Swagger 2.0
    export_swagger_json(openapi_spec, output_dir)
    
    # 导出 Postman Collection
    export_postman_collection(openapi_spec, output_dir)
    
    # 创建 README
    create_readme(output_dir)
    
    print()
    print("=" * 60)
    print("✨ 所有规范文件导出完成！")
    print("=" * 60)
    print()
    print("📂 生成的文件：")
    print(f"   • {output_dir}/openapi.json")
    print(f"   • {output_dir}/openapi.yaml")
    print(f"   • {output_dir}/swagger.json")
    print(f"   • {output_dir}/postman_collection.json")
    print(f"   • {output_dir}/README.md")
    print()
    print("📖 使用指南：")
    print(f"   查看 {output_dir}/README.md 了解详细使用方法")
    print()
    print("🔗 下一步：")
    print("   1. 如果本地部署，启动 API 服务: python start_api.py")
    print("   2. 配置内网穿透: ngrok http 8000")
    print("   3. 在 Coze 上传 openapi.json 创建插件")
    print("   4. 查看完整指南: docs/guides/COZE_INTEGRATION_GUIDE.md")


if __name__ == "__main__":
    main()
