# GA4GH Community Stack — Synaptic Four unified local lifecycle

.PHONY: help install up down destroy

help:
	@echo "GA4GH Community Stack — local lifecycle"
	@echo ""
	@echo "  make install   pip install -e ./cli (lab-stack CLI)"
	@echo "  make up        lab-stack demo start"
	@echo "  make down      lab-stack demo stop"
	@echo "  make destroy   lab-stack demo destroy"
	@echo ""
	@echo "Also: lab-stack init, lab-stack generate compose"

install:
	pip install -e "./cli[dev]"

up:
	lab-stack demo start

down:
	lab-stack demo stop

destroy:
	lab-stack demo destroy
