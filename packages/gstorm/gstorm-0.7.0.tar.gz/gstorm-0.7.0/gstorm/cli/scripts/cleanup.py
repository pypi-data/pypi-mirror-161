import os
import click
from gstorm.helpers.Logging import (log, LogLevel)
from gstorm import helpers


@click.command()
@click.option('--src', default=None, help='Graphql schema file to clean')
@click.option('--dst', default=None, help='Graphql schema file path to store the new file')
def cleanup(src, dst):
    [src_path, dst_path] = [os.path.join(
        os.getcwd(), path) for path in [src, dst]]
    helpers.silent_removefile(dst_path)
    with open(src_path, 'r') as src_file:
        with open(dst_path, 'w+') as dst_file:
            for line in src_file:
                is_whitespace = not line.strip()
                if is_whitespace:
                    dst_file.write(line)
                    continue
                line = line.rstrip()  # clean
                line = line.split('#')[0].rstrip()  # remove comment
                # append if not empty
                if line:
                    dst_file.write(line + '\n')
            dst_file.write('\n')
    log(LogLevel.SUCCESS, 'Done')
