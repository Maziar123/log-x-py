"""
13_complex_data_pipeline.py - Complex Data Processing Pipeline
Demonstrates 7-level nested structure with ETL operations and microservices
"""

import asyncio
import sys
import time

from logxpy import aaction, log, to_file

to_file(sys.stdout)


# ============================================================================
# Level 1: Pipeline Orchestrator (Entry Point)
# ============================================================================
class PipelineOrchestrator:
    """Main pipeline orchestration service"""

    @log.logged
    async def run_pipeline(self, pipeline_id: str, data_source: str, config: dict):
        """LEVEL 1: Orchestrate complete data pipeline"""
        log.info("▓" * 60)
        log.info("▓▓▓  🚀 DATA PIPELINE EXECUTION START  ▓▓▓")
        log.info("▓" * 60)

        async with aaction("pipeline_execution", pipeline_id=pipeline_id, source=data_source):
            with log.scope(pipeline_id=pipeline_id):
                # Initialize pipeline
                context = await self._initialize_pipeline(pipeline_id, config)

                # Extract phase
                extracted = await DataExtractor().extract_data(data_source, context)

                # Transform phase
                transformed = await DataTransformer().transform_data(extracted, config)

                # Load phase
                loaded = await DataLoader().load_data(transformed, config)

                # Validate & Monitor
                await PipelineMonitor().validate_and_monitor(pipeline_id, loaded)

                log.info("▓" * 60)
                log.success("▓▓▓  ✅ PIPELINE COMPLETED SUCCESSFULLY  ▓▓▓")
                log.info("▓" * 60)

                return {
                    "pipeline_id": pipeline_id,
                    "status": "completed",
                    "records_processed": loaded["count"],
                    "duration_ms": context["duration"],
                }

    @log.logged
    async def _initialize_pipeline(self, pipeline_id: str, config: dict):
        """LEVEL 2: Initialize pipeline context"""
        log.info("░" * 60)
        log.info("░░░  📋 INITIALIZATION PHASE  ░░░")
        log.info("░" * 60)
        await asyncio.sleep(0.01)

        return {
            "pipeline_id": pipeline_id,
            "start_time": time.time(),
            "duration": 0,
            "config": config,
        }


# ============================================================================
# Level 2: Data Extractor (Extract Phase)
# ============================================================================
class DataExtractor:
    """Extracts data from various sources"""

    @log.logged
    async def extract_data(self, source: str, context: dict):
        """LEVEL 2: Extract data from source"""
        log.info("░" * 60)
        log.info("░░░  📥 EXTRACTION PHASE  ░░░")
        log.info("░" * 60)

        async with aaction("extraction", source=source):
            # Determine source type
            source_type = await self._detect_source_type(source)

            # Connect to source
            connection = await self._establish_connection(source, source_type)

            # Fetch data
            raw_data = await self._fetch_raw_data(connection, source_type)

            # Validate extraction
            validated = await self._validate_extraction(raw_data)

            log.success("✓ Extraction complete", records=len(validated))
            return validated

    @log.logged
    async def _detect_source_type(self, source: str):
        """LEVEL 3: Detect data source type"""
        log.info("  ├── Detecting source type", source=source)
        await asyncio.sleep(0.005)

        # Advanced source detection
        detected = await SourceDetector().analyze_source(source)

        log.debug(f"  │   ├─ Type: {detected['type']}")
        return detected

    @log.logged
    async def _establish_connection(self, source: str, source_type: dict):
        """LEVEL 3: Establish connection to source"""
        log.info("  ├── Establishing connection")

        # Get connection manager
        manager = await ConnectionManager().get_connection(source, source_type)

        log.success("  │   ✓ Connection established")
        return manager

    @log.logged
    async def _fetch_raw_data(self, connection: dict, source_type: dict):
        """LEVEL 3: Fetch raw data"""
        log.info("  ├── Fetching raw data")
        await asyncio.sleep(0.02)

        # Stream data in chunks
        chunks = await DataStreamer().stream_data(connection, batch_size=1000)

        log.debug(f"  │   ├─ Chunks fetched: {len(chunks)}")
        return chunks

    @log.logged
    async def _validate_extraction(self, raw_data: list):
        """LEVEL 3: Validate extracted data"""
        log.info("  └── Validating extraction")

        # Run validation rules
        validated = await ValidationEngine().validate_raw_data(raw_data)

        log.success(f"  ✓ Validation passed: {len(validated)} records")
        return validated


