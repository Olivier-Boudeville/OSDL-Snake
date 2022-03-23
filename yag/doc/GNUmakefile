.PHONY: doc all full-doc create-links html pdf clone-mirror          \
		export-doc export-to-official export-to-mirror               \
		clean clean-doc-local clean-links-local info info-web


PROJECT_VERSION := 1.1.8

DOC_BASE_NAME := yag-osdl

OVERALL_DOCUMENT_SOURCE := $(DOC_BASE_NAME).rst


CURRENT_YAG_HTML := $(DOC_BASE_NAME).html

HTML_TARGET := $(CURRENT_YAG_HTML)


CURRENT_YAG_PDF := $(DOC_BASE_NAME).pdf

PDF_TARGET := $(CURRENT_YAG_PDF)


DOC_GENERATED_FILES := $(HTML_TARGET) $(PDF_TARGET)



PROJECT_CSS := pygments-default.css,osdl-snake.css

PROJECT_ICON := osdl-snake-icon.png

WEB_CONTENT = *.html *.css *.pdf
#WEB_CONTENT = *.html *.css *.png *.pdf

# Read from the user's environment:
GITHUB_PAGES_BASE := $(shell basename "$(OSDL_SNAKE_WEB_MIRROR_BRANCH)")


# Default do-nothing target:
all:
	@echo "  Run 'make doc' to generate the YAG-OSDL documentation."


doc: html pdf



full-doc: $(DOC_GENERATED_FILES)


# This link does not need to be in version control:
create-links:
	@/bin/ln -sf $(CURRENT_YAG_HTML) index.html


# Expected here to be read from the environment; adapt accordingly:
MYRIAD_TOP = ${CEYLAN_MYRIAD}

DOCUTILS_TOP = .

include $(MYRIAD_TOP)/doc/GNUmakerules-docutils.inc

html: clean-doc $(HTML_TARGET)

pdf: clean-doc $(PDF_TARGET)


clone-mirror:
	@ echo "  Creating a separate repository in $(GITHUB_PAGES_BASE)"
	@cd ../../ && git clone https://github.com/Olivier-Boudeville/OSDL-Snake.git $(GITHUB_PAGES_BASE) && cd $(GITHUB_PAGES_BASE) && git checkout -b gh-pages
	@echo "Please remove all initial content in that selected 'gh-pages' branch."



export-doc: clean-doc full-doc export-to-official export-to-mirror


# Note: in terms of web roots, currently there is only 'Snake', not 'OSDL-Snake'
# (and 'Ceylan-Snake').


# Drawback: scp will not preserve symlinks, it will duplicate files instead.
#
# rsync would not, but requires a different source layout (copies a full tree,
# not a set of files), so currently not used:
# rsync -avze "ssh $(SP)" $(SOME_WEB_TREE) $(WEB_SRV):$(WEB_ROOT)/Snake/
#
export-to-official: create-links $(DOC_GENERATED_FILES)
	@echo "   Exporting YAG-OSDL documentation to official website ($(WEB_SRV))"
	@/bin/scp $(SP) -r $(WEB_CONTENT) $(WEB_SRV):$(WEB_ROOT)/Snake/


# H option for cp so that a local MathJax is copied in target branch:
export-to-mirror: create-links clean-doc create-links doc
	@echo "   Exporting YAG-OSDL documentation to mirror website in $(OSDL_SNAKE_WEB_MIRROR_BRANCH)"
	@/bin/cp -rfH $(WEB_CONTENT) $(OSDL_SNAKE_WEB_MIRROR_BRANCH) && cd $(OSDL_SNAKE_WEB_MIRROR_BRANCH) && git add . && git merge -s ours && git commit -m "YAG-OSDL doc updated." && git push && git pull --ff-only


clean: clean-doc-local

clean-doc: clean-doc-local clean-links


clean-doc-local:
	@echo "     Cleaning documentation"
	-@/bin/rm -f *.aux *.log *.maf *.mtc* *.stc* *.tex *.toc $(DOC_GENERATED_FILES)


clean-links-local:
	-@/bin/rm -f index.html


info: info-web
	@echo "MYRIAD_TOP = $(MYRIAD_TOP)"


info-web:
	@echo "HTML_TARGET = $(HTML_TARGET)"
	@echo "SP = $(SP)"
	@echo "WEB_CONTENT = $(WEB_CONTENT)"
	@echo "WEB_SRV = $(WEB_SRV)"
	@echo "WEB_ROOT = $(WEB_ROOT)"
	@echo "OSDL_SNAKE_WEB_MIRROR_BRANCH = $(OSDL_SNAKE_WEB_MIRROR_BRANCH)"
	@echo "GITHUB_PAGES_BASE = $(GITHUB_PAGES_BASE)"
