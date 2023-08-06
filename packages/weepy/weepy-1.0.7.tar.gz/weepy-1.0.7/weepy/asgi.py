from .request import HTTPRequest, Request, InputParseError
from .response import HTTPResponse, Response, HTTPAbort
from .route import HTTPRoute, WSRoute


class ASGI:
	__slots__ = ()
	_content_type = ""
	_charset = ""
	_allow = None
	triggers: dict = {}

	def __init__(self, content_type: str = "application/json", charset: str = "UTF-8", allow=""):
		ASGI._content_type = content_type
		ASGI._charset = charset
		ASGI._allow = allow

	@staticmethod
	async def __call__(scope, receive, send):
		event = await receive()
		if scope["type"] == "http":
			while event["more_body"]:
				more = await receive()
				event["body"] += more["body"]
				event["more_body"] = more["more_body"]
			await ASGI._HTTP(scope, event, send)
		elif event["type"] == "websocket.connect":
			await ASGI._WS(scope, send, receive)

	@staticmethod
	async def _HTTP(scope, event, send):
		method, url_args, not_allowed, ct = HTTPRoute.get(scope["path"], scope["method"])

		request = HTTPRequest(scope, event)
		response = HTTPResponse(
			send,
			content_type=ct or ASGI._content_type,
			charset=ASGI._charset,
			allow=ASGI._allow
		)
		try:
			if not_allowed:
				await response.abort(status=405)
			elif not method:
				await response.abort(status=404)
			try:
				body = await method(request, response, *url_args)
			except InputParseError:
				await response.abort(status=400)
			if not response.processed:
				await response.process(body)
		except HTTPAbort:
			pass

	@staticmethod
	async def _WS(scope, send, receive):
		trigger, url_args, ct = WSRoute.get(scope["path"])
		if trigger:
			await send({"type": "websocket.accept"})
			while True:
				event = await receive()
				request = Request(scope, event, content_type=ASGI._content_type)
				response = Response(
					send,
					content_type=ct or ASGI._content_type,
					charset=ASGI._charset
				)
				try:
					await trigger(request, response, url_args)
				except InputParseError:
					response.send({"status": False, "error": "P001", "message": "Data JSON parse error"})
				if event["type"] == "websocket.disconnect":
					break
		else:
			await send({"type": "websocket.close"})
