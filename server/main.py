import logging
import grpc
from concurrent import futures
import time

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from helloworld_pb2 import HelloReply
from helloworld_pb2_grpc import GreeterServicer, add_GreeterServicer_to_server

import socket

logging.basicConfig(level=logging.INFO)


# Configure trace provider and OTLP exporter
resource = Resource(attributes={"service.name": "dummy-client"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Send traces via OTLP gRPC to collector (default localhost:4317)
otlp_exporter = OTLPSpanExporter(endpoint="otel-collector:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

def resolve(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        print(f"{hostname} resolved to {ip}")
        return f"{hostname} resolved to {ip}"
    except socket.error as e:
        print(f"DNS resolution failed for {hostname}: {e}")
        return f"DNS resolution failed for {hostname}: {e}"


# Create tracer
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("my-span"):

    x = resolve("tempo")
    logging.info(f"inside tracer {x}")

# gRPC service implementation
class Greeter(GreeterServicer):
    def SayHello(self, request, context):
        with tracer.start_as_current_span("SayHello"):
            print(f"replying with {request.name}")
            mes = resolve("otel-collector")
            return HelloReply(message=f"Hello, {mes}!")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    print("Starting gRPC server on port 50051...")
    server.start()
    print("gRPC server on port 50051 is listening...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Shutting down server.")
        server.stop(0)

if __name__ == '__main__':
    serve()
