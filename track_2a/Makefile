.PHONY: run image predict test report

IMAGE := booklet-nli
# The checkout is mounted at /app, so results and the booklet cache are written back to it as the host user.
DOCKER_RUN := docker run --rm --user $$(id -u):$$(id -g) -v "$(CURDIR):/app"

image:
	docker build -t $(IMAGE) .

# Downloads the 60 booklets once (checked against data/ost/booklets.json), replays every run in data/runs.yaml
# and fails if a score differs from the committed results; needs no API key.
run: image
	$(DOCKER_RUN) $(IMAGE) reproduce

# Predicts labels for a file in the challenge's input format (beginner or advanced); needs LLM_API_KEY in .env.
# Example: make predict INPUT=cases.jsonl OUTPUT=predictions.jsonl
predict: image
	$(DOCKER_RUN) --env-file .env $(IMAGE) predict "$(INPUT)" "$(OUTPUT)" --mode live

test: image
	$(DOCKER_RUN) --entrypoint /opt/venv/bin/pytest $(IMAGE) -q -p no:cacheprovider

# Prints technical_report.md to the submission PDF; runs on the host because it needs Chrome.
report:
	uv run booklet-nli report-pdf
