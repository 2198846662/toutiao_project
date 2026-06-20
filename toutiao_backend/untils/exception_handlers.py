
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from untils.exception import http_exception_handler, integrity_error_handler, sqlalchemy_error_handler, general_exception_handler
def register_exception_handlers(app):
    """
    注册全局异常处理器 (子类在前，父类在后；具体在前，抽象在后)
    """
    app.add_exception_handler(HTTPException, http_exception_handler) # 处理业务逻辑抛出的 HTTPException
    app.add_exception_handler(IntegrityError, integrity_error_handler) # 处理数据库完整性约束错误，如唯一约束冲突
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler) # 处理其他 SQLAlchemy 错误，如连接错误、查询错误等
    app.add_exception_handler(Exception, general_exception_handler)  # 捕获所有未处理的异常，返回通用错误响应
    return app