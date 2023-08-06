import datetime
import logging
from enum import Enum
from threading import Timer, Lock

from elasticsearch import Elasticsearch, helpers, RequestsHttpConnection, JSONSerializer


class IndexNameFrequency(Enum):
    """ Index type supported
    the handler supports
    - Daily indices
    - Weekly indices
    - Monthly indices
    - Year indices
    """
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2
    YEARLY = 3


class ElasticSerializer(JSONSerializer):
    """ JSON serializer inherited from the elastic search JSON serializer
    Allows to serialize logs for a elasticsearch use.
    Manage the record.exc_info containing an exception type.
    """

    def default(self, data):
        """ Default overrides the elasticsearch default method
        Allows to transform unknown types into strings
        :params data: The data to serialize before sending it to elastic search
        """
        try:
            return super(ElasticSerializer, self).default(data)
        except TypeError:
            return str(data)

class ElasticHandler(logging.Handler):
    # region Defaults for the class
    __DEFAULT_AUTH_USER = ''
    __DEFAULT_AUTH_PASSWD = ''
    __DEFAULT_INDEX_FREQUENCY = IndexNameFrequency.DAILY
    __DEFAULT_BUFFER_SIZE = 1000
    __DEFAULT_FLUSH_FREQ_IN_SEC = 1
    __DEFAULT_ADDITIONAL_FIELDS = {}
    __DEFAULT_ES_INDEX_NAME = 'python_logger'
    __DEFAULT_ES_DOC_TYPE = 'python_log'
    __DEFAULT_RAISE_ON_EXCEPTION = False
    __DEFAULT_TIMESTAMP_FIELD_NAME = "timestamp"
    __LOGGING_FILTER_FIELDS = ['msecs',
                               'relativeCreated',
                               'levelno',
                               'created']

    # region _INDEX_FREQUENCY_FUNCION_DICT
    @staticmethod
    def __get_es_datetime_str(timestamp):
        """ Returns elasticsearch utc formatted time for an epoch timestamp
        :param timestamp: epoch, including milliseconds
        :return: A string valid for elasticsearch time record
        """
        current_date = datetime.datetime.utcfromtimestamp(timestamp)
        return "{0!s}.{1:03d}Z".format(current_date.strftime('%Y-%m-%dT%H:%M:%S'), int(current_date.microsecond / 1000))

    @staticmethod
    def _get_daily_index_name(es_index_name):
        """ Returns elasticearch index name
        :param: index_name the prefix to be used in the index
        :return: A srting containing the elasticsearch indexname used which should include the date.
        """
        return "{0!s}-{1!s}".format(es_index_name, datetime.datetime.now().strftime('%Y.%m.%d'))

    @staticmethod
    def _get_weekly_index_name(es_index_name):
        """ Return elasticsearch index name
        :param: index_name the prefix to be used in the index
        :return: A srting containing the elasticsearch indexname used which should include the date and specific week
        """
        current_date = datetime.datetime.now()
        start_of_the_week = current_date - datetime.timedelta(days=current_date.weekday())
        return "{0!s}-{1!s}".format(es_index_name, start_of_the_week.strftime('%Y.%m.%d'))

    @staticmethod
    def _get_monthly_index_name(es_index_name):
        """ Return elasticsearch index name
        :param: index_name the prefix to be used in the index
        :return: A srting containing the elasticsearch indexname used which should include the date and specific moth
        """
        return "{0!s}-{1!s}".format(es_index_name, datetime.datetime.now().strftime('%Y.%m'))

    @staticmethod
    def _get_yearly_index_name(es_index_name):
        """ Return elasticsearch index name
        :param: index_name the prefix to be used in the index
        :return: A srting containing the elasticsearch indexname used which should include the date and specific year
        """
        return "{0!s}-{1!s}".format(es_index_name, datetime.datetime.now().strftime('%Y'))

    _INDEX_FREQUENCY_FUNCION_DICT = {
        IndexNameFrequency.DAILY: _get_daily_index_name,
        IndexNameFrequency.WEEKLY: _get_weekly_index_name,
        IndexNameFrequency.MONTHLY: _get_monthly_index_name,
        IndexNameFrequency.YEARLY: _get_yearly_index_name
    }

    # endregion
    # endregion

    def __init__(self,
                 index_name: str,
                 host: str = "localhost",
                 port: int = 9200,
                 raise_on_indexing_exceptions=__DEFAULT_RAISE_ON_EXCEPTION,
                 buffer_size=__DEFAULT_BUFFER_SIZE,
                 default_timestamp_field_name=__DEFAULT_TIMESTAMP_FIELD_NAME,
                 es_additional_fields=__DEFAULT_ADDITIONAL_FIELDS,
                 es_doc_type=__DEFAULT_ES_DOC_TYPE,
                 flush_frequency_in_sec=__DEFAULT_FLUSH_FREQ_IN_SEC,
                 index_name_frequency: IndexNameFrequency = __DEFAULT_INDEX_FREQUENCY):

        logging.Handler.__init__(self)

        self._buffer = []
        self._buffer_lock = Lock()
        self._timer = None

        self.es_doc_type = es_doc_type
        self.buffer_size = buffer_size
        self.flush_frequency_in_sec = flush_frequency_in_sec
        self.index_name_frequency = index_name_frequency
        self.es_additional_fields = es_additional_fields.copy()
        self.default_timestamp_field_name = default_timestamp_field_name
        self.raise_on_indexing_exceptions = raise_on_indexing_exceptions
        self.serializer = ElasticSerializer()

        self._index_name_func = ElasticHandler._INDEX_FREQUENCY_FUNCION_DICT[self.index_name_frequency]
        self._client: Elasticsearch = Elasticsearch(hosts=host,
                                                    port=port,
                                                    use_ssl=False,
                                                    connection_class=RequestsHttpConnection,
                                                    serializer=self.serializer
                                                    )
        self._index_name = index_name

    def __schedule_flush(self):
        if self._timer is None:
            self._timer = Timer(self.flush_frequency_in_sec, self.flush)
            self._timer.setDaemon(True)
            self._timer.start()

    def ping(self):
        """ Returns True if the handler can ping the Elasticsearch servers
        Can be used to confirm the setup of a handler has been properly done and confirm
        that things like the authentication is working properly
        :return: A boolean, True if the connection against elasticserach host was successful
        """
        self._client.ping()

    def flush(self):
        """ Flushes the buffer into ES
        :return: None
        """
        if self._timer is not None and self._timer.is_alive():
            self._timer.cancel()
        self._timer = None

        if self._buffer:
            try:
                with self._buffer_lock:
                    logs_buffer = self._buffer
                    self._buffer = []
                actions = (
                    {
                        '_index': self._index_name_func.__func__(self._index_name),
                        '_source': log_record
                    }
                    for log_record in logs_buffer
                )
                helpers.bulk(
                    client=self._client,
                    actions=actions,
                    stats_only=True
                )
            except Exception as exception:
                if self.raise_on_indexing_exceptions:
                    raise

    def close(self):
        """ Flushes the buffer and release any outstanding resource
        :return: None
        """
        if self._timer is not None:
            self.flush()
        self._timer = None

    def emit(self, record):
        """ Emit overrides the abstract logging.Handler logRecord emit method
        Format and records the log
        :param record: A class of type ```logging.LogRecord```
        :return: None
        """
        self.format(record)

        rec = self.es_additional_fields.copy()
        for key, value in record.__dict__.items():
            if key not in ElasticHandler.__LOGGING_FILTER_FIELDS:
                if key == "args":
                    value = tuple(str(arg) for arg in value)
                rec[key] = "" if value is None else value
        rec[self.default_timestamp_field_name] = self.__get_es_datetime_str(record.created)
        with self._buffer_lock:
            self._buffer.append(rec)

        if len(self._buffer) >= self.buffer_size:
            self.flush()
        else:
            self.__schedule_flush()
