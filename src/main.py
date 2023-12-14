from habr_parser import HabrFreelanceParser


client = HabrFreelanceParser()
pages = client.get_count_page()


for i in range(1, pages+1):
    tasks = client.get_tasks_ids(page=i)
    for task in tasks:
        print(client.get_task(task))
        print("-------")
