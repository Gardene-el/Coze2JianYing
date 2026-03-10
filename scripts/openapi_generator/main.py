#!/usr/bin/env python3
"""
生成包含 basic.py 和 easy.py 路由的 Coze 兼容 OpenAPI 文件。

核心策略：
1) 从 FastAPI app.openapi() 获取标准 schema（避免手写字段漂移）
2) 保留 app.backend.api.basic.router 和 app.backend.api.easy.router 中声明的路径
3) 仅保留被这些路径实际引用的 components/schemas
4) 转换到 OpenAPI 3.0.1 友好格式（移除 title，处理 null/anyOf，简化 allOf+nullable）
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import re
import sys
from copy import deepcopy
from typing import Any

import yaml
from fastapi.routing import APIRoute


CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.backend.api.basic import router as basic_router  # noqa: E402
from app.backend.api.easy import router as easy_router  # noqa: E402
from app.backend.api_main import app  # noqa: E402
import app.backend.core.common_types as _common_types  # noqa: E402
from pydantic import BaseModel  # noqa: E402


REF_PATTERN = re.compile(r"^#/components/schemas/(?P<name>[A-Za-z0-9_\-.]+)$")


def build_route_operation_id_map() -> dict[tuple[str, str], str]:
    """构建 (path, method) 到 endpoint 函数名的映射（包含 basic + easy）。"""
    mapping: dict[tuple[str, str], str] = {}
    for router in (basic_router, easy_router):
        for route in router.routes:
            if not isinstance(route, APIRoute):
                continue
            endpoint_name = route.endpoint.__name__
            for method in route.methods:
                mapping[(route.path, method.lower())] = endpoint_name
    return mapping


def convert_schema_to_openapi_3_0(schema: Any) -> Any:
    """将 OpenAPI 3.1 风格 schema 转为更保守的 3.0.1 兼容格式。"""
    if isinstance(schema, dict):
        if schema.get("type") == "null":
            return {"nullable": True}

        if "anyOf" in schema and isinstance(schema["anyOf"], list):
            any_of_list = schema["anyOf"]
            non_null_candidates = []
            has_null = False
            for item in any_of_list:
                if isinstance(item, dict) and item.get("type") == "null":
                    has_null = True
                else:
                    non_null_candidates.append(item)

            if has_null and len(non_null_candidates) == 1:
                converted = convert_schema_to_openapi_3_0(non_null_candidates[0])
                if isinstance(converted, dict):
                    converted["nullable"] = True
                    for key, value in schema.items():
                        if key in {"anyOf", "title"}:
                            continue
                        if key not in converted:
                            converted[key] = convert_schema_to_openapi_3_0(value)
                return converted

        converted: dict[str, Any] = {}
        for key, value in schema.items():
            if key == "title":
                continue

            if key == "exclusiveMinimum" and isinstance(value, (int, float)):
                converted["minimum"] = value
                converted["exclusiveMinimum"] = True
                continue

            if key == "exclusiveMaximum" and isinstance(value, (int, float)):
                converted["maximum"] = value
                converted["exclusiveMaximum"] = True
                continue

            converted[key] = convert_schema_to_openapi_3_0(value)

        if (
            converted.get("nullable") is True
            and isinstance(converted.get("allOf"), list)
            and len(converted["allOf"]) == 1
            and isinstance(converted["allOf"][0], dict)
            and "$ref" in converted["allOf"][0]
        ):
            return {"$ref": converted["allOf"][0]["$ref"]}

        return converted

    if isinstance(schema, list):
        return [convert_schema_to_openapi_3_0(item) for item in schema]

    return schema


def collect_schema_refs(obj: Any, refs: set[str] | None = None) -> set[str]:
    """递归收集对象中的 #/components/schemas/* 引用。"""
    if refs is None:
        refs = set()

    if isinstance(obj, dict):
        ref_value = obj.get("$ref")
        if isinstance(ref_value, str):
            match = REF_PATTERN.match(ref_value)
            if match:
                refs.add(match.group("name"))
        for value in obj.values():
            collect_schema_refs(value, refs)
    elif isinstance(obj, list):
        for item in obj:
            collect_schema_refs(item, refs)

    return refs


