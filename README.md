# Fender Digital Platform Engineering Challenge

The **User** model should have the following properties (at minimum):

1. name
2. email
3. password

You should determine what, *if any*, additional models you will need.

**Endpoints**

All of these endpoints should be written from a user's perspective.

1. **User** Registration
2. Login (*token based*) - should return a token, given *valid* credentials
3. Logout - logs a user out
4. Update a **User**'s Information
5. Delete a **User**

**README**

Please include:
- a readme file that explains your thinking
- how to setup and run the project
- if you chose to use a database, include instructions on how to set that up
- if you have tests, include instructions on how to run them
- a description of what enhancements you might make if you had more time.
- Know issues *if any*

**Additional Info**

- We expect this project to take a few hours to complete (but no rush, take your time and do your best!)
- You can use Rails/Sinatra, Python, Go, node.js or shiny-new-framework X, as long as you tell us why you chose it and how it was a good fit for the challenge. 
- Feel free to use whichever database you'd like; we suggest Postgres or DynamoDB for noSql db. 
- Bonus points for security, specs, lambda, dynamodb and set up any free CI to test it.
- Do as little or as much as you like.

Please fork this repo and commit your code into that fork.  Show your work and process through those commits.

####

I've used Djagno, flask, falcon and Pyramid before, so I didn't want to use any of them for this challenge. It's an opportunity to learn some new things.

*sanic*

An asynchronous Python 3 web framework. I chose this for speed and as an excuse to learn how async programming in Python 3 works.

*email-validator*

Used to validate user email addresses. Deliverability checks are disabled for the sake of brevity.

*argon2_cffi*

C extension for the Argon2 hashing function. Argon2 was chosen as it is the most promising new algorithm to emerge in recent times: https://en.wikipedia.org/wiki/Argon2

*passlib*

Manages the salting, hashing and verification of user passwords (depends on argon2_cffi).

*aioredis*

An asynchronous Redis library. sanic is async, so it made sense to minimise the amount of blocking DB interactions.


## Design

Redis was chosen as the database as I am familiar with it, it is simple to use and it is extremely fast. I had initially attempted to use DynamoDB, but found that I was spending too much time trying to learn its intricacies. Redis, in contrast, is trivial to set up and start using.

Traditional database models are not used here. Initially, I tried to find a Redis ORM (similar to the one that we had created in Digit Game Studios), but none met my expectations. One potential candidate was *astra*. For the sake of simplicity, I reverted to using manual Redis commands.


# Running
> docker-compose -f docker-compose.yml up -d

The API should be available at `127.0.0.1:9443`.

###Tests
> $ pip install --upgrade -r requirements.txt && pytest

Functionality in the acceptance tests is not separated out, in order to allow the entire flow to be tested atomically and to avoid duplication. I would argue that such separation is unnecessary as a failure at any step in the process will break the entire functionality.


# Known issues

* Warnings are raised on some tests, but appear not to affect the outcome.
* The same database is used between the live application and tests, due to a failure to discover how to effectively override the globally shared reference to the Redis instance.
* Some modules are named generically, which could interfere with installed packages/modules.
* While transactions (MULTI/EXEC) are used, atomicity cannot be guaranteed.
* In accordance with the principle of least privilege, JSON Patch is deliberately not used; the client should (in this circumstance) not have the power to dictate to the server how to process requests.
