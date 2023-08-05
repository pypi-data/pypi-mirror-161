from dacite import from_dict
from dacite.exceptions import WrongTypeError, MissingValueError

def getObject(data_class: type = None, data = None):
    ''
    try:
        if data is None:
            return None
        result: data_class = from_dict(data_class=data_class, data=data)
    except WrongTypeError as wte:
        # 데이터 타입이 다른 경우 에러 처리
        raise wte 
    except MissingValueError as mve:
        # 필수 필드가 비었을 경우 에러 처리
        raise mve
    
    return result