def build_selected_paths(full_schema: dict[str, Any]) -> dict[str, Any]:
    """保留 basic_router 和 easy_router 中声明的所有路径，basic 在前、easy 在后。"""
    route_operation_id_map = build_route_operation_id_map()
    used_operation_ids: set[str] = set()
    all_path_items = full_schema.get("paths", {})

    # 按 basic → easy 的路由声明顺序收集路径（保持各 router 内部顺序）
    ordered_paths: list[str] = []
    for router in (basic_router, easy_router):
        for route in router.routes:
            if isinstance(route, APIRoute) and route.path not in ordered_paths:
                ordered_paths.append(route.path)

    selected_paths: dict[str, Any] = {}
    for path in ordered_paths:
        path_item = all_path_items.get(path)
        if path_item is None:
            continue

        path_item_copy = deepcopy(path_item)
        for method, operation in list(path_item_copy.items()):
            if not isinstance(operation, dict):
                continue

            normalized = route_operation_id_map[(path, method.lower())]

            if normalized in used_operation_ids:
                idx = 2
                candidate = f"{normalized}_{idx}"
                while candidate in used_operation_ids:
                    idx += 1
                    candidate = f"{normalized}_{idx}"
                normalized = candidate

            operation["operationId"] = normalized
            used_operation_ids.add(normalized)

            responses = operation.get("responses")
            if isinstance(responses, dict) and "422" in responses:
                responses.pop("422", None)

        selected_paths[path] = path_item_copy

    return selected_paths


def normalize_schema_name(name: str) -> str:
    """规范化 schema 名称，移除 FastAPI 自动生成的冗余后缀。"""
    return name


