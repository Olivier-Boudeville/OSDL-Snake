ARCHIVE_DIR=$$HOME/Archive

PROJECT_VERSION = 0.6
PROJECT_NAME    = yag

ARCHIVE_FILE    = $(ARCHIVE_DIR)/`date +'%Y%m%d'`-$(PROJECT_NAME)-osdl-$(PROJECT_VERSION).tar.bz2


DIRS  = `cd yag; find . ! \( -type d -a -name '.svn*' -prune \) -a -type d`
FILES = `find $(PROJECT_NAME) ! \( -type d -a -name '.svn*' -prune \) -a -type f`

YAG_ARCHIVE_ROOT = yag-osdl-$(PROJECT_VERSION)

.PHONY : bz2 info


bz2:
	@echo "    Saving $(PROJECT_NAME) in $(ARCHIVE_FILE)"
	@cd .. && mkdir -p $(YAG_ARCHIVE_ROOT) && DIR_LIST=$(DIRS) && for d in $$DIR_LIST; do mkdir -p $(YAG_ARCHIVE_ROOT)/$$d; done && FILE_LIST=$(FILES) && for f in $$FILE_LIST; do cp -f $$f `echo $$f | sed 's|^yag|$(YAG_ARCHIVE_ROOT)|1'`; done; tar cjf $(ARCHIVE_FILE) $(YAG_ARCHIVE_ROOT) && rm -rf $(YAG_ARCHIVE_ROOT)
	

info:
	@echo "PROJECT_NAME = $(PROJECT_NAME)"
	@echo "ARCHIVE_FILE = $(ARCHIVE_FILE)"	
	@cd .. && echo "FILES        = $(FILES)"
	@cd .. && echo "DIRS        = $(DIRS)"
