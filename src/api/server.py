
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from app.models import Category, Item, items

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

@app.get('/items')
async def index() -> dict[str, dict[int, Item]]:
    return {'items': items}

@app.get('/items/{item_id}')
async def get_item_by_id(item_id: int) -> Item:
    if item_id not in items:
        raise HTTPException(status_code=404, detail=f'Item with {item_id=} does not exist')
    return items[item_id]

Selection = dict[
    str, str | int | float | Category | None
]

@app.get('/items/')
async def query_item_by_parameters(
    name: str | None = None,
    price: float | None = None,
    count: int | None = None,
    category: Category | None = None,
) -> dict[str, Selection | list[Item]]:
    def check_item(item: Item) -> bool:
        return all(
            (
                name is None or item.name == name,
                price is None or item.price == price,
                count is None or item.count == count,
                category is None or item.category is category
            )
        )
    selection = [item for item in items.values() if check_item(item)]
    print(selection)
    return {
        'query': {
            'name': name,
            'price': price,
            'count': count,
            'category': category,
        },
        'selection': selection,
    }

@app.post('/')
async def add_item(item: Item) -> dict[str, Item]:
    if item.id in items:
        raise HTTPException(status_code=400, detail=f'Item with {item.id=} already exists')

    items[item.id] = item
    return {'added': item}

@app.put('/update/{item_id}')
async def update_item(
    item_id: int,
    name: str | None = None,
    price: float | None = None,
    count: int | None = None,
    category: Category | None = None,
) -> dict[str, Item]:
    if item_id not in items:
        raise HTTPException(
            status_code=404, detail=f'Item with {item_id=} does not exist'
        )
    if all(info is None for info in (name, price, count, category)):
        raise HTTPException(
            status_code=400, detail='No parameters provided for update'
        )

    item = items[item_id]
    if name:
        item.name = name
    if price is not None:
        item.price = price
    if count is not None:
        item.count = count
    if category:
        item.category = category

    return {'updated': item}

@app.delete('/delete/{item_id}')
async def delete_item(item_id: int) -> dict[str, Item]:
    if item_id not in items:
        raise HTTPException(
            status_code=404, detail=f'Item with {item_id=} does not exist'
        )

    item = items.pop(item_id)
    return {'deleted': item}
