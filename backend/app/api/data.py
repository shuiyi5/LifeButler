"""
数据 CRUD API — 日程/待办/记账/购物/笔记/读书/饮食
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from datetime import datetime, date, timedelta
from typing import Optional
import json
from app.config.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.calendar import CalendarEvent
from app.models.todo import Todo
from app.models.finance import Transaction
from app.models.shopping import ShoppingItem
from app.models.note import Note
from app.models.reading import ReadingPlan
from app.models.health import MealRecord

router = APIRouter()

# ─── 日程 CRUD ─────────────────────────────────────

@router.get("/calendar")
async def list_events(
    start: Optional[str] = None,
    end: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(CalendarEvent).where(CalendarEvent.user_id == user.id)
    if start:
        try:
            s = datetime.strptime(start, "%Y-%m-%d")
            query = query.where(CalendarEvent.start_time >= s)
        except ValueError:
            pass
    if end:
        try:
            e = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)
            query = query.where(CalendarEvent.start_time < e)
        except ValueError:
            pass
    query = query.order_by(CalendarEvent.start_time)
    result = await db.execute(query)
    events = result.scalars().all()
    return [
        {"id": e.id, "title": e.title, "description": e.description or "",
         "start_time": e.start_time.isoformat(), "end_time": e.end_time.isoformat() if e.end_time else None,
         "location": e.location or ""}
        for e in events
    ]


@router.post("/calendar")
async def create_event(
    data: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start = datetime.strptime(data["start_time"], "%Y-%m-%dT%H:%M")
    end = datetime.strptime(data["end_time"], "%Y-%m-%dT%H:%M") if data.get("end_time") else start + timedelta(hours=1)
    event = CalendarEvent(
        user_id=user.id, title=data.get("title", "新日程"),
        description=data.get("description", ""), start_time=start, end_time=end,
        location=data.get("location", ""),
    )
    db.add(event)
    await db.commit()
    return {"id": event.id, "message": "创建成功"}


@router.put("/calendar/{event_id}")
async def update_event(
    event_id: int, data: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CalendarEvent).where(and_(CalendarEvent.id == event_id, CalendarEvent.user_id == user.id)))
    event = result.scalar_one_or_none()
    if not event:
        return {"error": "日程不存在"}
    if "title" in data: event.title = data["title"]
    if "description" in data: event.description = data["description"]
    if "location" in data: event.location = data["location"]
    if "start_time" in data: event.start_time = datetime.strptime(data["start_time"], "%Y-%m-%dT%H:%M")
    if "end_time" in data: event.end_time = datetime.strptime(data["end_time"], "%Y-%m-%dT%H:%M")
    await db.commit()
    return {"message": "更新成功"}


@router.delete("/calendar/{event_id}")
async def delete_event(
    event_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CalendarEvent).where(and_(CalendarEvent.id == event_id, CalendarEvent.user_id == user.id)))
    event = result.scalar_one_or_none()
    if not event:
        return {"error": "日程不存在"}
    await db.delete(event)
    await db.commit()
    return {"message": "删除成功"}

# ─── 待办 CRUD ─────────────────────────────────────

@router.get("/todos")
async def list_todos(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Todo).where(Todo.user_id == user.id)
    if status:
        query = query.where(Todo.status == status)
    if priority:
        query = query.where(Todo.priority == priority)
    query = query.order_by(Todo.created_at.desc())
    result = await db.execute(query)
    todos = result.scalars().all()
    return [
        {"id": t.id, "title": t.title, "description": t.description or "",
         "priority": t.priority, "status": t.status, "category": t.category or "",
         "due_date": t.due_date.isoformat() if t.due_date else None,
         "created_at": t.created_at.isoformat() if t.created_at else None}
        for t in todos
    ]


@router.post("/todos")
async def create_todo(
    data: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    due = None
    if data.get("due_date"):
        try: due = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
        except ValueError: pass
    todo = Todo(
        user_id=user.id, title=data.get("title", "新待办"),
        description=data.get("description", ""),
        priority=data.get("priority", "medium"),
        category=data.get("category", ""), due_date=due,
    )
    db.add(todo)
    await db.commit()
    return {"id": todo.id, "message": "创建成功"}


@router.put("/todos/{todo_id}")
async def update_todo(
    todo_id: int, data: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Todo).where(and_(Todo.id == todo_id, Todo.user_id == user.id)))
    todo = result.scalar_one_or_none()
    if not todo:
        return {"error": "待办不存在"}
    for field in ["title", "description", "priority", "status", "category"]:
        if field in data: setattr(todo, field, data[field])
    if "due_date" in data and data["due_date"]:
        try: todo.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()
        except ValueError: pass
    await db.commit()
    return {"message": "更新成功"}


@router.delete("/todos/{todo_id}")
async def delete_todo(
    todo_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Todo).where(and_(Todo.id == todo_id, Todo.user_id == user.id)))
    todo = result.scalar_one_or_none()
    if not todo:
        return {"error": "待办不存在"}
    await db.delete(todo)
    await db.commit()
    return {"message": "删除成功"}

# ─── 记账 CRUD ─────────────────────────────────────

@router.get("/finance")
async def list_transactions(
    period: str = Query("month"),
    type: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    start_date = today - timedelta(days=7) if period == "week" else today.replace(day=1)
    query = select(Transaction).where(and_(Transaction.user_id == user.id, Transaction.date >= start_date))
    if type:
        query = query.where(Transaction.type == type)
    query = query.order_by(Transaction.date.desc(), Transaction.created_at.desc())
    result = await db.execute(query)
    txns = result.scalars().all()
    return [
        {"id": t.id, "type": t.type, "amount": t.amount, "category": t.category,
         "description": t.description or "", "date": t.date.isoformat()}
        for t in txns
    ]


@router.post("/finance")
async def create_transaction(
    data: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    t_date = date.today()
    if data.get("date"):
        try: t_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError: pass
    txn = Transaction(
        user_id=user.id, type=data.get("type", "expense"),
        amount=data.get("amount", 0), category=data.get("category", "其他"),
        description=data.get("description", ""), date=t_date,
    )
    db.add(txn)
    await db.commit()
    return {"id": txn.id, "message": "创建成功"}


@router.put("/finance/{txn_id}")
async def update_transaction(
    txn_id: int, data: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Transaction).where(and_(Transaction.id == txn_id, Transaction.user_id == user.id)))
    txn = result.scalar_one_or_none()
    if not txn:
        return {"error": "记录不存在"}
    for field in ["type", "amount", "category", "description"]:
        if field in data: setattr(txn, field, data[field])
    if "date" in data:
        try: txn.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError: pass
    await db.commit()
    return {"message": "更新成功"}


@router.delete("/finance/{txn_id}")
async def delete_transaction(
    txn_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Transaction).where(and_(Transaction.id == txn_id, Transaction.user_id == user.id)))
    txn = result.scalar_one_or_none()
    if not txn:
        return {"error": "记录不存在"}
    await db.delete(txn)
    await db.commit()
    return {"message": "删除成功"}

# ─── 购物清单 CRUD ─────────────────────────────────

@router.get("/shopping")
async def list_shopping(
    show_purchased: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(ShoppingItem).where(ShoppingItem.user_id == user.id)
    if not show_purchased:
        query = query.where(ShoppingItem.is_purchased == False)
    query = query.order_by(ShoppingItem.category, ShoppingItem.created_at.desc())
    result = await db.execute(query)
    items = result.scalars().all()
    return [
        {"id": i.id, "name": i.name, "category": i.category, "quantity": i.quantity,
         "unit": i.unit, "is_purchased": i.is_purchased}
        for i in items
    ]

@router.post("/shopping")
async def create_shopping(data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    item = ShoppingItem(user_id=user.id, name=data.get("name", ""), category=data.get("category", "其他"),
                        quantity=data.get("quantity", 1), unit=data.get("unit", "个"))
    db.add(item)
    await db.commit()
    return {"id": item.id, "message": "创建成功"}

@router.put("/shopping/{item_id}")
async def update_shopping(item_id: int, data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShoppingItem).where(and_(ShoppingItem.id == item_id, ShoppingItem.user_id == user.id)))
    item = result.scalar_one_or_none()
    if not item: return {"error": "不存在"}
    for f in ["name", "category", "quantity", "unit", "is_purchased"]:
        if f in data: setattr(item, f, data[f])
    await db.commit()
    return {"message": "更新成功"}

@router.delete("/shopping/{item_id}")
async def delete_shopping(item_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShoppingItem).where(and_(ShoppingItem.id == item_id, ShoppingItem.user_id == user.id)))
    item = result.scalar_one_or_none()
    if not item: return {"error": "不存在"}
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}

@router.delete("/shopping")
async def clear_purchased(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ShoppingItem).where(and_(ShoppingItem.user_id == user.id, ShoppingItem.is_purchased == True)))
    await db.commit()
    return {"message": "已清空已购"}

# ─── 笔记 CRUD ─────────────────────────────────────

@router.get("/notes")
async def list_notes(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.user_id == user.id).order_by(Note.updated_at.desc()).limit(50))
    notes = result.scalars().all()
    return [{"id": n.id, "title": n.title, "content": n.content, "updated_at": n.updated_at.isoformat() if n.updated_at else None} for n in notes]

@router.post("/notes")
async def create_note(data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    note = Note(user_id=user.id, title=data.get("title", "新笔记"), content=data.get("content", ""))
    db.add(note)
    await db.commit()
    return {"id": note.id, "message": "创建成功"}

@router.put("/notes/{note_id}")
async def update_note(note_id: int, data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(and_(Note.id == note_id, Note.user_id == user.id)))
    note = result.scalar_one_or_none()
    if not note: return {"error": "不存在"}
    if "title" in data: note.title = data["title"]
    if "content" in data: note.content = data["content"]
    note.updated_at = datetime.now()
    await db.commit()
    return {"message": "更新成功"}

@router.delete("/notes/{note_id}")
async def delete_note(note_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(and_(Note.id == note_id, Note.user_id == user.id)))
    note = result.scalar_one_or_none()
    if not note: return {"error": "不存在"}
    await db.delete(note)
    await db.commit()
    return {"message": "删除成功"}

# ─── 读书 CRUD ─────────────────────────────────────

@router.get("/reading")
async def list_reading(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReadingPlan).where(ReadingPlan.user_id == user.id).order_by(ReadingPlan.updated_at.desc()))
    plans = result.scalars().all()
    return [{"id": p.id, "book_title": p.book_title, "author": p.author or "", "total_pages": p.total_pages,
             "current_page": p.current_page, "status": p.status, "target_date": p.target_date.isoformat() if p.target_date else None} for p in plans]

@router.post("/reading")
async def create_reading(data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    td = None
    if data.get("target_date"):
        try: td = datetime.strptime(data["target_date"], "%Y-%m-%d").date()
        except ValueError: pass
    plan = ReadingPlan(user_id=user.id, book_title=data.get("book_title", "新书"), author=data.get("author", ""),
                       total_pages=data.get("total_pages", 300), target_date=td)
    db.add(plan)
    await db.commit()
    return {"id": plan.id, "message": "创建成功"}

@router.put("/reading/{plan_id}")
async def update_reading(plan_id: int, data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReadingPlan).where(and_(ReadingPlan.id == plan_id, ReadingPlan.user_id == user.id)))
    plan = result.scalar_one_or_none()
    if not plan: return {"error": "不存在"}
    for f in ["book_title", "author", "total_pages", "current_page", "status", "notes"]:
        if f in data: setattr(plan, f, data[f])
    if "target_date" in data and data["target_date"]:
        try: plan.target_date = datetime.strptime(data["target_date"], "%Y-%m-%d").date()
        except ValueError: pass
    plan.updated_at = datetime.now()
    if plan.current_page >= plan.total_pages: plan.status = "completed"
    await db.commit()
    return {"message": "更新成功"}

@router.delete("/reading/{plan_id}")
async def delete_reading(plan_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReadingPlan).where(and_(ReadingPlan.id == plan_id, ReadingPlan.user_id == user.id)))
    plan = result.scalar_one_or_none()
    if not plan: return {"error": "不存在"}
    await db.delete(plan)
    await db.commit()
    return {"message": "删除成功"}

# ─── 饮食健康 CRUD ─────────────────────────────────

@router.get("/health")
async def list_meals(
    d: Optional[str] = None,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    target = date.today()
    if d:
        try: target = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError: pass
    result = await db.execute(select(MealRecord).where(and_(MealRecord.user_id == user.id, MealRecord.date == target)).order_by(MealRecord.created_at))
    records = result.scalars().all()
    return [
        {"id": r.id, "meal_type": r.meal_type, "food_items": json.loads(r.food_items) if r.food_items else [],
         "calories_estimate": r.calories_estimate or 0, "water_ml": r.water_ml, "date": r.date.isoformat()}
        for r in records
    ]

@router.post("/health")
async def create_meal(data: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    t_date = date.today()
    if data.get("date"):
        try: t_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError: pass
    record = MealRecord(
        user_id=user.id, meal_type=data.get("meal_type", "snack"),
        food_items=json.dumps(data.get("food_items", []), ensure_ascii=False),
        calories_estimate=data.get("calories_estimate", 0), water_ml=data.get("water_ml", 0), date=t_date,
    )
    db.add(record)
    await db.commit()
    return {"id": record.id, "message": "创建成功"}

@router.delete("/health/{record_id}")
async def delete_meal(record_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MealRecord).where(and_(MealRecord.id == record_id, MealRecord.user_id == user.id)))
    record = result.scalar_one_or_none()
    if not record: return {"error": "不存在"}
    await db.delete(record)
    await db.commit()
    return {"message": "删除成功"}

# ─── 语音转文字 ─────────────────────────────────────

from fastapi import UploadFile, File
import httpx, base64, hashlib, hmac, time, json
from app.config.settings import settings

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), user: User = Depends(get_current_user)):
    """语音转文字：支持讯飞/百度/OpenAI"""
    audio_bytes = await audio.read()
    if settings.STT_PROVIDER == "xunfei":
        return await _xunfei(audio_bytes)
    elif settings.STT_PROVIDER == "baidu":
        return await _baidu(audio_bytes)
    elif settings.STT_PROVIDER == "openai":
        return await _openai(audio_bytes, audio.filename or "audio.webm")
    return {"text": "", "error": "未配置STT_PROVIDER"}

async def _openai(audio_bytes: bytes, filename: str):
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.OPENAI_BASE_URL}/audio/transcriptions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                files={"file": (filename, audio_bytes, "audio/webm")},
                data={"model": "whisper-1", "language": "zh"}
            )
            return {"text": resp.json().get("text", "")} if resp.status_code == 200 else {"text": "", "error": str(resp.status_code)}
    except Exception as e:
        return {"text": "", "error": str(e)}

async def _baidu(audio_bytes: bytes):
    """百度语音识别"""
    try:
        # 获取 access_token
        async with httpx.AsyncClient(timeout=10) as client:
            tok = await client.post(
                "https://aip.baidubce.com/oauth/2.0/token",
                params={"grant_type": "client_credentials",
                        "client_id": settings.BAIDU_API_KEY,
                        "client_secret": settings.BAIDU_SECRET_KEY}
            )
            token = tok.json().get("access_token", "")
            if not token:
                return {"text": "", "error": "百度token获取失败"}

            audio_b64 = base64.b64encode(audio_bytes).decode()
            resp = await client.post(
                "https://vop.baidu.com/server_api",
                json={"format": "webm", "rate": 16000, "channel": 1,
                      "cuid": settings.BAIDU_APP_ID, "token": token,
                      "speech": audio_b64, "len": len(audio_bytes)}
            )
            r = resp.json()
            if r.get("err_no") == 0:
                return {"text": "".join(r.get("result", []))}
            return {"text": "", "error": r.get("err_msg", "百度识别失败")}
    except Exception as e:
        return {"text": "", "error": str(e)}

async def _xunfei(audio_bytes: bytes):
    """讯飞语音识别（REST API）"""
    try:
        ts = str(int(time.time()))
        m = hashlib.md5()
        m.update((settings.XUNFEI_APP_ID + ts).encode())
        md5 = m.hexdigest()
        signa = base64.b64encode(
            hmac.new(settings.XUNFEI_API_SECRET.encode(), md5.encode(), hashlib.sha1).digest()
        ).decode()
        audio_b64 = base64.b64encode(audio_bytes).decode()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://iat-api.xfyun.cn/v2/iat",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"appid": settings.XUNFEI_APP_ID, "ts": ts,
                      "signa": signa, "engine_type": "sms16k",
                      "aue": "raw", "auf": "audio/L16;rate=16000",
                      "data": audio_b64}
            )
            r = resp.json()
            if r.get("code") == "0":
                data = json.loads(r.get("data", "{}"))
                ws = data.get("data", {}).get("result", {}).get("ws", [])
                text = "".join(w["cw"][0]["w"] for w in ws if w.get("cw"))
                return {"text": text}
            return {"text": "", "error": r.get("message", "讯飞识别失败")}
    except Exception as e:
        return {"text": "", "error": str(e)}
