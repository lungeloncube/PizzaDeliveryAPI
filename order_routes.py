from fastapi import Depends, APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from database import Session, engine
from fastapi.encoders import jsonable_encoder

order_router = APIRouter(prefix='/orders', tags=["orders"])
session = Session(bind=engine)


@order_router.get('/')
async def hello(Authorize: AuthJWT = Depends()):
    """
    # A sample route
    This returns a hello world"""
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, details='Invalid Token')

    return {"message": "Hello world"}


@order_router.post('/order', status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, Authorize: AuthJWT = Depends()):

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    new_order = Order(
        pizza_sizes=order.pizza_sizes,
        quantity=order.quantity

    )

    # attaching user to the order
    new_order.user = user
    session.add(new_order)
    session.commit()
    response = {'pizza_sizes': new_order.pizza_sizes,
                'quantity': new_order.quantity,
                'id': new_order.id,
                'order_status': new_order.order_status}

    return jsonable_encoder(response)


@order_router.get('/orders')
async def list_all_order(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token")
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        orders = session.query(Order).all()

        return jsonable_encoder(orders)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not a super user')


@order_router.get('/orders/{id}')
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token')
    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()
    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        return jsonable_encoder(order)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not allowed to carry out task')


@order_router.get('/user/orders')
async def get_user_orders(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token')
    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()
    return jsonable_encoder(current_user.orders)


@order_router.get('/user/orders/{id}/')
async def get_specific_order(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token')

    subject = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == subject).first()
    orders = current_user.orders
    for o in orders:
        if o.id == id:
            return jsonable_encoder(o)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail='No order with such id')


@order_router.put('/order/update/{id}')
async def update_order(id: int, order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token')

    order_to_update = session.query(Order).filter(Order.id == id).first()
    order_to_update.quantity = order.quantity
    order_to_update.pizza_sizes = order.pizza_sizes
    session.commit()

    response = {
        "id": order_to_update.id,
        "pizza_sizes": order_to_update.pizza_sizes,
        "quantity": order_to_update.quantity,
        "order_status": order_to_update.order_status
    }
    return jsonable_encoder(response)


@order_router.patch('/order/update/{id}/')
async def update_order_status(id: int, order: OrderStatusModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token')
    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == id).first()
        order_to_update.order_status = order.order_status
        session.commit()
        response = {
            "id": order_to_update.id,
            "pizza_sizes": order_to_update.pizza_sizes,
            "quantity": order_to_update.quantity,
            "order_status": order_to_update.order_status
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="this user is not allowed to perform this operation")


@order_router.delete('/order/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_specific_order(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token')
    order_to_delete = session.query(Order).filter(Order.id == id).first()
    session.delete(order_to_delete)
    session.commit()
    return order_to_delete
