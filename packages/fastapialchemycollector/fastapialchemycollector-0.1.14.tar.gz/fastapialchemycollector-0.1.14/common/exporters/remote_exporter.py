import logging
from typing import Sequence

import requests
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

from common.consts import METIS_REQUEST_SPAN_ATTRIBUTE_IDENTIFIER, \
    METIS_STATEMENT_SPAN_ATTRIBUTE
from common.utils.log import log

logger = logging.getLogger(__name__)


class MetisRemoteExporter(SpanExporter):
    @log
    def __init__(self, url, api_key):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update(
            {"x-api-key": api_key}
        )

    @log
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        try:

            data = [span.to_json(indent=None) for span in spans if
                    METIS_STATEMENT_SPAN_ATTRIBUTE in span.attributes or
                    METIS_REQUEST_SPAN_ATTRIBUTE_IDENTIFIER in span.attributes]
            if data:
                result = self.session.post(
                    url=self.url,
                    json=data
                )
                logger.debug(result.text)

            return SpanExportResult.SUCCESS
        except Exception as e:
            logger.error("Error exporting spans to remote: {}".format(e))
            return SpanExportResult.FAILURE
