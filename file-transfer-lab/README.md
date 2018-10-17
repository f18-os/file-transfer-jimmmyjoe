# Threaded File Server Lab

I updated my previous lab's code instead of using the new nora repo.

## Usage

Start the server with
```
python3 fileServer.py &
```

And then start the batch of test clients with
```
python3 fileClient.py
```

But be quick, the server times out after 10 seconds of silence.

## Options

For more verbosity, change the logging.level value from INFO to DEBUG.