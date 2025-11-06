"""
示例 API 路由
演示 FastAPI 的各种通讯方法和功能
"""
from fastapi import APIRouter, HTTPException, Query, Path, Body, File, UploadFile, Header, Cookie, Form, status
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from typing import Optional, List
from datetime import datetime
import io

from app.schemas.example_schemas import (
    ItemCreate, ItemUpdate, ItemResponse, MessageResponse,
    HealthResponse, FileUploadResponse, QueryParams,
    BatchItemsCreate, BatchItemsResponse
)

router = APIRouter(prefix="/api/example", tags=["示例接口"])

# 模拟数据存储
fake_db: List[dict] = []
next_id = 1


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health_check():
    """
    简单的健康检查接口
    - GET 方法
    - 无参数
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@router.get("/items", response_model=List[ItemResponse], summary="获取Items列表")
async def get_items(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否激活")
):
    """
    获取 Items 列表
    - GET 方法
    - Query 参数：分页、搜索、过滤
    """
    items = fake_db.copy()
    
    # 过滤
    if search:
        items = [item for item in items if search.lower() in item["name"].lower()]
    if is_active is not None:
        items = [item for item in items if item["is_active"] == is_active]
    
    # 分页
    return items[skip:skip + limit]


@router.get("/items/{item_id}", response_model=ItemResponse, summary="获取单个Item")
async def get_item(
    item_id: int = Path(..., ge=1, description="Item ID")
):
    """
    获取单个 Item
    - GET 方法
    - Path 参数
    """
    for item in fake_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="创建Item")
async def create_item(item: ItemCreate):
    """
    创建新的 Item
    - POST 方法
    - JSON Body
    """
    global next_id
    new_item = {
        "id": next_id,
        "created_at": datetime.now(),
        **item.model_dump()
    }
    fake_db.append(new_item)
    next_id += 1
    return new_item


@router.post("/items/batch", response_model=BatchItemsResponse, summary="批量创建Items")
async def create_items_batch(batch: BatchItemsCreate):
    """
    批量创建 Items
    - POST 方法
    - 嵌套 JSON 数据
    """
    global next_id
    created_items = []
    
    for item_data in batch.items:
        new_item = {
            "id": next_id,
            "created_at": datetime.now(),
            **item_data.model_dump()
        }
        fake_db.append(new_item)
        created_items.append(new_item)
        next_id += 1
    
    return BatchItemsResponse(
        created_count=len(created_items),
        items=created_items
    )


@router.put("/items/{item_id}", response_model=ItemResponse, summary="完整更新Item")
async def update_item_put(
    item_id: int = Path(..., ge=1, description="Item ID"),
    item: ItemCreate = Body(...)
):
    """
    完整更新 Item (PUT)
    - PUT 方法
    - 需要提供完整数据
    """
    for idx, db_item in enumerate(fake_db):
        if db_item["id"] == item_id:
            updated_item = {
                "id": item_id,
                "created_at": db_item["created_at"],
                **item.model_dump()
            }
            fake_db[idx] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")


@router.patch("/items/{item_id}", response_model=ItemResponse, summary="部分更新Item")
async def update_item_patch(
    item_id: int = Path(..., ge=1, description="Item ID"),
    item: ItemUpdate = Body(...)
):
    """
    部分更新 Item (PATCH)
    - PATCH 方法
    - 只更新提供的字段
    """
    for idx, db_item in enumerate(fake_db):
        if db_item["id"] == item_id:
            update_data = item.model_dump(exclude_unset=True)
            updated_item = {**db_item, **update_data}
            fake_db[idx] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/items/{item_id}", response_model=MessageResponse, summary="删除Item")
async def delete_item(
    item_id: int = Path(..., ge=1, description="Item ID")
):
    """
    删除 Item
    - DELETE 方法
    """
    for idx, db_item in enumerate(fake_db):
        if db_item["id"] == item_id:
            fake_db.pop(idx)
            return MessageResponse(message=f"Item {item_id} deleted successfully")
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/upload", response_model=FileUploadResponse, summary="文件上传")
async def upload_file(
    file: UploadFile = File(..., description="上传的文件")
):
    """
    文件上传
    - POST 方法
    - multipart/form-data
    """
    contents = await file.read()
    return FileUploadResponse(
        filename=file.filename,
        size=len(contents),
        content_type=file.content_type,
        message="File uploaded successfully"
    )


@router.post("/form", response_model=MessageResponse, summary="表单数据提交")
async def submit_form(
    name: str = Form(..., description="姓名"),
    email: str = Form(..., description="邮箱"),
    age: int = Form(..., ge=0, le=150, description="年龄"),
    message: Optional[str] = Form(None, description="留言")
):
    """
    表单数据提交
    - POST 方法
    - application/x-www-form-urlencoded
    """
    return MessageResponse(
        message=f"Form received: {name}, {email}, age {age}"
    )


@router.get("/headers", response_model=dict, summary="获取请求头")
async def read_headers(
    user_agent: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None),
    custom_header: Optional[str] = Header(None, alias="X-Custom-Header")
):
    """
    读取请求头
    - GET 方法
    - Header 参数
    """
    return {
        "user_agent": user_agent,
        "accept_language": accept_language,
        "custom_header": custom_header
    }


@router.get("/cookies", response_model=dict, summary="获取Cookies")
async def read_cookies(
    session_id: Optional[str] = Cookie(None),
    user_id: Optional[str] = Cookie(None)
):
    """
    读取 Cookies
    - GET 方法
    - Cookie 参数
    """
    return {
        "session_id": session_id,
        "user_id": user_id
    }


@router.get("/download", summary="文件下载")
async def download_file():
    """
    文件下载
    - GET 方法
    - 返回文件流
    """
    content = "This is a sample text file content.\n这是示例文本文件内容。"
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=sample.txt"}
    )


@router.get("/stream", summary="流式响应")
async def stream_data():
    """
    流式数据响应
    - GET 方法
    - 流式传输
    """
    async def generate():
        for i in range(10):
            yield f"data: Message {i}\n\n".encode()
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/error/400", summary="模拟400错误")
async def error_400():
    """模拟 400 Bad Request 错误"""
    raise HTTPException(status_code=400, detail="This is a simulated bad request error")


@router.get("/error/404", summary="模拟404错误")
async def error_404():
    """模拟 404 Not Found 错误"""
    raise HTTPException(status_code=404, detail="Resource not found")


@router.get("/error/500", summary="模拟500错误")
async def error_500():
    """模拟 500 Internal Server Error"""
    raise HTTPException(status_code=500, detail="This is a simulated server error")


@router.post("/mixed", response_model=MessageResponse, summary="混合参数")
async def mixed_params(
    item_id: int = Path(..., ge=1, description="Path参数"),
    name: str = Query(..., description="Query参数"),
    item: ItemCreate = Body(..., description="Body参数"),
    x_token: Optional[str] = Header(None, description="Header参数")
):
    """
    混合使用多种参数类型
    - POST 方法
    - Path + Query + Body + Header
    """
    return MessageResponse(
        message=f"Received: id={item_id}, name={name}, item={item.name}, token={x_token}"
    )
