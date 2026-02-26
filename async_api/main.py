from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis_client import redis_client
from sqlalchemy import select
from database import engine, Base, get_db
from models import Item
from schemas import ItemCreate, ItemResponse
from cache import get_cached, set_cached, invalidate
from rate_limits import rate_limit

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/items", response_model=ItemResponse, status_code=201, dependencies=[Depends(rate_limit)])
async def create_item(data: ItemCreate, db: AsyncSession = Depends(get_db)):
    item = Item(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)

    await invalidate("items:all")
    return item

@app.get("/items", response_model=list[ItemResponse])
async def get_items(search: str | None = None, db: AsyncSession = Depends(get_db)):
    cached = await get_cached("items:all")
    if cached:
        print(">>> cache HIT")
        return cached
    
    print(">>> cache MIS")

    query = select(Item)
    if search:
        query = query.where(Item.title.ilike(f"%{search}%"))
    result = await db.execute(query)
    items = result.scalars().all()



    items_data = [ItemResponse.model_validate(i).model_dump() for i in items]
    await set_cached("items:all", items_data, 30)

    return items


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item_by_id(item_id: int, db: AsyncSession = Depends(get_db)):
    cached = await get_cached(f"items:{item_id}")
    if cached:
        print(">>> cache HIT")
        return cached
    
    print(">>> cache MIS")

    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
        
    item_data = ItemResponse.model_validate(item).model_dump()
    await set_cached(f"items:{item_id}", item_data, 300)

    return item

@app.delete("/items/{item_id}", status_code=204)
async def remove_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    await db.delete(item)
    await db.commit()
    await invalidate(f"items:{item_id}")
    return None


@app.get("/health")
async def health():
    try:
        await redis_client.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "unavailable"
    return {"status": "ok", "redis": redis_status}
