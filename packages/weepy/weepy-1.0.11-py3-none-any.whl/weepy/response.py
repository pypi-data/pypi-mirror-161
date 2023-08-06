from datetime import datetime
try:
	from orjson import dumps  # type: ignore
except ModuleNotFoundError:
	try:
		from ujson import dumps as jdumps  # type: ignore
	except ModuleNotFoundError:
		from json import dumps as jdumps

	def dumps(*args, **kwargs):  # noqa
		return jdumps(*args, **kwargs).encode()


class Response:
	__slots__ = ("_send", "_type", "_redirect", "charset")

	def __init__(self, send, content_type="application/json", charset="UTF-8", allow=None):
		self._redirect = False
		self._send = send
		self._type = content_type
		self.charset = charset

	async def send(self, data):
		if self._type == "application/json" and type(data) in (list, dict):
			data = dumps(data).decode()
		if type(data) == bytes:
			await self._send({"type": "websocket.send", "body": data})
		else:
			await self._send({"type": "websocket.send", "text": data})

	@property
	def content_type(self) -> str:
		return self._type


class HTTPResponse(Response):
	__slots__ = ["_processed", "_headers", "_allow"]

	def __init__(self, send, content_type, charset, allow):
		self._processed: bool = False
		self._headers: list[tuple] = [(b"Access-Control-Allow-Origin", allow.encode())]
		self._allow = allow
		super().__init__(send, content_type, charset)

	async def process(self, data, status=200):
		if self._redirect:
			return
		await self.start(status)
		if self._type == "application/json" and type(data) in (list, dict):
			body = dumps(data)
		elif type(data) == bytes:
			body = data
		elif type(data) == str:
			body = bytes(data, self.charset)
		else:
			body = b"" if data is None else bytes(str(data), self.charset)
		await self._send({"type": "http.response.body", "body": body})
		self._processed = True

	async def abort(self, status=400, data=b""):
		await self.process(data, status=status)
		raise HTTPAbort()

	async def start(self, status=200):
		if self._type[:4] == "text" or self._type[:11] == "application":
			self.add_header('Content-Type', self._type + ";charset=" + self.charset)
		else:
			self.add_header('Content-Type', self._type)
		await self._send({
			"type": "http.response.start",
			"status": status,
			"headers": self._headers
		})

	async def send(self, data: bytes):  # type: ignore
		await self._send({"type": "http.response.body", "body": data})

	async def redirect(self, location: str, status: int = 301) -> None:
		self._redirect = True
		self.add_header('Location', location)
		await self.start(status=status)

	def set_cookie(
			self, name: str, value: str, expires: datetime = None, maxAge="", **kwargs) -> None:
		cookie = name + "=" + value
		if expires:
			cookie += "; Expires=" + expires.strftime('%a, %d %b %Y %H:%M:%S %Z')
		elif maxAge:
			cookie += "; Max-Age=" + str(maxAge)
		for arg in kwargs:  # Domain=None,Path=None,Secure=False,HttpOnly=False
			cookie += "; " + arg[0].upper() + arg[1:] + "=" + kwargs[arg] if kwargs[arg] else "; " + arg[0].upper() + arg[1:]
		self.add_header("Set-Cookie", cookie)

	def add_header(self, name: str, value: str) -> None:
		self._headers.append((name.encode(), value.encode()))

	@property
	def processed(self):
		return self._processed

	@property
	def headers(self) -> list:
		return self._headers

	@property
	def content_type(self) -> str:
		return self._type


class HTTPAbort(Exception):
	pass
