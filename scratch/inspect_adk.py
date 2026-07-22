import inspect
from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor

print("A2aAgentExecutor source code:")
try:
    print(inspect.getsource(A2aAgentExecutor))
except Exception as e:
    print("Error getting source:", e)
