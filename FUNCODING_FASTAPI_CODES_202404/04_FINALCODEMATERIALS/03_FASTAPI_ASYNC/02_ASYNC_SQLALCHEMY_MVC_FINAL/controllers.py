from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User, Memo
from dependencies import get_db, get_password_hash, verify_password
from schemas import UserCreate, UserLogin, MemoCreate, MemoUpdate

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 회원 가입
@router.post("/signup")
async def signup(signup_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == signup_data.username))
    # 먼저 username이 이미 존재하는지 확인
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 동일 사용자 이름이 가입되어 있습니다.")
    hashed_password = get_password_hash(signup_data.password)
    new_user = User(username=signup_data.username, email=signup_data.email, hashed_password=hashed_password)
    db.add(new_user)
    
    try:
        await db.commit()
    except Exception as e:
        print (e)
        raise HTTPException(status_code=500, detail="회원가입이 실패했습니다. 기입한 내용을 확인해보세요.")
    
    await db.refresh(new_user)
    return {"message": "회원가입이 성공했습니다."}

# 로그인
@router.post("/login")
async def login(request: Request, signin_data: UserLogin, db: AsyncSession = Depends(get_db)): 
    result = await db.execute(select(User).where(User.username == signin_data.username))
    user = result.scalars().first()
    if user and verify_password(signin_data.password, user.hashed_password):
        request.session["username"] = user.username
        return {"message":"로그인이 성공했습니다."}
    else:
        raise HTTPException(status_code=401, detail="로그인이 실패했습니다.")

# 로그아웃
@router.post("/logout")
async def logout(request: Request):
    request.session.pop("username", None)
    return {"message": "로그아웃이 성공했습니다."}
    
# 메모 생성
@router.post("/memos/")
async def create_memo(request: Request, memo: MemoCreate, db: AsyncSession = Depends(get_db)):
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    new_memo = Memo(user_id=user.id, title=memo.title, content=memo.content)
    db.add(new_memo)
    await db.commit()
    await db.refresh(new_memo)
    return new_memo

# 메모 조회
@router.get("/memos/")
async def list_memos(request: Request, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")    
    
    result = await db.execute(select(Memo).where(Memo.user_id == user.id))
    memos = result.scalars().all()
    return templates.TemplateResponse("memos.html", {"request": request, "memos": memos, "username": username})

# 메모 수정
@router.put("/memos/{memo_id}")
async def update_memo(request: Request, memo_id: int, memo: MemoUpdate, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")     
    result = await db.execute(select(Memo).filter(Memo.user_id == user.id, Memo.id == memo_id))
    db_memo = result.scalars().first()
    if db_memo is None:
        return ({"error": "Memo not found"})

    if memo.title is not None:
        db_memo.title = memo.title
    if memo.content is not None:
        db_memo.content = memo.content
        
    await db.commit()
    await db.refresh(db_memo)
    return db_memo

# 메모 삭제
@router.delete("/memos/{memo_id}")
async def delete_memo(request: Request, memo_id: int, db: Session = Depends(get_db)):
    username = request.session.get("username")
    if username is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")     

    result = await db.execute(select(Memo).filter(Memo.user_id == user.id, Memo.id == memo_id))
    db_memo = result.scalars().first()    
    if db_memo is None:
        return ({"error": "Memo not found"})
        
    await db.delete(db_memo)
    await db.commit()
    return ({"message": "Memo deleted"})


@router.get("/about")
async def about():
    return {"message": "이것은 마이 메모 앱의 소개 페이지입니다."}