__main_loop_flag = True
__tasks = {}
def stop():
    global __main_loop_flag
    __main_loop_flag = False
def add_task(name,task):
    global __tasks
    __tasks[name] = task
def remove_task(name):
    global __tasks
    if name in __tasks:
        del __tasks[name]
def remove_all_tasks():
    global __tasks
    __tasks.clear()
def start():
    global __main_loop_flag,__tasks
    __main_loop_flag = True
    # main loop
    while __main_loop_flag:
        for funk in __tasks:
            fun = __tasks[funk]
            try:
                fun()
            except Exception as e:
                import sys
                sys.print_exception(e)
    remove_all_tasks()