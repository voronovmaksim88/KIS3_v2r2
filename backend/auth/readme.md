``` shell
# Генерация RSA приватного ключа размером 2048 бит:
openssl genrsa -out jwt-private.pem 2048
```

``` shell
# Извлечение публичного ключа из пары ключей и сохранение в формате PEM:
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```
