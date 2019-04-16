# Fender Digital Platform Engineering Challenge

I've used Djagno, flask, falcon and Pyramid before, so I didn't want to use any of them for this challenge. It's an opportunity to learn some new things.

**sanic**

An asynchronous Python 3 web framework. I chose this for speed and as an excuse to learn how async programming in Python 3 works.

**email-validator**

Used to validate user email addresses. Deliverability checks are disabled for the sake of brevity.

**argon2_cffi**

C extension for the Argon2 hashing function. Argon2 was chosen as it is the most promising new algorithm to emerge in recent times: https://en.wikipedia.org/wiki/Argon2

**passlib**

Manages the salting, hashing and verification of user passwords (depends on argon2_cffi).

**aioredis**

An asynchronous Redis library. sanic is async, so it made sense to minimise the amount of blocking DB interactions.


## Design

Redis was chosen as the database as I am familiar with it, it is simple to use and it is extremely fast. I had initially attempted to use DynamoDB, but found that I was spending too much time trying to learn its intricacies. Redis, in contrast, is trivial to set up and start using.

Traditional database models are not used here. Initially, I tried to find a Redis ORM (similar to the one that we had created in Digit Game Studios), but none met my expectations. One potential candidate was *astra*. For the sake of simplicity, I reverted to using manual Redis commands.


## Running
> docker-compose -f docker-compose.yml up -d

The API should be available at `127.0.0.1:9443`.

## Tests
> $ pip install --upgrade -r requirements.txt && pytest

Functionality in the acceptance tests is not separated out, in order to allow the entire flow to be tested atomically and to avoid duplication. I would argue that such separation is unnecessary as a failure at any step in the process will break the entire functionality.

## Known issues

* Warnings are raised on some tests, but appear not to affect the outcome.
* The same database is used between the live application and tests, due to a failure to discover how to effectively override the globally shared reference to the Redis instance.
* Some modules are named generically, which could interfere with installed packages/modules.
* While transactions (MULTI/EXEC) are used, atomicity cannot be guaranteed.
* In accordance with the principle of least privilege, JSON Patch is deliberately not used; the client should (in this circumstance) not have the power to dictate to the server how to process requests.
* HTTPS/TLS is not enabled by default.
* Flow should be updated to use sanic's `token` attribute on requests and responses.
* There is no test coverage for multiple users and/or concurrency.