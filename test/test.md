cd test
docker build -f Dockerfile.test -t test .
docker run --rm test-lambda