# ============================================================================
# Level 3: Source Detector (Discovery Service)
# ============================================================================
class SourceDetector:
    """Detects and analyzes data sources"""

    @log.logged
    async def analyze_source(self, source: str):
        """LEVEL 3: Analyze data source"""
        log.debug("    ├── Analyzing source structure")

        # Probe source
        metadata = await self._probe_source(source)

        # Infer schema
        schema = await self._infer_schema(metadata)

        return {
            "type": metadata["type"],
            "schema": schema,
            "format": metadata["format"],
        }

    @log.logged
    async def _probe_source(self, source: str):
        """LEVEL 4: Probe source for metadata"""
        log.debug("      ├── Probing source", source=source)
        await asyncio.sleep(0.01)

        # Deep inspection
        inspection = await SourceInspector().deep_inspect(source)

        return {
            "type": "database",
            "format": "postgresql",
            "version": inspection["version"],
        }

    @log.logged
    async def _infer_schema(self, metadata: dict):
        """LEVEL 4: Infer data schema"""
        log.debug("      └── Inferring schema")
        await asyncio.sleep(0.005)
        return {"columns": ["id", "name", "value", "timestamp"], "types": ["int", "str", "float", "datetime"]}


# ============================================================================
# Level 4: Source Inspector (Deep Analysis)
# ============================================================================
class SourceInspector:
    """Deep source inspection"""

    @log.logged
    async def deep_inspect(self, source: str):
        """LEVEL 4: Deep source inspection"""
        log.debug("        ├── Deep inspection")

        # Check capabilities
        capabilities = await self._check_capabilities(source)

        # Analyze performance
        perf = await self._analyze_performance(source)

        return {
            "version": "14.5",
            "capabilities": capabilities,
            "performance": perf,
        }

    @log.logged
    async def _check_capabilities(self, source: str):
        """LEVEL 5: Check source capabilities"""
        log.debug("          ├── Checking capabilities")
        await asyncio.sleep(0.005)

        # Query feature support
        features = await self._query_features(source)

        return features

    @log.logged
    async def _query_features(self, source: str):
        """LEVEL 6: Query available features"""
        log.debug("            ├── Querying features")
        await asyncio.sleep(0.005)

        # Check feature flags
        flags = await self._read_feature_flags()

        return flags

    @log.logged
    async def _read_feature_flags(self):
        """LEVEL 7: Read feature configuration (DEEPEST)"""
        log.debug("              └── LEVEL 7: Reading feature flags")
        await asyncio.sleep(0.002)
        return {"streaming": True, "batch": True, "incremental": True}

    @log.logged
    async def _analyze_performance(self, source: str):
        """LEVEL 5: Analyze source performance"""
        log.debug("          └── Analyzing performance")
        await asyncio.sleep(0.005)
        return {"latency_ms": 15, "throughput": "1000 rec/s"}


# ============================================================================
# Level 3: Connection Manager
# ============================================================================
class ConnectionManager:
    """Manages connections to data sources"""

    @log.logged
    async def get_connection(self, source: str, source_type: dict):
        """LEVEL 3: Get connection from pool"""
        log.debug("    ├── Getting connection from pool")

        # Acquire from pool
        conn = await self._acquire_from_pool(source_type)

        # Configure connection
        await self._configure_connection(conn, source_type)

        return conn

    @log.logged
    async def _acquire_from_pool(self, source_type: dict):
        """LEVEL 4: Acquire connection from pool"""
        log.debug("      ├── Acquiring from pool", type=source_type["type"])
        await asyncio.sleep(0.01)
        return {"conn_id": "pool_conn_42", "status": "active"}

    @log.logged
    async def _configure_connection(self, conn: dict, source_type: dict):
        """LEVEL 4: Configure connection settings"""
        log.debug("      └── Configuring connection")
        await asyncio.sleep(0.005)


# ============================================================================
# Level 3: Data Streamer
# ============================================================================
class DataStreamer:
    """Streams data in chunks"""

    @log.logged
    async def stream_data(self, connection: dict, batch_size: int):
        """LEVEL 3: Stream data in batches"""
        log.debug("    ├── Streaming data", batch_size=batch_size)
        await asyncio.sleep(0.02)

        # Simulate streaming 3 batches
        batches = []
        for i in range(3):
            batch = await self._fetch_batch(connection, i, batch_size)
            batches.append(batch)

        return batches

    @log.logged
    async def _fetch_batch(self, connection: dict, batch_num: int, size: int):
        """LEVEL 4: Fetch single batch"""
        log.debug(f"      ├── Batch {batch_num}", size=size)
        await asyncio.sleep(0.01)
        return [{"id": i, "value": i * 10} for i in range(size)]


