from pyperspace.rest_api import generate_api
from uvicorn.main import run
from argparse import ArgumentParser

def _get_arg_parser():
    argparser = ArgumentParser(description='Pyperspace Daemon')
    #argparser.add_argument('-c', '--config', metavar='<file>', help='configuration file', required=True)
    argparser.add_argument('--data-dir', metavar='<dir>', help='data directory', required=True)
    argparser.add_argument('--host', metavar='<IP>', help='hostname', default='0.0.0.0')
    argparser.add_argument('-p', '--port', metavar='<int>', type=int, help='port', required=True)
    return argparser

def main():
    args = _get_arg_parser().parse_args()
    run(generate_api(args.data_dir), host=args.host, port=args.port, workers=1)
    return 0
