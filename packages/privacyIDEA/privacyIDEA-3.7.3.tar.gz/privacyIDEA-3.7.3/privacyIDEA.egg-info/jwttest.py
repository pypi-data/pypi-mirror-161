import jwt
import datetime
import os
import binascii

privkey = b"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCpMoaJiCNrCtux
vZxYZJMm3MTQ1S93gcIMCqvGsCT7Av3ZA9/rRQU/56HAB9JbGTbFkzqNQFS8ofvD
7WbPS0jJ4nUrxVJGE1Zxr4+fu35c2lOZVgIDTmvaKZnBiOHJSoK2/SvlBZTrYRsP
VSWUefrMc+uE++fy5zFd6ddddX28Nxb6uYVwD4n5KnaySgggFLAsrwUt3r4lfw4+
a8YQ3gyu9+wKuabsF9sLR/SGUid65NRoaZFCtJ9HlcdOZSYXk3vObukY+o0wJ9aD
jjP+6OU0ii0dlJc3P0p1UmFpW9MRmkn9UCuRr7PaiGcvYiidTib7OiRxh1hgcYhn
F/4K+ColAgMBAAECggEBAIjCw0Z1mRNTwoKnnbFBEkRuXFPkjaqOYrfzBCfkhu+x
2lfIrvzvXC/sXaznZZunBMOsnr4/yn5yfBtBUEGsO5ibiFQp+beUt+HKo0/ccGZD
PyGJCLV9dOXxjEuIBeD7bi7U8t76pQWhBwtcqrSZ6CPMawmhyDlpsFiVxDPR3SD9
IgFny05Gqjd6R5Ewy9ULmrGxi2xFxSrrAafj2U3FxuHgeba44Q1S2kQPDBuzB5LM
yNHIfoi1tHxvMbwPQ/Ui0se8QbhS9CqsCaE54jak2+0oP6+sutrH0+KWs+EWo2y9
Th2bOz8BxEfMTd50kTSjRgfQ0eHubtVxbpHLtgvDSf0CgYEA06RBYNTc/NjHs8NT
fr0tbySDafjEpFHjPoVNzZjS18bCI845EurPx6Cqmt+sT2wu/4gex0iWWIt1KPau
I3BiMLg7p89lZrK/eMeEMC3IxIlnhWF2N0LjPB9zKqWakBQEt4G9ZuY1Yu2g3amp
hk3FC5WDGF4RrKZwpDo33XtLXsMCgYEAzKjmmrJRJ3EoA/qJFPQ9BTUEJG01RdMV
+55bMwcpjrCR7uHQkH7ahYo5N4TpEdUm1JaY+FXthMzIQynuK48+NODD8nz+clSZ
i+x5a308M9qieExD00dHnZF/yUDDcFBtRzvjED3eTp4UwgbgZNVjVPBzlHqRS52M
LE5sIno9lPcCgYBELLoerhMNo+sYfggMYHYdQj7OySLW58Xy4tAANYVdmpn5HLoH
3PnXjWrHfturreapy7hWa4x6s1mnO2c25UHL/dzBnq5EWboR9vse5fCxVq2xKocB
IBvAx0S67SOP29L1JebUGb4Cwxc5sCh6qdyacawMEmlRG0BXtqU+RDQwLwKBgDJ2
Jr3X37io5uPsPyaCfhUtmELfBnab8FylE/mF95IuKR1MYl9uV7T7etYcmFcERlm+
dCMvFKxczbf5u7bTz9O747SDaz2HbICaoumE7HYgn1SoAUUz2w2X1Xkq1cV4nykk
M/1KM+kQgy/AAE38a0yDKQxgGDkbtHcsMu9hUpPLAoGAOttFtXd+lt45VoJhYZyM
NHZDwxGMVb2AkjzwOgOI217mJFQsU+44xu/1F8bxj75O/86+vMB53H+MdMYV3w7P
kbonwF0UMxVhPCKvzaIePaA0oKdD/QMxD8ZCrzWJBD1mVCazNYGjYZbTjoDyLS7X
FZJtOqanwz+wAEnShjxzozE=
-----END PRIVATE KEY-----
"""

pubkey = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqTKGiYgjawrbsb2cWGST
JtzE0NUvd4HCDAqrxrAk+wL92QPf60UFP+ehwAfSWxk2xZM6jUBUvKH7w+1mz0tI
yeJ1K8VSRhNWca+Pn7t+XNpTmVYCA05r2imZwYjhyUqCtv0r5QWU62EbD1UllHn6
zHPrhPvn8ucxXenXXXV9vDcW+rmFcA+J+Sp2skoIIBSwLK8FLd6+JX8OPmvGEN4M
rvfsCrmm7BfbC0f0hlIneuTUaGmRQrSfR5XHTmUmF5N7zm7pGPqNMCfWg44z/ujl
NIotHZSXNz9KdVJhaVvTEZpJ/VArka+z2ohnL2IonU4m+zokcYdYYHGIZxf+Cvgq
JQIDAQAB
-----END PUBLIC KEY-----"""

payload = {"username": "hans",
                "realm": "realm1",
                "nonce": binascii.hexlify(os.urandom(10)),
                "role": "admin",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)}

#payload = {"some": "thing"}

print("#### ENCODE ####")
r = jwt.encode(payload, privkey, algorithm='RS256')
print r

print("#### DECODE ####")
r = jwt.decode(r, pubkey, algorithm="RS256")
print r
