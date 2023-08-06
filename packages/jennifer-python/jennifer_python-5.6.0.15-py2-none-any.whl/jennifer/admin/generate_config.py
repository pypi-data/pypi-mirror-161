import os

DEFAULT_CONFIG = """[JENNIFER]

server_address = 127.0.0.1
server_port = 5000
domain_id = 1000
inst_id = -1
log_path = /tmp/jennifer-python-agent.log
"""


def print_help():
    print("""
Usage: jennifer generate-config [output_file]

output_file: default output file name is jennifer.ini
""")


def generate_config(args):
    if len(args) < 2:
        filename = 'jennifer.ini'
    else:
        filename = args[1]
        if filename in ['--help', '-h']:
            print_help()
            return

    if os.path.exists(filename):
        print("%s is already exists." % filename)
        return

    working_directory = os.getcwd()
    with open(os.path.join(working_directory, filename), 'w') as f:
        f.write(DEFAULT_CONFIG)
        f.flush()
