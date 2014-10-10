package com.spotify.heroic.statistics;

public interface MetricManagerReporter {
    CallbackReporter.Context reportGetAllRows();

    CallbackReporter.Context reportQueryMetrics();

    CallbackReporter.Context reportStreamMetrics();

    CallbackReporter.Context reportStreamMetricsChunk();

    CallbackReporter.Context reportFindTimeSeries();

    CallbackReporter.Context reportWrite();

    CallbackReporter.Context reportRpcQueryMetrics();

    MetricBackendReporter newBackend(String id);
}