LOCAL = package
GIT = git
.PHONY: all info $(LOCAL) $(GIT)

all: info

info:
	@echo "LOCAL: $(LOCAL)"
	@echo "GIT: $(GIT)"

# LOCAL
package:
	@bash ./scripts/local/package.sh

# GIT
git:
	@bash ./scripts/git.sh
	