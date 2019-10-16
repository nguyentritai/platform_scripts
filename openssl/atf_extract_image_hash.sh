
#cert is expected in DER format
cert=$1
ext="1.3.6.1.4.1.4128.2100.201"
sha256_digest_size=64

openssl asn1parse -i -in $cert -inform der | grep -A 2 $ext | grep "OCTET STRING" | grep -o '.\{64\}$' 
