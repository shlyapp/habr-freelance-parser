from habr_parser import HabrFreelanceParser


client = HabrFreelanceParser()
tasks = client.get_tasks()
print(tasks)
