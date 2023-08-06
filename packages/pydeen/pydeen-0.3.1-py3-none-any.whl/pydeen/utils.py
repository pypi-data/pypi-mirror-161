pydeen_trace = True

def set_trace_mode(activated:bool):
    pydeen_trace = activated

def error(msg):
    print("ERROR:", msg)

def info(msg):
    print("INFO:", msg)

def warn(msg):
    print("WARNING:", msg)

def trace(msg):
    if pydeen_trace == True:
        print("TRACE:", msg)

