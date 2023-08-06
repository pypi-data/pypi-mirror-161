from re import Pattern


class Route:
	__slots__ = ("_instance")

	def __init__(self, *args, type: str = "http", **kwargs):
		if type.lower() == "http":
			self._instance: HTTPRoute | WSRoute = HTTPRoute(*args, **kwargs)
		elif type.lower() == "websocket":
			self._instance = WSRoute(*args, **kwargs)

	def __call__(self, call, *args):
		return self._instance(call, *args)


class WSRoute:
	__slots__ = ("_route", "_content_type")
	__routes: dict = {}
	__regex_routes: list = []

	def __init__(self, route: str | Pattern, content_type: str | None = None):
		self._content_type = content_type
		if type(route) == str:
			if route[0] != "/":
				raise Exception("Route must start with '/'! (%s)" % route)
			self._route: str | Pattern = route if route[-1] == ("/") else route + "/"
		elif type(route) == Pattern:
			self._route = route
		else:
			raise Exception("Route must be str or re.Pattern type! (%s, %s)" % (route, str(type(route))))

	def __call__(self, fce, *args):
		if type(self._route) == Pattern:
			self.__regex_routes.append((self._route, fce, self._content_type))
		else:
			if self._route not in self.__routes:
				self.__routes[self._route] = (fce, self._content_type)
			else:
				raise Exception("Route alreay set! (%s)" % self._route)
		return fce

	@staticmethod
	def get(path: str) -> tuple:
		route = WSRoute.__routes.get(path if path[-1] == "/" else path + "/", {})
		if route:
			return route[0], None, route[1]
		else:
			for item in WSRoute.__regex_routes:
				if match := item[0].match(path):
					return item[1], match.groups(), item[2]
		return None, None


class HTTPRoute(WSRoute):
	__slots__ = ("_route", "__methods", "_content_type")
	__routes: dict = {}
	__regex_routes: list = []

	def __init__(self, route: str | Pattern, methods: list = [], content_type: str | None = None):
		super().__init__(route, content_type)
		self.__methods = methods or ["GET"]

	def __call__(self, fce, *args):
		if type(self._route) == Pattern:
			self.__regex_routes.append((self._route, fce, self.__methods, self._content_type))
		else:
			for method in self.__methods:
				if self._route not in self.__routes:
					self.__routes[self._route] = {}
				elif method in self.__routes[self._route]:
					raise Exception("Route alreay set! (%s)" % self.__routes.get(method, self._route))
				self.__routes[self._route][method] = (fce, self._content_type)
		return fce

	@staticmethod
	async def _options(request, response):
		path = request.path
		methods = HTTPRoute.__routes.get(path if path[-1] == "/" else path + "/", {}).keys()
		if not methods:
			for item in HTTPRoute.__regex_routes:
				if item[0].match(path):
					methods = item[2]
					break
		response.headers.append((b"Access-Control-Allow-Headers", b"*"))
		response.headers.append((b"Access-Control-Allow-Methods", ",".join(methods).encode()))
		response.headers.append((b"Vary", b"Access-Control-Request-Headers"))
		return b""

	@staticmethod
	def get(path: str, method: str) -> tuple:  # type: ignore[override]
		if method == "OPTIONS":
			return HTTPRoute._options, (), False, "text/plain"
		route = HTTPRoute.__routes.get(path if path[-1] == "/" else path + "/", {})
		if result := route.get(method, False):
			return result[0], (), None, result[1]
		else:
			for item in HTTPRoute.__regex_routes:
				if match := item[0].match(path):
					route = True
					if method in item[2]:
						return item[1], match.groups(), None, item[3]
		if route and not result:
			return None, (), True, None
		return None, (), False, None
