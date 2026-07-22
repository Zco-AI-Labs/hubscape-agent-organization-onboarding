import inspect
import google.adk.a2a.executor.a2a_agent_executor as m

func = m.convert_a2a_request_to_agent_run_request
unwrapped = func.__wrapped__
print("Unwrapped source file:", inspect.getsourcefile(unwrapped))

# Search for _get_user_id in m's globals
get_user_id_func = unwrapped.__globals__.get("_get_user_id")
if get_user_id_func:
    print("_get_user_id source file:", inspect.getsourcefile(get_user_id_func))
    print("_get_user_id source code:")
    print(inspect.getsource(get_user_id_func))
else:
    print("_get_user_id not found in unwrapped globals")
