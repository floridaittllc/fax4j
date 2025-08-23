# HTTP Fax Server

This module provides a minimal Spring Boot based HTTP bridge for fax4j.

## Running

```bash
mvn spring-boot:run
```

## API

* `POST /fax` – submit a fax job using multipart form data. Required fields: `file`, `filename`, and `targetaddress`.
* `GET /fax/{id}` – retrieve fax job status.

### Sample requests

```bash
# submit a fax
curl -F "file=@/path/to/myfax.txt" -F "filename=myfax.txt" -F "targetaddress=555-555" http://localhost:8080/fax

# check status
curl http://localhost:8080/fax/<fax-id>
```
