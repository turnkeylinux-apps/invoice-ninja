COMMON_OVERLAYS = github-latest-release artisan

PHP_MEMORY_LIMIT=512M

include $(FAB_PATH)/common/mk/turnkey/composer.mk
include $(FAB_PATH)/common/mk/turnkey/lamp.mk
include $(FAB_PATH)/common/mk/turnkey.mk
