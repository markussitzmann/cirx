import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cirx")

# def count_box(fid):
#     count = 123456
#     logger.info("count box %s %s" % (fid, count))
#     return fid, count
#
#
# def chunk_creator(count_result, callback):
#     fid, count = count_result
#     chunk_size = 10000
#     chunk_number = int(count / chunk_size) + 1
#     logger.info("chunk number %s" % chunk_number)
#     chunks = range(0, chunk_number)
#     callback = subtask(callback)
#     return group(callback.clone([fid, count, chunk, chunk_size]) for chunk in chunks)()
#
#
# def chunk_box(fid, count, chunk_number, chunk_size):
#     records = range(1, count + 1)
#     chunk_records = [records[i:i + min(chunk_size, count)] for i in range(0, count, chunk_size)][chunk_number]
#     record: int = chunk_records[0]
#     last_record: int = chunk_records[-1]
#     logger.info("chunk box %s | %s %s | %s %s" % (count, chunk_number, chunk_size, record, last_record))
#     sleep(random.randint(1, 3))
#     logger.info("chunk box done %s | %s %s | %s %s" % (count, chunk_number, chunk_size, record, last_record))
#
#     return record, last_record



