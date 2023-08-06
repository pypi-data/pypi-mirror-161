import subprocess


class ProcessInvoker:

    def __init__(self, process_run_command, process_name):
        self.process_run_command = process_run_command
        self.process_name = process_name

    def invoke_process(self):
        try:
            command = self.build_command()
            pid = subprocess.Popen([command], shell=True).pid
            return f'process invoked: {pid}'
        except BaseException as ex:
            return f'error: {ex}'

    def build_command(self):
        return self.process_run_command.replace('{process-name}', self.process_name)
