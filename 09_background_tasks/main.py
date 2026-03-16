# 09 - Background Tasks
# Topics: BackgroundTasks, async tasks, email simulation, cleanup jobs

import time
import asyncio
from typing import List
from fastapi import FastAPI, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Background Tasks")

# Fake task log
task_log: List[dict] = []


# ─── Helper functions (background mein chalte hain) ───────────────────────────
def send_welcome_email(email: str, name: str):
    """Yeh function background mein chalega — user wait nahi karega"""
    time.sleep(2)  # Email bhejne ka simulation
    message = f"Welcome email {email} ko bhej diya gaya — {name} ke liye"
    task_log.append({"type": "email", "to": email, "status": "sent"})
    print(f"✉️  {message}")


def process_image(filename: str, user_id: int):
    """Image resize/compress karo background mein"""
    time.sleep(3)  # Processing simulation
    task_log.append({"type": "image_process", "file": filename, "user": user_id, "status": "done"})
    print(f"🖼️  Image {filename} process ho gaya")


def cleanup_temp_files(directory: str):
    """Temp files delete karo"""
    time.sleep(1)
    task_log.append({"type": "cleanup", "dir": directory, "status": "done"})
    print(f"🗑️  {directory} clean ho gaya")


async def send_notification_async(user_id: int, message: str):
    """Async background task"""
    await asyncio.sleep(1)
    task_log.append({"type": "notification", "user": user_id, "message": message})
    print(f"🔔 Notification bhej diya user {user_id} ko")


# ─── Schemas ─────────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    name: str
    email: EmailStr


class OrderCreate(BaseModel):
    user_id: int
    items: List[str]
    total: float


# ─── Routes ──────────────────────────────────────────────────────────────────
@app.post("/register")
def register_user(user: UserRegister, background_tasks: BackgroundTasks):
    # User turant register ho gaya
    # Email background mein jayega — user wait nahi karega
    background_tasks.add_task(send_welcome_email, user.email, user.name)
    background_tasks.add_task(cleanup_temp_files, "/tmp/registrations")

    return {
        "message": f"{user.name} register ho gaya!",
        "note": "Welcome email thodi der mein aayega",
    }


@app.post("/orders")
def create_order(order: OrderCreate, background_tasks: BackgroundTasks):
    # Order turant save hua
    # Notification aur processing background mein
    background_tasks.add_task(
        send_notification_async,
        order.user_id,
        f"Aapka order {len(order.items)} items ka place ho gaya",
    )

    return {
        "order_id": 12345,
        "user_id": order.user_id,
        "items": order.items,
        "total": order.total,
        "status": "confirmed",
    }


@app.post("/upload-and-process")
def upload_and_process(filename: str, user_id: int, background_tasks: BackgroundTasks):
    # Upload immediate
    # Processing background mein
    background_tasks.add_task(process_image, filename, user_id)

    return {
        "message": "File upload ho gaya, processing chal rahi hai...",
        "filename": filename,
        "status": "processing",
    }


@app.get("/tasks/log")
def get_task_log():
    return {"total_tasks": len(task_log), "tasks": task_log}


# ─── Multiple background tasks at once ───────────────────────────────────────
@app.post("/bulk-action")
def bulk_action(user_ids: List[int], background_tasks: BackgroundTasks):
    for uid in user_ids:
        background_tasks.add_task(
            send_notification_async,
            uid,
            "Bulk notification — important update!",
        )

    return {"message": f"{len(user_ids)} users ko notifications bhej di gayi"}