# ============================================================================
# Level 3: Validation Engine
# ============================================================================
class ValidationEngine:
    """Validates data quality"""

    @log.logged
    async def validate_raw_data(self, raw_data: list):
        """LEVEL 3: Validate raw data"""
        log.debug("    └── Validating data quality")

        # Schema validation
        await self._validate_schema(raw_data)

        # Quality checks
        await self._quality_checks(raw_data)

        return raw_data

    @log.logged
    async def _validate_schema(self, data: list):
        """LEVEL 4: Validate schema"""
        log.debug("      ├── Schema validation")
        await asyncio.sleep(0.005)

    @log.logged
    async def _quality_checks(self, data: list):
        """LEVEL 4: Data quality checks"""
        log.debug("      └── Quality checks")
        await asyncio.sleep(0.005)


# ============================================================================
# Level 2: Data Transformer (Transform Phase)
# ============================================================================
class DataTransformer:
    """Transforms data"""

    @log.logged
    async def transform_data(self, data: list, config: dict):
        """LEVEL 2: Transform extracted data"""
        log.info("░" * 60)
        log.info("░░░  🔄 TRANSFORMATION PHASE  ░░░")
        log.info("░" * 60)

        async with aaction("transformation"):
            # Apply transformations
            cleaned = await self._clean_data(data)
            enriched = await self._enrich_data(cleaned)
            aggregated = await self._aggregate_data(enriched)

            log.success("✓ Transformation complete")
            return aggregated

    @log.logged
    async def _clean_data(self, data: list):
        """LEVEL 3: Clean data"""
        log.info("  ├── Cleaning data")

        # Remove duplicates
        deduped = await DataCleaner().remove_duplicates(data)

        # Handle missing values
        cleaned = await DataCleaner().handle_missing_values(deduped)

        log.success("  │   ✓ Data cleaned")
        return cleaned

    @log.logged
    async def _enrich_data(self, data: list):
        """LEVEL 3: Enrich data"""
        log.info("  ├── Enriching data")

        # Add derived fields
        enriched = await EnrichmentService().add_derived_fields(data)

        # Lookup external data
        enhanced = await EnrichmentService().lookup_external_data(enriched)

        log.success("  │   ✓ Data enriched")
        return enhanced

    @log.logged
    async def _aggregate_data(self, data: list):
        """LEVEL 3: Aggregate data"""
        log.info("  └── Aggregating data")
        await asyncio.sleep(0.01)
        log.success("  ✓ Data aggregated")
        return data


# ============================================================================
# Level 3: Data Cleaner
# ============================================================================
class DataCleaner:
    """Cleans and normalizes data"""

    @log.logged
    async def remove_duplicates(self, data: list):
        """LEVEL 3: Remove duplicate records"""
        log.debug("    ├── Removing duplicates")
        await asyncio.sleep(0.01)
        return data

    @log.logged
    async def handle_missing_values(self, data: list):
        """LEVEL 3: Handle missing values"""
        log.debug("    └── Handling missing values")
        await asyncio.sleep(0.01)
        return data


# ============================================================================
# Level 3: Enrichment Service
# ============================================================================
class EnrichmentService:
    """Enriches data with additional information"""

    @log.logged
    async def add_derived_fields(self, data: list):
        """LEVEL 3: Add derived fields"""
        log.debug("    ├── Adding derived fields")
        await asyncio.sleep(0.01)
        return data

    @log.logged
    async def lookup_external_data(self, data: list):
        """LEVEL 3: Lookup external data"""
        log.debug("    └── Looking up external data")

        # Call external API
        _external = await ExternalAPIClient().fetch_enrichment_data(data)

        return data


