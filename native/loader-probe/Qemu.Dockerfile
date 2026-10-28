FROM delphi-qnx65:8.5
RUN apt-get update && apt-get install -y --no-install-recommends qemu-system-arm g++ && rm -rf /var/lib/apt/lists/*
