"""
对话相关 API 路由 — WebSocket聊天 + REST接口
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.agent.core import get_agent
from app.agent.memory import get_memory
from app.tools import get_all_tools

router = APIRouter()

_agent_initialized = False


def _init_agent():
    global _agent_initialized
    if not _agent_initialized:
        agent = get_agent()
        for tool in get_all_tools():
            agent.register_tool(tool)
        _agent_initialized = True


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    """WebSocket 聊天端点"""
    await websocket.accept()
    _init_agent()

    try:
        # 第一条消息应包含 token
        data = await websocket.receive_json()
        token = data.get("token")
        if not token:
            await websocket.send_json({"error": "需要认证"})
            await websocket.close()
            return

        from app.services.auth import decode_token
        payload = decode_token(token)
        if not payload:
            await websocket.send_json({"error": "无效token"})
            await websocket.close()
            return

        user_id = int(payload.get("sub"))
        agent = get_agent()
        memory = get_memory()
        await websocket.send_json({"type": "connected", "message": "连接成功"})

        while True:
            data = await websocket.receive_json()
            message = data.get("message", "")
            if not message:
                continue

            history = await memory.get_history(user_id, db)
            full_response = ""
            async for event in agent.stream(message, user_id, history, db=db):
                if event["type"] == "thinking":
                    await websocket.send_json({"type": "thinking"})
                elif event["type"] == "text":
                    full_response += event["content"]
                    await websocket.send_json({"type": "chunk", "content": event["content"]})
                elif event["type"] == "tool_call":
                    await websocket.send_json({"type": "tool_call", "tool": event["tool"], "input": event["input"]})
                elif event["type"] == "tool_result":
                    await websocket.send_json({"type": "tool_result", "tool": event["tool"], "result": event["result"]})

            await db.commit()  # 提交工具执行的数据库更改
            await websocket.send_json({"type": "done"})
            await memory.add_message(user_id, "user", message, db)
            await memory.add_message(user_id, "assistant", full_response, db)
            await db.commit()  # 提交聊天记录

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass


@router.post("/send")
async def send_message(
    data: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """REST 聊天接口（备用）"""
    _init_agent()
    message = data.get("message", "")
    agent = get_agent()
    memory = get_memory()
    history = await memory.get_history(user.id, db)
    response = await agent.invoke(message, user.id, history)
    await memory.add_message(user.id, "user", message, db)
    await memory.add_message(user.id, "assistant", response, db)
    await db.commit()
    return {"response": response}


@router.get("/history")
async def get_chat_history(
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取聊天历史"""
    memory = get_memory()
    history = await memory.get_history(user.id, db)
    return {"messages": history[-limit:]}
