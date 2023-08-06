SHELL := /bin/bash
# PWD := $(shell pwd)

DBDIR = data/DB
ANALYSES = data/Rivet
ifndef CONTUR_USER_DIR
	CONTUR_USER=$(HOME)/contur_users
	SHARE=$(CONTUR_USER)
else
	SHARE=$(CONTUR_USER_DIR)
endif


minimal: $(ANALYSES)/Rivet-ConturOverload.so $(SHARE)

all : $(ANALYSES)/Rivet-ConturOverload.so $(SHARE)  webpages doc

$(ANALYSES)/Rivet-ConturOverload.so : $(wildcard $(ANALYSES)/*.cc)
	$(ANALYSES)/buildrivet.sh


.PHONY : $(SHARE)
$(SHARE) :

	rm -rf $(SHARE)
	mkdir $(SHARE)
	contur-init -o $(SHARE)
	@echo "INFO: You should now source $(SHARE)/analysis-list to update environment variables"	

.PHONY : doc
doc :
	cd doc && make html
	@echo "HTML docs built at doc/_build/html/index.html"

.PHONY : check
check :
	cd tests && PYTHONDONTWRITEBYTECODE=1 pytest

.PHONY : check-keep
check-keep :
	cd tests && PYTHONDONTWRITEBYTECODE=1 pytest -k 'not teardown_module'

.PHONY : check-batch
check-batch :
	cd tests && PYTHONDONTWRITEBYTECODE=1 pytest test_batch_submit.py

.PHONY : check-exec
check-exec :
	cd tests && PYTHONDONTWRITEBYTECODE=1 pytest test_executables.py

.PHONY : docclean
docclean :
	@rm -rf doc/_build/html
	@rm -rf doc/_build/doctrees

.PHONY : clean
clean:
	@echo "Removing all generated files"
	@rm -f contur/*.pyc
	@rm -f contur/*/*.pyc
	@rm -rf data/DB/analyses.db
	@rm -rf data/DB/models.db
	@rm -f $(ANALYSES)/*.so
	@rm -rf $(SHARE)
	@rm -rf */__pycache__
	@rm -rf */*/__pycache__
	@rm -rf doc/_build/html
	@rm -rf doc/_build/doctrees
	@rm -rf tests/tmp
	@rm -rf tests/sources/tmp

.PHONY : webpages
webpages:
	rm -rf $(SHARE)
	mkdir $(SHARE)
	@echo "Making the dat files for SM comparisons"
	contur-smtest -o $(SHARE)/sm_plots -b all --wbv -s
	@echo "Making the webpage measurements listings, and the plots from the dat files"
	contur-mkshare -o $(SHARE) -w
	@echo "Making the sphinx bibliography"
	contur-mkbib --all
	@echo "This should have made the webpage input. Now go to ${CONTUR_WEBDIR}, and make"

