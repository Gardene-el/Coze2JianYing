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

from src.backend.api.basic import router as basic_router  # noqa: E402
from src.backend.api.easy import router as easy_router  # noqa: E402
from src.backend.main import gui_app as app  # noqa: E402
import src.backend.core.common_types as _common_types  # noqa: E402
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
            return {"$ref": converted["allOf"][0]["$ref"], "nullable": True}

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


def _get_common_schema_names_ordered() -> list[str]:
    """获取 common_types 中定义的所有 BaseModel 子类名称，按源码定义顺序排列。"""
    return [
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


def reorder_schemas(schemas: dict[str, Any]) -> dict[str, Any]:
    """重排序 schemas：通用类（按源码定义顺序）在前，其余保持原序。"""
    if not schemas:
        return schemas

    ordered_schemas: dict[str, Any] = {}

    # 1. 添加通用 schemas（按源码定义顺序）
    for name in _get_common_schema_names_ordered():
        if name in schemas:
            ordered_schemas[name] = schemas[name]

    # 2. 添加剩余 schemas
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


def inline_endpoint_schemas(spec: dict[str, Any]) -> dict[str, Any]:
    """将 paths 中仅被引用一次的 Request/Response schema 内联展开。

    通用数据结构（common_types 中定义的 BaseModel 子类）保留为 $ref 引用，
    其余 schema（如 XxxRequest / XxxResponse）直接展开到 paths 中，
    随后从 components/schemas 中移除已内联的 schema。
    """
    all_schemas = spec.get("components", {}).get("schemas", {})
    if not all_schemas:
        return spec

    # 收集通用 schema 名称（来自 common_types）
    common_schema_names: set[str] = set(_get_common_schema_names_ordered())

    # 收集所有被通用 schema 内部引用的 schema（递归），这些也应保留
    def collect_transitive_common(names: set[str]) -> set[str]:
        result = set(names)
        queue = list(names)
        while queue:
            name = queue.pop()
            schema = all_schemas.get(name)
            if schema is None:
                continue
            for ref_name in collect_schema_refs(schema):
                if ref_name not in result:
                    result.add(ref_name)
                    queue.append(ref_name)
        return result

    keep_as_ref = collect_transitive_common(common_schema_names)

    inlined_names: set[str] = set()

    def try_inline(obj: Any) -> Any:
        """递归替换 $ref 为内联 schema（仅对非通用 schema）。"""
        if isinstance(obj, dict):
            ref = obj.get("$ref")
            if ref and isinstance(ref, str):
                match = REF_PATTERN.match(ref)
                if match:
                    schema_name = match.group("name")
                    if schema_name not in keep_as_ref and schema_name in all_schemas:
                        inlined_names.add(schema_name)
                        return deepcopy(all_schemas[schema_name])
            return {k: try_inline(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [try_inline(item) for item in obj]
        return obj

    spec = deepcopy(spec)
    spec["paths"] = try_inline(spec["paths"])

    # 从 components/schemas 中移除已内联的 schema
    schemas = spec.get("components", {}).get("schemas", {})
    for name in inlined_names:
        schemas.pop(name, None)

    # 如果 schemas 为空，移除整个 components
    if not schemas:
        spec.pop("components", None)

    return spec


def inline_nullable_refs(spec: dict[str, Any]) -> dict[str, Any]:
    """将所有 nullable $ref 属性展开为内联 schema（去除 required 列表）。

    Coze 客户端在解析 OpenAPI 时，会将被 $ref 引用的 schema 中的 required 字段无条件视为
    必填，而不考虑宿主属性本身是否为 nullable/可选。通过把可选对象展开为内联副本并去掉
    required，可使 Coze 正确推断出这些子字段也是可选的。

    只替换 usage site（属性引用处），components/schemas 中的原始定义不受影响。
    """
    all_schemas = spec.get("components", {}).get("schemas", {})
    if not all_schemas:
        return spec

    def inline_properties(properties: dict[str, Any]) -> None:
        for prop_name, prop_schema in list(properties.items()):
            if not isinstance(prop_schema, dict):
                continue
            ref = prop_schema.get("$ref")
            if ref and prop_schema.get("nullable") is True:
                match = REF_PATTERN.match(ref)
                if match:
                    schema_name = match.group("name")
                    referenced = all_schemas.get(schema_name)
                    if referenced is not None and "required" in referenced:
                        inlined = deepcopy(referenced)
                        inlined.pop("required", None)
                        inlined["nullable"] = True
                        # 保留 property 级别的 description 覆盖
                        if "description" in prop_schema:
                            inlined["description"] = prop_schema["description"]
                        properties[prop_name] = inlined

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "properties" in obj and isinstance(obj["properties"], dict):
                inline_properties(obj["properties"])
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(spec)
    return spec


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

    # 将 nullable $ref 属性展开为内联 schema（消除 Coze 客户端对可选对象子字段的强制必填行为）
    spec = inline_nullable_refs(spec)

    # 将一次性 Request/Response schema 内联到 paths 中，仅保留通用数据结构的 $ref
    spec = inline_endpoint_schemas(spec)

    return spec


def main() -> None:
    parser = argparse.ArgumentParser(description="生成 basic + easy 路由的 Coze 兼容 OpenAPI")
    parser.add_argument(
        "--server-url",
        default=os.getenv("OPENAPI_SERVER_URL", "https://coze2jianying.pages.dev"),
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
