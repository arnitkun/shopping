## Steps to run
 - clone the repository: ``https://github.com/arnitkun/shopping``
 - checkout ``master`` branch
 - from root of the repository, run ``docker-compose up -d --build``
 - Check ```Shopping.postman_collection``` in the root of the repository for all the api examples.
 - To run tests, run ```pytest test_main.py``` from the root of the repository. 
 - To update the db instance url, db name and the server port update the app config file, this can also be an environment variable. 
Note: Mongodb is used. Uses transactions.
