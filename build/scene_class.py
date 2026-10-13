import sys, re
meta = open(sys.argv[1]).read()
m = re.search(r'scene_class:\s*(\S+)', meta)
print(m.group(1) if m else "")
