#!python
import sys
import daemon
import uvicorn
# from gunicorn.app.wsgiapp import run
from argparse import ArgumentParser


def server():
	parser = ArgumentParser(
		description="Simple development server for WeefPy framework"
	)
	parser.add_argument('--daemon', action="store_true", help="Run server as daemon")
	parser.add_argument('--config', nargs=1, default=[""], help="Path to gunicorn config file")
	parser.add_argument('--pythonpath', nargs=1, default=["."], help="Provided pythonpath")
	parser.add_argument('--host', nargs=1, default=[None], help="Server IP address")
	parser.add_argument('--port', nargs=1, default=[None], help="Server port")
	parser.add_argument(
		'--app', nargs=1, default=[None],
		help="Callable application in format file:app - where app is callable object"
	)
	args = parser.parse_args(sys.argv[1:])
	config = args.config[0]
	pythonpath = args.pythonpath[0]
	host = args.host[0] or "127.0.0.1"
	port = int(args.port[0] or "8000")
	app = args.app[0]

	# options = {
	# 	'bind': '%s:%s' % (host, port),
	# 	'workers': "4",
	# 	'pythonpath': pythonpath,
	# 	'worker-class': "uvicorn.workers.UvicornWorker"
	# }
	# if config:
	# 	options["config"] = config

	# sys.argv = [sys.argv[0]]
	# for key in options:
	# 	sys.argv.append("--%s" % key)
	# 	sys.argv.append(str(options[key]))
	# sys.argv.append(app)

	options = {}
	if config:
		options["env_file"] = config

	if args.daemon:
		with daemon.DaemonContext():
			# sys.exit(run())
			uvicorn.run(
				app,
				host=host,
				port=port,
				reload=True,
				app_dir=pythonpath,
				workers=4,
				log_level="info",
				timeout_keep_alive=3600,
				**options
			)
	else:
		# sys.exit(run())
		uvicorn.run(
			app,
			host=host,
			port=port,
			reload=True,
			app_dir=pythonpath,
			workers=4,
			log_level="info",
			timeout_keep_alive=3600,
			**options
		)

