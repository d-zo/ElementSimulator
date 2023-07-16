SOURCE_DIR = ../src
TEMP_DIR = temp_work_dir
OUTPUT_DIR = ../ElementSimulator
DOC_DIR = ../docs

DOC_BLACKLIST = __init__

.PHONY: all program pydoc

all: program pydoc

program: $(OUTPUT_DIR)/ElementSimulator.pyz

pydoc: $(DOC_DIR)/dokumentation/ElementSimulator.html

$(OUTPUT_DIR)/ElementSimulator.pyz: $(SOURCE_DIR)/__main__.py $(SOURCE_DIR)/ElementSimulator/*.py
	mkdir -p $(TEMP_DIR)/ElementSimulator;
	cp -r $(SOURCE_DIR)/* $(TEMP_DIR)/ElementSimulator/;
	cd $(TEMP_DIR); \
	python3 -m zipapp -c ElementSimulator;
	mv $(TEMP_DIR)/$(notdir $@) $@;
	rm -r $(TEMP_DIR);

$(DOC_DIR)/dokumentation/ElementSimulator.html: $(SOURCE_DIR)/ElementSimulator/*.py
	mkdir -p $(TEMP_DIR)/ElementSimulator;
	cp -r $(SOURCE_DIR)/ElementSimulator/* $(TEMP_DIR)/ElementSimulator/;
	cd $(TEMP_DIR); \
	pydoc -w ElementSimulator; \
	sed -i 's:<a href=".".*</a>::' ElementSimulator.html; \
	for pyfile in $(basename $(notdir $^)); do \
	   pydoc -w ElementSimulator.$$pyfile; \
	   sed -i "s:<font color=\"#ffffff\" face=\"helvetica, arial\"><a href=\".\">index</a>.*.py</a></font>::g;s:<a href=\"file.*</a>::g" ElementSimulator.$$pyfile.html; \
	done; \
	for blacklisted in $(DOC_BLACKLIST); do \
	   sed -i "s:<a href=\"ElementSimulator.$$blacklisted.html\">$$blacklisted</a><br>:<i>$$blacklisted</i><br>:" ElementSimulator.html; \
	   rm ElementSimulator.$$blacklisted.html; \
	done;
	mv $(TEMP_DIR)/*.html $(DOC_DIR)/;
	rm -r $(TEMP_DIR);
