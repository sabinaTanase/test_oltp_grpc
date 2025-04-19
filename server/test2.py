import logging
import time
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logging.basicConfig(level=logging.INFO)

logging.info("Hello from Python!")

# Configure trace provider and OTLP exporter
resource = Resource(attributes={"service.name": "dummy-client"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Send traces via OTLP gRPC to collector (default localhost:4317)
otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# Create tracer
tracer = trace.get_tracer(__name__)

# Start a span
with tracer.start_as_current_span("dummy-span"):
    print("Doing work in a traced span...")
    time.sleep(1)
    print("Done.")

print("Trace sent (if OTLP collector is running).")