.PHONY: dev index ask test zip

dev:
	cp -n .env.example .env || true
	docker compose up --build

index:
	bash scripts/index_sample.sh

ask:
	bash scripts/ask_sample.sh

test:
	cd backend && pytest -q

zip:
	cd .. && zip -r atlas.zip atlas -x "*/node_modules/*" "*/.next/*" "*/__pycache__/*"
