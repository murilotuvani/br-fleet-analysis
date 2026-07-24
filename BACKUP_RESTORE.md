
```bash
mongodump --uri="mongodb://mongoadmin:secret@127.0.0.1:27017/fleet?authSource=admin" --archive=fleet.gz --gzip
mongorestore --uri="mongodb://mongoadmin:secret@localhost:27017/fleet?authSource=admin" --archive=fleet.gz --gzip
```

