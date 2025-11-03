"""
快速测试 FastAPI 接口是否正常工作
"""
import requests
import time

BASE_URL = "http://127.0.0.1:8080"

def test_basic():
    """基础测试"""
    print("=" * 60)
    print("FastAPI 接口快速测试")
    print("=" * 60)
    
    # 等待服务启动
    print("\n⏳ 等待服务启动...")
    time.sleep(2)
    
    try:
        # 测试1: 根路径
        print("\n1️⃣ 测试根路径...")
        response = requests.get(f"{BASE_URL}/")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        # 测试2: 健康检查
        print("\n2️⃣ 测试健康检查...")
        response = requests.get(f"{BASE_URL}/api/example/health")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        
        # 测试3: 创建 Item
        print("\n3️⃣ 测试创建 Item...")
        data = {"name": "测试项目", "price": 99.99}
        response = requests.post(f"{BASE_URL}/api/example/items", json=data)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        item_id = response.json().get("id")
        
        # 测试4: 获取 Items 列表
        print("\n4️⃣ 测试获取列表...")
        response = requests.get(f"{BASE_URL}/api/example/items")
        print(f"   状态码: {response.status_code}")
        print(f"   找到 {len(response.json())} 个 items")
        
        # 测试5: 获取单个 Item
        if item_id:
            print(f"\n5️⃣ 测试获取单个 Item (ID: {item_id})...")
            response = requests.get(f"{BASE_URL}/api/example/items/{item_id}")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.json()}")
        
        print("\n" + "=" * 60)
        print("✅ 基础测试全部通过！")
        print("=" * 60)
        print(f"\n🌐 API 文档地址:")
        print(f"   Swagger UI: {BASE_URL}/docs")
        print(f"   ReDoc:      {BASE_URL}/redoc")
        print("\n💡 运行完整测试:")
        print("   python test_api_examples.py")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器！")
        print("请确保服务正在运行:")
        print(f"  uvicorn app.api_main:app --reload --port 8080")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

if __name__ == "__main__":
    test_basic()
