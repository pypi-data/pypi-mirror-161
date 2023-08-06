from copy import copy
from urllib.parse import unquote
from http.cookies import SimpleCookie
from email.parser import BytesParser as BP
try:
	from orjson import loads  # type: ignore
except ModuleNotFoundError:
	try:
		from ujson import loads  # type: ignore
	except ModuleNotFoundError:
		from json import loads


class Request:
	__slots__ = (
		"_scope", "_event", "_scheme", "_path",
		"_query_string", "_headers", "_ip", "_data",
		"_type", "_content_length"
	)

	def __init__(self, scope, event, content_type):
		self._scope = scope
		self._event = event
		self._query_string = None
		self._type = content_type
		self._headers = None
		self._data = None

	@staticmethod
	def _parse(data: bytes) -> dict:
		if not data:
			return {}
		parsed: dict = {}
		for item in unquote(data.decode()).split("&"):
			pair = item.split("=") + [""]
			if pair[0] in parsed:
				if type(parsed[pair[0]]) == list:
					parsed[pair[0]].append(pair[1])
				else:
					parsed[pair[0]] = [parsed[pair[0]], pair[1]]
			else:
				parsed[pair[0]] = pair[1]
		return parsed


	@property
	def scope(self):
		return self._scope

	@property
	def event(self):
		return self._event

	@property
	def path(self):
		return self._scope["path"]

	@property
	def query_params(self):
		if self._query_string is None:
			self._query_string = self._parse(self._scope["query_string"])
		return copy(self._query_string)

	@property
	def headers(self):
		if self._headers is None:
			self._headers = {}
			for header, value in self._scope["headers"]:
				self._headers[header.decode()] = value.decode()
		return copy(self._headers)

	@property
	def data(self):
		if self._data is None:
			if self._type[:16] == "application/json":
				try:
					self._data = loads(self._event.get("bytes") or self._event.get("text").encode())
				except Exception:
					raise ParseError
			else:
				self._data = self._event.get("text") or self._event["bytes"].decode()
		return self._data


class HTTPRequest(Request):
	__slots__ = (
		"_scope", "_event", "_scheme", "_path",
		"_query_string", "_headers", "_ip", "_data",
		"_version", "_method", "_cookies"
	)

	def __init__(self, scope, event):
		super().__init__(scope, event, "")
		self._cookies = None

	@property
	def method(self):
		return self._scope["method"]

	@property
	def cookies(self):
		if self._cookies is None:
			cookie: SimpleCookie = SimpleCookie()
			for header, value in self._scope["headers"]:
				if header.lower() == b"cookie":
					cookie.load(value.decode())
			self._cookies = {k: v for k, v in cookie.items()}
		return copy(self._cookies)

	@property
	def headers(self):
		if self._headers is None:
			self._headers = {}
			for header, value in self._scope["headers"]:
				if header.lower() != b"cookie":
					self._headers[header.decode()] = value.decode()
		return copy(self._headers)

	@property
	def data(self):
		if self._data is None:
			try:
				if not int(self.headers["content-length"]):
					self._data = {}
				elif self._headers["content-type"][:16] == "application/json":
					self._data = loads(self._event["body"])
				elif self._headers["content-type"] == "application/x-www-form-urlencoded":
					self._data = self._parse(self._event["body"])
				elif self._headers["content-type"][:19] == "multipart/form-data":
					m = BP().parsebytes(
						b"Content-Type: " + self._headers["content-type"].encode() +
						b"\n" + self._event["body"]
					)
					self._data = {
						p.get_param("name", header="content-disposition"): p.get_payload(decode=True) for p in m.get_payload()
					}
				else:
					self._data = self._event["body"]
			except Exception:
				raise ParseError
		return self._data


class InputParseError(Exception):
	pass
