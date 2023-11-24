import datetime
import random
import jwt
from fastapi import FastAPI, Form, File, UploadFile, Response, Cookie, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import FileResponse
from typing import Annotated

from .models.models import User, Identification, Feedback, UserCreate, UserLogin

app = FastAPI()
security = HTTPBasic()

SECRET_KEY = "mysecretkey" #just an example of secret key

ALGORITHM = "HS256" #algorythm of hesh

USERS_DATA = [
    {"username": "admin", "password": "adminpass"}
]

USER_DATA = [
      UserLogin(**{"username": "user1", "password": "pass1"}),
      UserLogin(**{"username": "user2", "password": "12345"})
]


# JWT

def get_user(username: str, password: str) -> bool:
    for user in USER_DATA:
        if username == user.username and password == user.password:
            return True
    return False


def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM) #the process of encoding


def get_user_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) #decoding tokin
        return payload.get("sub") #полезная нагрузка
        # sub - тема токена
        # iss - определяет приложение из которого отправляется токен
        # exp - время жизни токена
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token was expired',
            headers={"WWW-Authenticate": "Bearer"},
        )    #логика истечения срока действия токена
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Token',
            headers={"WWW-Authenticate": "Bearer"},
        )  #логика обработки ошибки декодирования токена


@app.post("/login")
async def get_the_login(user: UserLogin = Depends()):
    authenticate = get_user(user.username, user.password)
    if authenticate:
        return {"access token": create_jwt_token(
            {"sub": user.username}
        )}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid username or password',
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/protected_resource")
async def protected(token: str):
    get_user_token(token)
    return {"message": "protected!"}


db = []

sample_product_1 = {
    "product_id": 123,
    "name": "Smartphone",
    "category": "Electronics",
    "price": 599.99
}

sample_product_2 = {
    "product_id": 456,
    "name": "Phone Case",
    "category": "Accessories",
    "price": 19.99
}

sample_product_3 = {
    "product_id": 789,
    "name": "Iphone",
    "category": "Electronics",
    "price": 1299.99
}

sample_product_4 = {
    "product_id": 101,
    "name": "Headphones",
    "category": "Accessories",
    "price": 99.99
}

sample_product_5 = {
    "product_id": 202,
    "name": "Smartwatch",
    "category": "Electronics",
    "price": 299.99
}

sample_products = [sample_product_1, sample_product_2, sample_product_3, sample_product_4, sample_product_5]


@app.get("/product/{product_id}")
def get_product(product_id: int):
    prod_id = [i for i in sample_products if i['product_id'] == product_id]
    return prod_id[0]


@app.get("/products/search")
def search_product(keyword: str, limit: int = 10, category: str = None):
    #пробегаемся по списку словарей в поисках ключегого слова
    result = list(filter(lambda i: keyword.lower() in i['name'].lower(), sample_products))

    #если указана категория
    if category is not None:
        #пробегаемся по списку словарей
        result = list(filter(lambda i: category.lower() in i['category'].lower(), sample_products))

    return result[:limit] #срез


@app.post("/create_user", response_model=UserCreate)
def create_user(user: UserCreate):
    db.append(user)
    return user


fake_users = {
    1: {"username": "joecool2005", "email": "joecool2005@yahoo.com"},
    2: {"username": "katiegreen", "email": "kategreen@yahoo.com"}
}

feedback_db = []


@app.post("/feedback")
def post_feedback(feedback: Feedback):
    feedback_db.append({"name": feedback.name, "feedback": feedback.message})
    return f"Thank you for your feedback, {feedback.name}"


@app.get("/users/{user_id}")
def read_user(user_id: int):
    if user_id in fake_users:
        return fake_users[user_id]
    return {"error": "User does not exist in our database"}


@app.get("/")
async def root():
    return FileResponse("/Users/alexag/Desktop/fastApiProject/templates/index.html")


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/custom")
def read_custom_message():
    return {"message": "This is a custom message"}


@app.post("/calculate")
async def calc(num1: int = Form(ge=0, lt=None), num2: int = Form(ge=0, lt=None)):
    print("num1 = ", num1, "num2 = ", num2, )
    return {"result is", num1 + num2}


@app.get("/calculate", response_class=FileResponse)
def calc_form():
    return "/Users/alexag/Desktop/fastApiProject/templates/calculator.html"


@app.get("/users")
def get_users():
    # имитируем входящий JSON
    user_data = {
        "name": "alexa",
        "age": 1
    }
    #имитируем распаковку входящих данных
    adm_user_data: User = User(**user_data)
    return adm_user_data


@app.get("/auth")
def get_auth():
    user_data = {
        "login": "alexa",
        "email": "a.lexa@gg.com",
        "password": "12345psswd!"
    }

    get_user_data = Identification(**user_data)
    return get_user_data


@app.post("/user")
def check_age(user: User): # проверяем входные данные на соответствие модели класса
    if user.age >= 18:
        user.is_adult = True
    return user


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}


logindb = {
    "username": "alexa",
    "password": "12345678"
}

fake_login_db: list[UserLogin] = [UserLogin(**logindb)]

sessions: dict = {}


@app.post("/login_old")
async def login(user: UserLogin, response: Response):
    for usr in fake_login_db:
        if usr.username == user.username and usr.password == user.password:
            session_token = str(random.randint(100, 999))
            sessions[session_token] = user
            response.set_cookie("session_token", value=session_token, httponly=True)

            return {"message": "Cookie installed"}
    return {"message": "invalid input data"}


@app.get("/user")
async def user_info(session_token = Cookie()):
    user = sessions.get(session_token)
    if user:
        return user.dict()
    return {"message": "Unauthorized"}


#
# #basic authentication start block
# USER_DATA = [
#     UserLogin(**{"username": "user1", "password": "pass1"}),
#     UserLogin(**{"username": "user2", "password": "12345"})
# ]
#
#
# def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
#     user = get_user_from_db(credentials.username)
#     if user is None or user.password != credentials.password:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
#     return user
#
#
# def get_user_from_db(username: str):
#     for user in USER_DATA:
#         if user.username == username:
#             return user
#     return None
#
#
# @app.get("/protected_resourse")
# async def get_protected_resource(user: UserLogin = Depends(authenticate_user)):
#     return {"message": "You have access to the protected resource!", "user_info": user}
# #basic authentication final block




