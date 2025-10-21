FROM php:8.2-alpine3.22
RUN docker-php-ext-configure bcmath \
	&& docker-php-ext-install -j$(nproc) bcmath
COPY diceroller.php .
CMD ["php", "-S", "0.0.0.0:6005", "diceroller.php"]
