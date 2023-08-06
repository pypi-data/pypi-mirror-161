# STREAM SAGE PYTHON LOGGER

## Log format

```shell
[<Date> <Time>][<logLevel>][<context>][<file>:<line>][<LoggerOptionalParams>] <message>
```

Date format: `YYYY-MM-DD`<br/>
Time format: `HH:mm:ss`

LoggerOptionalParams exampe:
```shell
logger.info("hi", extra={"user": "USER"})
```


## Logger output

```shell
[2022-04-15 12:06:34][info][Sample App][samle_file.py:1] Sample LOG message
[2022-04-15 03:06:00][info][Sample App][samle_file.py:1][messageId:some-message-id][domain:message-domain] Sample LOG message with additional params
[2022-04-15 12:06:34][error][Sample App][samle_file.py:1][customer:customer] Sample ERROR message with additional params
[2022-04-15 21:43:36][debug][Sample App][samle_file.py:1][debugLevel:5] Sample Debug message in debug level 5
[2022-04-15 10:20:28][debug][Sample App][samle_file.py:1][debugLevel:2] Sample Debug message in debug level 2
```

# Installation
