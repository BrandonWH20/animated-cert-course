# Render/assemble a course.  Run every command from the repo root.
VENV ?= .venv/bin
ANIM ?= _template
Q    ?= m                 # m=medium(720p draft), h=high(1080p final)

.PHONY: render render-hi list check assemble setup
setup:             ## one-time: create venv + install manim
	python3 -m venv .venv && $(VENV)/pip install -r requirements.txt
render:            ## draft render: make render ANIM=<slug>
	$(VENV)/manim -q$(Q) --disable_caching animations/$(ANIM)/scene.py \
	  $$($(VENV)/python build/scene_class.py animations/$(ANIM)/meta.yaml) \
	  --media_dir animations/$(ANIM)/renders
render-hi:         ## final 1080p
	$(MAKE) render Q=h
list:              ## list animations
	@ls animations
check:             ## per-chapter drift: make check COURSE=courses/<name>/chapters.json
	$(VENV)/python build/synced.py check $(COURSE)
assemble:          ## concat + mux original audio: make assemble COURSE=courses/<name>/chapters.json
	$(VENV)/python build/synced.py assemble $(COURSE)
