# Snakebin

This is a very basic request bin. Use with uWSGI.

I made this for integrating with another project, as a way of handling asynchronous function calls which may take some time to complete and have a plain text output.

Remember to `flask db upgrade` first.

## Example usage

### List all jobs

`curl <GATEWAY>/api/v1.0/jobs`

```
{
  "jobs": []
}
```

### Add a new job

The header and job title are mandatory.

`curl -i -H "Content-Type: application/json" -X POST -d '{"title":"non-unique string up to 64 chars"}' http://<GATEWAY>/api/v1.0/jobs`

```
{
  "job": {
    "complete": false,
    "elapsed": {
      "human": "0 seconds",
      "seconds": 0
    },
    "id": 1,
    "results": "",
    "submitted": {
      "human": "2020/12/15 09:43",
      "seconds": 1608025436
    },
    "title": "non-unique string up to 64 chars"
  }
}
```

### Check on a job

Wether it's complete or not, get information about a job by referencing its number id.

`curl <GATEWAY>/api/v1.0/jobs/1`

```
{
  "job": {
    "complete": false,
    "elapsed": {
      "human": "2 minutes 38 seconds",
      "seconds": 158
    },
    "id": 1,
    "results": "",
    "submitted": {
      "human": "2020/12/15 09:43",
      "seconds": 1608025436
    },
    "title": "non-unique string up to 64 chars"
  }
}
```

### Update job

It will be marked complete and won't accept further updates.

`curl -i -H "Content-Type: application/json" -X PUT -d '{"results":"This data has no fixed length"}' <GATEWAY>/api/v1.0/jobs/1`

```
{
  "job": {
    "complete": true,
    "elapsed": {
      "human": "2 minutes 44 seconds",
      "seconds": 164
    },
    "id": 1,
    "results": "This data has no fixed length",
    "submitted": {
      "human": "2020/12/15 09:43",
      "seconds": 1608025436
    },
    "title": "non-unique string up to 64 chars"
  }
}
```
