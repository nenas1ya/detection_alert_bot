import json
import requests

cookies = {
    'token_access': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEzNDI0NTY5LCJpYXQiOjE3MTM0MjA5NjksImp0aSI6ImZhYTU1OWM2MzJjZjQxNDZhNmEzYWUwMTBlNTM5NDlkIiwidXNlcl9pZCI6MTA0fQ.rzIA27sEy2Piiz62U8zk6CqoezqJ9yFEX7r9Vmyz7x0',
    'token_refresh': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxMzUwNzM2OSwiaWF0IjoxNzEzNDIwOTY5LCJqdGkiOiJmZDAzNTQ4MzExMjk0YTViYjdlZDRkMjllMGMwYjE0NyIsInVzZXJfaWQiOjEwNH0.dIiaE1QoZJTP2cAGdmJiwyCx1A1TSW3Rt85arF2jPtc',
}

headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEzNDI4NDQzLCJpYXQiOjE3MTM0MjA5NjksImp0aSI6IjIxNTU5ODRjYjhhYTQ5ODZhYWFhMmRkZmI0MWU4MzcyIiwidXNlcl9pZCI6MTA0fQ.gJwh5AUAPlxA4GYlk8KjuYYOc3hBV465yi8fCsXPBxQ',
}

response = requests.get(
    'https://dutssd.admtyumen.ru/api/v1/detections/msc/?validation_status=AWAITING&created_at__gte=2024-03-31T19:00:00.000Z&created_at__lte=2024-04-30T18:59:59.999Z',
    cookies=cookies,
    headers=headers,
)


print(json.loads(response.text))