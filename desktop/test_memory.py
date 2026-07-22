import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from core.memory import get_memory_manager
m = get_memory_manager()
m.vector.clear()
r1 = m.vector.store('user likes Python and dark mode', {'type':'pref'})
print('stored:', r1['success'])
r2 = m.vector.store('user asked about Jarvis AI features', {'type':'conv'})
print('stored:', r2['success'])
r = m.search('python programming')
print(f'search results: {len(r)}')
for x in r:
    print(f'  {x["text"]} (score={x["score"]:.3f})')
r = m.search('jarvis artificial intelligence')
print(f'semantic search: {len(r)}')
for x in r:
    print(f'  {x["text"]} (score={x["score"]:.3f})')
