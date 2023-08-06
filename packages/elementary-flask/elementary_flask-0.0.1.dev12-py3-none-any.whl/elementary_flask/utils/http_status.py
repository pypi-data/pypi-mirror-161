from http import HTTPStatus

HTTP_STATUS_LIST = [(s.value, s.phrase) for s in HTTPStatus]
HTTP_STATUS_DICT = {status_code: status_message for status_code, status_message in HTTP_STATUS_LIST}
