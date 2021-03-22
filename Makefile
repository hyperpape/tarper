all: analyze 

analyze: compute
	python3 scripts/tables.py ./

compute: generate
	each commands "bash -s" --destination=experiment/ --retries=5

generate:
	scripts/allruns.sh
	@mkdir -p experiment/gz
	@mkdir -p experiment/zst
	@mkdir -p experiment/gzdup
	@mkdir -p experiment/zstdup

clean:
	rm -r experiment/* 
	rm -r commands/*

