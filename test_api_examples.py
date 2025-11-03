"""
FastAPI 示例接口测试脚本
测试所有 API 端点的功能
"""
import requests
import json
import time
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"

def print_response(title: str, response: requests.Response):
    """格式化打印响应"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    try:
        print(f"响应体:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"响应体 (非JSON):\n{response.text[:500]}")
    print(f"{'='*60}\n")


def test_root():
    """测试根路径"""
    response = requests.get(f"{BASE_URL}/")
    print_response("根路径", response)
    return response.status_code == 200


def test_health():
    """测试健康检查"""
    response = requests.get(f"{BASE_URL}/api/example/health")
    print_response("健康检查", response)
    return response.status_code == 200


def test_create_item():
    """测试创建 Item"""
    data = {
        "name": "Python测试项目",
        "description": "使用requests库创建的测试项目",
        "price": 123.45,
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/api/example/items", json=data)
    print_response("创建Item", response)
    
    if response.status_code == 201:
        return response.json()["id"]
    return None


def test_get_items():
    """测试获取 Item 列表"""
    # 无参数
    response = requests.get(f"{BASE_URL}/api/example/items")
    print_response("获取Items列表（无参数）", response)
    
    # 带分页参数
    params = {"skip": 0, "limit": 5}
    response = requests.get(f"{BASE_URL}/api/example/items", params=params)
    print_response("获取Items列表（带分页）", response)
    
    # 带搜索参数
    params = {"search": "测试", "is_active": True}
    response = requests.get(f"{BASE_URL}/api/example/items", params=params)
    print_response("获取Items列表（带搜索）", response)
    
    return response.status_code == 200


def test_get_item(item_id: int):
    """测试获取单个 Item"""
    response = requests.get(f"{BASE_URL}/api/example/items/{item_id}")
    print_response(f"获取Item {item_id}", response)
    return response.status_code == 200


def test_update_item_patch(item_id: int):
    """测试部分更新 Item (PATCH)"""
    data = {"price": 999.99, "description": "已通过PATCH更新"}
    response = requests.patch(f"{BASE_URL}/api/example/items/{item_id}", json=data)
    print_response(f"部分更新Item {item_id} (PATCH)", response)
    return response.status_code == 200


def test_update_item_put(item_id: int):
    """测试完整更新 Item (PUT)"""
    data = {
        "name": "完全更新的项目",
        "description": "通过PUT完整更新",
        "price": 888.88,
        "is_active": False
    }
    response = requests.put(f"{BASE_URL}/api/example/items/{item_id}", json=data)
    print_response(f"完整更新Item {item_id} (PUT)", response)
    return response.status_code == 200


def test_batch_create():
    """测试批量创建"""
    data = {
        "items": [
            {"name": "批量项目1", "description": "第一个", "price": 10.0, "is_active": True},
            {"name": "批量项目2", "description": "第二个", "price": 20.0, "is_active": True},
            {"name": "批量项目3", "description": "第三个", "price": 30.0, "is_active": False}
        ]
    }
    response = requests.post(f"{BASE_URL}/api/example/items/batch", json=data)
    print_response("批量创建Items", response)
    return response.status_code == 200


def test_upload_file():
    """测试文件上传"""
    # 创建一个内存中的文件
    files = {
        "file": ("test_upload.txt", "这是测试上传的文件内容\nLine 2\nLine 3", "text/plain")
    }
    response = requests.post(f"{BASE_URL}/api/example/upload", files=files)
    print_response("文件上传", response)
    return response.status_code == 200


def test_form_submit():
    """测试表单提交"""
    data = {
        "name": "张三",
        "email": "zhangsan@example.com",
        "age": 25,
        "message": "这是一条测试留言"
    }
    response = requests.post(f"{BASE_URL}/api/example/form", data=data)
    print_response("表单提交", response)
    return response.status_code == 200


def test_custom_headers():
    """测试自定义请求头"""
    headers = {
        "X-Custom-Header": "my-custom-value",
        "User-Agent": "PythonTestClient/1.0",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    response = requests.get(f"{BASE_URL}/api/example/headers", headers=headers)
    print_response("自定义请求头", response)
    return response.status_code == 200


def test_cookies():
    """测试 Cookies"""
    cookies = {
        "session_id": "abc123xyz789",
        "user_id": "user_456"
    }
    response = requests.get(f"{BASE_URL}/api/example/cookies", cookies=cookies)
    print_response("读取Cookies", response)
    return response.status_code == 200


def test_download():
    """测试文件下载"""
    response = requests.get(f"{BASE_URL}/api/example/download")
    print(f"\n{'='*60}")
    print(f"📋 文件下载")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
    print(f"文件内容:\n{response.text}")
    print(f"{'='*60}\n")
    
    # 保存文件
    with open("downloaded_test.txt", "wb") as f:
        f.write(response.content)
    print("✅ 文件已保存为 downloaded_test.txt\n")
    
    return response.status_code == 200


def test_stream():
    """测试流式响应"""
    response = requests.get(f"{BASE_URL}/api/example/stream", stream=True)
    print(f"\n{'='*60}")
    print(f"📋 流式响应")
    print(f"{'='*60}")
    print(f"状态码: {response.status_code}")
    print(f"流式数据:")
    
    for i, line in enumerate(response.iter_lines()):
        if line:
            print(f"  {line.decode('utf-8')}")
        if i >= 9:  # 只读取前10条
            break
    
    print(f"{'='*60}\n")
    return response.status_code == 200


def test_mixed_params():
    """测试混合参数"""
    item_id = 99
    query_params = {"name": "混合测试"}
    body_data = {
        "name": "混合参数项目",
        "description": "测试多种参数类型",
        "price": 555.55,
        "is_active": True
    }
    headers = {"X-Token": "secret-token-123"}
    
    response = requests.post(
        f"{BASE_URL}/api/example/mixed/{item_id}",
        params=query_params,
        json=body_data,
        headers=headers
    )
    print_response("混合参数测试", response)
    return response.status_code == 200


def test_errors():
    """测试错误处理"""
    # 测试 404
    response = requests.get(f"{BASE_URL}/api/example/error/404")
    print_response("404错误测试", response)
    
    # 测试 400
    response = requests.get(f"{BASE_URL}/api/example/error/400")
    print_response("400错误测试", response)
    
    # 测试 500
    response = requests.get(f"{BASE_URL}/api/example/error/500")
    print_response("500错误测试", response)
    
    # 测试不存在的 Item
    response = requests.get(f"{BASE_URL}/api/example/items/99999")
    print_response("获取不存在的Item", response)
    
    return True


def test_delete_item(item_id: int):
    """测试删除 Item"""
    response = requests.delete(f"{BASE_URL}/api/example/items/{item_id}")
    print_response(f"删除Item {item_id}", response)
    return response.status_code == 200


def main():
    """主测试函数"""
    print("\n" + "🚀" * 30)
    print("FastAPI 接口测试开始")
    print("🚀" * 30 + "\n")
    
    results = []
    
    try:
        # 测试根路径和健康检查
        print("📌 第一部分: 基础接口测试")
        results.append(("根路径", test_root()))
        results.append(("健康检查", test_health()))
        time.sleep(0.5)
        
        # 测试 CRUD 操作
        print("\n📌 第二部分: CRUD 操作测试")
        item_id = test_create_item()
        if item_id:
            results.append(("创建Item", True))
            results.append(("获取Items列表", test_get_items()))
            results.append(("获取单个Item", test_get_item(item_id)))
            results.append(("部分更新Item", test_update_item_patch(item_id)))
            results.append(("完整更新Item", test_update_item_put(item_id)))
        else:
            results.append(("创建Item", False))
        time.sleep(0.5)
        
        # 测试批量操作
        print("\n📌 第三部分: 批量操作测试")
        results.append(("批量创建", test_batch_create()))
        time.sleep(0.5)
        
        # 测试文件和表单
        print("\n📌 第四部分: 文件和表单测试")
        results.append(("文件上传", test_upload_file()))
        results.append(("表单提交", test_form_submit()))
        time.sleep(0.5)
        
        # 测试高级功能
        print("\n📌 第五部分: 高级功能测试")
        results.append(("自定义请求头", test_custom_headers()))
        results.append(("Cookies", test_cookies()))
        results.append(("文件下载", test_download()))
        results.append(("流式响应", test_stream()))
        results.append(("混合参数", test_mixed_params()))
        time.sleep(0.5)
        
        # 测试错误处理
        print("\n📌 第六部分: 错误处理测试")
        results.append(("错误处理", test_errors()))
        time.sleep(0.5)
        
        # 测试删除
        if item_id:
            print("\n📌 第七部分: 删除操作测试")
            results.append(("删除Item", test_delete_item(item_id)))
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器！")
        print("请确保 FastAPI 服务正在运行:")
        print("  python -m app.api_main")
        return
    
    # 打印测试总结
    print("\n" + "📊" * 30)
    print("测试总结")
    print("📊" * 30 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"总计: {passed}/{total} 测试通过")
    print(f"成功率: {passed/total*100:.1f}%")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查日志")


if __name__ == "__main__":
    main()