def normalize_schemas_and_refs(spec: dict[str, Any]) -> dict[str, Any]:
    """规范化所有 schema 名称并更新引用。"""
    schemas = spec.get("components", {}).get("schemas", {})
    if not schemas:
        return spec
    
    # 建立旧名称到新名称的映射
    name_mapping: dict[str, str] = {}
    for old_name in schemas:
        new_name = normalize_schema_name(old_name)
        if new_name != old_name:
            name_mapping[old_name] = new_name
    
    if not name_mapping:
        return spec
    
    # 更新 schemas 中的名称
    new_schemas: dict[str, Any] = {}
    for old_name, schema in schemas.items():
        new_name = name_mapping.get(old_name, old_name)
        new_schemas[new_name] = schema
    
    spec = deepcopy(spec)
    spec["components"]["schemas"] = new_schemas
    
    # 递归更新所有 $ref 引用
    def update_refs(obj: Any) -> Any:
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                if ref.startswith("#/components/schemas/"):
                    old_name = ref[len("#/components/schemas/"):]
                    if old_name in name_mapping:
                        obj["$ref"] = f"#/components/schemas/{name_mapping[old_name]}"
            return {k: update_refs(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [update_refs(item) for item in obj]
        return obj
    
    return update_refs(spec)


def get_dynamic_endpoint_groups() -> list[str]:
    """从 basic_router 和 easy_router 中动态获取 endpoint 顺序。"""
    endpoint_groups = []
    for router in (basic_router, easy_router):
        for route in router.routes:
            if isinstance(route, APIRoute):
                func_name = route.endpoint.__name__
                words = func_name.split('_')
                schema_prefix = ''.join(word.capitalize() for word in words)
                if schema_prefix not in endpoint_groups:
                    endpoint_groups.append(schema_prefix)
    return endpoint_groups


def reorder_schemas(schemas: dict[str, Any]) -> dict[str, Any]:
    """重排序 schemas：通用类在前，相关 Request/Response 连续。"""
    if not schemas:
        return schemas

    # 动态扫描 common_types 中定义的所有 BaseModel 子类，按源码定义顺序排列
    common_schemas = [
        name
        for name, cls in sorted(
            (
                (n, c)
                for n, c in inspect.getmembers(_common_types, inspect.isclass)
                if issubclass(c, BaseModel)
                and c is not BaseModel
                and inspect.getmodule(c) is _common_types
            ),
            key=lambda nc: inspect.getsourcelines(nc[1])[1],
        )
    ]
    
    # 动态获取 endpoint 分组（基于 basic.py 中的路由顺序）
    endpoint_groups = get_dynamic_endpoint_groups()

    ordered_schemas: dict[str, Any] = {}
    
    # 1. 添加通用 schemas
    for name in common_schemas:
        if name in schemas:
            ordered_schemas[name] = schemas[name]
    
    # 2. 按组添加 Request/Response/Body triplets
    for group in endpoint_groups:
        # 先添加 Request, Response, 然后 Body
        for suffix in ["Request", "Response", "Body"]:
            full_name = f"{group}{suffix}"
            if full_name in schemas:
                ordered_schemas[full_name] = schemas[full_name]
    
    # 3. 添加剩余的未分类 schemas
    for name, schema in schemas.items():
        if name not in ordered_schemas:
            ordered_schemas[name] = schema
    
    return ordered_schemas


def build_min_components(selected_paths: dict[str, Any], all_components: dict[str, Any]) -> dict[str, Any]:
    """根据选中路径裁剪 components/schemas。"""
    all_schemas = all_components.get("schemas", {}) if isinstance(all_components, dict) else {}
    needed = collect_schema_refs(selected_paths)

    resolved: dict[str, Any] = {}
    queue = list(needed)

    while queue:
        name = queue.pop()
        if name in resolved:
            continue
        schema = all_schemas.get(name)
        if schema is None:
            continue

        schema_copy = deepcopy(schema)
        resolved[name] = schema_copy

        nested_refs = collect_schema_refs(schema_copy)
        for nested_name in nested_refs:
            if nested_name not in resolved:
                queue.append(nested_name)

    # 重排序 schemas
    ordered_schemas = reorder_schemas(resolved)
    return {"schemas": ordered_schemas} if ordered_schemas else {}


def create_spec(server_url: str, title: str, version: str, description: str) -> dict[str, Any]:
    """创建最终 OpenAPI 文档。"""
    full_schema = app.openapi()
    selected_paths = build_selected_paths(full_schema)
    min_components = build_min_components(selected_paths, full_schema.get("components", {}))

    converted_paths = convert_schema_to_openapi_3_0(selected_paths)
    converted_components = convert_schema_to_openapi_3_0(min_components)

    spec: dict[str, Any] = {
        "openapi": "3.0.1",
        "info": {
            "title": title,
            "version": version,
            "description": description,
        },
        "paths": converted_paths,
        "servers": [{"url": server_url}],
    }

    if converted_components:
        spec["components"] = converted_components

    # 规范化 schema 名称和引用
    spec = normalize_schemas_and_refs(spec)

    return spec


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 basic + easy 路由的 Coze 兼容 OpenAPI")
    parser.add_argument(
        "--server-url",
        default=os.getenv("OPENAPI_SERVER_URL", "https://api.garden-eel.com/coze2jianying"),
        help="OpenAPI servers[0].url",
    )
    parser.add_argument(
        "--title",
        default="Coze2JianYing API",
        help="OpenAPI info.title",
    )
    parser.add_argument(
        "--version",
        default="v1",
        help="OpenAPI info.version",
    )
    parser.add_argument(
        "--description",
        default="包含 basic 和 easy 全量端点，用于 Coze OpenAPI 接入。",
        help="OpenAPI info.description",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(PROJECT_ROOT, "openapi.generated.yaml"),
        help="输出文件路径",
    )
    parser.add_argument(
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="输出格式",
    )

    args = parser.parse_args()

    spec = create_spec(
        server_url=args.server_url,
        title=args.title,
        version=args.version,
        description=args.description,
    )

    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if args.format == "yaml":
        class NoAliasDumper(yaml.SafeDumper):
            def ignore_aliases(self, data: Any) -> bool:  # type: ignore[override]
                return True

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(
                spec,
                f,
                Dumper=NoAliasDumper,
                allow_unicode=True,
                sort_keys=False,
                default_flow_style=False,
                indent=2,
            )
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)

    basic_path_count = len(spec.get("paths", {}))
    component_count = len(spec.get("components", {}).get("schemas", {}))
    print(f"✅ OpenAPI 已生成: {output_path}")
    print(f"📌 路径数量 (basic + easy): {basic_path_count}")
    print(f"📦 引用 schema 数量: {component_count}")


if __name__ == "__main__":
    main()