# ============================================================================
# Level 4: External API Client
# ============================================================================
class ExternalAPIClient:
    """Client for external APIs"""

    @log.logged
    async def fetch_enrichment_data(self, data: list):
        """LEVEL 4: Fetch from external API"""
        log.debug("      ├── Calling external API")

        # Authenticate
        token = await self._authenticate()

        # Make request
        response = await self._make_request(token, data)

        return response

    @log.logged
    async def _authenticate(self):
        """LEVEL 5: Authenticate with external service"""
        log.debug("        ├── Authenticating")
        await asyncio.sleep(0.01)
        return "token_xyz"

    @log.logged
    async def _make_request(self, token: str, data: list):
        """LEVEL 5: Make HTTP request"""
        log.debug("        └── Making HTTP request")
        await asyncio.sleep(0.02)
        return {"status": "success", "data": []}


# ============================================================================
# Level 2: Data Loader (Load Phase)
# ============================================================================
class DataLoader:
    """Loads data to destination"""

    @log.logged
    async def load_data(self, data: list, config: dict):
        """LEVEL 2: Load data to destination"""
        log.info("░" * 60)
        log.info("░░░  📤 LOADING PHASE  ░░░")
        log.info("░" * 60)

        async with aaction("loading"):
            # Prepare destination
            dest = await self._prepare_destination(config)

            # Batch write
            result = await self._batch_write(data, dest)

            # Verify load
            await self._verify_load(result)

            log.success("✓ Loading complete", records=len(data))
            return {"count": len(data), "destination": dest}

    @log.logged
    async def _prepare_destination(self, config: dict):
        """LEVEL 3: Prepare destination"""
        log.info("  ├── Preparing destination")
        await asyncio.sleep(0.01)
        return {"type": "data_warehouse", "table": "processed_data"}

    @log.logged
    async def _batch_write(self, data: list, dest: dict):
        """LEVEL 3: Batch write to destination"""
        log.info("  ├── Writing batches")
        await asyncio.sleep(0.02)
        return {"rows_inserted": len(data)}

    @log.logged
    async def _verify_load(self, result: dict):
        """LEVEL 3: Verify load success"""
        log.info("  └── Verifying load")
        await asyncio.sleep(0.005)


# ============================================================================
# Level 2: Pipeline Monitor
# ============================================================================
class PipelineMonitor:
    """Monitors pipeline execution"""

    @log.logged
    async def validate_and_monitor(self, pipeline_id: str, result: dict):
        """LEVEL 2: Validate and monitor"""
        log.info("░" * 60)
        log.info("░░░  📊 MONITORING & VALIDATION  ░░░")
        log.info("░" * 60)

        # Collect metrics
        await self._collect_metrics(pipeline_id, result)

        # Send alerts if needed
        await self._check_alerts(pipeline_id, result)

        log.success("✓ Monitoring complete")

    @log.logged
    async def _collect_metrics(self, pipeline_id: str, result: dict):
        """LEVEL 3: Collect metrics"""
        log.info("  ├── Collecting metrics")
        await asyncio.sleep(0.005)

    @log.logged
    async def _check_alerts(self, pipeline_id: str, result: dict):
        """LEVEL 3: Check alert conditions"""
        log.info("  └── Checking alerts")
        await asyncio.sleep(0.005)


# ============================================================================
# Main Execution
# ============================================================================
async def main():
    log.info("\n\n")
    log.info("▓" * 60)
    log.info("▓▓▓" + " " * 54 + "▓▓▓")
    log.info("▓▓▓  🔧 DATA PIPELINE ORCHESTRATION SYSTEM" + " " * 16 + "▓▓▓")
    log.info("▓▓▓" + " " * 54 + "▓▓▓")
    log.info("▓" * 60)
    log.info("\n")

    # Create orchestrator
    orchestrator = PipelineOrchestrator()

    # Run pipeline
    try:
        result = await orchestrator.run_pipeline(
            pipeline_id="PIPE_2024_001",
            data_source="postgresql://prod-db/sales",
            config={
                "batch_size": 1000,
                "parallel_workers": 4,
                "retry_policy": "exponential_backoff",
            },
        )

        log.info("\n")
        log.info("▓" * 60)
        log.success("▓▓▓  🎉 PIPELINE EXECUTION SUMMARY  ▓▓▓")
        log.info("▓" * 60)
        log.info(f"Pipeline ID: {result['pipeline_id']}")
        log.info(f"Status: {result['status']}")
        log.info(f"Records Processed: {result['records_processed']}")
        log.info("▓" * 60)
        log.info("\n\n")

    except Exception:
        log.exception("❌ Pipeline execution failed")


if __name__ == "__main__":
    asyncio.run(main())
