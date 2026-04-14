from __future__ import annotations

import time
from typing import Optional


def register_call_handlers(sio, *, user_room, active_calls):
    def ensure_call_id(call_id: Optional[str]) -> str:
        if call_id:
            return str(call_id)
        return f"call_{int(time.time() * 1000)}"

    @sio.event
    async def call_user(sid, data):
        session = await sio.get_session(sid)
        from_user_id = (session or {}).get("userId")
        if not from_user_id:
            await sio.emit("socket_error", {"message": "Unauthorized"}, to=sid)
            return

        to_user_id = str((data or {}).get("toUserId") or "").strip()
        offer = (data or {}).get("offer")
        call_type = str((data or {}).get("callType") or "video")
        call_id = ensure_call_id((data or {}).get("callId"))

        if not to_user_id or not offer:
            await sio.emit("socket_error", {"message": "toUserId and offer are required"}, to=sid)
            return

        active_calls[call_id] = {
            "callId": call_id,
            "callerId": from_user_id,
            "calleeId": to_user_id,
            "callType": call_type,
            "status": "ringing",
        }

        await sio.emit(
            "call_user",
            {"callId": call_id, "fromUserId": from_user_id, "callType": call_type, "offer": offer},
            room=user_room(to_user_id),
        )

    @sio.event
    async def accept_call(sid, data):
        session = await sio.get_session(sid)
        from_user_id = (session or {}).get("userId")
        call_id = str((data or {}).get("callId") or "").strip()
        answer = (data or {}).get("answer")

        if not from_user_id or not call_id or not answer:
            await sio.emit("socket_error", {"message": "callId and answer are required"}, to=sid)
            return

        call = active_calls.get(call_id)
        if not call:
            await sio.emit("socket_error", {"message": "Call not found"}, to=sid)
            return

        call["status"] = "accepted"
        await sio.emit(
            "accept_call",
            {"callId": call_id, "fromUserId": from_user_id, "answer": answer, "callType": call.get("callType")},
            room=user_room(call["callerId"]),
        )

    @sio.event
    async def reject_call(sid, data):
        session = await sio.get_session(sid)
        from_user_id = (session or {}).get("userId")
        call_id = str((data or {}).get("callId") or "").strip()
        reason = (data or {}).get("reason") or "rejected"
        if not from_user_id or not call_id:
            await sio.emit("socket_error", {"message": "callId is required"}, to=sid)
            return
        call = active_calls.pop(call_id, None)
        if not call:
            return
        await sio.emit("reject_call", {"callId": call_id, "fromUserId": from_user_id, "reason": reason}, room=user_room(call["callerId"]))

    @sio.event
    async def ice_candidate(sid, data):
        session = await sio.get_session(sid)
        from_user_id = (session or {}).get("userId")
        call_id = str((data or {}).get("callId") or "").strip()
        to_user_id = str((data or {}).get("toUserId") or "").strip()
        candidate = (data or {}).get("candidate")
        if not from_user_id or not call_id or not to_user_id or not candidate:
            return
        await sio.emit("ice_candidate", {"callId": call_id, "fromUserId": from_user_id, "candidate": candidate}, room=user_room(to_user_id))

    @sio.event
    async def end_call(sid, data):
        session = await sio.get_session(sid)
        from_user_id = (session or {}).get("userId")
        call_id = str((data or {}).get("callId") or "").strip()
        reason = (data or {}).get("reason") or "ended"
        if not from_user_id or not call_id:
            return
        call = active_calls.pop(call_id, None)
        if not call:
            return
        other = call["calleeId"] if from_user_id == call["callerId"] else call["callerId"]
        await sio.emit("end_call", {"callId": call_id, "fromUserId": from_user_id, "reason": reason}, room=user_room(other))

