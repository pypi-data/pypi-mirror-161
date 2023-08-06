from django.core.management.commands.runserver import Command as RunCommand


class Command(RunCommand):
	help = "List current labels"

	def handle(self, *args, **kwargs):
		print(args, kwargs)
