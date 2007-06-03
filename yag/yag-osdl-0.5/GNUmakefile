ARCHIVE_DIR=$$HOME/Archive

PROJECT_VERSION = 0.5
PROJECT_NAME    = yag-osdl-$(PROJECT_VERSION)

ARCHIVE_FILE    = $(ARCHIVE_DIR)/`date +'%Y%m%d'`-$(PROJECT_NAME).tar.bz2

FILES = `cd ..; find $(PROJECT_NAME) \( -path '*CVS*' -prune -o -path '*deprecated*' -prune \) -a \( -type d -a ! -name '*CVS*' -a ! -name '*deprecated*' \) -o \( -type f -a ! -name '*.pyc' \)`


.PHONY : bz2 info


bz2:
	@echo "    Saving $(PROJECT_NAME) in $(ARCHIVE_FILE)"
	@FILE_LIST=$(FILES); cd .. ; tar cjf $(ARCHIVE_FILE) $$FILE_LIST
	

info:
	@echo "PROJECT_NAME = $(PROJECT_NAME)"
	@echo "ARCHIVE_FILE = $(ARCHIVE_FILE)"	
	@echo "FILES        = $(FILES)"
