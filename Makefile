# $ make
# $ make all
all: info

LOCAL = package
GIT = git
.PHONY: info $(LOCAL) $(GIT)

# $ make info
info:
	@echo "LOCAL: $(LOCAL)"
	@echo "GIT: $(GIT)"

# $ make package
package:
	@bash ./scripts/local/package.sh

# $ make git
git:
	@bash ./scripts/git.sh
	