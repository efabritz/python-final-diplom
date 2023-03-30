from rest_framework.exceptions import APIException

class DatabaseTransferError(APIException):
    status_code = 400
    default_detail = "Unable to send data of yaml file to database."
    default_code = "error during database queries"

class UserNotFoundError(APIException):
    status_code = 400
    default_detail = "User id not defined"
    default_code = "User is NULL"

class OrderNotFoundError(APIException):
    status_code = 400
    default_detail = "Order id not defined"
    default_code = "Order is NULL"