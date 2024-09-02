from robocorp.tasks import task
import logging
# from robocorp import workitems
from RPA.Robocorp.WorkItems import WorkItems
@task
def minimal_task():
    message = "Hello"
    message = message + " aaaaaaaaaaaaaaaaaaaaaaaa!"
    # item = workitems.inputs
    # print("Received payload:", item.payload)
    # workitems.outputs.create(payload={"key": "value"})
    
    # for item in workitems.inputs:
    #     print("Received payload:", item.payload)
    #     workitems.outputs.create(payload={"key": "value"})

    library = WorkItems()
    library.get_input_work_item()

    variables = library.get_work_item_variables()
    for variable, value in variables.items():
        logging.info("%s = %s", variable, value)
        print("%s = %s", variable, value)