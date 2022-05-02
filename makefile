build-haystack:
	`git clone --branch v1.3.0 --depth 1 https://github.com/deepset-ai/haystack.git || true` && \
		cd haystack/rest_api/pipeline && \
		awk '{sub(/localhost/,"elasticsearch")}1' pipelines.haystack-pipeline.yml > pipelines.haystack-pipeline.yml.bk && \
		cat pipelines.haystack-pipeline.yml.bk > pipelines.haystack-pipeline.yml && \
		rm pipelines.haystack-pipeline.yml.bk && \
		cd ../.. && \
		awk '{gsub("xpdf-tools-linux-4.03","xpdf-tools-linux-4.04")}1' Dockerfile > Dockerfile.bk && \
		cat Dockerfile.bk > Dockerfile && \
		rm Dockerfile.bk && \
		awk '{sub(/#image: \"elasticsearch:7.9.2\"/,"image: \"elasticsearch:7.9.2\"")}1' docker-compose.yml > docker-compose.yml.bk && \
		awk '{sub(/image: \"deepset\/elasticsearch-countries-and-capitals\"/,"#image: \"deepset\/elasticsearch-countries-and-capitals\"")}1' docker-compose.yml.bk > docker-compose.yml && \
		rm docker-compose.yml.bk && \
		docker-compose build

build-solution:
	docker-compose -p faq build && \
		docker-compose -p faq up

run-bot:
	docker-compose -p faq exec rasa-server rasa run \
		--enable-api \
		-vv \
		--cors "*"

train-bot:
	docker-compose -p faq exec rasa-server rasa train

clean:
	docker-compose -p faq down