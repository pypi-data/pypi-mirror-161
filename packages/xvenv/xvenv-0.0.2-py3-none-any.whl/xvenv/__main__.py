try:
    from .xvenv import main_func
except:
    from xvenv import main_func

if __name__ == "__main__":
    rc = main_func()
