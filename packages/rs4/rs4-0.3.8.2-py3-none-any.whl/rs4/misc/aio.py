try:
    import asyncio as asyncio_
except ImportError:
    AIO = None
else:
    # asyncio abbreviations --------------------------------------------
    class AIO:
        def carryout (self, coro, close = True):
            loop = asyncio_.get_event_loop ()
            loop.run_until_complete (coro)
            close and loop.close ()

        def ensure_future (self, *coro):
            return asyncio_.ensure_future (coro) # Task

        async def map (self, func, iterable):
            futures = [self.submit (func (item)) for item in iterable]
            results = await asyncio_.gather (*futures)

        async def threaded (self, func, *args, **karg):
            loop = asyncio_.get_event_loop()
            return await loop.run_in_executor (None, func, *args, **karg) # Future
