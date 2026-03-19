init:
	# link fastfetch config into user's config dir
	mkdir -p $(HOME)/.config/fastfetch
	ln -sf $(PWD)/ffswap/config.jsonc $(HOME)/.config/fastfetch/config.jsonc

	# create executable script
	printf '#!/bin/sh\ncd $(PWD) || exit\npython3 -m ffswap "$$@"\n' | sudo tee /usr/local/bin/ffswap > /dev/null
	sudo chmod +x /usr/local/bin/ffswap

.PHONY: init test
